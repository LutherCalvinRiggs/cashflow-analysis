---
name: eval
description: Post-debug evaluation. Analyzes what went wrong, determines what to update to prevent recurrence. Use after fixing a bug to improve steering, skills, or standards.
---

## Usage

`/eval <feature-name>` — Evaluate after a debug session
`/eval` — Evaluate standalone

## Step 1: Analyze the Bug

Ask (or infer from recent context):
- What was the bug?
- What caused it? (code error, missing validation, wrong assumption, stale pattern)
- What category? (runtime error, logic bug, integration issue, config mistake, test gap)
- Was it preventable with existing standards?

## Step 2: Determine What to Update

| Category | Update Target |
|----------|--------------|
| Pattern violation that should be global | `~/.kiro/steering/code-standards.md` |
| Repo-specific gotcha | `<repo>/.kiro/steering/standards.md` |
| Missing test coverage pattern | `/run-tests` skill or repo steering |
| Process gap (missed step) | Relevant skill (e.g., `/orchestrate`, `/deploy`) |
| Detectable automatically | Propose a hook (PreToolUse/PostToolUse) |
| Feature-specific gotcha | `~/.kiro/memory/features/<name>/implementation-notes.md` |

## Step 3: Draft the Update

- Write the specific addition/change to the target file
- Keep it directive (what to do), not narrative (what happened)
- Present to user for approval before writing

## Step 4: Apply

- Write the approved update
- Confirm what was changed

## Rules

- One eval per bug. Don't scope-creep into multiple issues.
- Updates should be 1-3 lines. If longer, it's probably a skill, not a steering directive.
- Never remove existing standards — only add or refine.
