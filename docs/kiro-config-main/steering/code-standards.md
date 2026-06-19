# Code Standards

## Shared Code
- Maintain a canonical source for shared modules (e.g., `shared/src/`)
- Services that need shared code should consume it from the canonical source
- After editing shared code, redistribute to consuming services

## Database Access
- Always use your project's database abstraction helpers. Never instantiate raw connections directly.
- Use the designated read helper for SELECT queries
- Use the designated write helper for INSERT/UPDATE/DELETE
- Always disconnect in a `finally` block
- Before writing raw SQL with specific column names, verify columns against an existing query in the codebase. Don't assume column names.

## Handler Logging
Every API handler MUST have a log near the top (after parsing input) that includes:
1. A natural-language description of what the handler is doing
2. A traceable identifier (customer_id, order_id, request_id, etc.)

Example: `console.log('Creating support ticket', { call_id });`

This is critical for tracing requests in logs back to the event being debugged.

## Debugging & Review
- Validate automated review suggestions against the actual call chain before fixing
- Don't log expected outcomes (404s, not-found) as errors. Only log unexpected failures.
- Code review bot comments may be stale — check latest commit before acting on them.

## Validation
- Permissive validation for non-critical fields: skip invalid values rather than rejecting the entire request
- Never lose good data because one optional field has a bad value
- When documenting API response shapes, verify field names against the actual code that produces them. Don't assume key names from memory.

## Security
- Server-side computation over client trust. Priority, sentiment, classification — compute from data, never set by caller.
- All authenticated endpoints must verify the caller's permissions before executing
- Keep internal logic out of vendor-facing docs

## Imports
Before removing any `require`/`import`, grep the entire file for all usages. A removed import that is still referenced causes a silent ReferenceError at runtime.

## Testing

### Mocking Strategy
Mock at the **manager module level**, not at infrastructure/SDK level.
- ✅ Mock your application's own modules and managers
- ✅ Mock utility wrappers (e.g., queue send helpers)
- ❌ Don't mock SDK internals — test your code, not the SDK

### Test Payloads
- Test payloads must include all fields the production code path requires. Tests should resemble real data as closely as possible.

### Test Scope
Test **business logic**, not infrastructure plumbing.
- Test: handler validation, response shaping, manager function logic, error handling
- Don't test: "does the queue receive the message", "does the function invoke correctly"

## External APIs
- After writing implementation code, validate the payload against the live API during testing. Check docs for the correct endpoint and validation options.
- Don't assume ID formats (dashes, prefixes, casing) — verify against docs or live API response errors.

## Defensive Calls
- Wrap fire-and-forget async calls (notifications, analytics, webhooks) in try/catch — not .catch(). A synchronous error before the await (e.g., undefined variable access) won't be caught by .catch().
