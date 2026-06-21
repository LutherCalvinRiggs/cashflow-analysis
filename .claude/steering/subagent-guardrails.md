# Subagent Guardrails

These rules apply to all subagents spawned by the parent session. Subagents run unsupervised — they have no human in the loop during execution.

The parent agent (interactive session with the developer) is NOT bound by these rules. The parent retains full access and handles all operations that subagents cannot perform.

## Allowed

### File Operations
- Read any file in the repo
- Write and create files in the assigned feature worktree
- Delete files in the assigned feature worktree

### Shell Commands
- Test and lint scripts: `pytest`, `npm test`, `npm run lint`
- Read-only utilities: `grep`, `find`, `wc`, `cat`, `head`, `tail`, `diff`, `ls`, `tree`, `sort`, `uniq`, `awk` (read mode), `sed` (print mode only)
- No flags that destroy or force-overwrite (`-rf`, `--force`, `--hard`, etc.)

### Memory
- Read from `.claude/memory/`
- Write to `.claude/memory/` (handoff, update active-work, append to logs)

### Code Scope
- Modify source files within the assigned worktree
- Create new files and directories

## Forbidden

### Git — All Operations
- No `git add`, `git commit`, `git push`, `git checkout`, `git stash`, `git reset`, `git branch`, `git merge`, `git rebase`
- The parent session handles all git operations

### Network & External
- No outbound network requests (curl, wget, fetch, or equivalent)
- No PR creation or issue comments

### Dependencies
- No package installation
- No modifications to `requirements.txt` or `package.json`

### Database
- No direct database connections or raw SQL outside the app's SQLAlchemy layer

### Scope Boundary
- No writing files outside the assigned worktree

## When a Forbidden Action Is Needed

1. **Stop** — do not attempt the action
2. **Document** — note what is needed (e.g. "Requires: add `uuid` to requirements.txt")
3. **Continue** — proceed with any remaining work that doesn't depend on the blocked action

The parent session will review and perform the action.
