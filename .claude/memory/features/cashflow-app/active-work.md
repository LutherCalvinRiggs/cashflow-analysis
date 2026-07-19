**Feature:** cashflow-app
**Status:** In Progress — awaiting user testing before merge
**Last Updated:** 2026-07-19
**Branch:** claude/phase-1-extraction
**Open PR:** #3 — Phase 1 + 2 (not yet merged)

## What Was Done
- Phase 1 complete: PDF extraction, AI client wrapper, upload endpoint, merchant map + batched AI categorization, UploadPanel UI
- PII redaction hardening: always-on labeled-pattern filter before AI (pii_filter.py)
- Phase 2 complete: GET /api/transactions (paginated + filtered), GET /api/categories, Ledger.jsx, FilterBar.jsx
- /bip skill persisted to repo (.claude/skills/bip/SKILL.md)
- E2E test plan saved to .claude/memory/features/cashflow-app/tests/e2e-test-plan.md
- 40 automated tests passing (categorization, PII filter, transactions API)

## Next Steps
1. User runs e2e test plan against local stack (test plan in tests/e2e-test-plan.md)
2. Merge PR #3 to main
3. Begin Phase 3: Charts + stats API (GET /api/stats/monthly, /categories, /balance; Recharts components)

## Blockers
None — waiting on user testing
