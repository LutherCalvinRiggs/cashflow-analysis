# Project Plan — cashflow-analysis

## Overview

A locally-run web application that turns PDF bank statements into a structured, queryable financial ledger. The user uploads statements, an AI model extracts and categorizes transactions, and the app presents them as a filterable ledger with charts and a chat interface for open-ended financial questions.

The app is designed to be cloned, configured with an API key, and run entirely on a local machine. No cloud database, no external data storage. The AI provider is swappable — Anthropic, OpenAI, or any OpenAI-compatible endpoint.

This is a public build. Each commit ships a working increment and is documented with a LinkedIn post.

---

## Tech Stack

### Backend
- **Python** with **FastAPI** — lightweight API server, easy for Claude Code to extend
- **SQLite** via **SQLAlchemy** — single-file database, zero setup, portable between machines
- **pdfplumber** — PDF text extraction; handles most bank statement layouts
- **Anthropic Python SDK** (or `openai` SDK) — AI extraction and chat, provider-swappable via config

### Frontend
- **React** (Vite) — component-based UI, good for the ledger + chart + chat layout
- **Recharts** — charting library, straightforward integration with React
- **TailwindCSS** — utility-first styling, dark mode support built in

### Dev / Infra
- **SQLite** for persistence (no Docker required to get started)
- **dotenv** for config (API key, model name, provider base URL)
- **pytest** for backend tests
- **Vite dev server** proxied to FastAPI during development

### Why this stack
- FastAPI + SQLite = minimal setup, maximum portability
- React + Vite = fast iteration, no build complexity
- Everything runs on `localhost` with two terminal windows
- Claude Code works well with Python and React separately; clear API boundary between them makes handoffs clean

---

## Repository Structure

```
cashflow-analysis/
├── README.md
├── docs/
│   ├── PLAN.md              # This file
│   ├── PROMPTS.md           # All AI prompts used in the system
│   └── CATEGORIES.md        # Default category definitions + customization guide
├── backend/
│   ├── main.py              # FastAPI app entrypoint
│   ├── config.py            # API key, model, provider config from .env
│   ├── database.py          # SQLAlchemy setup, models
│   ├── models.py            # Pydantic schemas
│   ├── routes/
│   │   ├── upload.py        # PDF upload + extraction endpoint
│   │   ├── transactions.py  # CRUD + filter endpoints
│   │   ├── stats.py         # Aggregates, monthly summaries
│   │   └── chat.py          # Chat/Q&A endpoint
│   ├── services/
│   │   ├── pdf_extractor.py # pdfplumber text extraction
│   │   ├── ai_client.py     # Provider-agnostic AI wrapper
│   │   └── categorizer.py   # Categorization logic + prompt assembly
│   └── tests/
│       ├── test_extraction.py
│       └── test_categorization.py
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── UploadPanel.jsx
│   │   │   ├── Ledger.jsx
│   │   │   ├── FilterBar.jsx
│   │   │   ├── Charts.jsx
│   │   │   └── ChatPanel.jsx
│   │   ├── hooks/
│   │   │   └── useTransactions.js
│   │   └── api/
│   │       └── client.js    # Fetch wrapper for backend API
├── .env.example
└── .gitignore
```

---

## Database Schema

### `statements` table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| filename | TEXT | Original PDF filename |
| institution | TEXT | Bank name (extracted or user-provided) |
| account_last4 | TEXT | Last 4 digits of account |
| account_type | TEXT | checking / savings / credit |
| period_start | DATE | Statement start date |
| period_end | DATE | Statement end date |
| uploaded_at | TIMESTAMP | |
| raw_text | TEXT | Full extracted PDF text |

### `transactions` table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| statement_id | INTEGER FK | References statements.id |
| date | DATE | |
| description | TEXT | Raw description from statement |
| amount | REAL | Always positive |
| type | TEXT | credit / debit |
| category | TEXT | AI-assigned category |
| category_confidence | TEXT | high / medium / low |
| notes | TEXT | AI-generated annotation (optional) |
| is_internal_transfer | BOOLEAN | Flagged by AI |
| created_at | TIMESTAMP | |

