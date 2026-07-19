# Implementation Notes — cashflow-app

## LinkedIn Post Automation (2026-06-25)
After each commit, a "Building in Public" block is manually copy-pasted to LinkedIn. This needs to be automated — likely via a GitHub Action that triggers on push to main and posts via the LinkedIn API. Requires a LinkedIn API token. Revisit after Phase 1 ships.

---

## SQLite in-memory tests need StaticPool (2026-07-12)
`sqlite:///:memory:` creates a fresh database per connection. FastAPI TestClient opens its own connection, so tables created in the fixture are invisible to the route handler. Fix: pass `poolclass=StaticPool` to `create_engine` so all connections share a single underlying connection. Required in every test file that uses an in-memory DB with a running app.

```python
from sqlalchemy.pool import StaticPool
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

---

## FilterBar: delete keys, don't set empty strings (2026-07-16)
When a filter is cleared, delete the key from the filters object entirely. If you set `{ type: "" }`, `buildQuery` in Ledger will include `?type=` in the URL, which the FastAPI validator will reject (pattern `^(debit|credit)$`). The correct pattern:

```js
function set(key, value) {
  const next = { ...filters };
  if (value) { next[key] = value; } else { delete next[key]; }
  onChange(next);
}
```

---

## Layout: `h-full` in UploadPanel requires flex column parent (2026-07-16)
UploadPanel uses `h-full` on all its state renderings to vertically center content. This only works if `<main>` establishes a height context. Change `<main>` from `overflow-auto` to `flex-1 flex flex-col overflow-hidden`. Then wrap the ledger view's content in a `flex-1 min-h-0` div so Ledger's internal scroll container works correctly.

---

## PII redaction: conservative by design, known gaps documented (2026-07-11)
`pii_filter.py` uses labeled-pattern regex only — catches account/routing/card/SSN when preceded by a recognizable label or in an unambiguous format (4×4 card, 16-digit unbroken string). Intentionally does NOT redact unlabeled digit sequences (would strip transaction reference IDs). Known gaps: unlabeled account numbers, numbers in transaction descriptions, non-US formats (IBAN, sort codes, BSBs). Documented in module docstring and commit message.

---

## Merchant map: user edits are permanent, AI cannot downgrade (2026-07-10)
`upsert_entry()` in `merchant_mapper.py` checks the existing entry's `source` before updating. If `source == "user"`, the entry is never overwritten by AI. This prevents a future AI batch from reverting a manual correction. User edits set `source="user"` and `confidence=1.0`.

---

## Batched AI categorization: inject map context for consistency (2026-07-10)
The categorization prompt includes a sample of existing merchant-map entries so the AI assigns the same category to similar merchants. Without this, repeated uploads may get slightly different categories for the same merchant pattern due to LLM non-determinism. Map context is injected as a "here's how we've categorized similar merchants before" block.
