---
name: handoff
description: Record completed work to memory for session continuity. Called by agents/subagents when they finish a task. Writes structured state to ~/.kiro/memory/.
---

## Usage

`/handoff <feature-name>` — Record what was accomplished

## Inputs (from the calling agent)

The agent provides:
- Feature name
- Summary of what was done
- Files created/modified
- Tests written/run and results
- Decisions made
- Blockers or next steps
- Repo(s) worked in

## Actions

1. Write/update `~/.kiro/memory/features/<feature-name>/active-work.md`:
   ```
   **Feature:** <name>
   **Status:** <In Progress | Complete | Blocked>
   **Last Updated:** <timestamp>
   **Updated By:** <agent-name>
   **Repo(s):** <repos touched>
   **Worktree(s):** <worktree paths, e.g. ~/Code/api--feature, ~/Code/infra--feature>
   **Branch(es):** <current branch in each worktree>

   ## What Was Done
   <bullet summary>

   ## Files Changed
   <list>

   ## Next Steps
   <what to do next, or "None — feature complete">

   ## Blockers
   <or "None">
   ```

2. Append to `~/.kiro/memory/feature-work-log.md`:
   ```
   | <date> | <feature> | <action summary> | <outcome> |
   ```

3. If cross-repo work, update `~/.kiro/memory/cross-repo-active-work.md` with repo status.

## Rules

- Keep active-work.md under 20 lines
- Overwrite previous active-work.md content (it's current state, not history)
- Append to feature-work-log.md (it's chronological)
- Never delete or archive — that's the /archive skill's job
