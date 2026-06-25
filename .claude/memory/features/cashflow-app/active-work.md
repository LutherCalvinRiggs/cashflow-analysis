**Feature:** cashflow-app
**Status:** In Progress
**Last Updated:** 2026-06-25
**Branch:** claude/phase-1-extraction

## What Was Done
- Phase 0 complete and merged to main (PR #2) — backend, frontend, database
- BIP pipeline added: `bip_pipeline.py`, `/bip` skill, post-commit workflow integration
- Task 1.1 complete: `backend/services/pdf_extractor.py` — pdfplumber wrapper, per-page extraction, graceful error handling

## Next Steps
- Task 1.2: AI client wrapper — `backend/services/ai_client.py`, `complete(system, user) -> str`, Anthropic + OpenAI support
- Task 1.3: Upload endpoint — `POST /api/upload`, wires extractor + ai_client + DB
- Task 1.4: Categorization service

## Blockers
None
