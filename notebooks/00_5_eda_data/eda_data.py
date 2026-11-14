"""Read and summarize pinned dataset files for notebook 01."""

import csv
import hashlib
import json
import lzma
import re
import unicodedata
from collections import Counter, defaultdict
from math import isnan
from pathlib import Path
from time import sleep
from urllib.parse import quote, urljoin, urlsplit

import pandas as pd
import pyarrow.parquet as pq
import requests
from IPython.display import display

ALLOWED_SUFFIXES = (".json", ".jsonl", ".csv", ".parquet", ".jsonl.xz", ".txt")
HF_HOSTS = {
    "huggingface.co",
    "cdn-lfs.huggingface.co",
    "cdn-lfs-us-1.huggingface.co",
    "cas-bridge.xethub.hf.co",
    "us.aws.cdn.hf.co",
    "eu.aws.cdn.hf.co",
}


def source_url(spec):
    path = quote(spec["path"], safe="/")
    if spec["host"] == "hf":
        return f"https://huggingface.co/datasets/{spec['repo']}/resolve/{spec['rev']}/{path}"
    return f"https://raw.githubusercontent.com/{spec['repo']}/{spec['rev']}/{path}"


def local_file(staging, spec):
    path = Path(spec["key"], spec.get("local", spec["path"]))
    if (
        path.is_absolute()
        or path.drive
        or ".." in path.parts
        or not path.name.endswith(ALLOWED_SUFFIXES)
        or not re.fullmatch("[0-9a-f]{40}", spec["rev"])
        or not 0 < spec["bytes"] <= 600_000_000
    ):
        raise ValueError("Mục trong manifest nằm ngoài phạm vi tải")
    target = (staging / path).resolve()
    if not target.is_relative_to(staging.resolve()):
        raise ValueError("Đường dẫn đích vượt ra ngoài thư mục raw")
    return target


def check_file(path, spec):
    if path.stat().st_size != spec["bytes"]:
        raise ValueError("Sai kích thước")
    sha = hashlib.sha256()
    blob = hashlib.sha1(f"blob {spec['bytes']}\0".encode(), usedforsecurity=False)
    with path.open("rb") as stream:
        head = stream.read(64)
        stripped = head.lstrip()
        if spec["path"].endswith(".parquet"):
            stream.seek(-4, 2)
            valid = head.startswith(b"PAR1") and stream.read(4) == b"PAR1"
        elif spec["path"].endswith(".xz"):
            valid = head.startswith(b"\xfd7zXZ\x00")
        elif spec["path"].endswith((".json", ".jsonl")):
            valid = stripped.startswith((b"{", b"["))
        else:
            valid = b"\0" not in head and not stripped.startswith(b"<")
        if not valid:
            raise ValueError("Chữ ký tệp không khớp định dạng")
        stream.seek(0)
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(block)
            if spec["digest_type"] == "git-blob-sha1":
                blob.update(block)
    verified = blob.hexdigest() if spec["digest_type"] == "git-blob-sha1" else sha.hexdigest()
    if verified != spec["digest"]:
        raise ValueError("Hash khác metadata nguồn")
    return sha.hexdigest()


def fetch_one(staging, spec):
    path = local_file(staging, spec)
    if path.exists():
        return check_file(path, spec)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    for attempt in range(3):
        try:
            with requests.Session() as session:
                session.trust_env = False
                url = source_url(spec)
                allowed = HF_HOSTS if spec["host"] == "hf" else {"raw.githubusercontent.com"}
                for _ in range(6):
                    parsed = urlsplit(url)
                    if (
                        parsed.scheme != "https"
                        or parsed.hostname not in allowed
                        or parsed.username
                        or parsed.password
                        or parsed.port not in (None, 443)
                    ):
                        raise ValueError("Redirect nằm ngoài máy chủ đã kiểm")
                    with session.get(
                        url,
                        stream=True,
                        allow_redirects=False,
                        timeout=(15, 55),
                        headers={"Accept-Encoding": "identity"},
                    ) as response:
                        if response.is_redirect:
                            url = urljoin(url, response.headers["Location"])
                            continue
                        if response.status_code != 200:
                            raise ValueError(f"HTTP {response.status_code}")
                        mime = response.headers.get("Content-Type", "").lower()
                        if "text/html" in mime or "xml" in mime:
                            raise ValueError("Máy chủ trả trang HTML/XML")
                        size = 0
                        with partial.open("wb") as out:
                            for block in response.iter_content(chunk_size=1024 * 1024):
                                size += len(block)
                                if size > spec["bytes"]:
                                    raise ValueError("Máy chủ trả quá kích thước")
                                out.write(block)
                        break
                else:
                    raise ValueError("Quá nhiều redirect")
            sha = check_file(partial, spec)
            partial.replace(path)
            return sha
        except (OSError, ValueError, requests.RequestException):
            partial.unlink(missing_ok=True)
            if attempt == 2:
                raise
            sleep(attempt + 1)


