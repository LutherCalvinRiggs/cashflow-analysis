---
name: update-memory
description: Save current progress to memory files for a feature. Use after completing work, making decisions, or before ending a session.
---

## Usage

`/update-memory <feature-name>`

## Location

All files in `.claude/memory/features/<feature-name>/`

## Files to update

- `active-work.md` — Status, current task, next steps, current branch (keep to 10-15 lines max)
- `plan.md` — Checklist with completion status
- `decisions.md` — Technical decisions made this session (append)
- `implementation-notes.md` — Gotchas, patterns discovered (append)

## Also update

- `.claude/memory/feature-work-log.md` — Append one-line entry: date, feature, action, outcome

## Rules

- Create the feature directory if it doesn't exist
- Only update files that have new information
- Keep `active-work.md` minimal — just enough to resume cold
- If work is complete, set status to "Complete" and suggest archiving
- Commit memory files to the repo so state persists across web sessions
