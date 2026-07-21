# Implementation Notes — cashflow-app

## LinkedIn Post Automation (2026-06-20)
After each commit, a "Building in Public" block is manually copy-pasted to LinkedIn. This needs to be automated — likely via a GitHub Action that triggers on push to main and posts via the LinkedIn API. Requires a LinkedIn API token. Revisit after Phase 1 ships.

## Gotchas (2026-07-19)
- **Env var is `AI_API_KEY`, not `ANTHROPIC_API_KEY`** — CLAUDE.md still says the latter; `config.py` and `.env.example` are the truth. Fix CLAUDE.md at some point.
- **Commit numbering drifted from plan numbering** — e.g. commit "2.2 Ledger" is plan task 2.3, commit "1.4 upload UI" is plan task 1.6. Trust file existence + plan.md checkboxes, not commit labels.
- **No `test_extraction.py`** — plan task 1.5 is only partially done; extraction has no automated coverage (categorization, PII filter, transactions API do).
- **`main.py` must run with CWD = `backend/`** — bare module imports and relative SQLite path. The root `start:api` script handles this.
- Unplanned services added: `pii_filter.py` (PII redaction before AI), `merchant_mapper.py` (merchant map + batched AI fallback in categorizer), `prompt_loader.py`.
