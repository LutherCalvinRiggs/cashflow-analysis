---
name: bip
description: Generate a "Build in Public" LinkedIn post draft from a recent commit or issue. Run automatically after every commit+push. Fetches context via GitHub MCP, applies conversion mappings, saves draft to drafts/.
---

## Usage

`/bip` — draft from the latest commit  
`/bip <sha>` — draft from a specific commit hash  
`/bip issue:<number>` — draft from a specific issue  

---

## Steps

### 1. Determine source

- If args match `issue:<n>`: use `mcp__github__get_issue` or `mcp__github__issue_read` for issue `n`
- If args look like a SHA (hex string): use that commit
- Otherwise: run `git rev-parse HEAD` to get the latest commit SHA

### 2. Fetch data via GitHub MCP

For commits: use `mcp__github__get_commit` with `detail: "stats"` on `LutherCalvinRiggs/cashflow-analysis`.  
For issues: use `mcp__github__issue_read` on the same repo.

### 3. Classify the commit

Look at the commit message and changed filenames. Pick the closest type:

| Type | Signals |
|---|---|
| `data-parsing` | pdf, extract, pars, pdfplumber, text |
| `llm-architecture` | ai_client, categoriz, prompt, memory, context |
| `math-guardrails` | math, calc, balance, guardrail, validation |
| `bug-fix` | fix, bug, crash, error, broken in commit message |
| `database` | database, models, migration, schema, sqlite |
| `api-endpoint` | route, endpoint, upload, api, fastapi |
| `frontend-ui` | .jsx, .tsx, component, frontend, tailwind |
| `general` | anything else |

### 4. Apply the conversion mapping

Translate the technical change into user-facing impact using the matching lens:

- `data-parsing` → "Handling irregular, messy bank transaction descriptions so users get clean dashboards"
- `llm-architecture` → "Giving the AI long-term memory to recall historical cash flow trends without exploding context windows"
- `math-guardrails` → "Preventing LLM math hallucinations by decoupling arithmetic from natural language so the AI never miscalculates a balance"
- `bug-fix` → "A transparent look at what broke and how fixing it makes the financial pipeline more reliable"
- `database` → "Structuring financial data so it's queryable, private, and never leaves the user's machine"
- `api-endpoint` → "Building the bridge between raw PDF data and the clean dashboard the user actually sees"
- `frontend-ui` → "Making financial clarity accessible — no finance degree required"
- `general` → Use judgment based on the commit message

### 5. Generate the post

Produce these six fields:

**hook** — Scroll-stopping first line, under 10 words. High stakes. No corporate jargon.  
**the_problem** — The real-world financial or technical pain this addresses.  
**the_solution** — How this commit directly resolves it.  
**technical_payload** — 1–2 sentences on the engineering approach.  
**call_to_action** — A direct question inviting engagement from devs or finance-minded readers.  
**formatted_full_text** — Full mobile-optimized post (see format below).

#### Formatting rules for `formatted_full_text`

```
<hook — under 10 words>
<blank line>
<one sentence naming the real financial frustration>
<blank line>
• <verb-led bullet, under 15 words>
• <verb-led bullet, under 15 words>
• <verb-led bullet, under 15 words>
• <optional 4th bullet>
<blank line>
<1–2 sentence technical note>
<blank line>
<call_to_action as a direct question>
<blank line>
Commit: https://github.com/LutherCalvinRiggs/cashflow-analysis/commit/<full-sha>
<blank line>
Link to the public repo is in the comments below!
```

NO: "excited to share", "game-changer", passive voice, flowery adjectives  
YES: direct verbs, specific file/feature names, honest about complexity

### 6. Save the draft

Create the `drafts/` directory if it doesn't exist.  
Save to: `drafts/linkedin_bip_<YYYY-MM-DD>_<source>.md`

File format:
```
# LinkedIn Draft — <date>
Source: `<source>`

---

## Structured Fields

**Hook:** <hook>

**The Problem:** <the_problem>

**The Solution:** <the_solution>

**Technical Payload:** <technical_payload>

**Call to Action:** <call_to_action>

---

## Full Post (copy-paste ready)

<formatted_full_text>
```

### 7. Print the result

Print the full post to the conversation so the user can review it inline without opening the file.

---

## Product context (inject into every post)

- App name: cashflow-analysis
- What it does: reads PDF bank statements, extracts every transaction via AI, stores locally, answers conversational finance questions
- Key differentiator: local-first (no cloud, no subscriptions), swappable AI provider, open-source
- Agent Harness: context steering + dynamic memory + isolated deterministic math to prevent balance hallucinations
- Target reader: professionals managing household budgets + developers interested in AI agent architecture
- Repo: https://github.com/LutherCalvinRiggs/cashflow-analysis

---

## Rules

- Never post to LinkedIn — output drafts only
- If GitHub MCP is unavailable, fall back to `git log -1 --format="%H %s" HEAD` and `git diff HEAD~1 HEAD --stat` via Bash
- Generate a draft for every commit regardless of type prefix
- `drafts/` is gitignored — never stage or commit files from it
