---
name: create-pr
description: Create a pull request with a structured description. Use after committing work on a feature branch.
---

## Usage

`/create-pr` — Create PR for current branch

## Steps

1. Get current branch (`git branch --show-current`)
2. Get commits ahead of main (`git log main..HEAD --oneline`)
3. Get changed files (`git diff main..HEAD --name-only`)
4. Generate PR title (concise, under 70 chars)
5. Generate PR description:
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
6. Present to user for approval/editing
7. Create PR using the `mcp__github__create_pull_request` tool targeting `main`
8. Return the PR URL

## Rules

- Always target `main`
- Never create without user confirmation
- If branch has no commits ahead of main, say so and stop
