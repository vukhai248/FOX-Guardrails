"""Fill {SLOT} placeholders of an independently written PII set with fake, checksum-valid values.

The sentences come from a separate agent that never saw the recognizers; only the values are ours.
Usage: python -X utf8 scripts/fill_pii_slots.py IN.jsonl OUT_POS.jsonl OUT_NEG.jsonl
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_pii_fixtures as gen  # noqa: E402

gen.RNG.seed(424242)
SLOTS = {
    "PHONE": ("VN_PHONE", gen.phone), "CCCD": ("VN_CCCD", gen.cccd),
    "CMND": ("VN_CMND", lambda: gen.digits(9)),
    "CARD": ("CREDIT_CARD", gen.card),
    "BANK": ("VN_BANK_ACCOUNT", lambda: gen.digits(random.choice([10, 12, 13]))),
    "MST": ("VN_TAX_ID", gen.mst), "OTP": ("OTP", lambda: gen.digits(6)),
    "PASSWORD": ("PASSWORD", lambda: "Shop#" + gen.digits(4)),
    "EMAIL": ("EMAIL", lambda: f"synthetic.{gen.digits(3)}@example.com"),
    "PASSPORT": ("VN_PASSPORT", lambda: "C" + gen.digits(7)),
    "PLATE": ("VN_LICENSE_PLATE", lambda: f"{gen.RNG.randint(11, 99)}A-{gen.digits(3)}.{gen.digits(2)}"),
    "BHYT": ("VN_HEALTH_INSURANCE", lambda: "DN" + gen.digits(13)),
    "NAME": ("PERSON", lambda: gen.RNG.choice(gen.NAMES)),
    "ADDRESS": ("VN_ADDRESS", lambda: f"{gen.RNG.randint(1, 300)} {gen.RNG.choice(gen.STREETS)}, "
                                      f"{gen.RNG.choice(gen.WARDS)}, {gen.RNG.choice(gen.CITIES)}"),
}
random.seed(424242)
pos, neg = [], []
for line in open(sys.argv[1], encoding="utf-8"):
    if not line.strip():
        continue
    case = json.loads(line)
    if case["label"] == "benign":
        neg.append({"id": case["id"], "text": case["text"]})
        continue
    slot = next(name for name in SLOTS if "{" + name + "}" in case["text"])
    entity, maker = SLOTS[slot]
    value = maker()
    pos.append({"id": case["id"], "entity": entity, "value": value,
                "text": case["text"].replace("{" + slot + "}", value)})
for path, rows in ((sys.argv[2], pos), (sys.argv[3], neg)):
    with open(path, "w", encoding="utf-8", newline="\n") as out:
        out.writelines(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
print(f"positive={len(pos)} benign={len(neg)}")
