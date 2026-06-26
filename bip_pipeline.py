"""
Build in Public Pipeline — generates LinkedIn post drafts from GitHub commits/issues.

Reads the latest commit (or a specific commit/issue) from the cashflow-analysis repo,
sends the technical context to an LLM, and writes a structured LinkedIn draft to drafts/.

Usage:
    python bip_pipeline.py                     # latest commit on default branch
    python bip_pipeline.py --commit abc1234    # specific commit hash (full or short)
    python bip_pipeline.py --issue 42          # specific issue number
    python bip_pipeline.py --commit abc1234 --dry-run  # print without saving
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# ── Configuration ─────────────────────────────────────────────────────────────

REPO_OWNER = "LutherCalvinRiggs"
REPO_NAME = "cashflow-analysis"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic")
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")
AI_BASE_URL = os.getenv("AI_BASE_URL", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

DRAFTS_DIR = Path(__file__).parent / "drafts"

# ── Schema ────────────────────────────────────────────────────────────────────


class LinkedInPost(BaseModel):
    hook: str = Field(description="Scroll-stopping first line, under 10 words, no filler")
    the_problem: str = Field(description="The real-world financial or technical pain this addresses")
    the_solution: str = Field(description="How this commit or issue directly resolves it")
    technical_payload: str = Field(description="One or two sentences on the engineering approach")
    call_to_action: str = Field(description="A question that invites engagement from devs or finance-minded readers")
    formatted_full_text: str = Field(description="Full mobile-optimized post with double line breaks ready to paste into LinkedIn")


# ── GitHub API ────────────────────────────────────────────────────────────────


def _gh_headers() -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def fetch_commit(sha: str) -> dict:
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{sha}"
    resp = requests.get(url, headers=_gh_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


def fetch_latest_commit() -> dict:
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits"
    resp = requests.get(url, headers=_gh_headers(), params={"per_page": 1}, timeout=15)
    resp.raise_for_status()
    commits = resp.json()
    if not commits:
        raise ValueError("No commits found in repository")
    return fetch_commit(commits[0]["sha"])


def fetch_issue(number: int) -> dict:
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{number}"
    resp = requests.get(url, headers=_gh_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── Context builders ──────────────────────────────────────────────────────────


def _commit_type_hint(message: str, filenames: list[str]) -> str:
    """Classify the commit to help the LLM apply the right conversion mapping."""
    msg = message.lower()
    files = " ".join(filenames).lower()

    if any(w in msg for w in ("fix", "bug", "crash", "error", "broken")):
        return "bug-fix"
    if any(w in files for w in ("ai_client", "categoriz", "extract", "prompt")):
        return "llm-architecture"
    if any(w in files for w in ("database", "models", "migration", "schema")):
        return "database"
    if any(w in files for w in ("pdf", "extract", "pars")):
        return "data-parsing"
    if any(w in files for w in ("math", "calc", "balance", "guardrail")):
        return "math-guardrails"
    if any(w in files for w in (".jsx", ".tsx", "component", "frontend", "ui")):
        return "frontend-ui"
    if any(w in files for w in ("route", "endpoint", "api")):
        return "api-endpoint"
    return "general"


def build_context_from_commit(data: dict) -> tuple[str, str]:
    """Returns (context_text, source_slug)."""
    commit = data["commit"]
    message = commit["message"]
    sha = data["sha"][:7]
    date = commit["author"]["date"]

    files = data.get("files", [])
    changed = [f["filename"] for f in files]

    # Collect diff excerpts for code files only (capped to avoid token bloat)
    excerpts = []
    for f in files[:6]:
        if "patch" in f and re.search(r"\.(py|jsx|js|ts|tsx|md)$", f["filename"]):
            excerpts.append(f"### {f['filename']}\n{f['patch'][:600]}")

    commit_type = _commit_type_hint(message, changed)

    full_sha = data["sha"]
    commit_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/commit/{full_sha}"

    context = f"""COMMIT: {sha}
COMMIT_URL: {commit_url}
DATE: {date}
MESSAGE: {message}
TYPE_HINT: {commit_type}
FILES CHANGED: {', '.join(changed[:12])}

CODE DIFF (excerpt):
{''.join(excerpts) if excerpts else 'No diff available'}
"""
    return context, f"commit-{sha}"


def build_context_from_issue(data: dict) -> tuple[str, str]:
    """Returns (context_text, source_slug)."""
    context = f"""ISSUE #{data['number']}: {data['title']}
STATE: {data['state']}
LABELS: {', '.join(l['name'] for l in data.get('labels', []))}
BODY:
{data.get('body') or 'No description provided'}
"""
    return context, f"issue-{data['number']}"


# ── Prompt ────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """You are a "Build in Public" content strategist for a developer building an AI-powered personal finance app called cashflow-analysis.

PRODUCT CONTEXT:
- Reads PDF bank statements, extracts every transaction via AI, and stores them locally — no cloud, no third-party data sharing
- Categorizes spending using a 20-category AI-assisted taxonomy tailored for a household budget
- Answers conversational questions ("How much did we spend on childcare last quarter?") via a chat interface
- Uses a custom Agent Harness: context steering, dynamic memory retrieval, and isolated deterministic math (decoupled from the LLM to prevent balance miscalculations)
- Open-source, self-hosted, runs on localhost with two terminal windows

TARGET AUDIENCE: Professionals managing household budgets who are frustrated with opaque finance apps + developers curious about AI agent architecture.

