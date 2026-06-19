---
name: status
description: Quick cross-repo status report. Shows all active features, their state, and what's next. Lighter than /orchestrate — just reads and reports.
---

## Usage

`/status` — Full status report across all repos and features

## Actions

1. Read `~/.kiro/memory/cross-repo-active-work.md`
2. Read `~/.kiro/memory/feature-work-log.md` (last 10 entries)
3. Scan `~/.kiro/memory/features/` — read each `active-work.md`

## Output Format

```
📋 Status Report — <date>

Cross-Repo: <feature name or "Idle">
  Status: <status>
  Repos: <list>
  Current task: <one line>

Active Features:
  • <feature-1> — <status> — <next step>
  • <feature-2> — <status> — <next step>

Recent Activity:
  | Date | Feature | Action | Outcome |
  (last 5 entries from work log)
```

## Rules

- Read only. Never modify files.
- If no active work, say "All clear — no active features."
