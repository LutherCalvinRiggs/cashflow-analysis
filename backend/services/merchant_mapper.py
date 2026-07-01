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
) -> MerchantMap:
    """Create or update a MerchantMap entry. Uses suggested_key if provided, else normalizes description."""
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
        return existing

    entry = MerchantMap(
        pattern=pattern,
        display_name=description,
        category=category,
        confidence=confidence,
        source=source,
    )
    db.add(entry)
    return entry
