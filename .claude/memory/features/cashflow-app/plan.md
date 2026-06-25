# Plan — cashflow-app

Build the full cashflow-analysis application across 5 phases per docs/PLAN.md.

---

## Phase 0 — Repo Scaffolding ✅ COMPLETE (merged to main)
*Goal: Empty but runnable skeleton. Both servers start without errors.*

- [x] **0.1** Initialize backend
  - `backend/main.py` — FastAPI app, `GET /health` returns `{ status: "ok" }`
  - `backend/config.py` — load all env vars (API key, model, provider, DB URL)
  - `backend/requirements.txt` — fastapi, uvicorn, pdfplumber, sqlalchemy, python-dotenv, anthropic, openai
  - `.env.example` — ANTHROPIC_API_KEY, AI_PROVIDER, AI_MODEL, AI_BASE_URL, DATABASE_URL

- [x] **0.2** Initialize frontend
  - Vite + React scaffold in `frontend/`
  - Tailwind configured
  - `vite.config.js` — proxy `/api` to `http://localhost:8000`
  - `App.jsx` — placeholder layout: sidebar + main content + chat panel

- [x] **0.3** Initialize database
  - `backend/database.py` — SQLAlchemy engine + session factory
  - `backend/database.py` — define ORM models for `statements`, `transactions`, `monthly_stats`, `categories`
  - Tables created on startup via `Base.metadata.create_all()`
  - `GET /health` confirms tables exist

---

## Phase 1 — PDF Ingestion + AI Extraction
*Goal: Upload a PDF, get structured transactions back, store them.*

- [x] **1.1** PDF text extraction service
  - `backend/services/pdf_extractor.py` using pdfplumber
  - Extract text page by page, return `{ pages: [...], full_text: "..." }`
  - Handle corrupt/unreadable PDFs gracefully — log error, return empty result with warning

- [ ] **1.2** AI client wrapper
  - `backend/services/ai_client.py` — single function `complete(system_prompt, user_prompt) -> str`
  - Reads `AI_PROVIDER`, `AI_MODEL`, `AI_BASE_URL`, `ANTHROPIC_API_KEY` from config
  - Anthropic branch: uses `anthropic.Anthropic` client
  - OpenAI branch: uses `openai.OpenAI` client with optional base_url override
  - No provider-specific types leak out of this file

- [ ] **1.3** AI extraction endpoint
  - `backend/routes/upload.py` — `POST /api/upload` accepts multipart PDF
  - Calls pdf_extractor → ai_client with EXTRACTION prompt from `docs/PROMPTS.md`
  - Parses AI JSON response, writes to `statements` + `transactions` tables
  - Calls categorizer on extracted transactions (task 1.4 dependency)
  - Returns `{ statement_id, transaction_count, warnings: [] }`

- [ ] **1.4** Categorization service
  - `backend/services/categorizer.py` — takes list of transactions, calls AI with CATEGORIZATION prompt
  - Loads category list from `categories` table (seeded from `docs/CATEGORIES.md`)
  - Seeds `categories` table on first call if empty
  - Returns transactions with `category`, `category_confidence`, `notes` populated

- [ ] **1.5** Backend tests — extraction + categorization
  - `backend/tests/test_extraction.py` — mock ai_client, test JSON parsing, bad PDF handling
  - `backend/tests/test_categorization.py` — mock ai_client, test category assignment logic

- [ ] **1.6** Upload UI
  - `frontend/src/components/UploadPanel.jsx` — drag-and-drop + file picker, PDF only
  - Shows upload progress, extraction result summary (transaction count, warnings)
  - Calls `POST /api/upload` via `api/client.js`

---

## Phase 2 — Ledger + Filters
*Goal: View all transactions in a filterable table.*

- [ ] **2.1** Transactions API
  - `backend/routes/transactions.py` — `GET /api/transactions`
  - Query params: `category`, `account`, `date_from`, `date_to`, `type`, `page`, `limit`
  - Returns `{ transactions: [...], total: N, page: N, limit: N }`

