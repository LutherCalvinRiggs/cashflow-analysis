# AI-Assisted Development Workflow

A comprehensive reference for replicating a solo-developer + AI-agent development workflow. This document is AI-agnostic — any LLM, agent framework, or coding assistant can use it to understand and replicate the workflow.

---

## 1. Overview

This workflow enables a solo developer to manage a multi-repo product with AI assistance. The AI agent acts as a pair programmer that:

- Plans and implements features across multiple repositories
- Maintains persistent memory of work state across sessions
- Follows strict coding standards and git conventions
- Handles debugging, testing, deployment, and documentation

The developer makes all architectural decisions. The agent executes, suggests, and tracks.

---

## 2. Git Workflow

### Branch Naming
- **Convention:** `luther/<worktree_name>/<feature_name>`

### Commit Discipline
- Stage specific files (`git add <file>`), never `git add .`
- One logical change per commit
- Semantic chunking: group related changes by purpose
- Always push to remote after committing
- No force pushes without explicit permission

### Worktrees for Parallel Development

Worktrees enable working on multiple features simultaneously without branch switching.

**Layout:**
```
~/Code/
├── api/                  ← main worktree (stays on staging)
├── api--feature-a/       ← feature worktree
├── api--feature-b/       ← feature worktree
├── frontend/
├── frontend--feature-a/
├── mobile/
├── mobile--feature-a/
...
```

**Rules:**
- Main worktree stays on `staging`/`main`. No feature work there.
- Worktree directory naming: `<repo>--<feature-name>` (double-dash separator)
- One feature per worktree. Worktree persists for the feature's full lifecycle.
- **A new worktree must be an exact replica of the main worktree and its state.** After creation, it needs:
  - Install dependencies using your project's package manager
  - Environment variables copied from the main worktree (`.env` files, local config)
- Cross-repo features use the same suffix across all repos
- Worktrees are created/removed across **all repos** together unless told otherwise
- Never auto-remove worktrees. Only remove on explicit developer command.

**Commands:**
```bash
# Create
git -C ~/Code/<repo> worktree add ~/Code/<repo>--<feature> luther/<worktree_name>/<feature_name>

# List
git -C ~/path/to/code/<repo> worktree list

# Remove (only after confirming work is pushed and PRs merged)
git -C ~/path/to/code/<repo> worktree remove ~/path/to/code/<repo>--<feature>
```

---

## 3. Persistent Memory System

The agent maintains state across sessions using a file-based memory system at `~/.agent/memory/`.

### Directory Structure
```
~/.agent/memory/
├── features/
│   └── <feature-name>/
│       ├── active-work.md        ← Current status (overwritten each update)
│       ├── plan.md               ← Implementation checklist
│       ├── decisions.md          ← Technical decisions (append-only)
│       └── implementation-notes.md ← Gotchas, patterns (append-only)
├── archive/
│   └── <date>-<feature-name>.md  ← Completed features
├── cross-repo-active-work.md     ← Multi-repo feature tracking
└── feature-work-log.md           ← Chronological log (append-only)
```

### active-work.md Format
```markdown
**Feature:** <name>
**Status:** <In Progress | Complete | Blocked>
**Last Updated:** <timestamp>
**Repo(s):** <repos touched>
**Worktree(s):** <worktree paths>
**Branch(es):** <current branch in each worktree>

## What Was Done
<bullet summary>

## Next Steps
<what to do next>

## Blockers
<or "None">
```

### Rules
- `active-work.md`: Keep under 20 lines. Overwrite on each update (current state, not history).
- `feature-work-log.md`: Append-only chronological log.
- `decisions.md` / `implementation-notes.md`: Append-only.
- Never delete feature directories — use the archive workflow for that.

---

## 4. Feature Development Lifecycle

Every feature follows a structured lifecycle with explicit phase transitions.

### Phase 1: Planning

1. Analyze the requirement
2. Read relevant existing code to understand patterns
3. Create implementation checklist in `plan.md`
4. Flag risks or blockers
5. Update `active-work.md` (status: "Planning Complete")
6. Present plan to developer
7. **Wait for approval before building**

### Phase 2: Building

1. Read `plan.md` for next unchecked task
2. Read reference files to match existing patterns
3. Implement the task
4. Write tests immediately after implementation
5. Run tests, confirm passing
6. Check off task in `plan.md`
7. Update `active-work.md`
8. **Report progress, wait for "Continue" or "Pause"**

### Phase 3: Completion

1. Record final state to memory (handoff)
2. Present: files changed, test results, suggested commit message
3. **Wait for commit approval**

