---
name: handoff
description: Record completed work to memory for session continuity. Called when finishing a task or ending a session. Writes structured state to .claude/memory/.
---

## Usage

`/handoff <feature-name>` — Record what was accomplished

## Inputs (from the calling agent)

- Feature name
- Summary of what was done
- Files created/modified
- Tests written/run and results
- Decisions made
- Blockers or next steps

## Actions

1. Write/update `.claude/memory/features/<feature-name>/active-work.md`:
   ```
   **Feature:** <name>
   **Status:** <In Progress | Complete | Blocked>
   **Last Updated:** <timestamp>
   **Branch:** <current branch>

   ## What Was Done
   <bullet summary>

   ## Files Changed
   <list>

   ## Next Steps
   <what to do next, or "None — feature complete">

   ## Blockers
   <or "None">
   ```

2. Append to `.claude/memory/feature-work-log.md`:
   ```
   | <date> | <feature> | <action summary> | <outcome> |
   ```

## Rules

- Keep `active-work.md` under 20 lines
- Overwrite previous `active-work.md` content (current state, not history)
- Append to `feature-work-log.md` (chronological)
- Memory updates should be committed to the repo alongside code changes so state persists across sessions
