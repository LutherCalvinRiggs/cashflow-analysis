# Decisions — cashflow-app

## 2026-07-19
- **Backend runs on Homebrew Python 3.13.3** (`backend/.venv`), not pyenv's 3.9.6 — `models.py` uses `str | None` syntax which requires 3.10+. Rebuild the venv with `/opt/homebrew/bin/python3.13 -m venv .venv` if it's ever recreated.
- **Root `package.json` with `npm run start`** (concurrently: `start:api` + `start:web`) boots both servers. Named `start`, not `dev`, to avoid colliding with `frontend`'s own `npm run dev`.
- **`pytest==8.3.4` pinned in `backend/requirements.txt`** — it was missing; tests couldn't run from a fresh install.
- **`.env` lives at repo root** (not `backend/`) — `load_dotenv()` walks up from `config.py` and finds it; the BIP pipeline reads `GITHUB_TOKEN` from the same file.

## 2026-07-20/21
- **Reconciled a parallel session's commits by merging, not force-pushing.** Another session had pushed 3 commits to `claude/phase-1-extraction` (bip skill fix, an e2e test plan, a memory update) while this session was also working the branch. Merged rather than overwrote; kept this session's e2e-test-plan.md (had real results) as the base and folded in the other session's extra test scenarios; accepted its task-2.5 "no hook needed" call after verifying against the code, rejected its task-1.5 "covered" claim since `test_extraction.py` doesn't exist.
- **`/eval` outcome: 2 existing `code-standards.md` rules were actively wrong, not just violated.** "Let unexpected exceptions propagate to FastAPI's default handler" breaks any frontend expecting JSON errors (confirmed empirically — this is what caused the "Unexpected token 'I'" bug). "Never query inside a loop" was violated by the original categorizer batch loop and was the root cause of the merchant_map UNIQUE crash. Both rules updated rather than just noting the violation. Also added: never infer row-creation from ORM session-membership checks; and a pre-push divergence check in the (user-global) git-workflow skill.
