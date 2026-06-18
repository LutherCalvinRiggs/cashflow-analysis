# cashflow-analysis

A personal finance tool that ingests PDF bank statements, categorizes transactions with AI, stores them in a local database, and provides an interactive dashboard and chat interface for understanding your cash flow.

Built in public. Follow along on [LinkedIn](https://www.linkedin.com/in/lutherriggs) as each phase ships.

---

## What it does

- Upload PDF bank statements from any institution
- AI extracts and categorizes every transaction using your own category definitions
- Transactions are stored in a local SQLite database (portable, no cloud required)
- Dashboard shows chronological ledger, filterable by category, account, and date range
- Charts show monthly income vs. expenses, category breakdowns, and running balance trends
- Chat interface lets you ask natural language questions about your finances

## Design philosophy

- Self-hostable: clone the repo, add your API key, run it locally
- AI-provider agnostic: swap between Anthropic, OpenAI, or any compatible API via a single config
- No data leaves your machine except the API calls you make
- Built to be extended: clean separation between ingestion, storage, and UI layers

## Stack

See [`docs/PLAN.md`](docs/PLAN.md) for the full technical plan and task list.

## Getting started

> Setup instructions will live here once v1 scaffolding is complete.

## Built in public

This project is developed openly, commit by commit. Each meaningful commit includes a LinkedIn post explaining what was built and why. The goal is to show how a real personal finance tool gets built from scratch using AI-assisted development.

## License

MIT
