"""Read pinned sources and profile their suitability for FOX INPUT."""

import bz2
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

import pandas as pd
from eda_data import PII_PATTERN, SECRET_PATTERN, fingerprint, kind, records, texts, values
from IPython.display import display

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parent.parent


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_records(path):
    if path.name.endswith(".jsonl.bz2"):
        with bz2.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                if line.strip():
                    yield json.loads(line)
    elif path.suffix == ".tsv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            yield from csv.DictReader(stream, delimiter="\t")
    else:
        yield from records(path)


def verify_file(file):
    path = ROOT / file["path"]
    if "digest" not in file:
        if not path.is_file():
            raise FileNotFoundError(path)
        return path
    if path.stat().st_size != file["bytes"]:
        raise ValueError(f"Sai kích thước: {file['path']}")
    algorithm = file["digest_type"]
    digest = hashlib.sha256() if algorithm == "sha256" else hashlib.sha1(usedforsecurity=False)
    if algorithm == "git-blob-sha1":
        digest.update(f"blob {file['bytes']}\0".encode())
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != file["digest"]:
        raise ValueError(f"Sai hash: {file['path']}")
    return path


def records_for(file, source):
    path = verify_file(file)
    if source != "phoatis":
        yield from read_records(path)
        return
    paths = [verify_file(item) for item in file["aligned"]]
    with (
        path.open(encoding="utf-8") as queries,
        paths[0].open(encoding="utf-8") as intents,
        paths[1].open(encoding="utf-8") as tags,
    ):
        for query, intent, tag in zip(queries, intents, tags, strict=True):
            if len(query.split()) != len(tag.split()):
                raise ValueError("Lệch số token và tag PhoATIS")
            yield {"seq.in": query.rstrip("\r\n"), "intent": intent.strip(), "slots": tag.strip()}


def locked_index():
    manifest = read_json(AUDIT / "eda_sources.json")
    found, missing = defaultdict(set), []
    for name, relative, _, cols, _ in manifest["benchmark"]:
        path = ROOT / relative
        if not path.is_file():
            missing.append(name)
            continue
        for row in records(path):
            if name == "CyberSecEval VI" and row.get("speaking_language") != "Vietnamese":
                continue
            for value in texts(row, cols):
                found[fingerprint(value)].add(name)
    return found, missing


def row_texts(row, file, spec):
    columns = file.get("text", spec["text"])
    if spec["id"] == "phoatis":
        return [row["seq.in"]]
    if spec["id"] == "vi_alpaca":
        return ["\n".join(v for v in (row.get("instruction"), row.get("input")) if v)]
    if spec["id"] == "5cd":
        return [
            item["value"]
            for item in row.get("conversations", [])
            if item.get("from") in {"human", "user"} and isinstance(item.get("value"), str)
        ]
    if spec["id"] == "oasst2" and row.get("role") != "prompter":
        return []
    return list(texts(row, columns))


def safe_value(value):
    if isinstance(value, str) and (
        len(value) > 100 or any(ord(char) < 32 or char in "<>|" for char in value)
    ):
        return "[giá trị khác]"
    return str(value)


def subset(row, spec, file):
    """Target strata for measuring coverage. Does not assign FOX labels."""
    source = spec["id"]
    if source == "oasst2":
        return (
            row.get("role") == "prompter"
            and row.get("lang") in {"vi", "en"}
            and row.get("deleted") is False
            and row.get("review_result") is True
            and row.get("synthetic") is False
        )
    if source == "aya":
        return row.get("language_code") in {"vie", "eng"}
    if source == "nailyk":
        return row.get("language") in {"vi", "en"}
    if source == "tensor_trust":
        return file["split"] == "attacks" and row.get("is_self_attack") is False
    return True


def show_table(items, limit=100):
    if items:
        display(pd.DataFrame(items).head(limit))


