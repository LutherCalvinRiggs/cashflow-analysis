# Plan — categorization-pipeline

## Goal
Build `backend/services/categorizer.py` that takes a `statement_id`, calls the AI with the categorization prompts from PROMPTS.md, and writes `category`, `confidence`, and `notes` back to each Transaction row. Wire it into `POST /api/upload` so it runs automatically after extraction.

## Context
- Categorization prompts already exist in `docs/PROMPTS.md` and are loaded by `backend/services/prompt_loader.py`
- `ai_client.complete()` is provider-agnostic
- `Transaction.confidence` is already a Float — keep `_confidence_to_float()` helper pattern
- The categorization AI response returns `[{id, category, confidence, notes}]` — "id" maps back to Transaction.id
- PLAN.md schema specifies a `notes TEXT` column on transactions (currently missing from database.py)

## Tasks

- [ ] **T1** Add `notes` column to `Transaction` in `backend/database.py`
- [ ] **T2** Create `backend/services/categorizer.py` — `categorize(statement_id, db)` function
- [ ] **T3** Update `backend/routes/upload.py` — call `categorize()` after commit, surface any warnings
- [ ] **T4** Write `backend/tests/test_categorization.py`

## Risks
- AI may return IDs that don't match (partial response, truncation) — categorizer must handle mismatches gracefully, not crash
- Large statements (100+ transactions) could hit token limits — acceptable for v1, log a warning

## Billing Estimate
TBD