### `monthly_stats` table
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | |
| month | TEXT | YYYY-MM |
| account_last4 | TEXT | |
| total_credits | REAL | |
| total_debits | REAL | |
| net | REAL | |
| ending_balance | REAL | |
| category_breakdown | TEXT | JSON blob |
| computed_at | TIMESTAMP | |

---

## Task List

Tasks are ordered for sequential execution by Claude Code. Each task should be a single commit. Sub-tasks are implementation notes, not separate commits.

---

### Phase 0 — Repo scaffolding
**Goal:** Empty but runnable skeleton. Both servers start without errors.

- [ ] **0.1** Initialize backend
  - Create `backend/` with `main.py`, `config.py`, `requirements.txt`
  - FastAPI app with a single `GET /health` endpoint returning `{ status: "ok" }`
  - `.env.example` with `ANTHROPIC_API_KEY`, `AI_MODEL`, `AI_BASE_URL`, `DATABASE_URL`
  - `.gitignore` covering `.env`, `__pycache__`, `*.db`, `node_modules`, `dist`

- [ ] **0.2** Initialize frontend
  - Vite + React scaffold in `frontend/`
  - Tailwind configured
  - Proxy `/api` to `http://localhost:8000` in `vite.config.js`
  - Single `App.jsx` with placeholder layout: sidebar + main content area + chat panel

- [ ] **0.3** Initialize database
  - SQLAlchemy setup in `database.py`
  - Create all three tables on startup
  - Confirm tables exist on `GET /health`

---

### Phase 1 — PDF ingestion + AI extraction
**Goal:** Upload a PDF, get structured transactions back, store them.

