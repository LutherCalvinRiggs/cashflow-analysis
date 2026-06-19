# Core Safety & Defensive Coding Reference

> Code examples below are written in JavaScript. The patterns and principles apply regardless of language — adapt syntax as needed.

## Verify Imports Before Removing

Before removing any `require`/`import` statement, always verify the symbol is not used anywhere else in the file.

```bash
grep -n "symbolName" path/to/file.js
```

- If the symbol appears in any function body, conditional, or expression — do not remove the import
- A removed import that is still referenced causes `ReferenceError` at runtime, silently breaking functionality

**Failure mode:** A handler function was removed from imports while still being called at two locations in the same file, causing a runtime crash on that code path.

## Defensive Coding

### Type Coercion for Comparisons
- Query parameters are always strings — parse before comparing with DB values (numeric)
- Use `parseInt(value, 10)` or `parseFloat(value)` before strict equality checks
- Common scenarios: location_id, customer_id, limit, offset filters

```javascript
// ✅ Good
const locationId = parseInt(event.queryStringParameters?.location_id, 10);
const items = allItems.filter(item => item.location_id === locationId);

// ❌ Bad — String vs number comparison always fails
const locationId = event.queryStringParameters?.location_id;
const items = allItems.filter(item => item.location_id === locationId);
```

### Null/Undefined Guards
- Add fallback to empty array when calling array methods on DB results
- Pattern: `const results = await DB.query() || [];`

```javascript
// ✅ Good
const results = await DB.findItems(customerId) || [];
const filtered = results.filter(item => item.active);

// ❌ Bad — Crashes if DB returns null
const results = await DB.findItems(customerId);
const filtered = results.filter(item => item.active);
```

### Optional Chaining & Nullish Coalescing
- Use `?.` for nested property access: `user?.profile?.email`
- Use `??` for null/undefined fallbacks (not falsy): `value ?? defaultValue`
- Difference: `0 ?? 5` returns `0`, but `0 || 5` returns `5`

### Array Method Safety
```javascript
const ids = (items || []).map(item => item.id);
const active = (items || []).filter(item => item.active);
```

### Common Scenarios
- DB queries may return null/undefined — always add `|| []` fallback
- All query params are strings — parse with `parseInt(value, 10)`
- Use `|| {}` fallback: `event.queryStringParameters || {}`
- Check `.length` before accessing `[0]`

## Finally Block Error Handling

ALWAYS add `.catch()` to async cleanup operations in finally blocks. Without it, a disconnect error replaces the original error (e.g. 404 → 500).

```javascript
module.exports.handler = async (event) => {
  let DB_READER;
  try {
    DB_READER = await dbReader();
    try {
      const result = await sharedFunction(DB_READER, customer_id);
      return generateResponse(result);
    } finally {
      // ✅ Catch prevents masking original error
      await DB_READER.disconnect().catch(e => console.error('DB disconnect error', e));
    }
  } catch (error) {
    if (error.message === 'Resource not found') {
      return generateResponse({ error: 'Resource not found' }, 404);
    }
    return generateResponse({ error: 'Internal server error' }, 500);
  }
};

// ❌ Bad — Disconnect error masks original error
} finally {
  await DB_READER.disconnect(); // If this throws, original error is lost
}
```

## Input Validation

- Use double validation: validate at endpoint level for quick feedback, validate again in shared functions
- Separate validation checks for specific error messages
- For GET endpoints: `event.queryStringParameters?.param_name`
- For numeric validation: `if (isNaN(customer_id)) return error("Invalid customer_id")`
- ALWAYS verify function parameter order before calling
- Return 400 Bad Request for validation errors with specific messages

## Endpoint Authorization Check (IDOR Prevention)

Any endpoint with a resource owner ID in the path must verify the authenticated user matches before processing.

```javascript
const resourceOwnerId = parseInt(event.pathParameters?.uid, 10);
if (!resourceOwnerId) return generateResponse({ error: 'Invalid ID' }, 400);

const authenticatedId = parseInt(event.requestContext?.authorizer?.user_id, 10);
if (authenticatedId !== resourceOwnerId) return generateResponse({ error: 'Forbidden' }, 403);
```

- Apply to: POST/PUT/DELETE `/:uid/...` endpoints, any owner-specific write
- Return 403 (not 404) when IDs don't match — don't reveal resource existence
- Check BEFORE any DB connection or business logic
- **Not required for**: Admin endpoints, read-only endpoints where authorizer scopes data, endpoints where JWT identity is the DB lookup key

## Error Handling

- NEVER return `error.message` directly to clients — reveals DB structure, file paths, API keys
- ALWAYS return generic messages: "Internal server error" or "Failed to process request"
- Log detailed errors with `console.error` including full context and stack traces
- In helper functions, ALWAYS re-throw errors so callers know operations failed
- Status codes: 400 validation, 401 auth, 404 not found, 500 server errors

## Production Logging Safety

- NEVER log full objects with `JSON.stringify()` in production
- NEVER log objects containing customer data: items, invoices, customers, orders, payments

```javascript
// ✅ Good — Specific fields only
console.log('Processing item', { item_id: item.id, status: item.status });

// ✅ Good — Redacted PII
console.log('Customer lookup', { customer_id: customerId, email: redactEmail(customer.email) });

// ✅ Good — Aggregated metrics
console.log('Batch processed', { total_items: items.length, failed_count: failedItems.length });

// ❌ Bad
console.log("item", JSON.stringify(item, null, 2));
console.log("Processing customer", customer);
```

