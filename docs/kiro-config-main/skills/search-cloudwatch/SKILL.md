---
name: search-logs
description: Search application logs for errors, exceptions, and specific patterns. Use when debugging production/staging issues or investigating error reports.
---

## Usage

`/search-logs <service-name>` — Search logs for a specific service
`/search-logs <service-name> <search-term>` — Search with specific pattern

## Steps

1. Identify the log group or log stream for the target service
2. Determine time range (default: last 1 hour)
3. Run a log query using your platform's logging CLI or console
4. Present findings: matching lines, timestamps, frequency

## Query Tips

- Search for `ERROR` or `Exception` to find failures
- Include a request/trace ID to follow a specific request
- Filter by time window to narrow results
- Sort by timestamp descending for most recent first

## Output

Report findings as:
```
Service: <name>
Time range: <start> to <end>
Matches found: <count>

[timestamp] <log line>
[timestamp] <log line>
```

## Rules

- Refer to your project's logging reference for service names and log group paths
- Read-only — never modify or delete log data
- If no matches found, widen the time range before concluding no errors exist
