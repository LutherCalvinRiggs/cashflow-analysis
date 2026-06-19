# Workflow Decisions

## 2026-06-17 — NEEDLE Evaluated, Deferred

**Context:** Researched NEEDLE (Rust-based headless agent orchestrator with SQLite bead queue) for parallel task execution.

**Decision:** Defer NEEDLE. Subagents already provide parallel execution, role-based routing, and dependency ordering. NEEDLE's added value (persistence, retry, work-stealing) is unnecessary at current scale (2-3 concurrent features).

**Revisit when:** Hitting persistence limits (sessions crashing and losing state), needing 10+ parallel workers, or wanting auto-retry on failures.

## 2026-06-17 — Subagent Guardrails Established

**Context:** Giving agents full code execution permissions requires safety boundaries.

**Decision:** Subagents are Tier 0 (local machine only). They can read/write code in their worktree, run tests, read application logs, and read/write memory. They cannot: git (any operation), push, deploy, install deps, modify package.json, access DBs, curl, modify infra/CI.

**Rationale:** Parent agent handles all git/deploy/infra. Subagents produce code; developer reviews and ships.

## 2026-06-17 — Subagent Git Workflow

**Context:** Should subagents commit their own work?

**Decision:** No. All work for a ticket/sprint lands on a single branch. Parent sets up the branch before spawning subagents. Parent reviews, stages, and commits after subagent work completes. This keeps commit history clean and intentional.

## 2026-05-30 — AI-Agnostic Workflow Document

**Context:** Needed a comprehensive reference doc that could be passed to any agent on any platform to replicate our workflow.

**Decision:** Created `~/.kiro/docs/ai-assisted-development-workflow.md`. Covers: git workflow, memory system, feature lifecycle, session continuity, code standards, testing, debugging, PRs, deployment, migrations, archiving. All references are generic (no platform-specific tools mentioned).

## 2026-05-30 — Branch Naming Convention Updated

**Context:** Needed branch names that encode both worktree and feature context.

**Decision:** `luther/<worktree_name>/<branch_name>` — enables tracing any branch back to its worktree and purpose.
