"""Console script `fox-guard`. Các lệnh `serve`, `proxy`, `audit why` thêm ở B6–B8."""

import csv
import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from fox_guard import __version__

# Console Windows mặc định cp1252, không in được tiếng Việt.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

app = typer.Typer(help="FOX-Guard: guardrails phát hiện prompt injection và che PII.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """FOX-Guard CLI."""


@app.command()
def version() -> None:
    """In phiên bản FOX-Guard."""
    typer.echo(__version__)


rules_app = typer.Typer(help="Lớp 2: gói luật phát hiện prompt injection.", no_args_is_help=True)
app.add_typer(rules_app, name="rules")


@rules_app.command("list")
def rules_list() -> None:
    """Liệt kê các luật: id, nhóm, kỹ thuật, trạm, mức."""
    from fox_guard.detectors.rules import load_rules

    for item in load_rules():
        rule = item.rule
        stations = ",".join(rule.stations)
        typer.echo(f"{rule.id}\tnhóm {rule.group}\t{rule.technique}\t{stations}\t{rule.severity}")


@rules_app.command("report")
def rules_report(
    cases: Annotated[Path, typer.Argument(help="JSONL, mỗi dòng có id, text, station (mặc định input).")],
    out: Annotated[Path, typer.Option("--out", help="File CSV kết quả.")],
) -> None:
    """Chạy luật trên từng ca và xuất CSV "luật nào bắt ca nào" cho Phần C."""
    from fox_guard.detectors.rules import run_rules
    from fox_guard.normalize import normalize

    rows = 0
    with cases.open(encoding="utf-8") as source, out.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["id", "station", "matched_rules", "max_severity"])
        for line in source:
            if not line.strip():
                continue
            case = json.loads(line)
            station = case.get("station", "input")
            findings = run_rules(normalize(case["text"]), station)
            ranks = {"medium": 1, "high": 2}
            top = max((f.severity for f in findings), key=ranks.__getitem__, default="")
            matched = ";".join(f.detector.removeprefix("rules:") for f in findings)
            writer.writerow([case["id"], station, matched, top])
            rows += 1
    typer.echo(f"{rows} ca → {out}")


audit_app = typer.Typer(help="Lớp 4: tra cứu nhật ký quyết định (chỉ chứa text đã che).",
                        no_args_is_help=True)
app.add_typer(audit_app, name="audit")
DbOption = Annotated[Path, typer.Option("--db", help="File SQLite audit.")]


def _open(db: Path):
    """Open an existing audit DB; a wrong --db path is an error, never a new empty database."""
    from fox_guard.audit.store import AuditStore

    try:
        return AuditStore.open_existing(db)
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(1) from error


@audit_app.command("why")
def audit_why(decision_id: str, db: DbOption = Path("var/fox_guard.sqlite")) -> None:
    """In lý do của một quyết định từ bản ghi audit (không cần text gốc)."""

    row = _open(db).get(decision_id)
    if row is None:
        typer.echo(f"Không tìm thấy quyết định {decision_id}", err=True)
        raise typer.Exit(1)
    typer.echo(f"{row['ts']}  trạm={row['station']}  nguồn={row['source']}  "
               f"hành động={row['action']}  rủi ro={row['risk']}  giảm cấp={bool(row['degraded'])}")
    for reason in json.loads(row["reasons_json"]):
        typer.echo(f"  - {reason}")
    for finding in json.loads(row["findings_json"]):
        typer.echo(f"    {finding['detector']} [{finding['severity']}] {finding['evidence']}")
    typer.echo(f"  văn bản (đã che): {row['text_redacted']}")


@audit_app.command("export")
def audit_export(out: Annotated[Path, typer.Argument(help="File JSONL kết quả.")],
                 db: DbOption = Path("var/fox_guard.sqlite")) -> None:
    """Xuất toàn bộ quyết định ra JSONL (cho Phần C và dashboard)."""

    typer.echo(f"{_open(db).export_jsonl(out)} quyết định → {out}")


if __name__ == "__main__":
    app()
