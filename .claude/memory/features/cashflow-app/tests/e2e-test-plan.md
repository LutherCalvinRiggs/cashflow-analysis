# E2E Test Plan — cashflow-app

**Scope:** everything on branch `claude/phase-1-extraction` — upload → extraction → categorization → ledger → filters.
**Written:** 2026-07-19

## Preconditions
- [x] `.env` at repo root has a real `AI_API_KEY` (no placeholder)
- [x] `npm run start` from repo root — both servers up
- [x] `curl localhost:8787/health` returns `{"status":"ok","db":"ok"}`
- [ ] At least 2 real PDF bank statements on hand (different months, ideally different layouts). Optional but valuable: one scanned/image-only PDF, one non-PDF file (e.g. .png renamed or a .txt)

> Note: DB starts empty. Run Section 1 before Sections 3–4 — ledger tests need data.

---

## 1. Upload — happy path
- [x] 1.1 Open `localhost:5173`, locate UploadPanel. Drag-and-drop a statement PDF → progress indicator appears
- [x] 1.2 On completion, summary shows a plausible transaction count and no warnings
- [x] 1.3 Repeat via the file-picker (not drag-and-drop) with the second statement
- [x] 1.4 Spot-check accuracy: pick 5 transactions from the source PDF, confirm each appears in the ledger with correct **date, description, amount, and debit/credit direction**
- [x] 1.5 Spot-check categorization: are the AI-assigned categories sensible for ~10 transactions? Note any misfires (feeds the prompt-tuning loop, not pass/fail)
- [ ] 1.6 PII check: expand a few rows / inspect the DB (`sqlite3 backend/cashflow.db 'select description from transactions limit 20;'`) — no full account numbers, card numbers, routing numbers, or SSNs should appear

## 2. Upload — edge cases
- [ ] 2.1 Non-PDF file: picker should refuse it, or the API should reject it with a user-facing error — not a stack trace
- [ ] 2.2 Scanned/image-only PDF (if available): expect a graceful result with a warning about no extractable text — not a crash
- [ ] 2.3 Same PDF uploaded twice: observe what happens. **Known unknown** — duplicate handling may not exist; record whether transactions double up
- [ ] 2.4 Upload with backend killed mid-flight (stop `api` in the concurrently output): frontend should surface an error, not hang

## 3. Ledger
- [ ] 3.1 Transactions listed most-recent-first
- [ ] 3.2 Credits render green, debits red; amounts formatted correctly (watch signs — a common extraction bug)
- [x] 3.3 Click a row → expands showing AI notes and category confidence, plus an editable category dropdown (added 2026-07-20)
- [ ] 3.4 Pagination: with both statements uploaded, page through; total count consistent; no repeated or skipped rows across pages
- [ ] 3.5 Category badges match the expanded row's category

## 4. Filters
- [ ] 4.1 Category filter: pick one category → only those rows; total updates
- [ ] 4.2 Type filter (credit/debit): rows and totals consistent
- [ ] 4.3 Date range: set a range covering only one statement → only that month's rows
- [ ] 4.4 Exclude-transfers toggle: transfer-categorized rows disappear
- [ ] 4.5 Combined filters (category + date range) behave as AND
- [ ] 4.6 Clearing filters restores the full ledger
- [ ] 4.7 Filter to an empty result → sane empty state, not an error or infinite spinner

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