CONVERSION MAPPINGS — classify the commit and apply the matching human lens:
- data-parsing → "Handling irregular, messy bank transaction descriptions so users get clean dashboards instead of raw gibberish"
- llm-architecture → "Giving the AI a long-term memory so it recalls historical cash flow trends without exploding context windows or API costs"
- math-guardrails → "Preventing LLM math hallucinations by decoupling arithmetic from natural language so the AI never miscalculates a balance"
- bug-fix → "A transparent look at what broke and why fixing it makes the financial pipeline more reliable"
- database → "Structuring financial data so it's queryable, private, and never leaves the user's machine"
- api-endpoint → "Building the bridge between raw PDF data and the clean dashboard the user actually sees"
- frontend-ui → "Making financial clarity accessible — no finance degree required"
- general → Use your judgment based on the commit message and files

FORMATTING RULES for formatted_full_text:
1. Line 1: Scroll-stopper hook, under 10 words. High stakes. No corporate jargon.
2. Empty line after line 1 (double newline — critical for LinkedIn mobile rendering)
3. One sentence naming the real financial frustration this addresses
4. Empty line
5. Body: 3–5 bullet points. Each bullet under 15 words. Start with a verb or number.
6. Empty line
7. Technical note: 1–2 sentences on the engineering approach. Can be slightly more detailed.
8. Empty line
9. The call_to_action as a direct question to the reader
10. Empty line
10. Empty line
11. "Commit: <COMMIT_URL from context>" (the full GitHub commit URL)
12. Empty line
13. Final line exactly: "Link to the public repo is in the comments below!"

NO: flowery adjectives, "excited to share", "game-changer", passive voice, filler phrases
YES: direct verbs, specific numbers where possible, honest about complexity

Return ONLY valid JSON matching the schema. No explanation, no markdown wrapper."""


def _user_prompt(context: str) -> str:
    return f"""Generate a LinkedIn "Build in Public" post from the following repository context:

{context}"""


# ── LLM calls ─────────────────────────────────────────────────────────────────


def generate_post(context: str) -> LinkedInPost:
    if AI_PROVIDER == "anthropic":
        return _call_anthropic(context)
    return _call_openai(context)


def _call_anthropic(context: str) -> LinkedInPost:
    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    schema = LinkedInPost.model_json_schema()
    # Remove $defs indirection if Pydantic added any — Anthropic handles flat schemas best
    schema.pop("$defs", None)
    schema["additionalProperties"] = False

    response = client.messages.create(
        model=AI_MODEL,
        max_tokens=2048,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _user_prompt(context)}],
        tools=[{
            "name": "create_linkedin_post",
            "description": "Create a structured LinkedIn Build in Public post",
            "input_schema": schema,
        }],
        tool_choice={"type": "tool", "name": "create_linkedin_post"},
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "create_linkedin_post":
            return LinkedInPost(**block.input)

    raise RuntimeError("Anthropic returned no tool_use block")


def _call_openai(context: str) -> LinkedInPost:
    from openai import OpenAI

    kwargs: dict = {"api_key": OPENAI_API_KEY}
    if AI_BASE_URL:
        kwargs["base_url"] = AI_BASE_URL

    client = OpenAI(**kwargs)

    response = client.beta.chat.completions.parse(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": _user_prompt(context)},
        ],
        response_format=LinkedInPost,
        max_tokens=2048,
    )

    parsed = response.choices[0].message.parsed
    if parsed is None:
        raise RuntimeError("OpenAI returned no parsed output")
    return parsed


# ── Output ────────────────────────────────────────────────────────────────────


def save_draft(post: LinkedInPost, source: str) -> Path:
    DRAFTS_DIR.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = re.sub(r"[^a-z0-9]+", "-", source.lower()).strip("-")[:40]
    path = DRAFTS_DIR / f"linkedin_bip_{date_str}_{slug}.md"

    path.write_text(
        f"# LinkedIn Draft — {date_str}\n"
        f"Source: `{source}`\n\n"
        "---\n\n"
        "## Structured Fields\n\n"
        f"**Hook:** {post.hook}\n\n"
        f"**The Problem:** {post.the_problem}\n\n"
        f"**The Solution:** {post.the_solution}\n\n"
        f"**Technical Payload:** {post.technical_payload}\n\n"
        f"**Call to Action:** {post.call_to_action}\n\n"
        "---\n\n"
        "## Full Post (copy-paste ready)\n\n"
        f"{post.formatted_full_text}\n"
    )
    return path


def print_result(post: LinkedInPost, path: Path | None) -> None:
    divider = "─" * 60
    print(f"\n{divider}")
    print("BUILD IN PUBLIC — LINKEDIN DRAFT")
    print(divider)
    print(post.formatted_full_text)
    print(divider)
    if path:
        print(f"\nSaved → {path}")


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a LinkedIn BIP post from a GitHub commit or issue.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--commit", metavar="SHA", help="Commit hash (full or short)")
    group.add_argument("--issue", metavar="N", type=int, help="Issue number")
    parser.add_argument("--dry-run", action="store_true", help="Print post but don't save to drafts/")
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY and not OPENAI_API_KEY:
        sys.exit("Error: set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env")

    try:
        if args.issue:
            print(f"Fetching issue #{args.issue}...")
            data = fetch_issue(args.issue)
            context, source = build_context_from_issue(data)
        elif args.commit:
            print(f"Fetching commit {args.commit}...")
            data = fetch_commit(args.commit)
            context, source = build_context_from_commit(data)
        else:
            print("Fetching latest commit...")
            data = fetch_latest_commit()
            context, source = build_context_from_commit(data)
    except requests.HTTPError as e:
        sys.exit(f"GitHub API error: {e}")

    print(f"Generating post for {source}...")
    post = generate_post(context)

    path = None if args.dry_run else save_draft(post, source)
    print_result(post, path)


if __name__ == "__main__":
    main()
