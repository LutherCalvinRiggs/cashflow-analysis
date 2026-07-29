**Feature:** cashflow-app
**Status:** In Progress — e2e testing underway, PR #3 open awaiting merge
**Last Updated:** 2026-07-28
**Branch:** claude/phase-1-extraction
**Open PR:** #3 — Phase 1 + 2 (not yet merged)

## What Was Done
- Phase 1 complete: PDF extraction, AI client wrapper, upload endpoint, merchant map + batched AI categorization, UploadPanel UI, always-on PII redaction before AI
- Phase 2 complete: GET /api/transactions (paginated + filtered), GET /api/categories, Ledger.jsx, FilterBar.jsx. Task 2.5 (useTransactions hook) intentionally skipped — fetching handled directly in Ledger.jsx, no separate hook needed
- Dev environment set up: backend venv on Python 3.13 (`backend/.venv`), root `package.json` with `npm run start`, pytest pinned in requirements.txt. Backend on 8787 (8000 claimed by macOS AirPlay Receiver)
- Live e2e testing found and fixed 2 real bugs (merchant_map UNIQUE crash, category-edit not reaching siblings) — see decisions.md 2026-07-20/21
- Built merchant category-edit feature: PATCH /api/transactions/{id}/category + click-to-expand ledger rows
- **2026-07-28: Investigated and fixed the PII-in-UI bug Luther spotted** — see decisions.md for full diagnosis and fix. `pii_filter.py` now redacts reference/transaction numbers and street addresses embedded in descriptions; `upload.py` now stores redacted text in `statements.raw_text` (was storing the unredacted original). 53 backend tests passing (up from 48; PII suite 20→25).
- Cleared the 2 stale test statements + 15 transactions from `cashflow.db` (predated the fix) at Luther's request — `merchant_map` left intact. **Waiting on Luther to re-upload his 2 test PDFs** to verify the fix live in the ledger.
- **2026-07-28: found real bank-statement data (reference numbers, an ATM address, a third party's business name) had leaked into the public repo** — as code comments/test fixtures in this session's new commit, and pre-existing in test fixtures from an earlier session. Scrubbed the working tree, then rewrote branch history (`git filter-repo --refs claude/phase-1-extraction --replace-text ...`, scoped to this branch only — confirmed via pickaxe search that no affected commit is shared with `main`) and force-pushed. Backup of pre-rewrite history kept at local branch `backup/phase-1-extraction-pre-scrub-2026-07-28`. **Gotcha: filter-repo resets the working tree to match rewritten HEAD, silently discarding uncommitted changes** — this wiped an in-progress memory-file update mid-session; had to be redone from the system-reminder diff snapshots. Always commit or stash before running filter-repo.

## Next Steps
- **Luther will re-upload his 2 test statement PDFs** next session — verify ledger shows `[REF]`/`[ADDRESS]` instead of raw reference numbers/street address, then resume e2e plan section 1.6 as complete
- **New: a dev-server startup issue needs debugging** (not urgent, deferred by Luther to "another time") — see implementation-notes.md 2026-07-28 for what was observed (port conflicts + corrupted Vite dep cache leaving the frontend stuck serving 503s / blank page)
- Continue e2e test plan (`.claude/memory/features/cashflow-app/tests/e2e-test-plan.md`) — upload edge cases, ledger, filters, resilience sections not yet run
- Remaining backlog (see TaskList): #1 test_extraction.py still missing, #3 frontend test tooling, #4 CLAUDE.md env var drift (`ANTHROPIC_API_KEY` vs actual `AI_API_KEY`), #6 review upload.py error-detail information disclosure
- Once e2e testing is complete: merge PR #3 to main, then begin Phase 3 (charts + stats API)
- Local backup branch `backup/phase-1-extraction-pre-scrub-2026-07-28` can be deleted once Luther confirms the rewritten branch/PR looks right

## Blockers
None — server-issue debugging explicitly deferred by Luther to a future session
