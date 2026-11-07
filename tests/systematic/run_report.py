"""Run S1–S5 once and write a grouped failure report.

python -X utf8 -m tests.systematic.run_report docs/reports/systematic-run-1.md
"""

import sys
import time
from collections import defaultdict
from pathlib import Path

from . import checks, oracle

CHECKS = [
    ("S1 link qua renderer thật", checks.s1_links, True),
    ("S2 parse_url vs WHATWG", checks.s2_urls, True),
    ("S3 audit không giữ bí mật", checks.s3_audit, False),
    ("S4 quan hệ biến đổi", checks.s4_metamorphic, False),
    ("S5 câu hợp lệ giữ nguyên", checks.s5_benign, False),
    ("S6 text gửi đi không mang bí mật", checks.s6_sent_text, False),
    ("S7 độ trễ đầu vào xấu nhất", checks.s7_worst_case_latency, False),
]


def main(out: str) -> None:
    lines = ["# Lần chạy bộ kiểm hệ thống", ""]
    total = 0
    for title, fn, needs_node in CHECKS:
        if needs_node and not oracle.available():
            lines += [f"## {title}", "", "Bỏ qua: không có Node hoặc web_ui/node_modules.", ""]
            continue
        started = time.perf_counter()
        failures = fn()
        total += len(failures)
        groups = defaultdict(list)
        for f in failures:
            groups[(f["kind"], f.get("form", f.get("station", "")))].append(f)
        lines += [f"## {title}: {len(failures)} lỗi ({time.perf_counter() - started:.1f} s)", ""]
        if groups:
            lines += ["| Nhóm | Số ca | Ví dụ |", "| --- | --- | --- |"]
            for (kind, sub), items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
                examples = " · ".join(f"`{(i.get('text') or i.get('url'))!r}`"[:140] for i in items[:3])
                lines.append(f"| {kind} {sub} | {len(items)} | {examples.replace('|', '¦')} |")
            lines.append("")
    lines.insert(1, f"Tổng: **{total}** lỗi.")
    Path(out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "systematic-run.md")
