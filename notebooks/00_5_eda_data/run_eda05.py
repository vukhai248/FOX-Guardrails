"""Generate and execute one EDA 0.5 notebook at a time."""

import argparse
import json

import nbformat
from eda05 import AUDIT, ROOT, read_json
from nbclient import NotebookClient

TRACKER = ROOT / "docs" / "research" / "eda-0.5-data-review.md"
RESULTS = ROOT / "var" / "eda05"


def make_notebook(spec):
    source = spec["id"]
    intro = f"""# 0.5 · EDA sàng lọc {spec["name"]}

- Nguồn: [{spec["name"]}]({spec["url"]})
- Revision: {spec["revision"]}
- Quyền dùng theo hồ sơ nguồn: {spec["license"]}
- Đơn vị text: {spec["unit"]}

EDA 0.5 quyết định vai trò của nguồn trước EDA 01. Notebook đọc tệp pin cục bộ,
kiểm hash, thống kê schema, số lượng, ngôn ngữ, nhãn, nhóm, độ dài và trùng benchmark.
Nhãn/ngôn ngữ do nguồn cung cấp. Output chỉ chứa số liệu và metadata tổng hợp.
Đối chiếu trùng dùng NFKC, casefold và gộp khoảng trắng.
"""
    if spec["status"] == "blocked":
        intro += "\n**Chỉ kiểm metadata.** Tệp dữ liệu trả HTTP 403, chưa có EDA theo dòng.\n"
    code = f"""from pathlib import Path
import json
import sys

here = Path.cwd().resolve()
project = next(
    folder for folder in (here, *here.parents)
    if (folder / "notebooks" / "00_5_eda_data" / "eda05.py").is_file()
)
sys.path.insert(0, str(project / "notebooks" / "00_5_eda_data"))
from eda05 import examine

result = examine({source!r})
print("EDA05_RESULT=" + json.dumps({{
    k: v for k, v in result.items() if k not in ("files_summary", "distributions")
}}, ensure_ascii=False))
"""
    return nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell(intro),
            nbformat.v4.new_code_cell(code),
            nbformat.v4.new_markdown_cell(
                f"**Đề xuất: {spec['decision']}.** {spec['reason']}\n\n"
                "Khi dùng cho huấn luyện, cần ánh xạ nhãn, rà chất lượng và khóa chia theo nhóm."
            ),
        ],
        metadata={"kernelspec": {"name": "python3", "language": "python", "display_name": "Python 3"}},
    )


def evidence(notebook):
    for cell in notebook.cells:
        for output in cell.get("outputs", []):
            for line in output.get("text", "").splitlines():
                if line.startswith("EDA05_RESULT="):
                    return json.loads(line.removeprefix("EDA05_RESULT="))
    raise ValueError("Notebook không có kết quả EDA")


def report(specs):
    content = [
        "# EDA 0.5 · Nhật ký sàng lọc dữ liệu FOX-Guardrails",
        "",
        "Phạm vi là INPUT đa lĩnh vực cho Prompt Guard 2, nhãn 0/1 và cân bằng VI–EN.",
        "EDA 0.5 quyết định giữ nguồn nào trước khi xây tập huấn luyện. TMĐT là một lát cắt.",
        "",
        "Quy trình gồm tải theo revision, kiểm digest, chạy từng notebook rồi cập nhật nhật ký.",
        "Số liệu tính theo dòng nguồn. Với hội thoại, đơn vị text là lượt người dùng.",
        "Đối chiếu benchmark dùng các trường tham chiếu trong manifest EDA 01.",
        "",
        "| Nguồn và notebook | Tình trạng | Dòng gốc | Text duy nhất | Lượt khớp benchmark¹ | Đề xuất |",
        "|---|---|---:|---:|---:|---|",
    ]
    notes = []
    for source, spec in specs.items():
        file = RESULTS / f"{source}.json"
        if not file.exists():
            continue
        result = read_json(file)
        notebook = f"[{spec['name']}](../../notebooks/00_5_eda_data/00_5_{source}.ipynb)"
        blocked = result["status"] == "blocked"
        state = "403 · chỉ metadata" if blocked else f"{result['files']} lượt đọc"
        match_display = (
            "—" if blocked or spec.get("locked") else (f"{sum(result.get('benchmark_hits', {}).values()):,}")
        )
        content.append(
            f"| {notebook} | {state} | {result['rows']:,} | "
            f"{result.get('unique_texts', 0):,} | {match_display} | {spec['decision']} |"
        )
        notes.append(f"- **{spec['name']}.** {spec['reason']}")
        if result.get("benchmark_hits"):
            hits_by_set = ", ".join(f"{name}: {count:,}" for name, count in result["benchmark_hits"].items())
            notes.append(f"  Khớp benchmark: {hits_by_set}.")
        if result.get("missing_refs"):
            notes.append("  Tệp benchmark còn thiếu: " + ", ".join(result["missing_refs"]) + ".")
        pairs = [x for x in result.get("cross_split", []) if x["text trùng"] or x["nhóm trùng"]]
        if pairs:
            top = max(pairs, key=lambda x: (x["text trùng"], x["nhóm trùng"]))
            notes.append(
                f"  Cặp split nhiều text trùng nhất ({top['split A']} / {top['split B']}) có "
                f"{top['text trùng']:,} text và {top['nhóm trùng']:,} ID nhóm trùng."
            )
    content.extend(
        [
            "",
            "¹ Tổng lượt theo từng benchmark. Một dòng có thể khớp nhiều benchmark.",
            "",
            "## Nhận xét từng nguồn",
            "",
            *notes,
            "",
            "Xem [manifest tải](../../notebooks/00_5_eda_data/downloads.json) và "
            "[quy tắc đọc từng nguồn](../../notebooks/00_5_eda_data/sources.json).",
            "",
        ]
    )
    if TRACKER.exists():
        marker = "## Quyết định sau đối chiếu"
        _, separator, assessment = TRACKER.read_text(encoding="utf-8").partition(marker)
        if separator:
            content.append(marker + assessment)
    TRACKER.write_text("\n".join(content), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*")
    args = parser.parse_args()
    specs = read_json(AUDIT / "sources.json")
    ordered = args.sources or list(specs)
    RESULTS.mkdir(parents=True, exist_ok=True)
    TRACKER.parent.mkdir(parents=True, exist_ok=True)
    for source in ordered:
        print(f"EDA 0.5: {source}", flush=True)
        notebook = make_notebook(specs[source])
        NotebookClient(notebook, timeout=900, resources={"metadata": {"path": str(AUDIT)}}).execute()
        result = evidence(notebook)
        nbformat.validate(notebook)
        nbformat.write(notebook, AUDIT / f"00_5_{source}.ipynb")
        (RESULTS / f"{source}.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        report(specs)
        print(f"  {result['status']}; {result['rows']:,} rows; tracker updated", flush=True)


if __name__ == "__main__":
    main()
