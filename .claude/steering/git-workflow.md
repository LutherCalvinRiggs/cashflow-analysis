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

## After every commit

After every commit and push, output this exact block:

```
Building in Public: Commit #${commit_number}

${concise_one_liner_desc_of_commit}

${commit_url}
```

- `commit_number` — total commit count: `git rev-list --count HEAD`
- `concise_one_liner_desc_of_commit` — plain English, no conventional commit prefix
- `commit_url` — `https://github.com/LutherCalvinRiggs/cashflow-analysis/commit/<sha>`

## Subagents and git
- Subagents do NOT commit or push — parent session handles all git operations
- Subagents produce code; parent reviews, stages, and commits
