**Feature:** cashflow-app
**Status:** In Progress — e2e testing underway, PR #3 open awaiting merge
**Last Updated:** 2026-07-20
**Branch:** claude/phase-1-extraction
**Open PR:** #3 — Phase 1 + 2 (not yet merged)

## What Was Done
- Phase 1 complete: PDF extraction, AI client wrapper, upload endpoint, merchant map + batched AI categorization, UploadPanel UI, always-on PII redaction before AI
- Phase 2 complete: GET /api/transactions (paginated + filtered), GET /api/categories, Ledger.jsx, FilterBar.jsx. Task 2.5 (useTransactions hook) intentionally skipped — fetching handled directly in Ledger.jsx, no separate hook needed
- Dev environment set up: backend venv on Python 3.13 (`backend/.venv`, required — repo's pyenv default 3.9.6 can't parse `models.py`'s `X | None` syntax), root `package.json` with `npm run start` (concurrently, `-k` flag so Ctrl+C stops both), pytest pinned in requirements.txt
- Backend moved off port 8000 → 8787 (macOS Control Center/AirPlay Receiver claims 8000 by default)
- Live e2e testing found and fixed 2 real bugs: (1) merchant_map UNIQUE constraint crash when a batch has 2+ transactions from the same merchant (session's autoflush=False + missing db.flush()); (2) merchant category edits only reached the clicked transaction, not its siblings, because the AI's suggested_key was discarded and matching used strict substring containment instead of word-subset
- Built the merchant category-edit feature: PATCH /api/transactions/{id}/category + click-to-expand ledger rows with a category dropdown; also fixed new_map_entries always reporting 0
- 48 automated tests passing (categorization, PII filter, transactions API)

## Next Steps
- Continue e2e test plan (`.claude/memory/features/cashflow-app/tests/e2e-test-plan.md`) — upload edge cases, ledger, filters, resilience sections not yet run
- Remaining backlog (see TaskList): #1 test_extraction.py still missing (real gap — no automated coverage of AI JSON parsing, the highest-risk untested path), #3 frontend test tooling, #4 CLAUDE.md env var drift (`ANTHROPIC_API_KEY` vs actual `AI_API_KEY`), #6 review upload.py error-detail information disclosure
- Once e2e testing is complete: merge PR #3 to main, then begin Phase 3 (charts + stats API)

## Blockers
None
