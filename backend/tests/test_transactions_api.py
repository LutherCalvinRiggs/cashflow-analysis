import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, Category, Transaction, get_db
from main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    # Set (and restore) the override per-test rather than at module import time —
    # multiple test files overriding get_db at import time collide, since all
    # test modules are imported before any test runs, and whichever import ran
    # last silently wins for the entire session.
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(engine)
    db = TestSession()
    db.add(Category(name="Groceries", description="Grocery stores", color="#22c55e"))
    db.add(Category(name="Utilities", description="Utilities", color="#3b82f6"))
    db.add(Category(name="Childcare", description="Childcare", color="#a855f7"))
    db.add(Category(name="Internal Transfer", description="Internal transfer", color="#64748b"))
    for i in range(5):
        db.add(Transaction(
            statement_id=1,
            date=f"2026-0{i+1}-15",
            description=f"MERCHANT {i}",
            amount=float(10 * (i + 1)),
            type="debit" if i % 2 == 0 else "credit",
            category="Groceries" if i < 3 else "Utilities",
            is_internal_transfer=1 if i == 4 else 0,
        ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(engine)
    app.dependency_overrides.pop(get_db, None)


client = TestClient(app)


def test_list_transactions_returns_all():
    r = client.get("/api/transactions")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5


def test_filter_by_category():
    r = client.get("/api/transactions?category=Groceries")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 3
    assert all(tx["category"] == "Groceries" for tx in data["items"])


def test_filter_by_type():
    r = client.get("/api/transactions?type=debit")
    assert r.status_code == 200
    assert all(tx["type"] == "debit" for tx in r.json()["items"])


def test_filter_by_date_range():
    r = client.get("/api/transactions?date_from=2026-02-01&date_to=2026-03-31")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert all("2026-02" <= tx["date"][:7] <= "2026-03" for tx in data["items"])


def test_exclude_transfers():
    r = client.get("/api/transactions?exclude_transfers=true")
    assert r.status_code == 200
    assert all(not tx["is_internal_transfer"] for tx in r.json()["items"])


def test_pagination():
    r = client.get("/api/transactions?page=1&page_size=2")
    assert r.status_code == 200
    data = r.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["pages"] == 3


def test_sorted_most_recent_first():
    r = client.get("/api/transactions")
    dates = [tx["date"] for tx in r.json()["items"]]
    assert dates == sorted(dates, reverse=True)


def test_list_categories():
    r = client.get("/api/categories")
    assert r.status_code == 200
    names = [c["name"] for c in r.json()]
    assert "Groceries" in names
    assert "Utilities" in names


def test_update_category_persists_and_returns_pattern():
    r = client.get("/api/transactions?category=Groceries")
    tx_id = r.json()["items"][0]["id"]

    r = client.patch(f"/api/transactions/{tx_id}/category", json={"category": "Utilities"})
    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "Utilities"
    assert body["updated_count"] >= 1

    r = client.get(f"/api/transactions?category=Utilities")
    assert any(tx["id"] == tx_id for tx in r.json()["items"])


def test_update_category_applies_retroactively_to_matching_merchant():
    db = TestSession()
    db.add(Transaction(
        statement_id=1, date="2026-06-01", description="MERCHANT 0",
        amount=25.0, type="debit", category="Groceries",
    ))
    db.commit()
    db.close()

    r = client.get("/api/transactions?category=Groceries")
    target = next(tx for tx in r.json()["items"] if tx["description"] == "MERCHANT 0")

    r = client.patch(f"/api/transactions/{target['id']}/category", json={"category": "Utilities"})
    assert r.status_code == 200
    assert r.json()["updated_count"] == 2  # both "MERCHANT 0" rows

    r = client.get("/api/transactions?category=Utilities")
    merchant_0_rows = [tx for tx in r.json()["items"] if tx["description"] == "MERCHANT 0"]
    assert len(merchant_0_rows) == 2


def test_update_category_reaches_siblings_with_unique_reference_numbers():
    """Regression test: descriptions carry unique trailing reference numbers and the AI's
    suggested_key drops filler words (e.g. "To"), so a naive re-normalize-and-substring-match
    approach only updates the one clicked row. All siblings sharing the merchant must update.
    """
    from database import MerchantMap

    db = TestSession()
    db.add(MerchantMap(
        pattern="zelle payment jane doe", display_name="Zelle Payment To Jane Doe LLC",
        category="Childcare", confidence=0.6, source="ai",
    ))
    db.add(Transaction(
        statement_id=1, date="2026-06-01", description="Zelle Payment To Jane Doe LLC 90123456789",
        amount=125.0, type="debit", category="Childcare", confidence=0.6,
    ))
    db.add(Transaction(
        statement_id=1, date="2026-06-08", description="Zelle Payment To Jane Doe LLC 90223456789",
        amount=125.0, type="debit", category="Childcare", confidence=0.6,
    ))
    db.commit()
    db.close()

    r = client.get("/api/transactions?category=Childcare")
    items = r.json()["items"]
    assert len(items) == 2
    target_id = items[0]["id"]

    r = client.patch(f"/api/transactions/{target_id}/category", json={"category": "Internal Transfer"})
    assert r.status_code == 200
    assert r.json()["updated_count"] == 2
    assert r.json()["pattern"] == "zelle payment jane doe"  # reused, not a new per-transaction pattern

    r = client.get("/api/transactions?category=Internal Transfer")
    assert len(r.json()["items"]) == 2

    r = client.get("/api/transactions?category=Childcare")
    assert len(r.json()["items"]) == 0

    db = TestSession()
    entries = db.query(MerchantMap).filter(MerchantMap.pattern == "zelle payment jane doe").all()
    assert len(entries) == 1  # updated in place, not duplicated
    assert entries[0].category == "Internal Transfer"
    assert entries[0].source == "user"
    db.close()


def test_update_category_unknown_transaction_404():
    r = client.patch("/api/transactions/9999/category", json={"category": "Utilities"})
    assert r.status_code == 404


def test_update_category_unknown_category_400():
    r = client.get("/api/transactions?category=Groceries")
    tx_id = r.json()["items"][0]["id"]
    r = client.patch(f"/api/transactions/{tx_id}/category", json={"category": "Not A Real Category"})
    assert r.status_code == 400
