# Execution ledger — plan: docs/plans/prompts/codex-phanB.md (Đợt 1)

Base bc03e73, isolated feat/b-core at D:/create/DATN/.worktrees/b-core.
User authorized implementation after collision check; Claude requires K5 before B1/B2.

## Collision check / rulings

- Anti currently works in web repo qa/a-wave3 with uncommitted qa2_supplementary.spec.ts. No editing that checkout, its env, DB or servers during this round. K5 uses separate fix/a-k5 worktree.
- B1/B2 own source and backend unit tests in FOX repo, Anti later owns teencode_vi.tsv and tests/fixtures/**. Specific prompt explicitly assigns evidence_unicode.json to Codex, overriding general fixture ownership for this single file. No other fixture edits.
- Shared DL Python environment: avoid installing/upgrading libraries or changing the global editable package binding. Tests use worktree-local PYTHONPATH; no dependency on Anti checkout state. All prescribed packages already installed. Editable install completed only inside ignored b-core/.venv with --system-site-packages, --no-deps, --no-build-isolation; pip confirmed the shared DL package was outside the environment and left it untouched.
- B1 consumes B2 normalize(text, *, max_chars, decode_max_depth); normalization returns signals:Finding and clean. B2 imports Finding from types.py. Types/config established first; guard integration completed once normalization exists.
- decoded is a bounded flat list of normalized view objects, each with no children; breadth-first depth2 and cumulative expansion budget. No hidden unbounded recursive tree.
- digits_map maps output digit indices to clean starts. Source intervals can be exposed separately so word-digit matches preserve their final word.
- No B3, classifier download, remote migrations or live QA data writes. Review migration K5 remains pending Claude approval.

## Tasks

- [x] Read specs / check isolation. Baseline pytest: 2 passed in0.33s; ruff: All checks passed.
- [x] K5 implementation/checkpoint complete before B product code: 82 Node,93 Python,34 restored PostgreSQL checks; independent source review no findings. No remote migration.
- [x] B1 models/config tests RED→GREEN, then Guard + SDK docs integration. Commits5788f78/bc66f50, independent contracts24tests clean.
- [x] B2 eight normalization steps, six evidence cases, negative controls, decoding budgets, benchmark RED→GREEN. Commitsf662f60/42b79de/768ba3d/ed8ef9f; TSV precedence and NFKC segmentation review findings resolved with regressions.
- [x] Full tests/ruff, real output examples, learning document, independent review. Root95passed2skipped0.65s; Ruff0; warm2KB p95=4.825ms/40samples. Missing Anti datasets are explicitly skipped/unverified. Whole-branch review no outstanding findings; reviewer15focused tests pass.
- [x] Commit scoped packages, report codex-B1.md and stop before B3. Parent handoff checkpoint records final artifacts; no merge/push/remote migration.
