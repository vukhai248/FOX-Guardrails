# K1–K4 execution ledger

Spec: FOX-Guardrails/docs/plans/prompts/codex-phanA.md, Đợt1 K1–K4 (03/11/2026).
Base2df89f9, feat/a-backend; isolated worktree retained. User previously authorized completing assigned work in one handoff.

- [x] K1 lazy admin clients, safe missing-config response, no-env build.
- [x] K2 permanent INVALID_PRODUCT and signed session-expired handling with idempotent DB state.
- [x] K3 offload chat log writes; concurrent request regression.
- [x] K4 catalog-backed smoke seed + explicit email_address_invalid stop; docs.
- [x] Full checks, independent review, codex-K.md; ready for checkpoint commit.

Pre-flight/rulings:
- Auth module and latest admin handlers exist only on frontend e1850a9; backend still has pre-review eager/insecure baseline handlers. Reuse those exact approved frontend admin handlers unchanged on backend (no new handler behavior), then implement lazy auth in Codex-owned lib/server/auth.ts. This avoids editing Anti's active worktree and avoids reimplementing authorization. Record sync in requests; verify admin files identical to source commit.
- Expiry must match the signed session ID and never alter paid/COD orders. Existing one-argument fail_stripe_order only handles unbound sessions; add a new reviewed migration with a two-argument overload. Keep original create-failure cleanup semantics unchanged.
- K3 offloads only logging as requested; workflow invocation remains synchronous baseline, not a claim that all model work is nonblocking.
- K4 --products-from-db explicitly maps distinct placeholder IDs to sorted existing IDs for smoke fixtures; official C datasets should use explicit real IDs. No catalog/Auth/DB mutation during --dry-run.
- Do not execute remote migrations/seed. Đợt3 waits for Claude's integration branch and backend-tagged QA bugs.

Verification: full pytest93passed, full Node77passed with v8pool1/concurrency1, no-env Nextbuild29/29+TypeScript0, ESLint0. Default full Node parallel hit V8 OOM; logged and retried all tests serially, none skipped. Independent focused review43Node+18Python passed;4admin blobs exactly source, no findings. New SQL only; all service acceptance remains separate.