### Scope Rules
- One task at a time from the checklist
- Don't refactor unrelated code
- Match existing project patterns exactly
- If scope needs to change, ask first

---

## 5. Session Continuity

### Starting a Session (Pickup)
1. Read `~/.agent/memory/features/<feature-name>/active-work.md`
2. Identify: what we're working on, where we left off, next step, blockers
3. Use the worktree path from memory as the working directory
4. **Never work in the main worktree for feature work**
5. Orient and wait for instruction — don't start work automatically

### Ending a Session (Handoff)
1. Write/update `active-work.md` with current state
2. Append to `feature-work-log.md`
3. If cross-repo, update `cross-repo-active-work.md`
4. Keep state minimal — just enough to resume cold

### Status Check
Read all memory files and present a summary table of active features, their status, and next steps. Read-only — never modify files during a status check.

---

## 6. Code Standards

> **Note:** The standards below are representative examples from this project. They may not be a 1-for-1 match for your codebase — adapt them to your project's specific patterns, libraries, and conventions.

### Database Access
- Use your project's database abstraction helpers exclusively
- Use the designated read helper for SELECT queries
- Use the designated write helper for INSERT/UPDATE/DELETE
- Always disconnect in a `finally` block
- Never instantiate raw database connections directly

### Handler Logging
Every API handler must have a `console.log` near the top that includes:
1. A natural-language description of what the handler is doing
2. A traceable identifier (customer_id, ticket_ref, invoice_id, lot_id, etc.)

This is critical for tracing requests in logs back to the event being debugged.

### Validation
- Permissive for non-critical fields: skip invalid values rather than rejecting the entire request
- Never lose good data because one optional field has a bad value

### Security
- Server-side computation over client trust (priority, sentiment, classification — compute from data, never set by caller)
- All internal endpoints require permission checks
- Keep internal logic out of vendor-facing docs

### Imports
Before removing any `require`/`import`, grep the entire file for all usages. A removed import that is still referenced causes a silent ReferenceError at runtime.

### Service Config
- Changes to your service config file (e.g. API definition, routing config) require a dev server restart
- Check your auth allow-list before adding new HTTP methods
- Consolidate handlers when multiple methods share a resource path

---

## 7. Testing Standards

### Philosophy
Test **business logic**, not infrastructure plumbing.
- ✅ Test: handler validation, response shaping, manager function logic, error handling
- ❌ Don't test: "does the queue receive the message", "does the function invoke correctly"

### Mocking Strategy
Mock at the **manager module level**, not at infrastructure/SDK level.
- ✅ Mock your own manager/service modules
- ❌ Don't mock infrastructure SDK internals

### Test Payloads
Must include all fields the production code path requires. Tests should resemble real data as closely as possible.

---

## 8. Debugging Workflow

Debugging is strictly scoped — fix only the reported issue, nothing else.

### Steps
1. **Identify:** Extract error message, affected files, line numbers, root cause
2. **Minimal Fix:** Only fix the specific issue. No refactoring, no feature additions.
3. **Verify:** Run relevant tests. If no tests exist for this path, write one.
4. **Record:** Update memory with the fix details.

### Post-Debug Evaluation
After fixing a bug, evaluate what went wrong and determine if standards/skills need updating:
- Pattern violation → update code standards
- Repo-specific gotcha → update repo-specific notes
- Missing test coverage → update test patterns
- Process gap → update relevant workflow step
- Feature-specific gotcha → update implementation notes

Updates should be 1-3 lines, directive (what to do), not narrative (what happened).

---

## 9. Pull Request Workflow

### Creating a PR
1. Detect current repo and branch
2. Get diff against target branch (`git log staging..HEAD --oneline`)
3. Generate concise PR title (under 70 chars)
4. Generate structured PR description:
   - Summary (what and why)
   - Changes (file-level)
   - Testing (what was tested, results)
   - Notes (anything reviewers should know)
5. Present to developer for approval
6. Create via CLI: `gh pr create --base staging --title "<title>" --body "<body>"`

