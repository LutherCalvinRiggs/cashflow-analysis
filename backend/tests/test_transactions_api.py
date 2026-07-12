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


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(engine)
    db = TestSession()
    db.add(Category(name="Groceries", description="Grocery stores", color="#22c55e"))
    db.add(Category(name="Utilities", description="Utilities", color="#3b82f6"))
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
