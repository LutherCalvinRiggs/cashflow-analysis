# Development Standards Reference

> Code examples below are written in JavaScript. The patterns and principles apply regardless of language — adapt syntax as needed.

## Sibling Function Synchronization

When fixing a bug or updating a pattern in a handler, grep for sibling functions with the same pattern before committing.

- Sibling functions share naming patterns: `get*ByEmail` / `get*ById`, `create*Invoice` / `create*Return`, `process*Payment` / `process*Refund`
- If a sibling has the same bug, fix it in the same PR
- If cannot fix in same PR, add TODO comment with issue/ticket reference

```bash
grep -n "functionPattern\|error_field.*403\|403.*error_field" src/handler.js
```

**When to apply:** Security/auth logic fixes, error handling patterns, validation patterns, any fix where root cause is a shared pattern.

## Shared Function Reuse

- Before writing new logic, search your shared managers directory for similar functionality
- Reuse over rewrite — call existing shared functions instead of duplicating
- If 2+ functions share similar logic, extract to shared function
- Build complex operations by composing simpler shared functions

```javascript
// ✅ Good — Reuse existing
const refundData = await dataManager.getRefundData(DB, customerId, invoiceId);

// ✅ Good — Compose functions
const [locations, unpaidInvoices, stats] = await Promise.all([
  getPurchaseLocations(DB, customerId),
  getUnpaidInvoices(DB, customerId),
  getCustomerStats(DB, customerId)
]);
```

### Extraction Checklist
- Logic used in 2+ places
- Logic is complex (>10 lines)
- Logic interacts with external services
- Logic transforms data in reusable way

## Database Field Verification

- Verify actual database column names before accessing — don't assume
- Date fields typically prefixed with `date_`: `date_created`, `date_processed`, `date_failed_payment`, `date_cancelled`
- Check existing queries in codebase for field name patterns

```javascript
// ❌ Bad — Assumes field name
const failedDate = invoice.failed_payment;

// ✅ Good — Actual field name
const failedDate = invoice.date_failed_payment;
```

### Verification Methods
- Search codebase: `grep -r "SELECT.*FROM table_name" shared/src/`
- Log query results: `console.log('Fields:', Object.keys(result[0]));`

## Variable Extraction for Consistency

Extract variables when the same logic or fallback is used multiple times.

```javascript
// ❌ Bad — Repeated fallback logic, inconsistent usage
const isPastDeadline = new Date(item.deadline_date || item.fallback_date) < new Date();
const daysRemaining = calculateDaysRemaining(item.fallback_date); // Inconsistent!

// ✅ Good — Extract once, use consistently
const deadlineField = item.deadline_date || item.fallback_date;
const isPastDeadline = new Date(deadlineField) < new Date();
const daysRemaining = calculateDaysRemaining(deadlineField);
```

- Extract when same expression used 2+ times
- Use descriptive variable names that explain the logic
- Extract early in function, use consistently throughout

## State Machine Pattern

Use priority-based state machines when aggregating status from multiple sources (internal DB + external APIs).

```javascript
const getRefundStatus = async (refund, externalPaymentId) => {
  // Priority 1: Internal failures always win
  if (refund.date_failed) return 'failed';
  if (refund.date_cancelled) return 'cancelled';

  // Priority 2: Check external payment API if available
  if (externalPaymentId) {
    const externalStatus = await getExternalRefundStatus(externalPaymentId);
    if (externalStatus === 'failed' || externalStatus === 'canceled') return 'failed';
    if (externalStatus === 'succeeded') return 'completed';
    if (externalStatus === 'pending' && refund.date_processed) return 'submitted';
  }

  // Priority 3: Fall back to internal status
  if (refund.date_processed) return 'completed';
  return 'pending';
};
```

- Define clear priority: worst case > intermediate > best case
- Check internal failures first, then external API, then internal status
- If external API fails, fall back to internal status only
- Never return undefined — always have a fallback status

## Database Error Handling

Wrap database queries in try/catch in shared functions for debugging context:

```javascript
// ✅ Good
module.exports.getInvoiceStatus = async (DB, invoiceId) => {
  let invoice;
  try {
    const invoiceResult = await DB.findOneBy('invoices', 'id', invoiceId, '*');
    invoice = invoiceResult?.[0];
  } catch (error) {
    console.error('Error fetching invoice', { error, invoiceId });
    throw error;
  }
  if (!invoice) throw new Error('Invoice not found');
  return invoice;
};
```

- Log errors with relevant context (IDs, parameters) before re-throwing
- Always re-throw so callers can handle appropriately
- Log query context (table, filters) but NOT sensitive data