def examine(source):
    spec = read_json(AUDIT / "sources.json")[source]
    print(f"Nguồn: {spec['url']}")
    print(f"Revision: {spec['revision']} | Quyền dùng: {spec['license']}")
    print(f"Phạm vi text: {spec['unit']}")
    if spec["status"] == "blocked":
        show_table(spec["blocked"])
        return {"status": "blocked", "rows": 0, "files": 0}
    reference, missing_refs = ({}, []) if spec.get("locked") else locked_index()
    schemas, summaries, values_table, overlap = [], [], [], []
    all_text, all_groups, seen_labels = defaultdict(set), defaultdict(set), {}
    total_bench, label_clashes = Counter(), set()
    for file in spec["files"]:
        split = file["split"]
        fields, absent, blank = defaultdict(set), Counter(), Counter()
        histograms = {name: Counter() for name in spec["profile"]}
        languages = defaultdict(Counter)
        source_groups = defaultdict(Counter)
        groups, distinct, matched = set(), set(), Counter()
        n = text_rows = selected = evidence_rows = unique_raw = 0
        lengths, pii, secret = [], 0, 0
        for row in records_for(file, source):
            n += 1
            if not isinstance(row, dict):
                raise TypeError(f"Record không phải object: {file['path']}")
            for key, value in row.items():
                fields[key].add(kind(value))
                if value is not None:
                    absent[key] += 1
                if isinstance(value, str) and not value.strip():
                    blank[key] += 1
            for field, counter in histograms.items():
                found = list(values(row, field.split(".")))
                if not found:
                    counter["[thiếu]"] += 1
                for value in set(map(safe_value, found)):
                    counter[value] += 1
            raw_lang = next(values(row, spec["language"].split(".")), None) if spec["language"] else None
            raw_labels = values(row, spec["label"].split(".")) if spec["label"] else ()
            raw_label = tuple(sorted(set(map(safe_value, raw_labels))))
            if raw_lang is not None:
                lang = safe_value(raw_lang)
                languages[lang][", ".join(raw_label) or "[chưa có nhãn]"] += 1
                if lang in {"vi", "vie", "Vietnamese", "mixed", "Mixed"} and spec["origin"]:
                    for value in values(row, spec["origin"].split(".")):
                        source_groups[lang][safe_value(value)] += 1
            for field in spec["group"]:
                for value in values(row, field.split(".")):
                    if isinstance(value, str | int) and str(value).strip():
                        groups.add((field, fingerprint(str(value))))
            contents = [value for value in row_texts(row, file, spec) if value.strip()]
            if not contents:
                continue
            text_rows += 1
            selected += subset(row, spec, file)
            unique_raw += len(contents)
            hits = set()
            for value in contents:
                digest = fingerprint(value)
                distinct.add(digest)
                lengths.append(len(value))
                hits.update(reference.get(digest, ()))
                if raw_label:
                    old = seen_labels.setdefault(digest, raw_label)
                    if old != raw_label:
                        label_clashes.add(digest)
                if evidence_rows < 1000:
                    pii += bool(PII_PATTERN.search(value))
                    secret += bool(SECRET_PATTERN.search(value))
                    evidence_rows += 1
            matched.update(hits)
        total_bench.update(matched)
        all_text[split].update(distinct)
        all_groups[split].update(groups)
        summaries.append(
            {
                "tệp": file["path"],
                "split": split,
                "dòng": n,
                "dòng có text": text_rows,
                "đơn vị text": unique_raw,
                "text duy nhất": len(distinct),
                "lặp sau chuẩn hóa": unique_raw - len(distinct),
                "dòng mục tiêu sơ bộ": selected,
                "ký tự p50": round(median(lengths)) if lengths else None,
                "ký tự p95": sorted(lengths)[int((len(lengths) - 1) * 0.95)] if lengths else None,
                "ký tự tối đa": max(lengths, default=0),
                "số ID nhóm": len(groups),
                "dòng khớp benchmark theo từng bộ": dict(matched),
                "text kiểm dấu hiệu PII": evidence_rows,
                "tín hiệu PII": pii,
                "tín hiệu secret": secret,
            }
        )
        schemas.extend(
            {
                "tệp": Path(file["path"]).name,
                "trường": key,
                "kiểu": ", ".join(sorted(types)),
                "null/vắng": n - absent[key],
                "chuỗi rỗng": blank[key],
            }
            for key, types in sorted(fields.items())
        )
        for field, counts in histograms.items():
            values_table.extend(
                {"split": split, "trường": field, "giá trị": value, "dòng": count}
                for value, count in counts.most_common(10)
            )
        for lang, counts in sorted(languages.items(), key=lambda x: -x[1].total())[:8]:
            values_table.append(
                {"split": split, "trường": "language × source label", "giá trị": lang, "dòng": dict(counts)}
            )
        for lang, counts in source_groups.items():
            values_table.append(
                {
                    "split": split,
                    "trường": "nguồn upstream theo ngôn ngữ",
                    "giá trị": lang,
                    "dòng": dict(counts.most_common(8)),
                }
            )
    for i, left in enumerate(all_text):
        for right in list(all_text)[i + 1 :]:
            overlap.append(
                {
                    "split A": left,
                    "split B": right,
                    "text trùng": len(all_text[left] & all_text[right]),
                    "nhóm trùng": len(all_groups[left] & all_groups[right]),
                }
            )
    print("Độ đầy đủ, độ dài, số lượng và trùng benchmark")
    show_table(summaries)
    print("Schema thực tế")
    show_table(schemas, 180)
    print("Phân bố nhãn, ngôn ngữ và nguồn từ metadata")
    show_table(values_table, 220)
    print("Trùng giữa split gốc")
    show_table(overlap)
    print("Text có nhãn gốc khác nhau:", len(label_clashes))
    if spec.get("locked"):
        print("Nguồn là benchmark đã khóa. Bỏ qua phép so khớp benchmark với chính nó.")
    else:
        print("Benchmark thiếu tệp:", missing_refs)
    print("Đếm PII/secret trên tối đa 1.000 text đầu mỗi tệp; đây là tín hiệu regex.")
    return {
        "status": "executed",
        "files": len(summaries),
        "rows": sum(r["dòng"] for r in summaries),
        "target_rows": sum(r["dòng mục tiêu sơ bộ"] for r in summaries),
        "unique_texts": len(set().union(*all_text.values())),
        "benchmark_hits": dict(total_bench),
        "cross_split": overlap,
        "label_clashes": len(label_clashes),
        "missing_refs": missing_refs,
        "files_summary": summaries,
        "distributions": values_table,
    }
