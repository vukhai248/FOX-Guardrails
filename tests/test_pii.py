"""Lớp 3 PII: recognizers, checksums, hard negatives, vault, station policy, log redaction."""

import json
from pathlib import Path

import pytest

from fox_guard import Guard, GuardContext
from fox_guard.normalize import normalize
from fox_guard.pii.policy import mask_value, province_only
from fox_guard.pii.recognizers import card_brand_ok, cccd_ok, detect_pii, luhn_ok, tax_id_ok
from fox_guard.pii.vault import PiiVault

FIXTURES = Path(__file__).parent / "fixtures"


def found(text):
    return [(m.entity, m.value) for m in detect_pii(normalize(text))]


def _cases(name):
    return [json.loads(line) for line in (FIXTURES / name).read_text("utf-8").splitlines() if line.strip()]


def test_checksums():
    assert luhn_ok("4242424242424242") and not luhn_ok("4242424242424241")
    assert card_brand_ok("4242424242424242") and card_brand_ok("9704000000000018")
    assert not card_brand_ok("1234567812345670")
    assert tax_id_ok("0100123453") and not tax_id_ok("0100123454")
    assert cccd_ok("079203001234") and not cccd_ok("003203001234") and not cccd_ok("079903001234")


@pytest.mark.parametrize("case", _cases("pii_positive.jsonl"), ids=lambda c: c["id"])
def test_synthetic_pii_is_detected(case):
    entities = detect_pii(normalize(case["text"]))
    assert any(m.entity == case["entity"] for m in entities), [(m.entity, m.value) for m in entities]


@pytest.mark.parametrize("case", _cases("pii_hard_negative.jsonl"), ids=lambda c: c["id"])
def test_hard_negatives_have_no_pii(case):
    assert found(case["text"]) == []


def test_fixture_sizes():
    assert len(_cases("pii_positive.jsonl")) >= 120
    assert len(_cases("pii_hard_negative.jsonl")) >= 30


def test_obfuscated_numbers_map_back_to_clean():
    text = "sdt 0 9 1 2 . 3 4 5 . 6 7 8 nha"
    [match] = detect_pii(normalize(text))
    assert match.entity == "VN_PHONE" and normalize(text).clean[match.start:match.end] == match.value
    assert found("số không chín một hai ba bốn năm sáu bảy tám")[0][0] == "VN_PHONE"


def test_contextual_entities_need_context():
    assert found("mã sản phẩm 100234567") == []
    assert found("CMND 100234567") == [("VN_CMND", "100234567")]
    assert found("0071000123456") == []
    assert found("stk 0071000123456") == [("VN_BANK_ACCOUNT", "0071000123456")]
    assert found("MST 0394217863")[0][0] == "VN_TAX_ID"


def test_all_digit_card_is_not_treated_as_hex_hash():
    assert found("thẻ 4242424242424242") == [("CREDIT_CARD", "4242424242424242")]


def test_masks():
    assert mask_value("VN_PHONE", "0912345678") == "0912***678"
    assert mask_value("VN_CCCD", "079203001234") == "0792******34"
    assert mask_value("CREDIT_CARD", "4242 4242 4242 4242") == "[số thẻ đã che]"
    assert mask_value("OTP", "482913") == "[đã xoá]"
    assert mask_value("EMAIL", "synthetic.user@example.com") == "s***@example.com"
    assert province_only("12 Lý Thường Kiệt, phường Hàng Bài, quận Hoàn Kiếm, Hà Nội") == "Hà Nội"


def test_vault_stable_placeholders_owner_and_ttl():
    now = [0.0]
    vault = PiiVault(ttl_seconds=60, clock=lambda: now[0])
    first = vault.placeholder("s", "u1", "VN_PHONE", "0912 345 678")
    assert first == "<PHONE_1>" and vault.placeholder("s", "u1", "VN_PHONE", "0912345678") == first
    assert vault.placeholder("s", "u1", "VN_PHONE", "0987654321") == "<PHONE_2>"
    assert vault.placeholder("other", "u2", "VN_PHONE", "0912345678") == "<PHONE_1>"  # per session
    now[0] = 61
    assert vault.lookup("s", "<PHONE_1>") is None  # expired, gone from memory


def _ctx(station, user="user-a", **extra):
    return GuardContext(session_id="s1", user_ref=user, station=station, **extra)


