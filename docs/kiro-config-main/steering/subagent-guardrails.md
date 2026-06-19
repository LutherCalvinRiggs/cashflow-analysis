# Subagent Guardrails

These rules apply to all subagents spawned by the parent session. Subagents run unsupervised in feature worktrees — they have no human in the loop during execution.

The parent agent (interactive session with the developer) is NOT bound by these rules. The parent retains full access and handles all operations that subagents cannot perform.

## Allowed

### File Operations
- Read any file in the assigned feature worktree
- Write and create files in the assigned feature worktree
- Delete files in the assigned feature worktree
- Read files from other worktrees or the main worktree for reference (patterns, shared code, examples)
- Create new files and directories within the feature worktree

### Shell Commands
- Test and lint scripts appropriate for your project's stack
- Read-only shell utilities: `grep`, `find`, `wc`, `cat`, `head`, `tail`, `diff`, `ls`, `tree`, `echo`, `sort`, `uniq`, `awk` (read mode), `sed` (print mode only)
- Any shell command that reads without modifying — no flags that remove, destroy, or force-overwrite (`-rf`, `--force`, `--delete`, `--purge`, `--hard`, etc.)

### Logging (Read-Only)
- Query application logs for debugging purposes
- No write or delete operations against log data

### Memory & Docs
- Read from `~/.kiro/memory/`
- Write to `~/.kiro/memory/` (handoff, update active-work, append to logs)
- Read from `~/.kiro/docs/`
- Write to `~/.kiro/docs/`

### Code Scope
- Modify source files within the feature worktree
- Create new files and directories that don't exist yet

## Forbidden

### Git — All Operations
- No `git add`, `git commit`, `git push`, `git checkout`, `git stash`, `git reset`, `git branch`, `git merge`, `git rebase`
- The parent agent handles all git operations before and after subagent execution

### Network & External
- No outbound network requests (curl, wget, fetch, or equivalent)
- No PR creation or issue comments
- No notifications, emails, or webhooks

### Dependencies
- No package installation of any kind
- No modifications to dependency manifests (package.json, requirements.txt, go.mod, or equivalent)

### Cloud Write/Modify/Delete
- No cloud CLI commands that create, modify, update, delete, or deploy anything
- No deployment framework commands

### Database
- No database connections (staging or production)
- No SQL queries of any kind

### Infrastructure & CI
- No infrastructure config modifications (`.tf`, CDK, Pulumi, or equivalent)
- No CI/CD workflow modifications

### Deployment
- No deploy commands of any kind
- No dev server start commands

### Scope Boundary
- No writing files outside the assigned feature worktree
- No modifying the main worktree or other feature worktrees

## When a Forbidden Action Is Needed

If a subagent determines that a forbidden action is required to complete its task, it must:

1. **Stop** — do not attempt the action
2. **Document** — note what is needed in its output (e.g., "Requires: install uuid package", "Requires: CI workflow update for new service")
3. **Continue** — proceed with any remaining work that doesn't depend on the blocked action

The parent agent will review these notes and perform the actions after subagent execution.

## Worktree Isolation

- Each subagent operates in exactly one feature worktree
- The parent sets up the branch and worktree state before spawning subagents
- All subagent work for a ticket/sprint lands on a single branch
- The parent reviews, stages, and commits after subagent work completes
