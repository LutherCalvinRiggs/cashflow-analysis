"""
PII redaction for bank statement text before it is sent to the AI provider
or persisted to the local database.

WHAT IS CAUGHT
--------------
- Account / member numbers with a recognizable label:
    "Account Number:", "Acct #:", "Acct No:", "Member Number:", "Member No:", etc.
  The last 4 digits are preserved so the AI can still extract account_last4.
- Routing / transit / ABA numbers with a label → replaced with [ROUTING]
- Card numbers in grouped 4×4 format (spaces or dashes) → ****last4
- SSNs in NNN-NN-NNNN or NNN NN NNNN format → [REDACTED]
- Labeled transaction/reference numbers: "Transaction#:", "Trans ID:",
  "Conf#:", "PPD ID:", etc. → [REF]
- Bare long digit runs (8+ consecutive digits) left over after the above —
  catches unlabeled Zelle/ACH/wire reference numbers embedded directly in
  transaction descriptions (e.g. "Zelle Payment To Jane Doe 22989085846")
  → [REF]. Already-masked fragments like "...1198" or "Card 0352" are
  untouched since they're under 8 digits.
- Common US street addresses embedded in a description (e.g. ATM location
  lines like "4445 Vernon Blvd") → [ADDRESS]. Heuristic match on
  "<number> <words> <street suffix>"; city/state that follows is not
  caught.

KNOWN GAPS (conservative by design)
------------------------------------
- Unlabeled account numbers: if a statement prints the account number in a
  header block without a recognizable label, it will NOT be caught.
- Non-US formats: IBANs, UK sort codes, Australian BSBs are not caught.
- Addresses without a recognized street suffix, or non-US address formats.
If full privacy is required, point AI_BASE_URL at a local model (Ollama, LM
Studio, etc.) so no text leaves the machine at all.
"""

import re


def _keep_last4(match, prefix_group: int, digits_group: int) -> str:
    prefix = match.group(prefix_group)
    digits = match.group(digits_group)
    return f"{prefix}****{digits[-4:]}"


# Labeled account number: "Account Number: 483920173627" → "Account Number: ****3627"
_ACCOUNT_RE = re.compile(
    r"((?:acct\.?|account|member)\s*(?:number|num|no\.?|#)?\s*[:\-]?\s*)(\d{6,17})",
    re.IGNORECASE,
)

# Labeled routing/transit number: "Routing Number: 021000021" → "Routing Number: [ROUTING]"
_ROUTING_RE = re.compile(
    r"((?:routing|transit|aba)\s*(?:number|num|no\.?|#)?\s*[:\-]?\s*)(\d{9})\b",
    re.IGNORECASE,
)

# Card number in grouped 4×4 format: "4532 0151 1283 0366" or "4532-0151-1283-0366"
_CARD_RE = re.compile(
    r"\b(\d{4})[\s\-](\d{4})[\s\-](\d{4})[\s\-](\d{4})\b",
)

# Card number as 16 unbroken digits — unambiguous in a bank statement context
_CARD_UNBROKEN_RE = re.compile(r"\b(\d{12})(\d{4})\b")

# SSN: "123-45-6789" or "123 45 6789"
_SSN_RE = re.compile(
    r"\b\d{3}[\s\-]\d{2}[\s\-]\d{4}\b",
)

# Labeled transaction/reference number: "Transaction#: 22990339876",
# "PPD ID: 9111111103", "Conf#: 12345678" → "[REF]"
_REF_RE = re.compile(
    r"((?:transaction|trans|conf|confirmation|ppd|ref|reference)\.?\s*"
    r"(?:id|number|num|no\.?|#)?\s*[:\-]?\s*)(\d{5,})",
    re.IGNORECASE,
)

# Street address embedded in a description, e.g. an ATM location line:
# "4445 Vernon Blvd" → "[ADDRESS]". Street number + 1-4 words + a common
# street suffix; the trailing city/state is intentionally left alone.
_ADDRESS_RE = re.compile(
    r"(?<![\d/\-])\b\d{1,6}\s+[A-Za-z0-9.]+(?:\s+[A-Za-z0-9.]+){0,3}?\s+"
    r"(?:Blvd|Boulevard|Ave|Avenue|St|Street|Rd|Road|Dr|Drive|Ln|Lane|"
    r"Way|Ct|Court|Pl|Place|Cir|Circle|Pkwy|Parkway|Hwy|Highway)\b\.?",
    re.IGNORECASE,
)

# Bare long digit runs left over after every labeled pattern above has run —
# catches unlabeled P2P/ACH reference numbers (e.g. Zelle's trailing
# transaction ID). 8+ digits distinguishes these from check numbers and
# short reference codes, which are typically <=7 digits.
_LONG_DIGIT_RUN_RE = re.compile(r"\b\d{8,}\b")


def redact(text: str) -> str:
    """Remove common PII patterns from bank statement text before sending to the AI.

    Conservative: only redacts when the label or format makes the pattern unambiguous.
    Preserves the last 4 digits of account and card numbers so the AI can still
    extract account_last4 from the statement header.
    """
    # Account numbers (labeled)
    text = _ACCOUNT_RE.sub(lambda m: _keep_last4(m, 1, 2), text)

    # Routing numbers (labeled) — no useful digits to preserve
    text = _ROUTING_RE.sub(lambda m: f"{m.group(1)}[ROUTING]", text)

    # Card numbers (grouped 4×4) — preserve last 4
    text = _CARD_RE.sub(lambda m: f"****{m.group(4)}", text)

    # Card numbers (16 unbroken digits) — preserve last 4
    text = _CARD_UNBROKEN_RE.sub(lambda m: f"****{m.group(2)}", text)

    # SSNs — no useful digits to preserve
    text = _SSN_RE.sub("[REDACTED]", text)

    # Street addresses embedded in descriptions (e.g. ATM location lines)
    text = _ADDRESS_RE.sub("[ADDRESS]", text)

    # Labeled transaction/reference numbers — no useful digits to preserve
    text = _REF_RE.sub(lambda m: f"{m.group(1)}[REF]", text)

    # Any remaining bare long digit runs (unlabeled P2P/ACH reference numbers)
    text = _LONG_DIGIT_RUN_RE.sub("[REF]", text)

    return text
