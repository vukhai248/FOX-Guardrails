"""ai4privacy openpii (language vi) → PII spans in FOX entity names (Phần C §2.4). Test only.

Label mapping (stated in the report, as the spec requires). Labels FOX does not handle are kept as
`unmapped` so recall is computed only on mapped entities and the rest are listed separately.
Address parts that touch (STREET, BUILDINGNUM, CITY, ZIPCODE separated by spaces/commas) merge into
one VN_ADDRESS span; GIVENNAME/SURNAME next to each other merge into one PERSON span.

Output: data/processed/openpii/test.jsonl (not committed). python -X utf8 -m eval.datasets.external.openpii
"""

import json
from collections import Counter
from pathlib import Path

from ..common import write_jsonl

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "openpii" / "vi_validation.jsonl"
OUT = ROOT / "data" / "processed" / "openpii"

MAPPING = {
    "GIVENNAME": "PERSON", "SURNAME": "PERSON",
    "EMAIL": "EMAIL",
    "TELEPHONENUM": "VN_PHONE",
    "IDCARDNUM": "VN_ID",            # CCCD or CMND: FOX has both, compared as one group
    "CREDITCARDNUMBER": "CREDIT_CARD",
    "TAXNUM": "VN_TAX_ID",
    "PASSPORTNUM": "VN_PASSPORT",
    "STREET": "VN_ADDRESS", "BUILDINGNUM": "VN_ADDRESS", "CITY": "VN_ADDRESS", "ZIPCODE": "VN_ADDRESS",
}
NOT_PII_FOR_FOX = {"DATE", "TIME", "AGE", "GENDER", "SEX", "TITLE", "AMOUNT", "CURRENCY", "BANKNAME"}
MERGE_GAP = set(" ,.-/")


def merge(spans: list[dict], text: str) -> list[dict]:
    out = []
    for span in sorted(spans, key=lambda s: s["start"]):
        prev = out[-1] if out else None
        gap = text[prev["end"]:span["start"]] if prev else None
        if prev and prev["entity"] == span["entity"] and span["entity"] in ("VN_ADDRESS", "PERSON") \
                and len(gap) <= 3 and set(gap) <= MERGE_GAP:
            prev["end"] = span["end"]
            prev["value"] = text[prev["start"]:prev["end"]]
        else:
            out.append(dict(span))
    return out


def build() -> tuple[list[dict], Counter]:
    unmapped = Counter()
    cases = []
    for line in RAW.read_text("utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        text = row["source_text"]
        spans = []
        for mask in row["privacy_mask"]:
            entity = MAPPING.get(mask["label"])
            if entity:
                spans.append({"entity": entity, "start": mask["start"], "end": mask["end"],
                              "value": text[mask["start"]:mask["end"]], "source_label": mask["label"]})
            elif mask["label"] not in NOT_PII_FOR_FOX:
                unmapped[mask["label"]] += 1
        cases.append({"case_id": f"openpii-vi-{row['uid']}", "split": "test", "label": "pii" if spans else "none",
                      "station": "input", "text": text, "spans": merge(spans, text)})
    return cases, unmapped


def main() -> dict:
    cases, unmapped = build()
    write_jsonl(OUT / "test.jsonl", cases)
    summary = {"cases": len(cases), "entities": dict(Counter(s["entity"] for c in cases for s in c["spans"])),
               "unmapped_labels": dict(unmapped)}
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return summary


if __name__ == "__main__":
    main()
