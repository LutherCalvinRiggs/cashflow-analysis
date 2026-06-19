# Git Workflow

## Branch Source
Always branch from `staging` unless explicitly told otherwise. Never assume `main`/`master` is the correct base.

## Branch Naming
Pattern: `luther/<worktree>/<branch_name>`

## PR Target
PRs target `staging` unless explicitly told otherwise.

## Commit Discipline
- Stage specific files, not `git add .`
- Keep commits focused on one logical change
- Use semantic chunking: group related changes into distinct commits by purpose (e.g., new endpoint, bug fix, migration, test updates)
- Before committing unrelated work (new feature, template, doc for a different deliverable), ask: does this belong on the current branch or its own? Separate deliverables that ship independently need separate branches.
- Always push to remote after committing
- No force pushes without explicit permission
- Before force-pushing, rebase onto `origin/staging` to prevent merge conflicts on the PR.

## Worktrees

Worktrees enable parallel feature work in the same repo. Each worktree is scoped to a **feature**, not a branch — it persists for the feature's entire lifecycle and may contain multiple branches over time.

### Layout
```
~/Code/
├── api/                  ← main worktree (stays on staging)
├── api--feature-a/       ← feature worktree
├── frontend/
├── frontend--feature-a/
├── mobile/
├── mobile--feature-a/
```

### Conventions
- Main worktree stays on `staging`. No feature work there.
- Worktree directory: `<repo>--<feature-name>` (double-dash separator).
- One feature per worktree. Branches may change within it as the feature evolves.
- Each worktree needs its own dependency install (run the appropriate install command for your stack).
- Cross-repo features use the same worktree suffix across repos.
- Worktrees are created/removed across all repos together unless explicitly told otherwise.

### Commands
```bash
# Create
git -C <path/to/repo> worktree add <path/to/repo--FEATURE> luther/<branch>

# List
git -C <path/to/repo> worktree list

# Remove (explicit user command only)
git -C <path/to/repo> worktree remove <path/to/repo--FEATURE>
```

### Rules
- Check `git worktree list` before creating to avoid conflicts.
- A worktree persists until the user explicitly says to remove it. Never auto-remove.
- When starting a new branch within a worktree: `git checkout -b luther/<new-branch> origin/staging`
- Before removing, confirm all work is pushed and PRs are merged.
- Track worktree path in memory files (`active-work.md` includes worktree path).
