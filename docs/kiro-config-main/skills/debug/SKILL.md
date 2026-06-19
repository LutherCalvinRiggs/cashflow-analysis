---
name: debug
description: Analyze and fix a specific bug from an error message, screenshot, or description. Strictly scoped — fixes only the reported issue, nothing else.
---

## Usage

`/debug <feature-name>` — Debug within a feature's context
`/debug` — Debug standalone (no feature context)

## Step 0: Get Input

- Automatically run `pbpaste` to read the clipboard contents
- If clipboard has content (error message, stack trace, log output), use it as the bug input
- If clipboard is empty, ask the user: "What's the bug? Give me an error message, screenshot, or description."

## Step 1: Identify

- If feature name provided, read `~/.kiro/memory/features/<feature-name>/`
- Extract: error message, affected files, line numbers, root cause

Present:
```
🐛 Issue: [error message]
   Affected: [file:line]
   Root Cause: [brief]
   Fix Scope: [what will change]
```

## Step 2: Minimal Fix

- ONLY fix the specific issue
- Do NOT refactor, add features, or fix other issues
- If broader changes needed, explain and get approval

## Step 3: Verify

- Run relevant tests
- If no tests exist for this path, write one
- Confirm fix resolves the original issue

## Step 4: Record

- If feature name provided, call `/handoff <feature-name>`
- Note the fix in implementation-notes if it's a recurring gotcha

## Scope Enforcement

- If tempted to fix other issues: note them, don't fix
- If file has multiple issues: fix ONLY the reported one
- If issue is in vendor/external code: explain what's wrong and what to communicate
