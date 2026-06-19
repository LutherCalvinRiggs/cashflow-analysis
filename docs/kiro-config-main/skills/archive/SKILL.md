---
name: archive
description: Move a completed feature to archive. Captures final state, clears active tracking. Use when a feature is done and tested.
---

## Usage

`/archive <feature-name>` — Archive a completed feature

## Actions

1. Read `~/.kiro/memory/features/<feature-name>/active-work.md`
2. Confirm status is "Complete" (if not, ask user to confirm archiving incomplete work)
3. **Check for related documentation** in `~/.kiro/docs/` (files containing feature name)
4. Create `~/.kiro/memory/archive/<date>-<feature-name>.md` with:
   ```
   # <feature-name>
   **Completed:** <date>
   **Repos:** <repos involved>

   ## Summary
   <what was built>

   ## Key Decisions
   <from decisions.md + any architecture decisions from docs>

   ## Implementation Details
   <from active-work.md + technical details from docs>

   ## Files Changed
   <from active-work.md>

   ## Lessons Learned
   <from implementation-notes.md + key learnings from docs>

   ## Documentation Sources
   <list of docs that were integrated and deleted>
   ```
5. **Delete related documentation** from `~/.kiro/docs/` after successful integration
6. Remove `~/.kiro/memory/features/<feature-name>/` directory
7. If cross-repo-active-work.md references this feature, reset to Idle
8. Append to feature-work-log.md: `| <date> | <feature> | Archived | Complete |`

## Rules

- Always confirm before deleting the feature directory
- **Search `~/.kiro/docs/` for related documentation** (fuzzy match on feature name)
- **Integrate key information** from docs into archive entry before deleting docs
- Keep archive entries comprehensive but concise — preserve decisions, learnings, and context
- Don't archive if there are unresolved blockers without user confirmation
- **Clean up documentation** — delete source docs from `~/.kiro/docs/` after successful integration
