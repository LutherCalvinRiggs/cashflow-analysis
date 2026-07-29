import re
from pathlib import Path

_PROMPTS_FILE = Path(__file__).parent.parent.parent / "docs" / "PROMPTS.md"


def _raw() -> str:
    return _PROMPTS_FILE.read_text()


def _extract(header: str) -> str:
    text = _raw()
    idx = text.find(header)
    if idx == -1:
        raise ValueError(f"Section '{header}' not found in PROMPTS.md")
    match = re.search(r"```\s*\n(.*?)```", text[idx:], re.DOTALL)
    if not match:
        raise ValueError(f"No code block found after '{header}'")
    return match.group(1).strip()


def extraction_system_prompt() -> str:
    return _extract("### System Prompt — Extraction")


def extraction_user_prompt(statement_text: str) -> str:
    template = _extract("### User Prompt — Extraction")
    return template.replace("{STATEMENT_TEXT}", statement_text)


def categorization_system_prompt() -> str:
    return _extract("### System Prompt — Categorization")


def categorization_user_prompt(categories_json: str, transactions_json: str) -> str:
    template = _extract("### User Prompt — Categorization")
    return template.replace("{CATEGORIES_JSON}", categories_json).replace("{TRANSACTIONS_JSON}", transactions_json)
