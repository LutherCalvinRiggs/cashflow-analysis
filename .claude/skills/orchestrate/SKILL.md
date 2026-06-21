---
name: orchestrate
description: Full feature development workflow. Plans, builds, tests, and completes features with structured phase transitions. Use when starting or resuming a feature that needs planning through implementation.
---

## Usage

`/orchestrate <feature-name> [requirement]` — Start or continue a feature
`/orchestrate resume <feature-name>` — Resume from last checkpoint

## State

All state in `.claude/memory/features/<feature-name>/`:
- `active-work.md`, `plan.md`, `decisions.md`, `implementation-notes.md`

## Initialization

1. Check if `.claude/memory/features/<feature-name>/` exists
   - Exists: read `active-work.md`, resume from current state
   - New: create directory, proceed to Planning
2. If another feature is "In Progress", ask before proceeding

## Phase 1: Planning

```
🎯 Planning Phase
```

1. Analyze requirement
2. Read relevant existing code for patterns
3. Read `docs/PLAN.md` to align with the project task list
4. Create implementation checklist in `plan.md`
5. Flag risks or blockers
6. Update `active-work.md` (status: "Planning Complete")
7. Present plan
8. Prompt: **"Plan ready. 'Approved' to start, 'Replan' to revise."**

## Phase 1.5: Billing Estimate

After plan is approved, run `/estimate-billing` using the `plan.md` tasks:
1. Decompose and estimate per the estimate-billing skill
2. Append estimate to `plan.md` under `## Billing Estimate`
3. Present estimate summary
4. Prompt: **"Estimate recorded. 'Continue' to start building, 'Revise' to adjust."**

## Phase 2: Building

```
💻 Building Phase — Task: [specific task]
```

1. Read `plan.md` for next unchecked task
2. Read reference files to match patterns
3. For substantial tasks, spawn a subagent via the Agent tool with `isolation: "worktree"` and pass the task, relevant file paths, and steering context. For small tasks, implement directly.
4. Write tests immediately
5. Run tests, confirm passing
6. Check off task in `plan.md`
7. Update `active-work.md`
8. Prompt: **"Task complete. [N] tests passing. 'Continue' for next, 'Pause' to stop."**

## Phase 3: Completion

```
🎉 Feature Complete
```

1. Call `/handoff <feature-name>` with full summary
2. Present: files changed, test results, suggested commit message
3. Commit memory updates alongside code changes
4. Prompt: **"Ready to commit?"**

## Commands

| Command | Action |
|---------|--------|
| Approved / Continue | Next phase/task |
| Test | Run tests on current work |
| Fix | Debug a failing test |
| Replan | Revise the plan |
| Review | Show progress summary |
| Pause | Save state, stop |

## Scope Rules

- One task at a time from checklist
- Don't refactor unrelated code
- Match existing project patterns
- If scope needs to change, ask first
