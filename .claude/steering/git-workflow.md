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

## Approval gates — REQUIRED before every git operation

### Before committing
1. Show the proposed commit message
2. List every file being staged
3. **Wait for explicit approval before running `git commit`**

### Before pushing
1. Show the branch and number of commits being pushed
2. **Wait for explicit approval before running `git push`**

### Before creating a PR
1. Show the full PR title and description
2. **Wait for explicit approval before creating**

Never commit, push, or create a PR without going through these gates first. "Approved" or "yes" from the user is the trigger to proceed.

## After every commit

After every commit and push:

1. Output this exact block:

```
Building in Public - Commit #${commit_number}:

${concise_one_liner_desc_of_commit}

${commit_url}
```

- `commit_number` — total commit count: `git rev-list --count HEAD`
- `concise_one_liner_desc_of_commit` — plain English, no conventional commit prefix
- `commit_url` — `https://github.com/LutherCalvinRiggs/cashflow-analysis/commit/<sha>`

2. Run `/bip` to generate a LinkedIn draft for the commit.
   - Run for every commit regardless of type prefix
   - The draft is saved to `drafts/` (gitignored) and printed inline

## Subagents and git
- Subagents do NOT commit or push — parent session handles all git operations
- Subagents produce code; parent reviews, stages, and commits