csv.field_size_limit(2_000_000)


def read_llmail(path):
    with path.open(encoding="utf-8") as stream:
        if stream.readline().strip() != "{":
            raise ValueError("LLMail không khớp cấu trúc object")
        parts = []
        closed = False
        for line in stream:
            if line.rstrip("\r\n") == "}":
                closed = True
                break
            if line.startswith('  "') and parts:
                yield parse_mail_item(parts)
                parts.clear()
            parts.append(line)
        if parts:
            yield parse_mail_item(parts)
        if not closed or any(line.strip() for line in stream):
            raise ValueError("LLMail có phần cuối không hợp lệ")


def parse_mail_item(parts):
    key, row = next(iter(json.loads("{" + "".join(parts).rstrip().removesuffix(",") + "}").items()))
    return {**row, "@key": key}


def records(path):
    if path.suffix == ".parquet":
        parquet = pq.ParquetFile(path, arrow_extensions_enabled=False)
        for batch in parquet.iter_batches(batch_size=2048):
            yield from batch.to_pylist()
    elif path.suffix == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                if None in row or None in row.values():
                    raise ValueError("Dòng CSV lệch schema")
                yield row
    elif path.suffix in {".jsonl", ".xz"}:
        opener = lzma.open if path.suffix == ".xz" else open
        with opener(path, "rt", encoding="utf-8-sig") as stream:
            for line in stream:
                if len(line) > 2_000_000:
                    raise ValueError("Một dòng JSONL vượt giới hạn")
                if line.strip():
                    yield json.loads(line)
    elif path.name == "labelled_unique_submissions_phase1.json":
        yield from read_llmail(path)
    elif path.suffix == ".json" and path.stat().st_size <= 65_000_000:
        with path.open(encoding="utf-8-sig") as stream:
            rows = json.load(stream)
        if not isinstance(rows, list):
            raise ValueError("File JSON phải là danh sách record")
        yield from rows
    else:
        raise ValueError("Định dạng EDA không được hỗ trợ")


def values(node, key):
    if isinstance(node, list):
        for item in node:
            yield from values(item, key)
    elif not key:
        if node is not None:
            yield node
    elif isinstance(node, dict):
        yield from values(node.get(key[0]), key[1:])


def texts(row, fields):
    for field in fields:
        if field == "@mail":
            subject, body = row.get("subject"), row.get("body")
            if isinstance(subject, str) and isinstance(body, str):
                yield f"{subject}\n{body}"
        else:
            yield from (
                value for value in values(row, field.split(".")) if isinstance(value, str) and value.strip()
            )


def fingerprint(text):
    normalized = " ".join(unicodedata.normalize("NFKC", text).casefold().split())
    return hashlib.sha256(normalized.encode("utf-8", errors="surrogatepass")).digest()


def public_name(value):
    if isinstance(value, (str, int, bool)) and re.fullmatch(r"[\w@./ :&+-]{1,48}", str(value)):
        return str(value)
    return "[giá trị khác]"


PII_PATTERN = re.compile(
    r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b"
    r"|(?<!\d)(?:\+84[\s.-]?|0)[35789](?:[\s.-]?\d){8}(?!\d)"
)
MARKUP_PATTERN = re.compile(r"<\s*(?:script|iframe|object|embed)\b|javascript\s*:", re.I)
SECRET_PATTERN = re.compile(
    r"-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----|\b(?:ghp_|github_pat_|sk_live_)[A-Za-z0-9_]{12,}"
)


def load_manifest(project):
    return json.loads((project / "notebooks" / "00_5_eda_data" / "eda_sources.json").read_text(encoding="utf-8"))


def source_table(manifest):
    entries = {item["key"]: item for item in manifest["files"]}
    return pd.DataFrame(
        [
            {
                "mã": key,
                "nguồn": spec["repo"],
                "license khai báo": spec["license"],
                "vai trò": spec["purpose"],
            }
            for key, spec in entries.items()
        ]
    )


def datasets(project, manifest, download_missing=False):
    for name, relative, role, fields, labels in manifest["benchmark"]:
        path = project / relative
        group = name.split(" ·")[0]
        if name.startswith("CyberSecEval"):
            group = "CyberSecEval"
        yield group, name, path, role, fields, labels
    staging = project / "data" / "raw" / "eda01"
    for spec in manifest["files"]:
        key = spec["key"]
        path = local_file(staging, spec)
        if not path.exists() and download_missing:
            fetch_one(staging, spec)
        if path.exists():
            check_file(path, spec)
        fields, labels = manifest["fields"][key]
        yield key, spec["path"], path, spec["purpose"], fields, labels


def is_null(value):
    return value is None or isinstance(value, float) and isnan(value)


def kind(value):
    return {str: "text", list: "list", dict: "object", bool: "bool", int: "int", float: "float"}.get(
        type(value), "other"
    )


