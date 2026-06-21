# Code Standards

## Python (Backend)

### Route handlers
- Thin handlers: validate input with Pydantic, call a service function, return result
- No business logic in `routes/` — that belongs in `services/`
- Use `HTTPException` for client errors; let unexpected exceptions propagate to FastAPI's default handler

### Services
- Each service function does one thing
- Database sessions opened in service, always closed in `finally`
- Never return raw SQLAlchemy model instances to routes — convert to Pydantic schema first

### Database
- All DB access goes through SQLAlchemy session
- Use `try/finally` to close sessions — never leave them open
- Fetch in bulk, process in memory — never query inside a loop

### AI client
- `services/ai_client.py` exposes only `complete(system_prompt, user_prompt) -> str`
- No Anthropic-specific types leak out of `ai_client.py`
- Prompt strings come from `docs/PROMPTS.md` — never hardcode prompts inline in service code

### Testing
- Mock at the service boundary, not the SDK level
- Use pytest fixtures for DB setup/teardown
- Test happy path and known failure modes (bad PDF text, AI returns malformed JSON)

### Logging
- Use Python's `logging` module, not `print`
- Include enough context to trace a request (e.g. statement_id, transaction count)
- Never log raw PDF text or full AI responses — too large, may contain PII

## React (Frontend)

### Components
- One component per file, named to match the file
- Keep components presentational — data fetching in hooks or parent, not inside components
- Handle loading and error states explicitly — never silently swallow fetch errors

### API calls
- All API calls go through `api/client.js` — never use `fetch` directly in a component

### State
- Prefer local state for UI-only concerns (open/close, form input)
- Lift state up only when two siblings share the same data
