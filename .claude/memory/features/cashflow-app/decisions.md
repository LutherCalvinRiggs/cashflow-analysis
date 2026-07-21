# Decisions — cashflow-app

## 2026-07-19
- **Backend runs on Homebrew Python 3.13.3** (`backend/.venv`), not pyenv's 3.9.6 — `models.py` uses `str | None` syntax which requires 3.10+. Rebuild the venv with `/opt/homebrew/bin/python3.13 -m venv .venv` if it's ever recreated.
- **Root `package.json` with `npm run start`** (concurrently: `start:api` + `start:web`) boots both servers. Named `start`, not `dev`, to avoid colliding with `frontend`'s own `npm run dev`.
- **`pytest==8.3.4` pinned in `backend/requirements.txt`** — it was missing; tests couldn't run from a fresh install.
- **`.env` lives at repo root** (not `backend/`) — `load_dotenv()` walks up from `config.py` and finds it; the BIP pipeline reads `GITHUB_TOKEN` from the same file.
