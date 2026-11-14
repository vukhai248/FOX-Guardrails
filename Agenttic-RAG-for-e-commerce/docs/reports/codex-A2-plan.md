# A2 — Implementation plan

> Execute inline with `superpowers:executing-plans`, test-first, then independent review. One checkpoint commit for A2; stop afterwards.

Goal: server-owned orders and Stripe test Checkout/webhook; preserve API §3.
Spec: `FOX-Guardrails/docs/plans/A-hoan-thien-web.md` A2 and `E-phan-cong-agent.md` §2/3/7.

## Constraints and decisions

- Worktree `D:/create/DATN/.worktrees/a1-backend`, branch `feat/a-backend`, base `db7f3d4`.
- Never run setup.sql or SQL against Supabase. Test the new migration on an ephemeral local PostgreSQL engine with a minimal handwritten fixture.
- No UI edits, package.json edits, prompt changes, real payment keys or committed .env files.
- Ignore `.env.bench` and `*.env.bench` now, before A7 creates credentials.
- Use Node's built-in test runner and installed TypeScript, no vitest dependency.
- VND integer amounts: canonical unit price is rounded DB `final_price`, never request price. All line items come from the server snapshot.
- Database RPC creates the order and deducts COD stock in one transaction. Stripe payment finalization locks the order, validates session/amount/currency and deducts stock once in the same transaction.
- Revoke client order writes; existing INSERT-own policy must not allow bypassing server pricing/payment validation.
- Existing frontend branch owns checkout/checkout-success changes. Record integration/testing needs in requests.md.

## Task 1 — Payment transaction migration

Files: `database/migrations/2026-11_payment_and_address.sql`, `web_ui/src/lib/server/__tests__/payment-db.test.cjs`, fixture/loader test utilities.

Interfaces: service-only RPCs `create_shop_order`, `decrement_stock_for_order`, `attach_stripe_session`, `finalize_stripe_order`, `fail_stripe_order`; all args use `p_` prefixes. Stored order contains canonical `items`, `total`, structured address, payment state and internal `stock_decremented_at`.

- [x] Write tests for canonical prices, duplicate quantities, out-of-stock rollback, COD deduction, unpaid Stripe unchanged stock, duplicate webhook/decrement, amount/currency/session mismatch, unauthorized SQL calls and direct client writes.
- [x] Run tests before migration exists; expected missing migration/behavior failures.
- [x] Add columns/constraints/index plus security-definer functions with fixed search_path and service_role-only grants. No table/data reset.
- [x] Run database tests; expected all pass. Verify repeated migration and rollback without altering legacy rows.

## Task 2 — Order handlers and route wiring

Files: `web_ui/src/lib/server/order-core.ts`, `order-handlers.ts`, `payment-runtime.ts`; routes `api/orders/route.ts`, `api/orders/[id]/route.ts`, `api/orders/[id]/note/route.ts`, `api/stripe/route.ts`, `api/stripe/webhook/route.ts`; Node tests beside server logic.

Interfaces: factory `createOrderHandlers(deps)` implements create/detail/note/webhook. Dependency boundary authenticates Supabase token, invokes RPCs, reads owner-filtered orders and creates/verifies/expires Stripe sessions. Routes delegate to that factory. Legacy `/api/stripe` uses the same authenticated server order flow.

- [x] Write failing tests for unauthenticated/malformed/empty requests, numeric constraints, Unicode note limits, tampered prices/user_id, owner-only 404, note pending-only 409, checkout URL privacy, webhook signature/mode/payment checks and failures.
- [x] Run Node test suite; expected failures for missing handlers.
- [x] Implement pure validation/Stripe parameter construction, request handlers and lazy server-only adapters. Use configured APP_URL (local default) rather than untrusted Origin for redirects. Accept only sk_test_ keys and non-live signed events.
- [x] Verify real signed Stripe event verification using the SDK locally; tampering must fail. Test actual registered routes with injected external boundaries.
- [x] Run Node suite, TypeScript and eslint for new/changed files; expected zero errors in changed code.

## Task 3 — Review, evidence and checkpoint

Files: `docs/reports/codex-A2.md`, `docs/reports/requests.md`.

- [x] Run whole Python suite and Node suite, migration tests, typecheck/build where possible, git check-ignore and diff check.
- [x] Independent read-only review of staged diff and spec, especially SQL privileges, stock concurrency/idempotence, signature verification, price/owner checks and errors.
- [x] Fix material findings with regression tests and rerun relevant suites.
- [x] Report actual output and explicitly disclose no live Supabase migration/payment or full-system E2E.
- [x] Commit `feat(A2): ...`, retain worktree/branch, stop before A4.

## Review focus

- Two orders competing for the last item: row locks and transaction rollback; local embedded tests cannot substitute for multi-process Supabase contention testing.
- Duplicate/out-of-order Stripe events, including signed-but-live or unpaid events: cannot mark paid or decrement twice.
- Checkout session creation/attachment failure: order cannot become paid via client fallback; incomplete external calls require reconciliation/retry.
- Products whose stock/price change while checkout is running: paid amount is checked against immutable server order snapshot; no stock reservation before Stripe payment.
- Direct authenticated Supabase writes and RPC execution: cannot forge a paid order or bypass server authorization.