### Rules
- Always target `staging` (or `main` if `staging` doesn't exist)
- Never push without developer confirmation
- If branch has no commits ahead of target, stop and say so

---

## 10. Deployment Workflow

### Pre-Deploy Checks
1. Confirm branch is clean
2. Confirm on correct branch
3. Run tests
4. Confirm all tests pass

### Rules
- Always require explicit developer confirmation before deploying
- Show what will be deployed (commits, changes)
- For production deploys, double-confirm

---

## 11. Database Migrations

### File Naming
- Format: `YYYYMMDDHHMI.sql` and `YYYYMMDDHHMI_rollback.sql`
- Example: `202605191400.sql` + `202605191400_rollback.sql`

### Rules
- Always create a rollback script alongside the migration
- Never modify existing migration files
- Test migration locally before committing
- For destructive operations (DROP, DELETE), add a comment explaining why
- Check existing schema before creating (avoid duplicate columns/tables)

---

## 12. Archiving Completed Features

When a feature is done and tested:

1. Confirm status is "Complete"
2. Check for related documentation in `~/.agent/docs/`
3. Create archive entry at `~/.agent/memory/archive/<date>-<feature-name>.md` with:
   - Summary of what was built
   - Key decisions
   - Implementation details
   - Files changed
   - Lessons learned
4. Integrate and delete related docs from `~/.agent/docs/`
5. Remove the feature directory from `~/.agent/memory/features/`
6. Update cross-repo tracking if applicable
7. Append to feature-work-log

---

## 13. Key Behavioral Rules for the Agent

1. **Read before writing.** Always read existing code before implementing. Match patterns.
2. **One task at a time.** Work through the plan sequentially.
3. **Strict scope.** Don't fix unrelated issues. Don't add unrequested features.
4. **Developer decides.** Present plans, wait for approval. Never deploy without confirmation.
5. **Memory is truth.** Always update memory after completing work. Always read memory before starting.
6. **Worktree discipline.** Never do feature work in the main worktree. Always use the feature worktree.
7. **Test immediately.** Write and run tests right after implementing, not as an afterthought.
8. **Minimal fixes.** Debug fixes should be surgical. Note other issues but don't fix them.
9. **Confirm destructive actions.** Git force pushes, production deploys, data deletion — always ask first.
10. **Track everything.** Every session should leave a trail in memory that the next session can pick up.

---

## 14. Quick Reference: Agent Commands

These are the logical operations the agent should support:

| Command | Purpose |
|---------|---------|
| orchestrate `<feature>` | Start/resume full feature workflow |
| pickup-memory `<feature>` | Read state and orient on current work |
| update-memory `<feature>` | Save progress to memory |
| handoff `<feature>` | Record completed work for session continuity |
| status | Cross-repo status report |
| worktree create `<feature>` | Set up worktrees across repos |
| worktree remove `<feature>` | Clean up worktrees |
| create-pr | Create a pull request |
| deploy `<repo>` `<env>` | Guided deployment |
| debug `<feature>` | Scoped bug fix |
| eval | Post-debug evaluation |
| run-tests | Run tests for current repo |
| search-logs `<service>` | Search application logs |
| migration `<description>` | Create database migration |
| archive `<feature>` | Archive completed feature |

---

## 15. Setting Up on a New Machine

To replicate this workflow on a new machine:

1. **Clone all project repos** into a shared code directory
2. **Install language runtimes** required by the project
3. **Install dependencies** in each repo that requires them
4. **Configure cloud CLI tools** with appropriate credentials
5. **Install VCS CLI** (e.g., `gh` for GitHub) for PR creation
6. **Create the memory directory structure:**
   ```
   mkdir -p ~/.agent/memory/features
   mkdir -p ~/.agent/memory/archive
   touch ~/.agent/memory/feature-work-log.md
   touch ~/.agent/memory/cross-repo-active-work.md
   ```
7. **Create the docs directory:** `mkdir -p ~/.agent/docs/`
8. **Set up steering files** (code standards, git workflow, tech stack, product context) in a location the agent can reference
9. **Set up skill definitions** so the agent knows how to execute each workflow step
10. **Configure git** with the developer's identity and push defaults

The agent should be configured to:
- Have read/write access to the filesystem
- Be able to execute shell commands
- Have access to relevant cloud/deployment CLIs
- Be able to read/write the memory directory
- Reference steering files and skill definitions as system context

---

## 16. Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION START                              │
│  pickup-memory → read active-work → orient → wait           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    FEATURE WORK                               │
│  orchestrate → plan → [approve] → build → test → complete   │
│       ↕                                                      │
│  worktree create/remove    debug → eval                      │
│  run-tests                 migration                         │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    SHIP                                       │
│  create-pr → [merge] → deploy → verify                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    SESSION END                                │
│  handoff/update-memory → archive (if complete)               │
└─────────────────────────────────────────────────────────────┘
```

---

*This document describes the workflow as of May 2026. Update as the workflow evolves.*
