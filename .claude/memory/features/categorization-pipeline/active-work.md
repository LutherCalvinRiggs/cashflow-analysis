**Feature:** categorization-pipeline
**Status:** Complete
**Last Updated:** 2026-06-29
**Branch:** claude/phase-1-extraction

## What Was Done
- T1: Added `notes` column to Transaction, added `MerchantMap` table to database.py
- T2: Updated PROMPTS.md categorization prompt to return `suggested_key`
- T3: Created backend/services/merchant_mapper.py — normalize, lookup, apply_map, upsert_entry
- T4: Created backend/services/categorizer.py — map-first lookup, batched AI fallback (BATCH_SIZE=40)
- T5: Wired categorize() into POST /api/upload, added new_map_entries to UploadResponse
- T6: 12 tests passing in backend/tests/test_categorization.py

## Architecture
- MerchantMap table stores normalized merchant keys (e.g. "foodcellar lic")
- On upload: map hits get categories instantly (no AI call); misses go to AI in batches of 40
- AI returns suggested_key per transaction → new map entries created automatically
- User edits set source="user", confidence=1.0 — AI never downgrades user-verified entries
- map_context injected into every AI categorization call for consistency across batches

## Next Steps
- Task 1.4 (PLAN.md): Upload UI — UploadPanel.jsx
