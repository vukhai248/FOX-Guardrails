# A4 execution ledger

Spec: `FOX-Guardrails/docs/plans/A-hoan-thien-web.md` A4, ownership/API in E-phan-cong-agent.md.
Base: f1733bf. Existing isolated worktree: .worktrees/a1-backend, feat/a-backend.

- [x] Structured ToolResult, review reader, RLS ticket writer, legacy order rendering.
- [x] Skill selection and agent registration; input/context/output guard hooks.
- [x] Bench flags, provider payload records and temperature override.
- [x] Regression verification, independent review, report; ready for checkpoint commit.

Pre-flight: A2 creates structured order fields consumed by A4; no DB schema change required. A5 will consume guard metadata; keep default HTTP guard per E §3.
Ruling: preserve byte-for-byte legacy order output for rows without new populated fields; append structured details only for new rows — resolves new fields versus legacy snapshot requirement.
Ruling: guard scaffold supports only off; explicitly reject enabled modes until B implements them — prevents a false claim that protection is active.
Ruling: use this tracked report as Windows-native execution ledger; external Opus plan is not in task-brief script format. Stop after A4 as handoff requests.
Ruling: initial default Python lacks FastAPI; reuse previous session's DL Python rather than change dependencies.

Verification before review: 51 passed in 1.74s (DL Python, pytest -q, rag-service); git diff --check exit 0. Legacy snapshot, RLS JWT HTTP transport, actual tool execution through /chat, guard input/context/output, flags and payload recording all covered offline.

Review fix: Gemini tool thought_signature is bytes; JSON recording failed on a real signed follow-up. Reproduced RED in full call_gemini path, then serialize bytes as tagged reversible base64, preserving actual SDK bytes. No swallowing of recording errors.
Test quality: removed original A1 tool-registry stub; only remote retriever constructors are stubbed, so production registry and all tools now import for the whole suite.
Review ruling: A2 defaults unpaid/cod/empty note do not establish historical payment on legacy rows. Preserve legacy rendering when structured fields are absent and payment remains the migration default; regression uses actual migrated defaults. Recent-order list keeps original format; details expose new payment information.
Review fix: guard HTTP static fallback as well when final answer is empty; reproduced HTTP RED before patch. No reply bypasses the output extension point.

Final independent review: 53 passed in 1.78s; no unresolved findings, ready for A4 code checkpoint. Live integration/B/A5/A7/frontend/Stripe acceptance remain explicitly outside this checkpoint. Keep feat/a-backend and this worktree in place per existing handoff; no merge/push/cleanup menu needed because user already chose separate checkpoint work.