def preview(row, visible):
    out = {}
    for name, value in row.items():
        if is_null(value):
            out[name] = None
        elif isinstance(value, str):
            out[name] = public_name(value) if name in visible else f"text · {len(value)} ký tự"
        elif isinstance(value, (list, dict)):
            out[name] = f"{kind(value)} · {len(value)} mục"
        else:
            out[name] = value if name in visible else kind(value)
    return out


def profile(path, name, text_fields, label_fields, selectors, reference, locked):
    totals = Counter()
    nonnull, explicit, blank, seen = Counter(), Counter(), Counter(), Counter()
    types, distribution, overlap = defaultdict(set), defaultdict(Counter), Counter()
    examples = {}
    visible = set(label_fields) | {
        "case_id",
        "id",
        "task",
        "split",
        "position",
        "attack_category",
        "obfuscation",
    }
    for row in records(path):
        if name == "CyberSecEval VI" and row.get("speaking_language") != "Vietnamese":
            continue
        totals["dòng"] += 1
        for column, value in row.items():
            seen[column] += 1
            if is_null(value):
                explicit[column] += 1
            else:
                nonnull[column] += 1
                types[column].add(kind(value))
                blank[column] += isinstance(value, str) and not value.strip()

        for label in label_fields:
            distribution[label].update(public_name(v) for v in values(row, label.split(".")))
        for index, selector in enumerate(selectors or ()):
            if index not in examples and all(row.get(k) == v for k, v in selector.items()):
                examples[index] = {"dòng": totals["dòng"], **preview(row, visible)}
                break
        if selectors is None and len(examples) < 2:
            examples[len(examples)] = {"dòng": totals["dòng"], **preview(row, visible)}

        content = list(texts(row, text_fields))
        totals["thiếu text"] += not content
        if locked:
            for text in content:
                reference[fingerprint(text)].add(name)
        else:
            matched = set()
            for text in content:
                matched.update(reference.get(fingerprint(text), ()))
            totals["trùng benchmark"] += bool(matched)
            overlap.update(matched)
            for key, pattern in (
                ("PII?", PII_PATTERN),
                ("Markup?", MARKUP_PATTERN),
                ("Secret?", SECRET_PATTERN),
            ):
                totals[key] += any(pattern.search(text) for text in content)

    for key in ("thiếu text", "trùng benchmark", "PII?", "Markup?", "Secret?"):
        if key == "thiếu text" or not locked:
            totals.setdefault(key, 0)

    columns = [
        {
            "cột": x,
            "kiểu": ", ".join(sorted(types[x])) or "—",
            "non-null": nonnull[x],
            "null": explicit[x] + totals["dòng"] - seen[x],
            "key vắng": totals["dòng"] - seen[x],
            "chuỗi rỗng": blank[x],
        }
        for x in seen
    ]
    return totals, columns, distribution, overlap, [examples[x] for x in sorted(examples)]


def read_report(project, manifest, download_missing=False):
    reference = defaultdict(set)
    overview, columns, labels, matches, samples = (
        [],
        defaultdict(list),
        defaultdict(list),
        [],
        defaultdict(list),
    )
    selectors = manifest["samples"]
    for group, name, path, role, fields, tags in datasets(project, manifest, download_missing):
        info = {"bộ": group, "tệp/split": name, "vai trò": role}
        if not path.exists():
            overview.append({**info, "dòng": None, "trạng thái": "thiếu tệp"})
            continue
        locked = role.endswith("khóa")
        selection = selectors.get(group, {})
        wanted = selection.get(name, selection.get("*"))
        totals, schema, distribution, overlap, examples = profile(
            path, name, fields, tags, wanted, reference, locked
        )
        overview.append({**info, **totals, "trạng thái": "đã đọc"})
        columns[group].extend({"tệp/split": name, **item} for item in schema)
        for field, counter in distribution.items():
            labels[group].extend(
                {"tệp/split": name, "trường": field, "giá trị": v, "số": n} for v, n in counter.most_common(8)
            )
        matches.extend({"nguồn": group, "benchmark": name, "dòng": count} for name, count in overlap.items())
        samples[group].extend({"tệp/split": name, **item} for item in examples)
    return (
        pd.DataFrame(overview),
        columns,
        labels,
        pd.DataFrame(matches, columns=["nguồn", "benchmark", "dòng"]),
        samples,
    )


def show_dataset(report, group):
    overview, columns, labels, _, samples = report
    display(
        overview.loc[overview["bộ"].eq(group)]
        .drop(columns=["bộ", "vai trò"])
        .dropna(axis=1, how="all")
        .reset_index(drop=True)
    )
    with pd.option_context("display.max_rows", None, "display.max_colwidth", 75):
        if columns[group]:
            display(pd.DataFrame(columns[group]))
        if labels[group]:
            display(pd.DataFrame(labels[group]))
        if samples[group]:
            display(pd.DataFrame(samples[group][:3]).set_index(["tệp/split", "dòng"]).T.fillna("null / vắng"))
