---
name: eval
description: Post-debug evaluation. After fixing a bug, assess what went wrong and whether any standards, skills, or notes need updating to prevent recurrence.
---

## Usage

`/eval` — Run after a `/debug` session

## Steps

1. Review the bug that was just fixed
2. Categorize the root cause:

| Category | Update Target |
|----------|--------------|
| Violated an existing standard | `.claude/steering/code-standards.md` |
| Missing standard (new pattern needed) | `.claude/steering/code-standards.md` |
| Project-specific gotcha | `.claude/memory/features/<feature>/implementation-notes.md` |
| Missing test coverage | Note for `/run-tests` or add test immediately |
| Process gap | Relevant skill SKILL.md |

3. Draft 1–3 line directive updates (what to do, not what happened)
4. Present proposed updates to user for approval
5. Apply approved updates

## Rules

- Updates must be directive: "Always X" or "Never Y" — not narrative
- Do not update files without user approval
- If the bug was a one-off with no systemic cause, say so and skip