## Standard Validation Pattern

```javascript
module.exports.handlerName = async (event) => {
  let DB_READER;
  try {
    const { customer_id, limit, offset } = event.queryStringParameters || {};

    if (!customer_id) {
      return generateResponse({ error: "customer_id is required" }, 400);
    }

    const customerId = parseInt(customer_id, 10);
    if (isNaN(customerId)) {
      return generateResponse({ error: "customer_id must be a number" }, 400);
    }

    const safeLimit = limit ? parseInt(limit, 10) : 10;
    const safeOffset = offset ? parseInt(offset, 10) : 0;

    if (isNaN(safeLimit) || safeLimit < 1 || safeLimit > 100) {
      return generateResponse({ error: "limit must be between 1 and 100" }, 400);
    }
    if (isNaN(safeOffset) || safeOffset < 0) {
      return generateResponse({ error: "offset must be non-negative" }, 400);
    }

    DB_READER = await dbReader();
    const result = await sharedFunction(DB_READER, customerId, safeLimit, safeOffset);
    return generateResponse(result);
  } catch (error) {
    console.error("Handler error:", error);
    if (error.message === "Resource not found") {
      return generateResponse({ error: "Resource not found" }, 404);
    }
    return generateResponse({ error: "Internal server error" }, 500);
  } finally {
    if (DB_READER) {
      await DB_READER.disconnect().catch(e => console.error('DB disconnect error', e));
    }
  }
};
```

**Key points:**
- `let DB_READER;` before try block for proper finally cleanup
- DB connection AFTER all validation
- Null check in finally: `if (DB_READER)` before disconnect
- Return 404 for not found, 400 for validation, 500 for generic

## Object Property Consistency

When transforming data, filters and accessors must use the actual property names in the transformed objects.

```javascript
// ✅ Good — Filter uses transformed property name
const processedItems = items.map(item => ({ item_status: item.status }));
const activeItems = processedItems.filter(item => item.item_status === 'ACTIVE');

// ❌ Bad — Filter uses original property name
const activeItems = processedItems.filter(item => item.status === 'ACTIVE'); // Wrong!
```

- Document property mapping clearly
- Add inline comments when names differ from source
- Test filters with actual transformed objects

## Dynamic Configuration (Parameter Store)

- Store frequently changing values in a config/parameter store, not hardcoded
- Create centralized utility functions in your shared module
- Handle parameter fetch failures gracefully with fallback values
- Build complete user-facing messages in utility functions, not at call sites

```javascript
// shared/src/supportUtils.js
module.exports.getSupportContact = async (prefix = 'please contact support') => {
  let email, phone;
  try { email = await getParam('support_email'); } catch (error) {
    console.error('Failed to fetch support_email param', { error: error.message });
  }
  try { phone = await getParam('support_phone'); } catch (error) {
    console.error('Failed to fetch support_phone param', { error: error.message });
  }
  if (email && phone) return `${prefix} by email (${email}) or phone (${phone}).`;
  if (email) return `${prefix} by email at ${email}.`;
  if (phone) return `${prefix} by phone at ${phone}.`;
  return `${prefix}.`;
};
```

**Good candidates:** Contact info, external URLs, feature flags, rate limits, business hours
**Not suitable:** Secrets (use a secrets manager), values that never change (use constants)

## Documentation Standards

- JSDoc on ALL exported functions: `@param`, `@returns`, `@throws`, `@example`
- Inline comments explain WHY, not WHAT
- When renaming endpoints, update ALL documentation files
- When changing response formats, update example responses
- Verify endpoint paths match between your routing/API definition and documentation

## Testing Standards

- Tests in `__tests__/` directory with `.test.js` suffix
- Structure: describe → nested describes for scenarios → it blocks
- Test all scenarios: valid, invalid, missing inputs, success, error, edge cases
- Clear all mocks in beforeEach
- 80% minimum coverage, 90% for critical paths

### Mocking Philosophy
- Mock **manager modules** and **utility functions**, not infrastructure SDK clients
- Example: mock `yourManager.sendEvent()`, not the underlying infrastructure SDK client
- This keeps tests fast, stable, and decoupled from infrastructure details

### What NOT to Test
- Queue message delivery (infrastructure concern)
- Function invocation mechanics
- SDK behavior
- Database connection establishment

### What TO Test
- Input validation and error responses
- Business logic in manager functions
- Response format and status codes
- Edge cases (missing fields, invalid data, empty results)

## Endpoint Patterns

