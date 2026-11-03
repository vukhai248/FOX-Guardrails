"""Console script `fox-guard`. Các lệnh `serve`, `proxy`, `audit why` thêm ở B6–B8."""

import sys

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


if __name__ == "__main__":
    app()
