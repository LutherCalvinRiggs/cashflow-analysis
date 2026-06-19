---
name: analyze-csv
description: Analyze CSV data files for patterns, metrics, and insights. Use when working with exported data (call logs, customer interactions, etc).
---

## Usage

`/analyze-csv <path-to-csv>` — Analyze a CSV file
`/analyze-csv` — Look for CSVs in ~/.kiro/feature-research/

## Steps

1. Read the CSV file (or list available CSVs)
2. Report: row count, columns, date range, data types
3. Ask what the user wants to know

## Analysis Capabilities

- Summary statistics (counts, averages, distributions)
- Time-based trends (by day, week, hour)
- Grouping and aggregation
- Anomaly detection (outliers, gaps)
- Cross-referencing with other data

## Output

Present findings as:
- Summary table
- Key insights (bullet points)
- Suggested next steps or deeper dives

## Rules

- For large files (>10MB), sample first and confirm before full analysis
- Present numbers with context (percentages, comparisons)
- If the user asks for a specific metric, compute it directly without preamble
