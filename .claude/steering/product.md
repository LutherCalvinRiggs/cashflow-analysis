# Product Context

cashflow-analysis is a locally-run personal finance tool. The user uploads PDF bank statements → AI extracts and categorizes transactions → SQLite stores them → React dashboard shows a filterable ledger, charts, and a chat interface.

## Core user flow
1. Upload PDF bank statement via `UploadPanel`
2. AI extracts every transaction (date, description, amount, type) using the extraction prompt
3. AI categorizes each transaction against the 20 categories in `docs/CATEGORIES.md`
4. Transactions stored in SQLite and displayed in filterable `Ledger`
5. `Charts` show monthly income vs expenses, category breakdown, running balance
6. `ChatPanel` answers natural language questions about the user's finances

## Key constraints
- Self-hostable: runs entirely on localhost, no cloud required except AI API calls
- No data leaves the machine except AI API calls
- AI provider is swappable via config (Anthropic ↔ OpenAI-compatible)
- Single user — no auth needed until Phase 5 (optional stretch)
- All AI prompts live in `docs/PROMPTS.md` — do not hardcode prompts in service code
- Categories live in `docs/CATEGORIES.md` — seeded to DB on first run
