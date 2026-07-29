# Implementation Notes — cashflow-app

## LinkedIn Post Automation (2026-06-25)
After each commit, a "Building in Public" block is manually copy-pasted to LinkedIn. This needs to be automated — likely via a GitHub Action that triggers on push to main and posts via the LinkedIn API. Requires a LinkedIn API token. Revisit after Phase 1 ships.

## Gotchas (2026-07-19/20)
- **Env var is `AI_API_KEY`, not `ANTHROPIC_API_KEY`** — CLAUDE.md still says the latter; `config.py` and `.env.example` are the truth. Tracked as TaskList #4.
- **Commit numbering drifted from plan numbering** — e.g. commit "2.2 Ledger" is plan task 2.3, commit "1.4 upload UI" is plan task 1.6. Trust file existence + plan.md checkboxes, not commit labels.
- **`test_extraction.py` genuinely does not exist** — confirmed by directory listing. A parallel session's memory update marked plan task 1.5 "done, covered in 1.4," but no such file was created; extraction (including AI JSON parsing, the highest-risk untested path) has zero automated coverage. Tracked as TaskList #1 — trust the file system over prior status claims.
- **`useTransactions` hook (plan 2.5) deliberately not built** — a parallel session's design call: Ledger.jsx fetches directly, no separate hook needed. Confirmed this matches the actual code and is a reasonable choice; accepted, not a gap.
- **`main.py` must run with CWD = `backend/`** — bare module imports and relative SQLite path. The root `start:api` script handles this.
- **Port 8000 is claimed by macOS Control Center (AirPlay Receiver) by default** — moved backend to 8787. Don't reuse 7000 either (also reserved, same reason).
- **`uvicorn --reload` does not watch `.env`** — only the `backend/` directory. Rotating an API key or otherwise editing `.env` requires a full stop/restart of `npm run start`, not just a reload.
- **`concurrently` needs `-k` (kill-others)** — without it, Ctrl+C can stop the frontend but leave the backend's `uvicorn --reload` subprocess running (Python `multiprocessing` spawn workers ignore SIGINT by design). `-k` force-kills every process when any one exits.
- **Backend venv must be Python 3.13+, not the repo's pyenv default (3.9.6)** — `models.py` uses `X | None` union syntax (3.10+). Rebuild with `/opt/homebrew/bin/python3.13 -m venv .venv` if the venv is ever recreated.
- **`merchant_map.pattern` has a UNIQUE constraint, and the session is `autoflush=False`** — `upsert_entry()` must `db.flush()` immediately after `db.add()` on a new entry, or a batch with 2+ transactions from the same merchant will try to insert duplicate patterns and crash with `sqlite3.IntegrityError` at commit time.
- **Merchant matching must use word-subset comparison, not substring containment** — the AI's `suggested_key` often drops filler words (e.g. "Zelle Payment **To** Jane Doe LLC" → key "zelle payment jane doe"), so `"pattern" in key` fails even though they're the same merchant. `find_related_entry` / `find_matching_transactions` compare word sets instead.
- Unplanned services added: `pii_filter.py` (PII redaction before AI), `merchant_mapper.py` (merchant map + batched AI fallback in categorizer), `prompt_loader.py`.

## Dev server instability — needs debugging (2026-07-28, deferred by Luther)
Starting `npm run start` found port 8787 and 5173 **already bound by orphaned processes** from an earlier, untracked session (found via `lsof -nP -iTCP:<port> -sTCP:LISTEN`, not visible via a plain `ps`/`lsof` glance). The new `start:api` failed immediately with `[Errno 48] Address already in use`; `concurrently -k` then killed the new (healthy) frontend process too, while a *stale* frontend from the earlier session kept serving on 5173 in a broken state — Vite's `node_modules/.vite/deps` cache appears to have been corrupted by two concurrent optimizer runs writing to it at once, leaving `react.js`, `react-dom_client.js`, and `react_jsx-dev-runtime.js` all returning `503` and the page rendering blank with zero console errors (the failure was silent — only visible via `read_network_requests`, not `read_console_messages`). Fixed for this session by killing the orphaned PIDs, deleting `frontend/node_modules/.vite`, and restarting clean — but **root cause of why stale servers were still running/bound is unconfirmed**. Luther wants this debugged properly in a future session, not patched around again.

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
