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


if __name__ == "__main__":
    app()
