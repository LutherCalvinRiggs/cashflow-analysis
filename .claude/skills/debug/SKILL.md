---
name: debug
description: Analyze and fix a specific bug from an error message or description. Strictly scoped — fixes only the reported issue, nothing else.
---

## Usage

`/debug <feature-name>` — Debug within a feature's context
`/debug` — Debug standalone

## Step 1: Get Input

Ask the user: "What's the bug? Paste the error message, stack trace, or describe the behavior."

## Step 2: Identify

If feature name provided, read `.claude/memory/features/<feature-name>/`.

Extract: error message, affected files, line numbers, root cause.

Present:
```
🐛 Issue: [error message]
   Affected: [file:line]
   Root Cause: [brief]
   Fix Scope: [what will change]
```

## Step 3: Minimal Fix

- ONLY fix the specific issue
- Do NOT refactor, add features, or fix other issues
- If broader changes are needed, explain and get approval first

## Step 4: Verify

- Run relevant tests with `/run-tests`
- If no tests exist for this path, write one
- Confirm fix resolves the original issue

## Step 5: Record

- If feature name provided, call `/handoff <feature-name>`
- If it's a recurring gotcha, note it in `implementation-notes.md`
- Call `/eval` to assess whether standards need updating

## Scope Enforcement

- If tempted to fix other issues: note them, don't fix
- If file has multiple issues: fix ONLY the reported one
