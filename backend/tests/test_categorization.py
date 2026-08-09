"""Tests for merchant_mapper and categorizer services."""
import json
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Category, MerchantMap, Transaction
from services.categorizer import BATCH_SIZE, categorize
from services.merchant_mapper import (
    apply_map,
    find_matching_transactions,
    find_related_entry,
    normalize,
    upsert_entry,
)


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
    session.add(Category(name="Internal Transfer", description="Movement between the user's own accounts", color="#444444"))
    session.commit()

    yield session
    session.close()


def _make_transaction(db, description="FOODCELLAR LIC NY", amount=42.50, tx_type="debit", statement_id=1, is_internal_transfer=False):
    tx = Transaction(
        statement_id=statement_id,
        date="2026-06-01",
        description=description,
        amount=amount,
        type=tx_type,
        is_internal_transfer=1 if is_internal_transfer else 0,
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


# ── find_related_entry() / find_matching_transactions() ──────────────────────
#
# Real-world bank descriptions carry unique trailing reference numbers, and the AI's
# suggested_key often drops filler words (e.g. "to"), so plain substring matching between
# a stored pattern and a transaction's normalized description frequently fails even though
# both describe the same merchant. These matchers use word-subset comparison instead.

def test_find_related_entry_matches_despite_filler_word_and_trailing_id(db):
    upsert_entry("Zelle Payment To Jane Doe LLC 90123456789", "zelle payment jane doe", "Childcare", 0.6, "ai", db)
    db.commit()

    entry = find_related_entry("Zelle Payment To Jane Doe LLC 99999999999", db)
    assert entry is not None
    assert entry.pattern == "zelle payment jane doe"


def test_find_related_entry_returns_none_when_no_word_subset_match(db):
    upsert_entry("Zelle Payment To Jane Doe LLC 90123456789", "zelle payment jane doe", "Childcare", 0.6, "ai", db)
    db.commit()

    assert find_related_entry("Whole Foods Market", db) is None


def test_find_matching_transactions_covers_all_reference_number_variants(db):
    _make_transaction(db, description="Zelle Payment To Jane Doe LLC 90123456789")
    _make_transaction(db, description="Zelle Payment To Jane Doe LLC 90223456789")
    _make_transaction(db, description="Whole Foods Market")

    matches = find_matching_transactions("zelle payment jane doe", db)
    assert len(matches) == 2
    assert all("Zelle Payment To Jane Doe LLC" in tx.description for tx in matches)


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


# ── categorize() — internal transfers (deterministic, no AI) ─────────────────

def test_categorize_assigns_internal_transfer_deterministically(db):
    tx = _make_transaction(db, description="Online Transfer To Chk ...1198 Transaction#: 12345678", is_internal_transfer=True)

    with patch("services.categorizer.complete") as mock_ai:
        result = categorize(statement_id=1, db=db)

    mock_ai.assert_not_called()
    assert tx.category == "Internal Transfer"
    assert tx.confidence == 1.0
    assert result["internal_transfers"] == 1
    assert result["categorized"] == 1


def test_categorize_excludes_internal_transfer_from_ai_category_list(db):
    _make_transaction(db, description="UNKNOWN MERCHANT XYZ", is_internal_transfer=False)

    ai_response = json.dumps([{
        "id": "1", "category": "Utilities", "confidence": "medium",
        "notes": None, "suggested_key": "unknown merchant xyz",
    }])

    with patch("services.categorizer.complete", return_value=ai_response) as mock_ai:
        categorize(statement_id=1, db=db)

    sent_system_prompt, sent_user_prompt = mock_ai.call_args[0]
    assert "Internal Transfer" not in sent_user_prompt


def test_categorize_mixed_batch_flagged_and_unflagged(db):
    transfer_tx = _make_transaction(db, description="Online Transfer To Chk ...1198", is_internal_transfer=True)
    other_tx = _make_transaction(db, description="UNKNOWN MERCHANT XYZ", is_internal_transfer=False)

    ai_response = json.dumps([{
        "id": str(other_tx.id), "category": "Utilities", "confidence": "medium",
        "notes": None, "suggested_key": "unknown merchant xyz",
    }])

    with patch("services.categorizer.complete", return_value=ai_response) as mock_ai:
        result = categorize(statement_id=1, db=db)

    db.refresh(transfer_tx)
    db.refresh(other_tx)
    assert transfer_tx.category == "Internal Transfer"
    assert other_tx.category == "Utilities"
    assert result["internal_transfers"] == 1
    assert result["categorized"] == 2
    # Only the non-transfer transaction should ever reach the AI
    _, sent_user_prompt = mock_ai.call_args[0]
    assert str(transfer_tx.id) not in sent_user_prompt
    assert str(other_tx.id) in sent_user_prompt


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