- [ ] **1.1** PDF text extraction service
  - `services/pdf_extractor.py` uses pdfplumber
  - Extract raw text page by page
  - Return `{ pages: [...], full_text: "..." }`
  - Handle extraction failures gracefully (log, don't crash)

- [ ] **1.2** AI extraction endpoint
  - `POST /api/upload` accepts multipart PDF
  - Calls pdf_extractor, then passes text to AI via `services/ai_client.py`
  - Uses EXTRACTION prompt from `docs/PROMPTS.md`
  - Parses JSON response, writes to `statements` + `transactions` tables
  - Returns `{ statement_id, transaction_count, warnings: [] }`

- [ ] **1.3** AI client wrapper (`services/ai_client.py`)
  - Single function: `complete(system_prompt, user_prompt) -> str`
  - Reads provider, model, base_url, api_key from config
  - Compatible with Anthropic SDK and OpenAI SDK (switchable via `AI_PROVIDER` env var)

- [ ] **1.4** Upload UI
  - `UploadPanel.jsx`: drag-and-drop or file picker, accepts PDF only
  - Shows upload progress, then extraction result summary
  - Displays warnings if any transactions were flagged

---

### Phase 2 — Ledger + filters
**Goal:** View all transactions in a filterable table.

- [ ] **2.1** Transactions API
  - `GET /api/transactions` with query params: `category`, `account`, `date_from`, `date_to`, `type`, `page`, `limit`
  - Returns paginated list + total count

- [ ] **2.2** Ledger component
  - `Ledger.jsx`: date | description | amount | type | category columns
  - Chronological by default, most recent first
  - Color-coded: credits green, debits red
  - Click row to expand and show AI notes

- [ ] **2.3** Filter bar
  - `FilterBar.jsx`: dropdowns for category, account, type; date range pickers
  - Filters apply immediately, update ledger and charts

- [ ] **2.4** Category management
  - `GET /api/categories` returns current category list
  - Categories stored in a `categories` table (id, name, description, color)
  - Seeded from `docs/CATEGORIES.md` default list on first run
  - UI to add / rename / reorder categories (Phase 2 stretch goal)

---

### Phase 3 — Charts + statistics
**Goal:** Visual overview of cash flow over time.

- [ ] **3.1** Stats API
  - `GET /api/stats/monthly` returns monthly income / expenses / net per account
  - `GET /api/stats/categories` returns category totals for a date range
  - `GET /api/stats/balance` returns running balance over time

- [ ] **3.2** Monthly bar chart
  - Income (green) vs. expenses (red) per month
  - Net line overlay
  - Recharts BarChart + LineChart combo

- [ ] **3.3** Category donut / breakdown chart
  - Category spend for selected period
  - Click slice to filter ledger to that category

- [ ] **3.4** Running balance line chart
  - Combined checking + savings balance over time
  - Optional: per-account toggle

---

### Phase 4 — Chat interface
**Goal:** Ask natural language questions, get answers grounded in the actual data.

- [ ] **4.1** Chat API
  - `POST /api/chat` accepts `{ message, conversation_history }`
  - Assembles context: monthly stats summary + recent transactions relevant to the question
  - Uses CHAT SYSTEM PROMPT from `docs/PROMPTS.md`
  - Returns `{ response, sources: [] }` (sources = transaction IDs referenced)

- [ ] **4.2** Context assembly service
  - Pull last 6 months of monthly stats
  - Pull top 20 transactions by amount for the relevant period
  - Pull category totals
  - Format as a compact financial context block injected into the system prompt

- [ ] **4.3** Chat UI
  - `ChatPanel.jsx`: message thread, input box, send button
  - Renders markdown in responses
  - Shows conversation history within session (not persisted to DB in v1)
  - Suggested starter questions shown on first open

---

### Phase 5 — Polish + public release prep
**Goal:** Repo is clean, documented, and ready for others to clone and run.

- [ ] **5.1** Setup documentation
  - `README.md` updated with full setup steps: clone, `.env`, install, run
  - Notes on swapping AI provider

- [ ] **5.2** Category customization guide
  - `docs/CATEGORIES.md` documents the default set and how to edit
  - UI for managing categories (if not done in 2.4)

- [ ] **5.3** Error handling pass
  - Graceful errors on bad PDFs, API failures, missing env vars
  - User-facing error messages (not stack traces)

- [ ] **5.4** Basic auth (optional, stretch)
  - Single hardcoded password via env var to protect the app if exposed on a network
  - Not required for localhost-only use

---

## Build in Public — LinkedIn Commit Posts

Each phase completion (and some individual tasks) should get a LinkedIn post. Suggested cadence:

| Commit | Post topic |
|---|---|
| Phase 0 complete | "Starting cashflow-analysis in public: here's the plan" |
| Phase 1 complete | "PDFs → structured transactions: how I'm using Claude to parse bank statements" |
| Phase 2 complete | "The ledger is live: filtering 18 months of transactions by category" |
| Phase 3 complete | "Charts don't lie: visualizing where the money actually goes" |
| Phase 4 complete | "Talking to my bank statements: building a chat interface for personal finance" |
| Phase 5 complete | "cashflow-analysis v1 is done. Here's how to run it yourself." |

Post format suggestion: 2–3 sentences on what shipped, a screenshot or short screen recording, link to the commit or diff, and one thing learned. Keep it practical, not promotional.

---

## Notes for Claude Code

- Work task by task in order. Each task = one commit with a clear message like `feat: 1.2 AI extraction endpoint`.
- Don't skip ahead — later phases depend on earlier ones being solid.
- When in doubt about a tech decision (ORM vs raw SQL, component library choice, etc.), leave a `# TODO: discuss with Luther` comment and move on.
- The `docs/` folder is the source of truth for prompts and categories — read it before touching the AI service layer.
- Keep the AI client wrapper (`ai_client.py`) truly provider-agnostic. No Anthropic-specific types should leak into other files.
- All environment config flows through `config.py`. No hardcoded strings elsewhere.
