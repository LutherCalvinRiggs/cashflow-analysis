---
name: worktree
description: Manage git worktrees for parallel feature development. Use when the user asks to create, list, remove, or rotate a worktree. Handles creation across multiple repos for cross-repo features, verifies no conflicts, installs dependencies, and updates memory tracking.
---

# Worktree Management

## Create a worktree

Triggered by: "create a worktree for <feature>" or "set up worktrees for <feature>"

Steps:
1. Determine which repos need worktrees (ask if unclear).
2. For each repo, run `git -C <repo-path> worktree list` to check for conflicts.
3. Create: `git -C <repo-path> worktree add <repo-path>--<feature> luther/<branch>`
   - If no branch name given, use `luther/<feature>` as default.
   - If branch already exists remotely, it will be checked out. Otherwise created fresh from HEAD.
4. Run the appropriate dependency install in each new worktree.
5. Update memory: add worktree path to the feature's `active-work.md`.
6. If cross-repo, update `~/.kiro/memory/cross-repo-active-work.md` with all worktree paths.

### Repo list

Worktrees are created/removed across all relevant repos together unless explicitly told otherwise. Update this table to match your project's repos.

| Repo | Path | Needs dependency install |
|------|------|--------------------------|
| (repo name) | `~/Code/(repo)` | Yes/No |

## List worktrees

Triggered by: "list worktrees" or "what worktrees are active"

Run `git -C <repo-path> worktree list` for each repo (or a specific repo if specified). Report in a table: repo, worktree path, branch, feature.

## Remove a worktree

Triggered by: "remove the <feature> worktree" or "clean up <feature> worktrees"

Steps:
1. Confirm all work is pushed (`git status` in the worktree — no uncommitted changes).
2. Confirm PRs are merged (ask user if unsure).
3. Run `git -C <repo-path> worktree remove <repo-path>--<feature>`.
4. Delete the branch if merged: `git -C <repo-path> branch -d luther/<branch>`.
5. Update memory: remove worktree path from `active-work.md`.
6. If cross-repo, update `cross-repo-active-work.md`.

**Never remove a worktree unless the user explicitly asks.**

## Rotate a branch within a worktree

Triggered by: "start a new branch in <worktree>" or "rotate <feature> to a new branch"

Steps:
1. `cd` into the worktree directory.
2. Ensure current work is committed and pushed.
3. `git fetch origin staging`
4. `git checkout -b luther/<new-branch> origin/staging`
5. Update memory with new branch name.

## Rules

- Worktree naming: `<repo>--<feature>` (double-dash separator).
- One feature per worktree. The worktree persists for the feature's full lifecycle.
- Never auto-remove worktrees. Only remove on explicit user command.
- Always check `git worktree list` before creating to avoid conflicts.
- Cross-repo features get the same suffix across all repos.
