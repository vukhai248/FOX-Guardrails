"""Download the external benchmarks into data/raw/ (gitignored). Run only after the owner approves.

python -X utf8 -m eval.datasets.external.fetch [bipia] [jbb] [openpii]
    [cyberseceval] [notinject] [multijail] [llmail]

Sources, licences and sizes (checked 07/11/2026 via the GitHub / Hugging Face APIs):
- BIPIA  github.com/microsoft/BIPIA (MIT). Email QA + Table QA contexts and the text attack files,
         about 1.9 MB. WebQA/Summarization need NewsQA/XSum and are not fetched.
- JBB    huggingface.co/datasets/JailbreakBench/JBB-Behaviors (MIT), 2 CSV ≈ 44 KB;
         github.com/JailbreakBench/artifacts (MIT), PAIR + GCG artifacts ≈ 0.5 MB.
- openpii huggingface.co/datasets/ai4privacy/pii-masking-openpii-1.5m (CC-BY-4.0, synthetic PII).
         The full files are 1–4 GB, so only `language == 'vi'` rows of the validation split are read
         through the datasets-server API (1,000 rows by default).
C3 (research 07/11, docs/research/benchmark-datasets-2026-11.md), all MIT:
- cyberseceval  github.com/meta-llama/PurpleLlama CybersecurityBenchmarks/datasets/prompt_injection
                (MIT, folder licence): EN 251 cases + multilingual 1,004 (50 Vietnamese), ≈ 1.5 MB.
- notinject     huggingface.co/datasets/leolee99/NotInject: 339 benign sentences with trigger words, 35 KB.
- multijail     huggingface.co/datasets/DAMO-NLP-SG/MultiJail: 315 harmful questions × 10 languages, CSV.
- llmail        huggingface.co/datasets/microsoft/llmail-inject-challenge: the files are 1.9 GB, so only
                emails_for_fp_tests.json (0.1 MB) + an evenly spaced sample of Phase 2 submissions
                (600 rows by default, datasets-server API) are fetched.
"""

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAW = Path(__file__).resolve().parents[3] / "data" / "raw"
UA = {"User-Agent": "fox-guard-thesis-eval/0.1"}

BIPIA = "https://raw.githubusercontent.com/microsoft/BIPIA/main/benchmark/"
BIPIA_FILES = [
    "email/train.jsonl",
    "email/test.jsonl",
    "table/train.jsonl",
    "table/test.jsonl",
    "text_attack_train.json",
    "text_attack_test.json",
]
JBB_FILES = {
    "jbb/harmful-behaviors.csv": "https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors/resolve/main/data/harmful-behaviors.csv",
    "jbb/benign-behaviors.csv": "https://huggingface.co/datasets/JailbreakBench/JBB-Behaviors/resolve/main/data/benign-behaviors.csv",
}
JBB_ARTIFACTS = "https://raw.githubusercontent.com/JailbreakBench/artifacts/main/attack-artifacts/"
JBB_ARTIFACT_FILES = [
    "PAIR/black_box/vicuna-13b-v1.5.json",
    "PAIR/black_box/llama-2-7b-chat-hf.json",
    "GCG/white_box/vicuna-13b-v1.5.json",
    "GCG/white_box/llama-2-7b-chat-hf.json",
]


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as response:
        return response.read()


def save(rel: str, data: bytes) -> None:
    path = RAW / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"{rel}: {len(data) / 1024:.1f} KB")


def fetch_bipia() -> None:
    for rel in BIPIA_FILES:
        save(f"bipia/{rel}", get(BIPIA + rel))


def fetch_jbb() -> None:
    for rel, url in JBB_FILES.items():
        save(rel, get(url))
    for rel in JBB_ARTIFACT_FILES:
        try:
            save(f"jbb/artifacts/{rel}", get(JBB_ARTIFACTS + rel))
        except Exception as error:  # an artifact missing upstream is reported, not fatal
            print(f"skip {rel}: {error}")


CSE = "https://raw.githubusercontent.com/meta-llama/PurpleLlama/main/CybersecurityBenchmarks/datasets/prompt_injection/"
HF = "https://huggingface.co/datasets/"


def fetch_cyberseceval() -> None:
    for name in ("prompt_injection.json", "prompt_injection_multilingual_machine_translated.json"):
        save(f"cyberseceval/{name}", get(CSE + name))


def fetch_notinject() -> None:
    for level in ("one", "two", "three"):
        name = f"NotInject_{level}-00000-of-00001.parquet"
        save(f"notinject/{name}", get(f"{HF}leolee99/NotInject/resolve/main/data/{name}"))


def fetch_multijail() -> None:
    save("multijail/MultiJail.csv", get(f"{HF}DAMO-NLP-SG/MultiJail/resolve/main/MultiJail.csv"))


def fetch_llmail(rows: int = 600, total: int = 0) -> None:
    base = f"{HF}microsoft/llmail-inject-challenge/resolve/main/data/"
    for name in ("emails_for_fp_tests.json", "objectives_descriptions.json", "scenarios.json"):
        save(f"llmail/{name}", get(base + name))
    if not total:
        size = json.loads(get("https://datasets-server.huggingface.co/size?dataset=microsoft/llmail-inject-challenge"))
        total = next(s["num_rows"] for s in size["size"]["splits"] if s["split"] == "Phase2")
    stride, out = max(1, total // rows), []
    for offset in range(0, stride * rows, stride * 10):
        query = urllib.parse.urlencode({"dataset": "microsoft/llmail-inject-challenge", "config": "default",
                                        "split": "Phase2", "offset": offset, "length": 10})
        for wait in (0, 5, 15, 45, 90):  # datasets-server answers 429 when paged too fast
            time.sleep(wait)
            try:
                page = json.loads(get(f"https://datasets-server.huggingface.co/rows?{query}"))
                break
            except urllib.error.HTTPError as error:
                if error.code != 429:
                    raise
        else:
            raise RuntimeError("datasets-server kept answering 429")
        out.extend(r["row"] for r in page["rows"])
        time.sleep(1.5)
    save("llmail/phase2_sample.jsonl", "\n".join(json.dumps(r, ensure_ascii=False) for r in out).encode())


def fetch_openpii(rows: int = 1000, page: int = 100) -> None:
    out = []
    for offset in range(0, rows, page):
        query = urllib.parse.urlencode(
            {
                "dataset": "ai4privacy/pii-masking-openpii-1.5m",
                "config": "default",
                "split": "validation",
                "where": "\"language\"='vi'",
                "offset": offset,
                "length": page,
            }
        )
        for attempt in range(3):
            try:
                body = json.loads(get("https://datasets-server.huggingface.co/filter?" + query))
                break
            except Exception:
                time.sleep(5 * (attempt + 1))
        else:
            raise RuntimeError("datasets-server did not answer")
        batch = [r["row"] for r in body.get("rows", [])]
        for row in batch:
            row.pop("mbert_tokens", None)
            row.pop("mbert_token_classes", None)
        out += batch
        if len(batch) < page:
            break
    save("openpii/vi_validation.jsonl", "\n".join(json.dumps(r, ensure_ascii=False) for r in out).encode())


if __name__ == "__main__":
    wanted = set(sys.argv[1:]) or {"bipia", "jbb", "openpii"}
    for name, fn in (("bipia", fetch_bipia), ("jbb", fetch_jbb), ("openpii", fetch_openpii),
                     ("cyberseceval", fetch_cyberseceval), ("notinject", fetch_notinject),
                     ("multijail", fetch_multijail), ("llmail", fetch_llmail)):
        if name in wanted:
            fn()
