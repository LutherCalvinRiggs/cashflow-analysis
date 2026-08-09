# E2E Test Plan — cashflow-app

**Scope:** everything on branch `claude/phase-1-extraction` — upload → extraction → categorization → ledger → filters.
**Written:** 2026-07-19

## Preconditions
- [x] `.env` at repo root has a real `AI_API_KEY` (no placeholder)
- [x] `npm run start` from repo root — both servers up
- [x] `curl localhost:8787/health` returns `{"status":"ok","db":"ok"}`
- [x] At least 2 real PDF bank statements on hand (different months, ideally different layouts). Optional but valuable: one scanned/image-only PDF, one non-PDF file (e.g. .png renamed or a .txt)

> Note: DB starts empty. Run Section 1 before Sections 3–4 — ledger tests need data.

---

## 1. Upload — happy path
- [x] 1.1 Open `localhost:5173`, locate UploadPanel. Drag-and-drop a statement PDF → progress indicator appears
- [x] 1.2 On completion, summary shows a plausible transaction count and no warnings
- [x] 1.3 Repeat via the file-picker (not drag-and-drop) with the second statement
- [x] 1.4 Spot-check accuracy: pick 5 transactions from the source PDF, confirm each appears in the ledger with correct **date, description, amount, and debit/credit direction**
- [x] 1.5 Spot-check categorization: are the AI-assigned categories sensible for ~10 transactions? Note any misfires (feeds the prompt-tuning loop, not pass/fail)
- [x] 1.6 PII check: fixed 2026-07-28, redesigned 2026-08-08 (audience-scoped redaction — see decisions.md). Luther re-uploaded both source PDFs and confirmed `[REF]`/`[ADDRESS]` render correctly in the ledger where account/routing/card/SSN patterns would appear; real ref#/addresses are now intentionally preserved in storage for future chat queries. Passing.

## 2. Upload — edge cases
- [x] 2.1 Non-PDF file: confirmed clean at both layers 2026-08-08 — frontend picker rejects with "Only PDF files are accepted." before any network call; API also rejects a `.txt` sent directly (bypassing the frontend) with `400 {"detail":"Only PDF files are accepted"}`, no stack trace
- [x] 2.2 Scanned/image-only PDF: confirmed 2026-08-08 with a synthetic image-only PDF (Pillow-rendered text-as-pixels, no text layer — pdfplumber confirmed `full_text == ""`) rather than a real scan, since that exercises the same "zero extractable text" code path without needing a physical document. API returns `422 {"detail":"No text could be extracted from the PDF"}`; frontend shows it as a clean per-file error, no crash
- [x] 2.3 Same PDF uploaded twice: **originally observed as a gap via real usage 2026-08-08** (doubled the ledger, 15 → 30 transactions, no warning). **Dedup added same day** — see decisions.md. Byte-identical re-uploads are now rejected with `409` before any extraction/AI call runs. Verified via 3 automated tests (`tests/test_upload.py`): duplicate rejected, AI never called twice, different files still both succeed. Scope: only catches exact byte-identical files, not the same statement re-exported/re-scanned with different bytes
- [x] 2.4 Upload with backend down: confirmed 2026-08-08. **Note on methodology**: `concurrently -k` kills the whole tree the instant either child dies, so "kill just api, leave web running" isn't reachable while running under `npm run start` — killing api cascades and kills web too. Ran backend and frontend as two independent standalone processes instead, killed only the backend, uploaded against the now-dead API from an already-loaded tab. Frontend showed `HTTP 502` (Vite's proxy reporting the backend unreachable) within ~1s, no hang, clean "Upload another statement" recovery. True mid-*request* timing (kill while the backend is actively processing, not just absent before the request starts) isn't reliably reproducible through this tooling — this is a close proxy, same code path (`uploadStatement`'s xhr error handler), same outcome

## 3. Ledger
- [x] 3.1 Transactions listed most-recent-first: confirmed 2026-08-08 (default sort desc, Jan 6 2025 at top through Dec 2024)
- [x] 3.2 Credits render green, debits red; amounts formatted correctly: confirmed 2026-08-08 — `$` sign, comma separators, 2 decimals, correct +/- prefix per type, no sign bugs observed
- [x] 3.3 Click a row → expands showing AI notes and category confidence, plus an editable category dropdown (added 2026-07-20)
- [x] 3.4 Pagination: confirmed 2026-08-08 with 60 temporary synthetic rows (real data alone is only 15, below the 50/page threshold — inserted, tested, deleted afterward, not real financial data). Page 1/2 = 50/25, zero overlap and zero gap between pages (verified via direct API query, not just visually), Next/Prev navigate correctly, both buttons correctly disable at their respective boundary
- [x] 3.5 Category badges match the expanded row's category: confirmed 2026-08-08 (badge "Income" == expanded dropdown "Income" for the same row; spot-checked other rows' badge colors are consistent throughout — Internal Transfer/gray, Childcare/purple, Fees & Interest/gray, Income/green)

