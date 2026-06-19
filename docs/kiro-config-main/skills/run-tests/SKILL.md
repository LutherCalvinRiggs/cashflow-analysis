---
name: run-tests
description: Run tests for the current repo or a specific service/module. Detects test framework and runs appropriately.
---

## Usage

`/run-tests` — Run all tests in current repo
`/run-tests <service>` — Run tests for a specific service

## Per-Repo Commands

Update this table to match your project's repos and test setup.

| Repo | Command |
|------|---------|
| (backend) | run your test suite |
| (frontend) | run lint and/or tests |
| (mobile) | run your test suite |
| (infra) | validate config per module |

## Common Issues

### Runtime Version Mismatch
If tests fail due to incompatible runtime version:
- Check your project's required runtime version
- Ensure your local environment matches
- Do NOT rewrite tests to work around version issues — fix the environment instead

## Output

Report:
```
✅ Tests: X passed, Y failed
📊 Coverage: Z%
❌ Failures: [list with file:line]
```

## Rules

- If tests fail, present failures clearly but don't auto-fix (use `/debug` for that)
- Always include coverage reporting where supported
- If no test framework exists for the repo, say so