def test_round_trip_restores_only_for_owner():
    guard = Guard()
    decision = guard.check_input("SĐT mình 0912345678, CCCD 079203001234", _ctx("input"))
    assert decision.action == "mask" and decision.risk == "low"
    assert "0912345678" not in decision.text and "<PHONE_1>" in decision.text and "<CCCD_1>" in decision.text
    answer = "Shop gọi <PHONE_1>; CCCD <CCCD_1> đã ghi nhận."
    owner = guard.check_output(answer, _ctx("output"))
    assert "0912345678" in owner.text and "079203001234" not in owner.text and "0792******34" in owner.text
    stranger = guard.check_output(answer, _ctx("output", user="user-b"))
    assert "0912345678" not in stranger.text and "0912***678" in stranger.text


def test_context_policy_by_source_and_intent():
    guard = Guard()
    tool = ("Người nhận: Nguyễn Văn An, SĐT 0987654321, "
            "12 Lý Thường Kiệt, phường Hàng Bài, quận Hoàn Kiếm, Hà Nội")
    status = guard.check_context(tool, _ctx("context", source="tool:order_lookup", intent="order_status"))
    assert "Lý Thường Kiệt" not in status.text and status.text.endswith("Hà Nội")
    assert "Nguyễn Văn An" in status.text and "0987654321" not in status.text
    change = guard.check_context(tool, _ctx("context", source="tool:order_lookup", intent="address_change"))
    assert "Lý Thường Kiệt" in change.text
    review = guard.check_context("anh Trần Minh Khoa sđt 0901234567 khen máy",
                                 _ctx("context", source="review"))
    assert "Trần Minh Khoa" not in review.text and "0901234567" not in review.text
    # A third party's number from a review is never restored, even for the requester.
    placeholder = next(p for p in ("<PHONE_1>", "<PHONE_2>", "<PHONE_3>") if guard.vault.lookup("s1", p)
                       and guard.vault.lookup("s1", p).value == "0901234567")
    assert "0901234567" not in guard.check_output(f"Gọi {placeholder}", _ctx("output")).text


def test_output_masks_raw_secrets_and_flags_unknown_placeholders():
    guard = Guard()
    decision = guard.check_output("Thẻ 4242 4242 4242 4242, OTP là 482913. Gọi <PHONE_9>", _ctx("output"))
    assert "[số thẻ đã che]" in decision.text and "482913" not in decision.text
    assert "<PHONE_9>" in decision.text
    assert decision.risk == "medium"
    assert any(f.detector == "pii:unknown_placeholder" for f in decision.findings)


def test_pii_findings_do_not_raise_risk_and_evidence_is_masked():
    decision = Guard().check_input("thẻ 4242424242424242 mã OTP là 123456", _ctx("input"))
    assert decision.risk == "low"
    assert all("4242424242424242" not in f.evidence and "123456" not in f.evidence for f in decision.findings)


def test_redact_for_log_never_contains_raw_pii():
    guard = Guard()
    raw_values = []
    for case in _cases("pii_positive.jsonl"):
        if case["entity"] in ("PERSON", "VN_ADDRESS"):
            continue
        redacted = guard.redact_for_log(case["text"], _ctx("output"))
        raw_values.append((case["id"], case["value"], redacted))
    leaked = [(cid, value) for cid, value, redacted in raw_values if value in redacted]
    assert not leaked
    assert guard.redact_for_log("gọi <PHONE_1>", _ctx("output")) == "gọi [PHONE]"


def test_pii_can_be_disabled():
    from fox_guard.config import GuardConfig

    guard = Guard(GuardConfig.model_validate({"pii": {"enabled": False}}))
    decision = guard.check_input("SĐT 0912345678", _ctx("input"))
    assert decision.action == "allow" and "0912345678" in decision.text


@pytest.mark.slow
def test_pii_2kb_p95(benchmark):
    text = ("Giao tới 12 Lý Thường Kiệt, phường Hàng Bài, quận Hoàn Kiếm, Hà Nội. SĐT 0912345678. "
            "Giá 25.990.000đ. ") * 20
    normalized = normalize(text[:2048])
    benchmark.pedantic(lambda: detect_pii(normalized), rounds=40, iterations=1, warmup_rounds=3)
    timings = sorted(benchmark.stats.stats.data)
    p95 = timings[int(0.95 * (len(timings) - 1))] * 1000
    print(f"\nB5 PII 2KB p95={p95:.3f} ms")
    assert p95 < 100
