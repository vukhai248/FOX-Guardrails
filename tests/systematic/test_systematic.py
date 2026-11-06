"""Systematic checks S1–S5 (plan 07/11/2026). Each must report zero failures.

A failure here means a whole class of input broke, not one sentence: run
`python -X utf8 -m tests.systematic.run_report <out.md>` to see every failing case grouped.
"""

import pytest

from . import checks, oracle

needs_oracle = pytest.mark.skipif(not oracle.available(),
                                  reason="needs node and web_ui/node_modules (markdown-to-jsx)")


def _assert_none(failures):
    shown = "\n".join(repr({k: v for k, v in f.items() if k in ("kind", "form", "url", "text", "out")})
                      for f in failures[:10])
    assert not failures, f"{len(failures)} failures, first ones:\n{shown}"


@pytest.mark.oracle
@needs_oracle
def test_s1_no_rendered_url_leaves_the_allowlist():
    _assert_none(checks.s1_links())


@pytest.mark.oracle
@needs_oracle
def test_s2_parse_url_agrees_with_whatwg_on_external_hosts():
    _assert_none(checks.s2_urls())


def test_s3_audit_never_keeps_a_decodable_secret():
    _assert_none(checks.s3_audit())


def test_s4_metamorphic_relations_hold():
    _assert_none(checks.s4_metamorphic())


def test_s5_benign_answers_are_allowed_unchanged():
    _assert_none(checks.s5_benign())
