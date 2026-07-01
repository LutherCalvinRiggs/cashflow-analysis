"""Tests for merchant_mapper and categorizer services."""
import json
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Category, MerchantMap, Transaction
from services.categorizer import BATCH_SIZE, categorize
from services.merchant_mapper import apply_map, normalize, upsert_entry


# ── In-memory DB fixture ───────────────────────────────────────────────────────

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed one category
    session.add(Category(name="Groceries", description="Supermarkets and grocery stores", color="#22c55e"))
    session.add(Category(name="Utilities", description="Electric, gas, water, internet", color="#3b82f6"))
    session.commit()

    yield session
    session.close()


def _make_transaction(db, description="FOODCELLAR LIC NY", amount=42.50, tx_type="debit", statement_id=1):
    tx = Transaction(
        statement_id=statement_id,
        date="2026-06-01",
        description=description,
        amount=amount,
        type=tx_type,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


# ── normalize() ───────────────────────────────────────────────────────────────

def test_normalize_strips_leading_digits():
    assert normalize("1284825 FoodCellar LIC") == "foodcellar lic"


def test_normalize_strips_hash_prefix():
    assert normalize("#0042 NETFLIX.COM") == "netflix com"


def test_normalize_lowercases():
    assert normalize("WHOLE FOODS MARKET") == "whole foods market"


def test_normalize_collapses_whitespace():
    assert normalize("  CON   EDISON  ") == "con edison"


# ── apply_map() ───────────────────────────────────────────────────────────────

def test_apply_map_hit(db):
    db.add(MerchantMap(pattern="foodcellar lic", display_name="FoodCellar LIC", category="Groceries", confidence=1.0, source="user"))
    db.commit()

    tx = _make_transaction(db, description="1284825 FoodCellar LIC NY")
    mapped, unmapped = apply_map([tx], db)

    assert len(mapped) == 1
    assert len(unmapped) == 0
    assert mapped[0].category == "Groceries"
    assert mapped[0].confidence == 1.0


def test_apply_map_miss(db):
    tx = _make_transaction(db, description="UNKNOWN MERCHANT 999")
    mapped, unmapped = apply_map([tx], db)

    assert len(mapped) == 0
    assert len(unmapped) == 1
    assert unmapped[0].category is None


# ── upsert_entry() ────────────────────────────────────────────────────────────

def test_upsert_creates_new_entry(db):
    entry = upsert_entry("FoodCellar LIC", "foodcellar lic", "Groceries", 0.6, "ai", db)
    db.commit()

    stored = db.query(MerchantMap).filter(MerchantMap.pattern == "foodcellar lic").first()
    assert stored is not None
    assert stored.category == "Groceries"
    assert stored.source == "ai"


def test_upsert_user_overrides_ai(db):
    upsert_entry("FoodCellar LIC", "foodcellar lic", "Groceries", 0.6, "ai", db)
    db.commit()
    upsert_entry("FoodCellar LIC", "foodcellar lic", "Dining Out", 1.0, "user", db)
    db.commit()

    stored = db.query(MerchantMap).filter(MerchantMap.pattern == "foodcellar lic").first()
    assert stored.category == "Dining Out"
    assert stored.confidence == 1.0
    assert stored.source == "user"


def test_upsert_ai_does_not_downgrade_user(db):
    upsert_entry("FoodCellar LIC", "foodcellar lic", "Groceries", 1.0, "user", db)
    db.commit()
    upsert_entry("FoodCellar LIC", "foodcellar lic", "Dining Out", 0.3, "ai", db)
    db.commit()

    stored = db.query(MerchantMap).filter(MerchantMap.pattern == "foodcellar lic").first()
    assert stored.category == "Groceries"
    assert stored.source == "user"


# ── categorize() — map hit path (no AI call) ──────────────────────────────────

def test_categorize_uses_map_skips_ai(db):
    db.add(MerchantMap(pattern="foodcellar lic", display_name="FoodCellar LIC", category="Groceries", confidence=1.0, source="user"))
    db.commit()

    tx = _make_transaction(db, description="1284825 FoodCellar LIC NY")

    with patch("services.categorizer.complete") as mock_ai:
        result = categorize(statement_id=1, db=db)

    mock_ai.assert_not_called()
    assert result["map_hits"] == 1
    assert tx.category == "Groceries"


# ── categorize() — AI path ────────────────────────────────────────────────────

def test_categorize_calls_ai_for_unmapped(db):
    tx = _make_transaction(db, description="UNKNOWN MERCHANT XYZ")

    ai_response = json.dumps([{
        "id": str(tx.id),
        "category": "Utilities",
        "confidence": "medium",
        "notes": "Could not determine exact merchant",
        "suggested_key": "unknown merchant xyz",
    }])

    with patch("services.categorizer.complete", return_value=ai_response):
        result = categorize(statement_id=1, db=db)

    db.refresh(tx)
    assert tx.category == "Utilities"
    assert tx.confidence == 0.6
    assert result["new_map_entries"] >= 0


def test_categorize_batches_large_statement(db):
    count = BATCH_SIZE + 5
    for i in range(count):
        _make_transaction(db, description=f"MERCHANT {i:03d}", statement_id=2)

    ai_response_factory = lambda batch_txs: json.dumps([
        {"id": str(tx.id), "category": "Groceries", "confidence": "high",
         "notes": None, "suggested_key": f"merchant {tx.description[-3:].lower()}"}
        for tx in batch_txs
    ])

    call_count = 0
    def fake_complete(system, user):
        nonlocal call_count
        call_count += 1
        # Transactions JSON is after the last "Transactions to categorize:\n"
        # and before the "\n\nReturn" schema example that the template appends.
        tx_section = user.split("Transactions to categorize:\n")[-1].split("\n\nReturn")[0]
        items = json.loads(tx_section)
        return json.dumps([
            {"id": item["id"], "category": "Groceries", "confidence": "high",
             "notes": None, "suggested_key": "merchant"}
            for item in items
        ])

    with patch("services.categorizer.complete", side_effect=fake_complete):
        result = categorize(statement_id=2, db=db)

    assert call_count == 2  # ceil(45 / 40) = 2 batches
    assert result["categorized"] == count
