---
name: create-pr
description: Create a pull request with a structured description. Use after committing work to create a PR targeting staging.
---

## Usage

`/create-pr` — Create PR for current branch

## Steps

1. Detect current repo and branch (`git branch --show-current`)
2. Get diff against staging (`git log staging..HEAD --oneline`)
3. Generate PR title (concise, under 70 chars)
4. Generate PR description:
   ```
   ## Summary
   <what was changed and why>

   ## Changes
   - <file: what changed>

   ## Testing
   - <what was tested, test results>

   ## Notes
   <anything reviewers should know>
   ```
5. Present to user for approval/editing
6. Run: `gh pr create --base staging --title "<title>" --body "<body>"`

## Rules

- Always target `staging` unless user specifies otherwise
- Never push without user confirmation
- If branch has no commits ahead of staging, say so and stop
