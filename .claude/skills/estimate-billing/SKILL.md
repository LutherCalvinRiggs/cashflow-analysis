---
name: estimate-billing
description: Analyze a feature or ticket and produce time estimates for both a human developer (no AI) and a fully AI-assisted workflow. Use when scoping work or as part of /orchestrate planning phase.
---

## Usage

`/estimate-billing <feature-name>` — Estimate from feature memory (reads plan.md)
`/estimate-billing <description>` — Estimate from inline description

## Integration with /orchestrate

When run as part of `/orchestrate`, execute after plan approval:
1. Use the `plan.md` task breakdown as input
2. Append the estimate summary to `plan.md` under `## Billing Estimate`
3. Present before prompting to start Building phase

## Step 1: Decompose

Break the work into discrete tasks. For each task identify:
- **Category**: Planning, Backend, Frontend, Testing
- **Complexity**: Trivial / Simple / Moderate / Complex / Very Complex
- **Dependencies**: What must exist first

## Step 2: Estimate — Human (No AI)

Estimate assuming a senior developer working solo, no AI tools:
- Include: reading docs, writing code, debugging, testing
- Use ranges (min–max hours)

## Step 3: Estimate — AI-Assisted

Estimate assuming full AI orchestration:

Typical reduction factors:
- Boilerplate/CRUD: 70–80% reduction
- Business logic with clear spec: 50–60% reduction
- Complex debugging: 20–30% reduction
- Architecture decisions: 10–20% reduction
- Manual testing/verification: 0% reduction

## Step 4: Present Summary

```
📊 Estimate: [Feature Title]

┌─────────────────────────────────────────────────┐
│ Tasks: [N]                                      │
│                                                 │
│ 🧑‍💻 Human (no AI):     [X]–[Y] hours            │
│ 🤖 AI-Assisted:        [X]–[Y] hours            │
│ ⚡ Time Saved:          ~[N]% ([X]–[Y] hours)   │
└─────────────────────────────────────────────────┘

| Task | Category | Complexity | Human | AI-Assisted |
|------|----------|------------|-------|-------------|

Assumptions:
- [key assumptions]

Risks:
- [things that could blow up the estimate]
```

## Guidelines

- Be honest — don't inflate human or deflate AI estimates
- If the requirement is ambiguous, note which interpretation you used
- Round to nearest 0.5h for tasks, present totals as ranges
