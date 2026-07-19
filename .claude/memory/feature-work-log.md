# Feature Work Log

Chronological log of all feature work. Append-only.

| Date | Feature | Action | Outcome |
|------|---------|--------|---------|
| 2026-06-25 | cashflow-app | Phase 0 complete — backend, frontend, database | Merged to main via PR #2 |
| 2026-06-25 | cashflow-app | BIP pipeline + /bip skill added | Post-commit LinkedIn draft generation wired into workflow |
| 2026-06-25 | cashflow-app | Task 1.1 — PDF extraction service | `pdf_extractor.py` complete, pushed to claude/phase-1-extraction |
| 2026-07-10 | cashflow-app | Tasks 1.2 + 1.3 — AI client wrapper + upload endpoint | `ai_client.py`, `POST /api/upload` wiring extractor + AI + DB |
| 2026-07-10 | cashflow-app | Task 1.4 — categorization service + merchant map | `categorizer.py`, `merchant_mapper.py`, `MerchantMap` table, batched AI (40/call) |
| 2026-07-11 | cashflow-app | PII redaction hardening | `pii_filter.py` — account, routing, card, SSN redaction before AI; 20 tests |
| 2026-07-12 | cashflow-app | Task 1.4 upload UI | `UploadPanel.jsx` — 4-state machine, drag-and-drop, progress bar, result summary |
| 2026-07-12 | cashflow-app | Task 2.1 — transactions API | `GET /api/transactions` (paginated + filtered) + `GET /api/categories`; 8 tests |
| 2026-07-15 | cashflow-app | Task 2.2 — Ledger component | `Ledger.jsx` — color-coded table, pagination, accepts filters prop |
| 2026-07-16 | cashflow-app | Task 2.3 — FilterBar component | `FilterBar.jsx` — category, type, date range, exclude-transfers; state lifted to App.jsx |
| 2026-07-19 | cashflow-app | /bip skill persisted to repo | `.claude/skills/bip/SKILL.md` committed with frontmatter |
| 2026-07-19 | cashflow-app | E2E test plan created | `.claude/memory/features/cashflow-app/tests/e2e-test-plan.md` |
| 2026-07-19 | cashflow-app | PR #3 opened — Phase 1 + 2 | Awaiting user e2e testing before merge |
