# E2E Test Plan — cashflow-app (Phase 1 + 2)

Last updated: 2026-07-19  
Branch under test: `claude/phase-1-extraction` (PR #3)  
Prerequisites: backend running on `localhost:8000`, frontend on `localhost:5173`, `.env` configured with a valid AI key.

---

## Setup

```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2 — frontend
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in a browser.

---

## 1. Upload flow

### 1.1 Idle state
- [ ] App loads on the **Upload** view by default
- [ ] Drop zone displays: "Drop a PDF bank statement here / or click to browse"
- [ ] Privacy note visible: "Your file is processed locally…"

### 1.2 File validation
- [ ] Drag a non-PDF file onto the drop zone → error state shown, no upload attempted
- [ ] Click Browse, select a non-PDF → same error

### 1.3 Happy path upload
- [ ] Drag or click-select a real PDF bank statement
- [ ] Progress bar appears and advances while uploading
- [ ] After processing: success card shows **Transactions** count and **Merchants learned** count
- [ ] "Upload another statement" button resets to idle state
- [ ] Re-uploading the same PDF does not duplicate transactions (idempotency)

### 1.4 Network / AI error
- [ ] Stop the backend mid-upload → error state shown with message
- [ ] Set an invalid AI key in `.env`, restart backend, upload → error surfaces in the UI (not a silent hang)

---

## 2. PII redaction (manual log inspection)

> These require checking what text actually reaches the AI. Enable debug logging or add a temporary `print(redacted_text)` in `routes/upload.py` before the `complete()` call.

- [ ] Statement with a labeled account number (e.g. "Account Number: 123456789012") → AI prompt contains `****9012`, not the full number
- [ ] Statement with a routing number → AI prompt contains `[ROUTING]`
- [ ] Statement with a 4×4 card number (e.g. `4111 1111 1111 1234`) → AI prompt contains `****1234`
- [ ] Statement with a 16-digit unbroken card number → AI prompt contains `****` + last 4
- [ ] Transaction reference IDs (short digit sequences, unlabeled) → **not** redacted

---

## 3. Ledger — rendering

### 3.1 Navigate to Ledger
- [ ] Click **Ledger** in the sidebar → ledger view renders
- [ ] If no statements uploaded yet: empty-state message shown ("No transactions found…")
- [ ] After upload: table renders with columns Date | Description | Amount | Type | Category

### 3.2 Row appearance
- [ ] Debit rows: amount shown as `-$X.XX` in red, type badge is red-tinted "debit"
- [ ] Credit rows: amount shown as `+$X.XX` in green, type badge is green-tinted "credit"
- [ ] Category badge uses the category's own color from the database
- [ ] Long descriptions truncate with ellipsis; hovering shows the full text in a tooltip
- [ ] Dates formatted as "Jan 15, 2026" (not raw ISO)

### 3.3 Sort order
- [ ] Most recent transaction appears first
- [ ] Within the same date, higher ID appears first

### 3.4 Pagination
- [ ] With ≤50 transactions: no pagination controls visible
- [ ] With >50 transactions: Prev / Next buttons appear
- [ ] Prev is disabled on page 1; Next is disabled on last page
- [ ] "Page X of Y" label updates correctly on navigation
- [ ] Total transaction count in header stays constant across pages

---

## 4. FilterBar

### 4.1 Category filter
- [ ] Category dropdown is populated (not empty) after upload
- [ ] Selecting a category re-fetches and shows only matching rows
- [ ] Row count and total update to reflect the filtered set
- [ ] Selecting "All categories" restores full list

### 4.2 Type filter
- [ ] "Debit" button shows only debit rows
- [ ] "Credit" button shows only credit rows
- [ ] "All" restores both
- [ ] Active button is visually distinct from inactive

### 4.3 Date range
- [ ] Setting `date_from` filters out transactions before that date
- [ ] Setting `date_to` filters out transactions after that date
- [ ] Setting both gives a closed range
- [ ] Clearing either date input restores full set

### 4.4 Exclude transfers
- [ ] Checking "Hide transfers" removes rows where `is_internal_transfer = true`
- [ ] Unchecking restores them

### 4.5 Combined filters
- [ ] Category + type together: results satisfy both constraints
- [ ] Date range + exclude transfers: results satisfy both constraints
- [ ] "Clear filters" link appears when any filter is active
- [ ] Clicking "Clear filters" resets all controls and restores unfiltered list

### 4.6 Filter persistence across views
- [ ] Set a category filter, navigate to Upload and back to Ledger → filters are preserved

---

## 5. Merchant map (behavioral)

- [ ] Upload the same statement twice → second upload shows 0 **Merchants learned** (all hits from map)
- [ ] Upload a second statement from a different month with overlapping merchants → overlapping merchants resolved from map, only new merchants go to AI

---

## 6. API smoke tests (curl / Postman)

```bash
# Health check
curl http://localhost:8000/health
# Expected: {"status":"ok","db":"ok"}

# All transactions
curl "http://localhost:8000/api/transactions" | jq '.total'

# Category filter
curl "http://localhost:8000/api/transactions?category=Groceries" | jq '.items[].category' | sort -u

# Type filter
curl "http://localhost:8000/api/transactions?type=debit" | jq '.items[].type' | sort -u

# Date range
curl "http://localhost:8000/api/transactions?date_from=2026-01-01&date_to=2026-01-31" | jq '.total'

# Exclude transfers
curl "http://localhost:8000/api/transactions?exclude_transfers=true" | jq '.items[].is_internal_transfer' | sort -u
# Expected: only false

# Pagination
curl "http://localhost:8000/api/transactions?page=2&page_size=5" | jq '{page,pages,total,count:.items|length}'

# Categories
curl "http://localhost:8000/api/categories" | jq '.[].name'
```

---

## 7. Automated test suite

```bash
cd backend
pytest tests/ -v
# Expected: 40 passed, 0 failed
```

Key test files:
- `tests/test_categorization.py` — 12 tests: normalize, map hit/miss, upsert, batch AI
- `tests/test_pii_filter.py` — 20 tests: account, routing, card (4×4 + unbroken), SSN, realistic header
- `tests/test_transactions_api.py` — 8 tests: list all, filter by category/type/date, exclude transfers, pagination, sort order, list categories

---

## Known gaps / out of scope for this phase

- No test for the frontend against a live backend (Playwright integration tests — Phase 4 candidate)
- No test for the AI extraction quality (non-deterministic; covered by manual upload test above)
- PII redaction of unlabeled numbers, numbers embedded in transaction descriptions, and non-US formats (IBAN, sort codes, BSBs) is a documented known gap — not tested here
- No load or concurrency testing
