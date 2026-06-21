# Git Workflow

## Branch naming
`claude/<feature-name>` — e.g. `claude/phase-1-pdf-extraction`

## Commit discipline
- One task from `docs/PLAN.md` = one commit
- Message format: `<type>: <task-id> <description>`
  - e.g. `feat: 1.2 AI extraction endpoint`
  - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- Stage specific files — never `git add .` without reviewing what's included
- Always push to remote after committing

## PRs
- All PRs target `main`
- Use `/create-pr` skill to generate the PR

## Subagents and git
- Subagents do NOT commit or push — parent session handles all git operations
- Subagents produce code; parent reviews, stages, and commits
