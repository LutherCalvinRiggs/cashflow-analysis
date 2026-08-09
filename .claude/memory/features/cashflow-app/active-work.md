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
- **2026-08-08: resumed e2e testing, verified 1.6 (PII check) live** — re-uploaded PDFs, confirmed `[REF]`/`[ADDRESS]` show correctly in the ledger.
- **2026-08-08: redesigned PII redaction to be audience-scoped instead of blanket** — Luther wants a future chat feature to answer real questions ("how much did I spend in Chicago") against full transaction data. Split `pii_filter.py`'s `redact()` into `redact()` (identity fields — account/routing/card/SSN — still always stripped before extraction and storage) and `redact_transaction_text()` (ref#/address — now stripped only from the categorization AI call's payload, never from storage). `Transaction.description` now keeps real addresses/reference numbers permanently. Full rationale and what was ruled out in decisions.md 2026-08-08. 56 tests passing (up from 53). **Not committed yet** — pending approval per CLAUDE.md gate.
- **2026-08-08: built batch upload, auto-redirect-to-ledger, FilterBar redesign, and a ledger sort toggle** — all 4 items Luther asked for in the same session. See decisions.md 2026-08-08 for full breakdown. Tested live in Chrome (year/month cascading, sort toggle, a 2-file failing batch upload); could not test the batch **success** path since no test PDF was available to the session.
- **2026-08-08: Luther independently re-uploaded his 2 real PDFs to test the redaction fix** — confirmed live it worked (real ref#/address showed up on the new statements #3/#4 vs. `[REF]`/`[ADDRESS]` on old #1/#2). Cleaned up the resulting duplicates: deleted #1/#2 and their 15 transactions, kept #3/#4, `merchant_map` untouched.
- **2026-08-08: re-added the debit/credit type filter** (dropped when FilterBar was redesigned) as a 5th select; confirmed working live.
- **2026-08-08: relocated the chat panel** from the right side to a collapsible left-side panel with an outlined CTA toggle under the nav links, per Luther's spec. Layout/shell only, verified live, no console errors. Actual chat functionality is still Phase 4 — Luther will explore that later.
- **2026-08-08: researched `firecrawl/anydoc`** at Luther's request (a PDF→Markdown converter he found) — verified real via GitHub/PyPI APIs but only 5 days old (v0.1.7). Recommended against adopting it yet; not implemented. Full detail in decisions.md.
- **2026-08-08: PII confirmed clean at the repo level** — grepped all tracked files across every new commit for the specific real values seen this session (name, city, account digits, ref#/address fragments); zero hits. `cashflow.db`/`.env` both untracked.
- **2026-08-08: completed e2e section 2 (upload edge cases) — all 4 pass** (2.1 non-PDF, 2.2 scanned/image-only PDF via a synthetic file, 2.3 duplicate upload, 2.4 backend down mid-upload). Details in decisions.md.
- **2026-08-08: added file-hash-based upload dedup** — byte-identical re-uploads now rejected with `409` before any AI call. Added `Statement.file_hash`, a small manual-migration step in `database.py` (no migration framework exists), and `tests/test_upload.py` (3 new tests). **Found and fixed a real cross-file test-isolation bug** while adding it — see decisions.md, worth reading before adding a 4th `TestClient`-based test file.
- 59/59 backend tests passing (up from 56).

## Next Steps
- **Get Luther's approval to commit** — redaction split, batch-upload/redirect/FilterBar/sort, type-filter re-add, chat-panel relocation, and upload dedup are all sitting uncommitted together in the working tree
- Batch-upload **success** path still untested (no test PDF was available to the agent this session) — will get exercised next time Luther uploads a real statement
- Backend has no test coverage yet for the new `year`/`month`/`sort` query params or the `/transactions/periods` endpoint — worth a follow-up unit test pass
- If Luther wants to revisit `anydoc`: do a side-by-side Markdown-output comparison against pdfplumber on real statement PDFs before touching `pdf_extractor.py`
- **New: a dev-server startup issue needs debugging** (not urgent, deferred by Luther to "another time") — see implementation-notes.md 2026-07-28 for what was observed (port conflicts + corrupted Vite dep cache leaving the frontend stuck serving 503s / blank page)
- Continue e2e test plan — section 2 done; sections 3 (ledger, partial), 4 (filters, informally verified), 5 (resilience), 6.1/6.2 (merchant map), 7 (API smoke tests), 8 (re-run automated suite count) still open
- Remaining backlog (see TaskList): #1 test_extraction.py still missing, #3 frontend test tooling, #4 CLAUDE.md env var drift (`ANTHROPIC_API_KEY` vs actual `AI_API_KEY`), #6 review upload.py error-detail information disclosure
- Known redaction gap surfaced 2026-08-08, not yet actioned: full name and city/state/zip pass through `raw_text` completely unredacted (only the street-address line is caught) — local-only exposure, not sent to any AI, but worth a follow-up if it matters to Luther
- Once e2e testing is complete: merge PR #3 to main, then begin Phase 3 (charts + stats API)
- Local backup branch `backup/phase-1-extraction-pre-scrub-2026-07-28` can be deleted once Luther confirms the rewritten branch/PR looks right

## Blockers
None — server-issue debugging explicitly deferred by Luther to a future session