- Standard flow: parse input → validate → call shared function → return response → handle errors
- **Handlers should be thin validators** — under 50 lines, business logic in shared managers
- Place imports at top of file, NOT inside functions
- Accept primitive parameters in shared functions, not objects
- Use a consistent response helper for all responses
- Kebab-case for paths: `/check-email-blocked`
- GET: `event.queryStringParameters` with optional chaining
- POST: `event.body ? JSON.parse(event.body) : {}`
- Always disconnect DB in finally block
- Add parameter logging near the top of each handler for traceability

### Router Pattern
```javascript
// ✅ Good — use module.exports to call sibling functions
module.exports.resourceHandler = async (event) => {
  switch(event.httpMethod) {
    case 'POST': return await module.exports.createResource(event);
    case 'GET': return await module.exports.getResource(event);
    default: return generateResponse('Method not allowed', 405);
  }
};

// ❌ Bad — this is unbound in module.exports arrow function context
return await this.createResource(event); // TypeError at runtime
```

## Queue Processor Configuration

### Timeout
- ALL queue-triggered functions MUST have an explicit timeout configured
- Never rely on default timeouts
- Baseline: set timeout to cover DB queries + external API calls with margin
- Set timeout to at least `batchSize × (expected time per message) × 2`

### Queue Permissions
- Do NOT add receive/delete/get-attributes permissions when triggered by event source mapping — the platform manages these automatically
- Only add explicit queue permissions for **sending** messages or interacting with other queues

### Batch Item Failures
- If declared, handler MUST return the appropriate batch failure response
- Implement for infrastructure failures (DB down), NOT for external API failures where retry causes duplicates

```yaml
# Example queue processor configuration
processQueueItems:
  handler: src/queueProcessor.handler
  timeout: 60
  events:
    - queue:
        arn: <your-queue-arn>
        batchSize: 10
        functionResponseType: ReportBatchItemFailures
```

## Email Normalization

Always normalize emails with `.toLowerCase()` before database lookups.

```javascript
// ✅ Good
const customer = await DB.findOneBy('customers', 'email', email.toLowerCase(), '*');

// ❌ Bad — Case-sensitive lookup may fail
const customer = await DB.findOneBy('customers', 'email', email, '*');
```

- Apply at point of database query, not just validation
- Also normalize when storing: `email: email.toLowerCase()`
- Apply to: customer lookups, authentication, email verification

## AI-Friendly Field Naming

Use descriptive field names that provide context for AI chatbots and API consumers.

```javascript
// ✅ Good — Context-specific names
return {
  customer_refunds: refunds,
  customer_refunds_data_limit: 10,
  customer_refunds_data_offset: 0,
  customer_refunds_total_count: 45,
  unpaid_invoice_ids: [123, 456, 789]
};

// ❌ Bad — Generic names lose context
return { data: refunds, limit: 10, offset: 0, total: 45, ids: [123, 456, 789] };
```

### Naming Patterns
- **Pagination**: `customer_refunds_data_limit`, not `limit`
- **ID Arrays**: `unpaid_invoice_ids`, not `ids`
- **Counts**: `total_unpaid_count`, not `count`
- **Status**: `membership_status`, not `status`
- **Nested objects**: `customer_info`, `membership_info`, not `info`, `details`

## Transformation Functions

Centralize common data transformations in shared functions.

```javascript
// ✅ Good — Shared transformation
const processLocations = (rawLocations) => {
  return rawLocations.map(loc => ({
    id: loc.id, name: loc.name, address: loc.address,
    city: loc.city, state: loc.state, zip: loc.zip,
    phone: loc.phone, hours: loc.hours, item_count: loc.item_count || 0
  }));
};

// Both functions use shared transformation
module.exports.getLocationSummary = async (DB, customerId) => {
  const locations = await DB.query('...');
  return { locations: processLocations(locations) };
};
```

### Extraction Triggers
- Identical `.map()` transformation in 2+ places
- Complex object restructuring (>5 fields)
- Conditional transformations with multiple branches

### Parameterization
```javascript
// ✅ Good — Single function with parameters
const processLocations = (locations, options = {}) => {
  const { includeHours = true, filterEmpty = false } = options;
  let processed = locations.map(loc => ({
    id: loc.id, name: loc.name,
    ...(includeHours && { hours: loc.hours })
  }));
  if (filterEmpty) processed = processed.filter(loc => loc.item_count > 0);
  return processed;
};

// ❌ Bad — Multiple similar functions
const processLocationsWithHours = (locations) => { /* ... */ };
const processLocationsWithoutHours = (locations) => { /* ... */ };
```

### Placement
- Simple transformations: helper functions in same file (not exported)
- Reused transformations: export from manager file
- Complex (>3 functions): dedicated utility file
