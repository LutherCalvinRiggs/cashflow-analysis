**Feature:** cashflow-app
**Status:** In Progress — e2e testing underway, PR #3 open awaiting merge
**Last Updated:** 2026-08-08
**Branch:** claude/phase-1-extraction
**Open PR:** #3 — Phase 1 + 2 (not yet merged)

## Where things stand
Phases 1+2 built and mostly e2e-tested live against real data. 65/65 backend tests passing. Today's session: PII redaction redesigned to be audience-scoped, batch upload + auto-redirect + FilterBar redesign + sort toggle shipped, chat panel relocated, upload dedup added, a categorization architecture fix (internal transfers assigned deterministically from extraction's flag, never guessed by the AI), and inline category creation from the ledger's category-edit panel (`POST /api/categories`, idempotent by design). Full narrative and rationale for all of it lives in `decisions.md` — this file is deliberately just the "resume cold" summary.

E2e test plan (`tests/e2e-test-plan.md`): sections 1–4 fully passing. Sections 5 (resilience), 6.1/6.2 (merchant map behavioral), 7 (API smoke tests), 8 (re-run automated suite count in the doc) still open.

**Uncommitted right now**: everything from today (redaction split, batch upload/FilterBar/sort, chat relocation, upload dedup, categorization fix) is sitting in the working tree pending Luther's approval per the CLAUDE.md commit gate.

## Next Steps
1. Continue e2e — section 5 (resilience) next
2. Get commit approval for today's uncommitted work
3. Batch-upload success path still untested (no test PDF available to the agent) — will happen naturally on Luther's next real upload
4. No test coverage yet for `year`/`month`/`sort`/`/transactions/periods`
5. Dev-server orphaned-process instability (2026-07-28) still deferred, not urgent
6. Once e2e passes: merge PR #3 → main, then start Phase 3 (charts + stats API)
7. `backup/phase-1-extraction-pre-scrub-2026-07-28` branch can be deleted once Luther confirms the rewritten history looks right

## Blockers
None
