---
name: pickup-memory
description: Read feature state from memory to orient on current work. Use at the start of every session, when resuming work, or to check what's active. Invoke with a feature name for specific context, or without to see all active features.
---

## Usage

`/pickup-memory <feature-name>` — Read a specific feature's state
`/pickup-memory` — Scan all active features and summarize

## With feature name

Read all files in `.claude/memory/features/<feature-name>/`:
- `active-work.md` — Current status and next steps
- `plan.md` — Implementation plan/checklist
- `decisions.md` — Technical decisions
- `implementation-notes.md` — Developer notes, gotchas

Present concise summary:
- What we're working on
- Where we left off
- Next immediate step
- Any blockers

## Without feature name

Scan `.claude/memory/features/` for all subdirectories. Read each `active-work.md`. Present summary table.

## Rules

- Do not start any work. Orient and wait for instruction.
- If a feature folder has no `active-work.md`, note "no status tracked."
- Ignore `archive/`.