### Objects That May Contain PII
- `customer` — email, phone, address, name
- `item` / `invoice` — customer references, payment details
- `order` / `purchase` — customer data, addresses
- `payment` — card details, billing info
- `transfer` / `shipment` — addresses, phone numbers

## Path Parameter Naming Consistency

The name in `event.pathParameters.{name}` MUST match the `{name}` in your route definition.

```javascript
// Route defined as: /{uid}/resource

// ✅ Good — matches {uid}
const resourceOwnerId = parseInt(event.pathParameters?.uid, 10);

// ❌ Bad — {id} does not exist in this route, always undefined
const resourceOwnerId = parseInt(event.pathParameters?.id, 10);
```

- Check sibling handlers in the same file for established convention
- Grep for `pathParameters` in the file to confirm naming pattern before writing

## Safe Date Construction

ALWAYS validate date values before passing to `new Date()`. `new Date(null)` returns Unix epoch; `new Date(undefined)` returns Invalid Date — both crash on `.toISOString()`.

```javascript
// ✅ Good
const deadline = item.deadline_date ? new Date(item.deadline_date) : null;
expiry: deadline ? deadline.toISOString() : null

// ✅ Good — Dependent calculations
const daysRemaining = deadline ? calculateDaysRemaining(deadline) : null;
const urgency = daysRemaining !== null ? (daysRemaining <= 1 ? 'urgent' : 'normal') : null;

// ❌ Bad
const deadline = new Date(item.deadline_date); // Crashes if null
expiry: deadline.toISOString() // Crashes if null
```

### Common nullable date fields:
`date_created`, `date_paid`, `date_processed`, `date_failed`, `date_cancelled`, `deadline_date`, `expiry_date`

## DB Connection Lifecycle

### Reuse Before Opening
- Before opening a new DB connection, check if an existing one is still open and in scope
- Pass existing writer connection to helper functions instead of opening a dedicated one

### Never Share with Fire-and-Forget
- NEVER pass a shared DB connection to a non-awaited operation
- The shared connection may be disconnected before the fire-and-forget query runs → silent data loss
- Fire-and-forget DB operations must open their own dedicated connection

```javascript
// ✅ Good — reuse existing, disconnect in finally
try {
  await storeData(DB, customerId, payload);
} finally {
  await DB.disconnect().catch(e => console.error('DB disconnect error', e));
}

// ❌ Bad — shared connection passed to fire-and-forget
storeData(DB_WRITER, customerId, payload)
  .catch(err => console.error('Storage failed', { err }));
// DB_WRITER.disconnect() called later — query may never complete
```

### When Dedicated Connection IS Needed
- Existing connection already disconnected
- Operation is fire-and-forget and may outlive the caller
- Operation needs different connection type (reader vs writer)

## Safe Numeric Operations

Use `parseFloat()` with fallback for arithmetic on database fields that may be null:

```javascript
// ✅ Good
const fee = (parseFloat(item.item_price) || 0) * 0.25;
const total = (parseFloat(invoice.subtotal) || 0) + (parseFloat(invoice.tax) || 0) + (parseFloat(invoice.fees) || 0);

// ❌ Bad — NaN if null
const fee = item.item_price * 0.25;
```

- Consider whether 0 is appropriate fallback (sometimes null should remain null)

## PII Redaction in Logs

- ALWAYS redact email addresses before logging → format: `u***@example.com`
- NEVER log full email addresses, phone numbers, addresses, or payment information
- Handle edge cases: multiple @ symbols, empty parts, invalid formats → return `'<redacted>'`
- If redaction function fails, return `'<redacted>'` as fallback

## Safe JSON Parsing

```javascript
// ✅ Good — Safe pattern
const body = event.body ? JSON.parse(event.body) : {};
const { field } = body;

// ❌ Bad — Crashes if event.body is null/undefined
JSON.parse(event.body) || {}
```

- Apply to ALL request handlers that accept JSON input
- If JSON.parse fails, catch and return 400 Bad Request

## Type Coercion in Comparisons

Database may return numeric IDs as strings. Use type coercion fallback:

```javascript
// ✅ Good — Handles both string and number
const isActive = pm.id === activePaymentMethodId ||
                 parseInt(pm.id, 10) === activePaymentMethodId;

// ❌ Bad — Fails if types don't match
const isActive = pm.id === activePaymentMethodId; // '123' !== 123
```

**Use coercion when:**
- Comparing database IDs with parsed query parameters
- Comparing values from different data sources
- Type of value is uncertain or inconsistent

**Don't use coercion when:**
- Both values from same source
- Type is guaranteed (both parsed with parseInt)
- Strict type checking required for security

## Async Completion

ALWAYS await async operations that must complete before the function returns. Unawaited Promises may be silently dropped when the runtime freezes or cleans up.

```javascript
// ✅ Good — awaited
await enqueueEvent({ event_type: 'user_action', user_id: id })
  .catch(err => console.error('Failed to enqueue event', { err }));

// ❌ Bad — fire-and-forget, may be dropped on function freeze
enqueueEvent({ event_type: 'user_action', user_id: id })
  .catch(err => console.error('Failed to enqueue event', { err }));
```

- Queue send operations and async side effects MUST be awaited
- Only exception: latency-critical hot paths where operation is genuinely optional and documented
- If exception made, add comment explaining why and acceptable loss scenario