- [ ] **2.2** Categories API
  - `backend/routes/transactions.py` — `GET /api/categories`
  - Returns full category list with name, description, color
  - Seeds from `docs/CATEGORIES.md` on first call if table is empty

- [ ] **2.3** Ledger component
  - `frontend/src/components/Ledger.jsx` — table: date | description | amount | type | category
  - Most recent first; credits green, debits red
  - Click row to expand — shows AI notes and category confidence
  - Pagination controls

- [ ] **2.4** Filter bar
  - `frontend/src/components/FilterBar.jsx` — dropdowns: category, account, type; date range pickers
  - Filters apply immediately on change, update ledger

- [ ] **2.5** useTransactions hook
  - `frontend/src/hooks/useTransactions.js` — manages filter state, fetches from API, handles loading/error

---

## Phase 3 — Charts + Statistics
*Goal: Visual overview of cash flow over time.*

- [ ] **3.1** Stats API
  - `backend/routes/stats.py` — `GET /api/stats/monthly`, `/api/stats/categories`, `/api/stats/balance`
  - Monthly: income, expenses, net per month per account
  - Categories: totals for a date range
  - Balance: running balance over time from transaction history

- [ ] **3.2** Monthly bar chart
  - `frontend/src/components/Charts.jsx` — income (green) vs expenses (red) per month
  - Net line overlay using Recharts BarChart + LineChart combo

- [ ] **3.3** Category breakdown chart
  - Donut/pie chart of category spend for selected period
  - Click slice → filters ledger to that category

- [ ] **3.4** Running balance line chart
  - Combined balance over time
  - Per-account toggle (stretch)

---

## Phase 4 — Chat Interface
*Goal: Ask natural language questions grounded in the actual data.*

- [ ] **4.1** Context assembly service
  - `backend/services/context_builder.py`
  - Pulls last 6 months of monthly stats
  - Pulls top 20 transactions by amount for relevant period
  - Pulls category totals
  - Formats compact context block per PROMPTS.md template

- [ ] **4.2** Chat API
  - `backend/routes/chat.py` — `POST /api/chat` accepts `{ message, conversation_history }`
  - Assembles context via context_builder, calls ai_client with CHAT prompt
  - Returns `{ response, sources: [] }`

- [ ] **4.3** Chat UI
  - `frontend/src/components/ChatPanel.jsx` — message thread, input box, send button
  - Renders markdown in responses
  - Conversation history within session (not persisted)
  - Suggested starter questions on first open

---

## Phase 5 — Polish + Release
*Goal: Repo is clean, documented, and ready for others to clone and run.*

- [ ] **5.1** Error handling pass
  - Graceful errors on bad PDFs, AI API failures, missing env vars
  - User-facing messages in frontend (no stack traces)
  - FastAPI exception handlers for common failure modes

- [ ] **5.2** README update
  - Full setup steps: clone, `.env`, install, run
  - Notes on swapping AI provider
  - Screenshots of the app

- [ ] **5.3** Basic auth (stretch)
  - Single hardcoded password via `AUTH_PASSWORD` env var
  - Simple middleware — not required for localhost-only use

---

## Billing Estimate

| | Human (no AI) | AI-Assisted |
|---|---|---|
| **Total** | 61–95h | 20–38h |
| **Time Saved** | — | ~62% (41–57h) |

Highest complexity: 1.3 Upload endpoint (wires extractor + AI + DB). Biggest risk: AI prompt tuning quality is iterative.

---

## Risks / Notes

- Task 1.3 depends on 1.2 and 1.4 — build AI client and categorizer before wiring the upload endpoint
- pdfplumber handles most bank statement layouts but may struggle with image-only PDFs — flag this in extraction warnings rather than crashing
- AI JSON parsing is the most likely failure point — extraction and categorization both need robust fallback handling
- Recharts requires React 18+ — confirm Vite scaffold uses React 18
