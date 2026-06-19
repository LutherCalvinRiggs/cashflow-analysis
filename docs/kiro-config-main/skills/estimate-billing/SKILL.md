---
name: estimate-billing
description: Analyze a ticket/feature/request and produce time estimates for both a human developer (no AI) and a fully AI-assisted orchestration workflow. Use when scoping work for billing, proposals, or sprint planning. Can run standalone or as part of /orchestrate planning phase.
---

## Usage

`/estimate-billing <feature-name>` — Estimate from feature memory (reads plan.md)
`/estimate-billing <description>` — Estimate from inline description
`/orchestrate` integration — Automatically called after Planning phase approval

If no feature-name matches a memory entry and no description is provided, ask: "What's the feature or requirement to estimate?"

## Integration with /orchestrate

When run as part of `/orchestrate`, execute after plan approval (end of Phase 1):
1. Use the `plan.md` task breakdown as input
2. Append the estimate summary to `plan.md` under a `## Billing Estimate` heading
3. Present the estimate before prompting to start Building phase

## Step 1: Decompose

Break the work into discrete tasks. For each task identify:
- **Category**: Planning, Backend, Frontend, Mobile, Infra, Migration, Testing, Deployment
- **Complexity**: Trivial / Simple / Moderate / Complex / Very Complex
- **Dependencies**: What must exist or be done first
- **Repos/services touched**: Which parts of the system are affected

If a `plan.md` already exists, derive tasks from it rather than re-analyzing.

## Step 2: Estimate — Human (No AI)

Estimate assuming a senior developer working solo, no AI tools:
- Include: reading docs, writing code, debugging, testing, code review, deployment
- Include: context switching overhead, looking up patterns, writing boilerplate
- Use ranges (min–max hours)

Multipliers:
- Multi-repo/service coordination: +20% per additional repo
- New external integration: +30%
- Database migration: +1–2h for schema + rollback + testing
- Infrastructure changes: +2–4h for plan/apply cycle + verification

## Step 3: Estimate — AI-Assisted

Estimate assuming full AI orchestration (agent workflow with skills, subagents, memory):
- Reduce: boilerplate generation, pattern matching, test writing, multi-file coordinated changes
- Keep similar: architectural decisions, ambiguous requirements, manual verification, deployment
- Reduce less: novel integrations, complex debugging, UI/UX decisions

Typical reduction factors:
- Boilerplate/CRUD: 70–80% reduction
- Business logic with clear spec: 50–60% reduction
- Complex debugging/investigation: 20–30% reduction
- Architecture/design decisions: 10–20% reduction
- Manual testing/verification: 0% reduction
- Deployment/infrastructure: 10–20% reduction

## Step 4: Present Summary

```
📊 Estimate: [Feature/Ticket Title]

┌─────────────────────────────────────────────────┐
│ Tasks: [N] across [services/repos]              │
│                                                 │
│ 🧑‍💻 Human (no AI):     [X]–[Y] hours            │
│ 🤖 AI-Assisted:        [X]–[Y] hours            │
│ ⚡ Time Saved:          ~[N]% ([X]–[Y] hours)   │
└─────────────────────────────────────────────────┘

| Task | Category | Complexity | Human | AI-Assisted |
|------|----------|------------|-------|-------------|
| ...  | ...      | ...        | Xh    | Xh          |

Assumptions:
- [key assumptions that affect the estimate]

Risks:
- [things that could blow up the estimate]
```

## Guidelines

- Be honest — don't inflate human estimates or deflate AI estimates to sell a narrative
- If the requirement is ambiguous, note which interpretation you used and how estimates change if wrong
- Round to nearest 0.5h for tasks, present totals as ranges
- Account for project-specific patterns (shared code, multi-service deploys) when applicable
