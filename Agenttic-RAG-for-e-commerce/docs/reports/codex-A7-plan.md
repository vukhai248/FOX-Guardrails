# A7 execution ledger

Spec: FOX-Guardrails/docs/plans/A-hoan-thien-web.md A7 and Claude review in prompts/codex-phanA.md.
Base: 0cdf528, feat/a-backend; existing isolated worktree.
User now requests completing all assigned remaining work and one consolidated handoff; no package pause.

- [x] Seed CLI JSONL validation, ignored root credentials and owned Auth accounts/roles.
- [x] Atomic SQL batch seed/reset, private mappings, deterministic IDs and idempotency.
- [x] Python/SDK/real PostgreSQL regressions, dry-run and all existing suites.
- [x] Independent review/report ready; consolidated handoff accompanies final completion commit.

Rulings/design:
- C's datasets directory currently only contains .gitkeep. Ship a neutral smoke fixture and schema, not invented attack labels or a claimed official dataset.
- Only orders/reviews are seedable; customer user_id fields refer to bench_customer_a/b aliases, never arbitrary real users. Products are read only; seed order snapshots use DB prices, do not charge Stripe or deduct real inventory.
- Root .env.bench stores generated namespace, project URL and passwords before remote writes; ignore and tracked-file checks precede every credential write. App-metadata ownership markers prevent taking over existing accounts; role comes from user_roles only.
- Namespace scopes mappings/reset across independent credential files. Deterministic UUID5 row IDs plus input hashes prevent overwriting real/unmapped rows and reject changed cases unless --reset.
- One service-role-only RPC performs reset + whole dataset insert in one transaction; mapping and inserted row cannot be orphaned by a mid-batch error. Reset refuses externally referenced bench orders rather than altering unmapped tickets by FK cascade/SET NULL.
- Migration is a new file for owner review/application. No remote DDL, setup.sql, account creation, merge or deployment required to prove local code; actual seed waits for migration installation and real C cases.
- Auth API cannot join the data transaction. Credentials persist for recovery; script never automatically deletes users or resets unknown passwords. Sign-in verification uses a separate anon client so admin credentials remain server-scoped.

Final verification: 90 pytest pass in5.18s; combined Node/PostgreSQL69/69pass,0skip; compileall0; TypeScript build+targeted ESLint0; Next build28/28 with dummy config. Seed-specific tests15 Python and6SQL. Independent review findings corrected: lock review rows during reset and reject mapping ownership mismatched to recreated Auth UUID; no remaining blockers in reviewed seed code.
