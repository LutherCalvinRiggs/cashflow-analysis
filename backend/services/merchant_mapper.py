import re

from sqlalchemy.orm import Session

from database import MerchantMap, Transaction


def normalize(description: str) -> str:
    """Strip leading digit clusters + punctuation, lowercase, collapse whitespace.

    '1284825 FoodCellar LIC' → 'foodcellar lic'
    '#0042 NETFLIX.COM'      → 'netflix.com'
    """
    text = description.strip()
    text = re.sub(r"^[\d\s#*\-]+", "", text)   # strip leading digits / symbols
    text = re.sub(r"[^\w\s]", " ", text)        # replace non-word chars with space
    text = text.lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def lookup(description: str, db: Session) -> MerchantMap | None:
    """Return the MerchantMap entry whose pattern matches this description, or None."""
    key = normalize(description)
    if not key:
        return None
    entry = db.query(MerchantMap).filter(MerchantMap.pattern == key).first()
    if entry:
        return entry
    # Partial match: check if any stored pattern is contained in the key or vice versa
    all_entries = db.query(MerchantMap).all()
    for entry in all_entries:
        if entry.pattern and (entry.pattern in key or key in entry.pattern):
            return entry
    return None


def find_related_entry(description: str, db: Session) -> MerchantMap | None:
    """Find an existing MerchantMap entry whose pattern's words all appear in this description.

    More lenient than lookup()'s substring match: bank descriptions commonly interleave
    filler words (e.g. "Zelle Payment To Luther LLC" vs. the AI's suggested_key "zelle
    payment luther") and unique trailing reference numbers. Used when a user edits a
    category so the edit reuses the merchant's existing canonical pattern instead of
    creating a new one keyed to this single transaction's unique reference number.
    """
    key_words = set(normalize(description).split())
    if not key_words:
        return None
    best = None
    for entry in db.query(MerchantMap).all():
        pattern_words = set(entry.pattern.split()) if entry.pattern else set()
        if pattern_words and pattern_words.issubset(key_words):
            if best is None or len(pattern_words) > len(best.pattern.split()):
                best = entry  # prefer the most specific (longest) matching pattern
    return best


def find_matching_transactions(pattern: str, db: Session) -> list[Transaction]:
    """Return all transactions whose normalized description contains every word in this pattern.

    Word-subset match (see find_related_entry) rather than substring containment, so a
    merchant-level category edit reaches every transaction from that merchant, not just
    ones whose description happens to contain the pattern as a contiguous substring.
    """
    pattern_words = set(pattern.split())
    if not pattern_words:
        return []
    matches = []
    for tx in db.query(Transaction).all():
        key_words = set(normalize(tx.description).split())
        if pattern_words.issubset(key_words):
            matches.append(tx)
    return matches


def apply_map(transactions: list[Transaction], db: Session) -> tuple[list[Transaction], list[Transaction]]:
    """Split transactions into (mapped, unmapped).

    Mapped transactions have category + confidence written in-place from the map.
    Returns (mapped, unmapped) — caller commits when ready.
    """
    mapped, unmapped = [], []
    for tx in transactions:
        entry = lookup(tx.description, db)
        if entry:
            tx.category = entry.category
            tx.confidence = entry.confidence
            mapped.append(tx)
        else:
            unmapped.append(tx)
    return mapped, unmapped


def upsert_entry(
    description: str,
    suggested_key: str | None,
    category: str,
    confidence: float,
    source: str,
    db: Session,
) -> tuple[MerchantMap, bool]:
    """Create or update a MerchantMap entry. Uses suggested_key if provided, else normalizes description.

    Returns (entry, created) — created is True only when a new row was inserted.
    """
    pattern = (suggested_key or "").strip().lower() or normalize(description)
    if not pattern:
        pattern = normalize(description)

    existing = db.query(MerchantMap).filter(MerchantMap.pattern == pattern).first()
    if existing:
        # User edits always win; AI never downgrades a user-verified entry
        if source == "user" or existing.source == "ai":
            existing.category = category
            existing.confidence = confidence
            existing.source = source
            existing.display_name = description
        return existing, False

    entry = MerchantMap(
        pattern=pattern,
        display_name=description,
        category=category,
        confidence=confidence,
        source=source,
    )
    db.add(entry)
    db.flush()  # make visible to subsequent lookups in this batch (session is autoflush=False)
    return entry, True
