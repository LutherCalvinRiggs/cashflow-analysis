---
name: pickup-memory
description: Read feature state from memory to orient on current work. Use when starting a session, resuming work, or checking what's active. Invoke with a feature name to get specific context, or without to see all active features.
---

## Usage

`/pickup-memory <feature-name>` — Read a specific feature's state
`/pickup-memory` — Scan all active features and summarize

## With feature name

Read all files in `~/.kiro/memory/features/<feature-name>/`:
- `active-work.md` — Current status and next steps
- `plan.md` — Implementation plan/checklist
- `decisions.md` — Technical decisions
- `implementation-notes.md` — Developer notes, gotchas
- `tests/` — Test plans and results

Present concise summary:
- What we're working on
- Where we left off (including worktree path — this is the working directory for all commands)
- Next immediate step
- Any blockers

## After pickup

Use the `Worktree(s)` path from `active-work.md` as the working directory for all file operations and commands. Never work in the main worktree for feature work — always use the feature worktree (e.g. `~/Code/api--feature`).

## Without feature name

Scan `~/.kiro/memory/features/` for all subdirectories. Read each `active-work.md`. Present summary table.

Also read `~/.kiro/memory/cross-repo-active-work.md` for cross-repo state.

## Rules

- Do not start any work. Orient and wait for instruction.
- If a feature folder has no `active-work.md`, note "no status tracked."
- Ignore `archive/`.
