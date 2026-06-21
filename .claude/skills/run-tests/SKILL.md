---
name: run-tests
description: Run tests for the backend, frontend, or both. Reports results clearly without auto-fixing failures.
---

## Usage

`/run-tests` — Run all tests
`/run-tests backend` — Backend only
`/run-tests frontend` — Frontend only

## Commands

| Target | Command |
|--------|---------|
| Backend (all) | `cd backend && pytest tests/ -v` |
| Backend (single file) | `cd backend && pytest tests/<file>.py -v` |
| Frontend | `cd frontend && npm test` |

## Output

```
✅ Tests: X passed, Y failed
📊 Coverage: Z%
❌ Failures: [list with file:line and error]
```

## Rules

- If tests fail, present failures clearly — do not auto-fix (use `/debug` for that)
- If no test framework is configured yet, say so
