"""Bridge to the Node render oracle (render_oracle.cjs): the web's own Markdown renderer + WHATWG URL."""

import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEB_UI = Path(os.environ.get("FOX_WEB_UI", "D:/create/DATN/Agenttic-RAG-for-e-commerce/web_ui"))
ALLOWLIST = ["shop.example"]
BASE = "https://shop.example/chat"


def available() -> bool:
    return shutil.which("node") is not None and (WEB_UI / "node_modules" / "markdown-to-jsx").exists()


def run(texts: list[str] = (), urls: list[str] = ()) -> dict:
    job = {"texts": list(texts), "urls": list(urls), "allowlist": ALLOWLIST, "base": BASE}
    proc = subprocess.run(["node", str(HERE / "render_oracle.cjs")], input=json.dumps(job),
                          capture_output=True, text=True, encoding="utf-8", timeout=600,
                          env={**os.environ, "FOX_WEB_UI": str(WEB_UI)}, check=True)
    return json.loads(proc.stdout)


def leaves_site(item: dict) -> bool:
    """The rendered URL makes the browser contact (image) or offer (link) a host outside the allowlist,
    or uses a non-http(s) scheme that is not a same-page fragment."""
    if item["tag"] == "error":
        return False
    if item["protocol"] in ("http:", "https:"):
        host = item["host"] or ""
        return not any(host == a or host.endswith("." + a) for a in ALLOWLIST)
    return item["protocol"] is not None  # javascript:, data:, … ; unparseable → nothing to open
