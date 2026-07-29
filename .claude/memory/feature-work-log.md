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
| 2026-07-19 | cashflow-app | E2E test plan created (session A) | `.claude/memory/features/cashflow-app/tests/e2e-test-plan.md` |
| 2026-07-19 | cashflow-app | PR #3 opened — Phase 1 + 2 | Awaiting user e2e testing before merge |
| 2026-07-19 | cashflow-app | Dev env setup + memory sync (session B, parallel) | Venv on Py3.13, root `npm run start`, pytest in reqs, 40 tests pass; memory caught up to reality (1.2–2.3 committed since last update) |
| 2026-07-20 | cashflow-app | E2E test plan rewritten from live testing (session B) | Plan rewritten in tests/e2e-test-plan.md reflecting actual test run in progress; 4 tasks queued (extraction tests, useTransactions hook, frontend test tooling, CLAUDE.md drift) |
| 2026-07-20 | cashflow-app | Live e2e test run — found and fixed 2 real bugs | (1) merchant_map UNIQUE constraint crash on repeat merchants in one batch (autoflush=False + no flush after add); (2) merchant category edits only reached the clicked transaction, not siblings, due to suggested_key being discarded and substring-only matching. Built PATCH /api/transactions/{id}/category + ledger row-edit UI; fixed new_map_entries counter bug too |
| 2026-07-20 | cashflow-app | Backend moved off port 8000 | macOS Control Center/AirPlay Receiver claims 8000 by default; moved to 8787 |
| 2026-07-20 | cashflow-app | Reconciled parallel session's commits | Merged (not force-pushed) another session's bip-skill fix, e2e test plan, and memory update; pushed 8 commits total to origin/claude/phase-1-extraction |
| 2026-07-21 | cashflow-app | `/eval` — 2 code-standards.md rules fixed, 1 added, git-workflow skill updated | Exception-propagation and query-in-loop rules were actively wrong (root causes of 2 bugs this session); added explicit-created-boolean rule; added pre-push divergence check to user-global git-workflow skill |
| 2026-07-21 | cashflow-app | Luther spotted PII visible in the UI | Not yet investigated. Next task: e2e test plan section 1.6 (PII check) |
| 2026-07-28 | cashflow-app | Fixed PII-in-UI bug Luther spotted | pii_filter.py now redacts embedded reference numbers + street addresses in descriptions; upload.py no longer stores unredacted raw_text at rest. 53 tests passing (was 48). Old test data purged pending re-upload for live verification |
| 2026-07-28 | cashflow-app | Dev server instability found, debugging deferred | Orphaned processes from an untracked prior session held ports 8787/5173 and corrupted Vite's dep cache (silent 503s, blank page, no console errors). Worked around by killing stale PIDs + clearing .vite cache; root cause unconfirmed. Luther wants this properly debugged in a future session |
| 2026-07-28 | cashflow-app | Found and scrubbed real bank data leaked into the public repo | Real reference numbers, an ATM address, and a third party's name had been used as code comments/test fixtures (partly pre-existing, partly introduced this session). Scrubbed working tree, then rewrote git history on claude/phase-1-extraction (git filter-repo --refs, scoped off main) and force-pushed. Backup kept at backup/phase-1-extraction-pre-scrub-2026-07-28. Saved feedback memory to prevent recurrence |