## 4. Filters
- [x] 4.1 Category filter: confirmed 2026-08-08 — `category=Childcare` → 4/4 rows, all correctly badged
- [x] 4.2 Type filter (credit/debit): confirmed 2026-08-08 — `type=credit` → 5/5 rows, all correctly badged
- [x] 4.3 Year/month (plan predates the FilterBar redesign — date-range inputs were replaced by year/month selects): confirmed 2026-08-08 — year=2024 → 9, year=2025 → 6 (sums to 15), month cascades correctly (2024 only offers December), year+month combo stays consistent
- [x] 4.4 Exclude-transfers toggle: confirmed 2026-08-08 — 15 → 11, exactly the 4 `is_internal_transfer=true` rows disappear. **Found a real categorization quirk while verifying, not a filter bug**: transaction #27 (an ATM withdrawal) is categorized "Internal Transfer" but its `is_internal_transfer` flag is `false`, so it correctly stays visible — the filter is flag-based, not category-label-based, and behaved exactly as designed. Worth feeding back into categorization prompt-tuning (an ATM withdrawal isn't really an "Internal Transfer")
- [x] 4.5 Combined filters (category + year) behave as AND: confirmed 2026-08-08 — `category=Internal Transfer&year=2024` → 3 (ground-truth verified via direct API query first)
- [x] 4.6 Clearing filters restores the full ledger: confirmed 2026-08-08 — 15 restored
- [x] 4.7 Filter to an empty result: confirmed 2026-08-08 — `category=Groceries` → clean "No transactions found" state, no error/spinner. **Minor copy nit, not a bug**: message says "Upload a statement to get started," which reads oddly for a filtered-empty-result (implies an empty DB, not just an empty filter combo) — cosmetic, not blocking

## 5. Resilience
- [ ] 5.1 Restart both servers (`Ctrl+C`, `npm run start` again) → data persists, ledger unchanged (SQLite file survives)
- [ ] 5.2 Temporarily set `AI_API_KEY` to garbage, restart, upload → expect a clear failure. **Known gap:** error handling pass is Phase 5 (task 5.1), so an ugly error is acceptable; note what actually happens
- [ ] 5.3 Browser hard-refresh mid-session → app recovers, ledger reloads

## 6. Merchant map (behavioral)
- [ ] 6.1 Upload the same statement twice → second upload shows 0 new merchant-map entries (all hits from map)
- [ ] 6.2 Upload a second statement from a different month with overlapping merchants → overlapping merchants resolved from map, only new merchants go to AI
- [x] 6.3 Edit a merchant's category via the ledger UI → change applies to every transaction from that merchant, not just the one clicked (verified 2026-07-20 with "Zelle Payment To Jane Doe LLC" — 4 transactions, all updated)

## 7. API smoke tests (curl)
```bash
curl http://localhost:8787/health
# Expected: {"status":"ok","db":"ok"}

curl "http://localhost:8787/api/transactions" | jq '.total'
curl "http://localhost:8787/api/transactions?category=Groceries" | jq '.items[].category' | sort -u
curl "http://localhost:8787/api/transactions?type=debit" | jq '.items[].type' | sort -u
curl "http://localhost:8787/api/transactions?date_from=2026-01-01&date_to=2026-01-31" | jq '.total'
curl "http://localhost:8787/api/transactions?exclude_transfers=true" | jq '.items[].is_internal_transfer' | sort -u
# Expected: only false

curl "http://localhost:8787/api/transactions?page=2&page_size=5" | jq '{page,pages,total,count:.items|length}'
curl "http://localhost:8787/api/categories" | jq '.[].name'
```

## 8. Automated test suite
```bash
cd backend
.venv/bin/python -m pytest tests/ -v
# Expected: 48 passed, 0 failed
```
Key test files:
- `tests/test_categorization.py` — normalize, map hit/miss, upsert, batch AI, word-subset merchant matching
- `tests/test_pii_filter.py` — account, routing, card (4×4 + unbroken), SSN, realistic header
- `tests/test_transactions_api.py` — list all, filter by category/type/date, exclude transfers, pagination, sort order, category PATCH endpoint

---

## Recording results
For each failure or surprise, note: section number, what happened, and (if backend) the `[api]` log lines from the `npm run start` output. Findings feed the post-test task iteration — see TaskList for the current backlog (extraction tests, frontend test tooling, CLAUDE.md env var drift, upload.py error-detail review).

## Known gaps / out of scope for this phase
- No test for the frontend against a live backend (Playwright integration tests — Phase 4 candidate)
- No test for AI extraction quality itself (non-deterministic; covered by manual spot-checks above, not automated)
- PII redaction of unlabeled numbers, numbers embedded in transaction descriptions, and non-US formats (IBAN, sort codes, BSBs) is a documented known gap — not tested here
- No load or concurrency testing
