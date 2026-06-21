---
name: status
description: Quick status report across all active features. Shows state and next steps. Read-only.
---

## Usage

`/status`

## Actions

1. Read `.claude/memory/feature-work-log.md` (last 10 entries)
2. Scan `.claude/memory/features/` — read each `active-work.md`

## Output Format

```
📋 Status Report — <date>

Active Features:
  • <feature-1> — <status> — <next step>
  • <feature-2> — <status> — <next step>

Recent Activity:
  | Date | Feature | Action | Outcome |
  (last 5 entries from work log)
```

## Rules

- Read only. Never modify files.
- If no active features: "All clear — no active features."
