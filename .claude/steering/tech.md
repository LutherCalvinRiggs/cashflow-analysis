# Tech Stack

## Backend
- Python + FastAPI — API server on localhost:8000
- SQLite via SQLAlchemy — single-file DB, auto-created on startup
- pdfplumber — PDF text extraction
- Anthropic Python SDK or openai SDK — provider-agnostic via `AI_PROVIDER` env var
- pytest — backend tests in `backend/tests/`

## Frontend
- React + Vite — SPA on localhost:5173
- TailwindCSS — utility-first styling
- Recharts — charting library
- Vite proxies `/api` → `http://localhost:8000`

## Configuration
- All env vars flow through `backend/config.py` — no hardcoded strings elsewhere
- `.env`: `ANTHROPIC_API_KEY`, `AI_PROVIDER`, `AI_MODEL`, `AI_BASE_URL`, `DATABASE_URL`
- `AI_PROVIDER`: `anthropic` or `openai` (OpenAI-compatible endpoint)
