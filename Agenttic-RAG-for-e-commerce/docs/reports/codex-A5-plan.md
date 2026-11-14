# A5-backend execution ledger

Spec: A-hoan-thien-web.md A5; C2 in codex-phanA.md Claude review 03/11/2026.
Base: e6fb8bd, feat/a-backend, existing isolated worktree .worktrees/a1-backend.

- [x] Migration additive for guard_decision_ids and server-only chat_logs access.
- [x] Guard log-text extension and batch writer with strict payload whitelist.
- [x] Connect /chat, current-turn tools/risk/session/user and error paths.
- [x] Offline transport/DB regressions, independent review, report; ready for checkpoint.

Design/rulings (implementation choices within approved A5 spec):
- Write two rows per completed exchange: role=user then role=agent (actual DB enum), one batch insert. Three exchanges => six messages; no tool payload/args or token is logged. Admin supports these roles.
- Preserve request session_id and verified user_id as specified. The admin groups by session_id; clients should keep UUIDs per user as A1 defines. Backend memory remains namespaced by verified user.
- Current-turn tool list resets each request, unlike accumulated LangGraph tool history. Risk maps safe/needs_ticket/attack to low/medium/high.
- Add guard_client.guard_log returning LogText(message, decision_ids). Off returns original text; enabled requires B's irreversible redaction implementation and otherwise refuses to produce a log. No fallback to raw under guard failure. This extra internal hook avoids confusing restored output/Decision.text with irreversible audit masking.
- Logging failure preserves completed chat/tool effects and emits a fixed code without exception text, PII, identity or credentials. No automatic retry that could duplicate a ticket. No durable queue in this package.
- SQL file only; owner applies after review. Do not execute setup.sql or run remote SQL. No frontend route changes; chat-logs response object accepted by Claude C2 remains canonical.
- A7 remains next checkpoint, not part of this package. No credential/account creation here.

Review follow-up: replaced hello-only log-failure test with real create_support_ticket code and a stubbed RLS transport; assert exactly one insert and HTTP 200 after logging fails.
Ruling: bound HTTP session_id to DB varchar(100) before the workflow starts. Otherwise a caller could intentionally choose 101 characters to get a successful chat with no audit log. Test first showed HTTP 200 plus prepare failure; now invalid requests return 422 before model/tool effects. Existing A1 UUID sessions fit.

Pre-review: pytest 67 passed in 2.52s; compileall exit 0; PGlite migration test 1 pass. C1/C2 prior checkpoint: 57 Node/SQL pass, TypeScript/lint exit 0. RED log 8 failed; migration missing-file RED then GREEN with real SQL fixture.

Final verification: pytest 69 passed in 2.85s; compileall exit 0; combined Node suites 58 pass/0 fail/0 skipped; git diff --check exit 0. Independent reviewer reran 69 pytest and 58 Node during review, final targeted re-review confirms no remaining findings. Preserve existing branch/worktree; stop before A7 per handoff.
