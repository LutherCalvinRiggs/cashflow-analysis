# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Backend** (once Phase 0 is complete):
```bash
cd backend
pip install -r requirements.txt
python main.py                  # starts FastAPI on localhost:8000
pytest tests/                   # run all tests
pytest tests/test_extraction.py # run a single test file
```

**Frontend** (once Phase 0 is complete):
```bash
cd frontend
npm install
npm run dev     # starts Vite dev server on localhost:5173, proxied to backend
npm run build
```

The Vite dev server proxies `/api` to `http://localhost:8000`. Both servers must be running during development.

**Environment**: Copy `.env.example` to `.env` and fill in:
- `ANTHROPIC_API_KEY` (or OpenAI key)
- `AI_PROVIDER` — `anthropic` or `openai`
- `AI_MODEL` — e.g. `claude-sonnet-4-6`
- `AI_BASE_URL` — optional, for custom endpoints
- `DATABASE_URL` — defaults to a local SQLite file

## Architecture

This is a locally-run personal finance tool: upload PDF bank statements → AI extracts and categorizes transactions → SQLite stores them → React dashboard displays them with filtering, charts, and a chat interface.

### Backend layout (`backend/`)
- `main.py` — FastAPI entrypoint
- `config.py` — all env config lives here; no hardcoded strings elsewhere
- `database.py` — SQLAlchemy setup; tables created on startup
- `models.py` — Pydantic request/response schemas
- `routes/` — one file per API group: `upload.py`, `transactions.py`, `stats.py`, `chat.py`
- `services/` — business logic: `pdf_extractor.py` (pdfplumber), `ai_client.py` (provider-agnostic wrapper), `categorizer.py`, `context_builder.py`, `chat_service.py`

### Frontend layout (`frontend/src/`)
- `App.jsx` — sidebar + main content area + chat panel layout
- `components/` — `UploadPanel`, `Ledger`, `FilterBar`, `Charts`, `ChatPanel`
- `api/client.js` — fetch wrapper; all API calls go through here

### Database (SQLite, 3 tables)
- `statements` — PDF metadata and raw extracted text
- `transactions` — individual transactions (FK to statements); stores AI-assigned category and confidence
- `monthly_stats` — precomputed monthly aggregates with a JSON `category_breakdown` column
- `categories` — seeded from `docs/CATEGORIES.md` on first run if table is empty

### AI layer
`services/ai_client.py` exposes a single function: `complete(system_prompt, user_prompt) -> str`. It reads `AI_PROVIDER` from config and delegates to either the Anthropic SDK or OpenAI SDK. **No Anthropic-specific types should leak out of this file.**

All prompts live in `docs/PROMPTS.md` — that is the source of truth. Do not hardcode or modify prompts inline in service code; reference this file instead.

## Development conventions

- Work task by task in the order defined in `docs/PLAN.md`. Each task = one commit (`feat: 1.2 AI extraction endpoint`).
- `docs/CATEGORIES.md` defines the 20 default categories. The AI uses the `description` field directly during categorization — specificity matters.
- When uncertain about a tech decision, leave a `# TODO: discuss with Luther` comment and continue.
- `docs/PROMPTS.md` defines four prompts: extraction, categorization, chat, and bulk re-categorization. Do not modify them without explicit instruction.
