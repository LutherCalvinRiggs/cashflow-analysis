import json
import logging

from sqlalchemy.orm import Session

from database import Category, MerchantMap, Transaction
from services.ai_client import complete
from services.merchant_mapper import apply_map, upsert_entry
from services.prompt_loader import categorization_system_prompt, categorization_user_prompt

logger = logging.getLogger(__name__)

BATCH_SIZE = 40


def _confidence_to_float(value: str | None) -> float | None:
    mapping = {"high": 1.0, "medium": 0.6, "low": 0.3}
    if value is None:
        return None
    return mapping.get(str(value).lower())


def _parse_json_list(raw: str) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


def _build_map_context(db: Session) -> str:
    entries = db.query(MerchantMap).order_by(MerchantMap.confidence.desc()).limit(200).all()
    if not entries:
        return "[]"
    return json.dumps([
        {"pattern": e.pattern, "display": e.display_name, "category": e.category, "source": e.source}
        for e in entries
    ])


def _categorize_batch(
    batch: list[Transaction],
    categories_json: str,
    map_context: str,
    db: Session,
) -> int:
    """Categorize one batch. Returns count of new map entries created."""
    transactions_json = json.dumps([
        {"id": str(tx.id), "description": tx.description, "amount": tx.amount, "type": tx.type}
        for tx in batch
    ])

    # Inject map context into the user prompt so the AI can match against known merchants
    augmented_transactions = (
        f"Known merchant map (use as context for consistent categorization):\n{map_context}\n\n"
        f"Transactions to categorize:\n{transactions_json}"
    )

    try:
        raw = complete(
            categorization_system_prompt(),
            categorization_user_prompt(categories_json, augmented_transactions),
        )
        results = _parse_json_list(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Categorization batch failed: %s", exc)
        return 0

    tx_by_id = {str(tx.id): tx for tx in batch}
    new_entries = 0

    for item in results:
        tx = tx_by_id.get(str(item.get("id")))
        if tx is None:
            continue

        category = item.get("category") or "Uncategorized"
        confidence_str = item.get("confidence")
        confidence = _confidence_to_float(confidence_str) or 0.6

        tx.category = category
        tx.confidence = confidence
        tx.notes = item.get("notes")

        suggested_key = item.get("suggested_key")
        entry = upsert_entry(
            description=tx.description,
            suggested_key=suggested_key,
            category=category,
            confidence=confidence,
            source="ai",
            db=db,
        )
        if entry not in db:
            new_entries += 1

    return new_entries


def categorize(statement_id: int, db: Session) -> dict:
    """Categorize all transactions for a statement using the merchant map + AI.

    Returns {"categorized": int, "map_hits": int, "new_map_entries": int, "warnings": list[str]}
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.statement_id == statement_id, Transaction.category.is_(None))
        .all()
    )

    if not transactions:
        return {"categorized": 0, "map_hits": 0, "new_map_entries": 0, "warnings": []}

    mapped, unmapped = apply_map(transactions, db)
    map_hits = len(mapped)

    categories = db.query(Category).all()
    categories_json = json.dumps([{"name": c.name, "description": c.description} for c in categories])
    map_context = _build_map_context(db)

    new_map_entries = 0
    warnings = []

    if unmapped:
        batches = [unmapped[i:i + BATCH_SIZE] for i in range(0, len(unmapped), BATCH_SIZE)]
        if len(batches) > 1:
            logger.info("Categorizing %d transactions in %d batches", len(unmapped), len(batches))
        for batch in batches:
            new_map_entries += _categorize_batch(batch, categories_json, map_context, db)

    db.commit()

    uncategorized = sum(1 for tx in transactions if tx.category is None)
    if uncategorized:
        warnings.append(f"{uncategorized} transaction(s) could not be categorized")

    return {
        "categorized": len(transactions) - uncategorized,
        "map_hits": map_hits,
        "new_map_entries": new_map_entries,
        "warnings": warnings,
    }
