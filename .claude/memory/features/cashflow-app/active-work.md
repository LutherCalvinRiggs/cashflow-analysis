**Feature:** cashflow-app
**Status:** In Progress
**Last Updated:** 2026-07-20
**Branch:** claude/phase-1-extraction

## What Was Done
- Phases 1 and most of 2 committed on this branch: 1.1–1.4, upload UI, PII redaction, transactions+categories API, Ledger, FilterBar
- Dev environment set up: backend venv on Python 3.13 (`backend/.venv`), npm deps installed
- Root `package.json` added — `npm run start` boots both servers via concurrently
- `pytest==8.3.4` added to requirements.txt; suite passes (40 tests)
- E2E test plan written: `.claude/memory/features/cashflow-app/tests/e2e-test-plan.md` (5 sections: upload happy path, upload edge cases, ledger, filters, resilience)
- 4 follow-up tasks queued in TaskList (not yet started), to work through after Luther's manual test run:
  1. `test_extraction.py` — missing extraction coverage (plan 1.5)
  2. `useTransactions` hook (plan 2.5)
  3. Frontend test tooling (Vitest + RTL) — currently only lint/build
  4. CLAUDE.md env var drift — docs say `ANTHROPIC_API_KEY`, code uses `AI_API_KEY`

## Next Steps
- **Waiting on Luther**: getting a real AI_API_KEY into `.env`, starting `npm run start`, running the e2e test plan
- Once results are in: triage findings, then work TaskList #1–4 in order
- Uncommitted (holding per Luther's request, not ready to commit): root package.json/package-lock.json, backend/requirements.txt, .claude/skills/bip/SKILL.md (merge conflict fix), all memory files

## Blockers
None — paused on user's manual test run, not stuck
