# Build in Public Pipeline

Generates LinkedIn post drafts from GitHub commits and issues. Reads the repo, sends technical context to an LLM, and writes a structured draft to `drafts/`.

## Setup

```bash
pip install -r bip_requirements.txt
```

Add `GITHUB_TOKEN` to your `.env` (copy from `.env.example`). A personal access token with read access to public repos is sufficient. Without it, the pipeline still works but is subject to GitHub's unauthenticated rate limit (60 req/hr).

## Usage

```bash
# Latest commit on the default branch
python bip_pipeline.py

# Specific commit (full or short SHA)
python bip_pipeline.py --commit f4bbd43

# Specific issue number
python bip_pipeline.py --issue 12

# Preview without saving to drafts/
python bip_pipeline.py --commit f4bbd43 --dry-run
```

## Output

Drafts are saved to `drafts/linkedin_bip_YYYY-MM-DD_<source>.md`. The `drafts/` directory is gitignored — your unpublished drafts stay local.

Each draft contains:
- **Structured fields** — hook, problem, solution, technical payload, call to action
- **Full post** — copy-paste ready text with double line breaks for LinkedIn mobile

## Configuration

All config is pulled from `.env`:

| Variable | Purpose |
|---|---|
| `AI_PROVIDER` | `anthropic` (default) or `openai` |
| `AI_MODEL` | Model to use, e.g. `claude-sonnet-4-6` |
| `ANTHROPIC_API_KEY` | Required if using Anthropic |
| `OPENAI_API_KEY` | Required if using OpenAI |
| `AI_BASE_URL` | Optional — for OpenAI-compatible endpoints |
| `GITHUB_TOKEN` | Optional but recommended to avoid rate limits |

## How it works

1. Fetches commit diff or issue body from the GitHub REST API
2. Classifies the commit type (data-parsing, llm-architecture, bug-fix, etc.)
3. Applies a conversion mapping to translate technical work into user-facing impact
4. Sends structured context + system prompt to the LLM
5. Forces structured output via Anthropic tool use or OpenAI `response_format`
6. Writes the result to `drafts/`
