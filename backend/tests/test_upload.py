import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, Category, Statement, get_db
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


client = TestClient(app)

# Minimal hand-crafted single-page PDF with real, extractable text — avoids
# needing reportlab/img2pdf (not installed) just to produce test fixtures.
MINIMAL_PDF_BYTES = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 200]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj
4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
5 0 obj<</Length 44>>
stream
BT /F1 12 Tf 10 100 Td (hello world) Tj ET
endstream
endobj
xref
0 6
trailer<</Size 6/Root 1 0 R>>
startxref
0
%%EOF"""

EXTRACTION_RESPONSE = json.dumps({
    "institution": "Test Bank",
    "account_last4": "1234",
    "account_type": "checking",
    "period_start": "2026-01-01",
    "transactions": [
        {"date": "2026-01-15", "description": "Test Merchant", "amount": 12.34, "type": "debit", "confidence": "high"},
    ],
    "warnings": [],
})

CATEGORIZATION_RESPONSE = json.dumps([
    {"id": "1", "category": "Groceries", "confidence": "high", "notes": None, "suggested_key": "test merchant"},
])


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
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(engine)
    app.dependency_overrides.pop(get_db, None)


def _upload(filename="statement.pdf"):
    return client.post(
        "/api/upload",
        files={"file": (filename, MINIMAL_PDF_BYTES, "application/pdf")},
    )


@patch("routes.upload.complete", return_value=EXTRACTION_RESPONSE)
@patch("services.categorizer.complete", return_value=CATEGORIZATION_RESPONSE)
def test_upload_succeeds_and_sets_file_hash(mock_categorize_ai, mock_extract_ai):
    resp = _upload()
    assert resp.status_code == 200
    body = resp.json()
    assert body["transaction_count"] == 1

    db = TestSession()
    statement = db.query(Statement).filter(Statement.id == body["statement_id"]).first()
    assert statement.file_hash is not None
    db.close()


@patch("routes.upload.complete", return_value=EXTRACTION_RESPONSE)
@patch("services.categorizer.complete", return_value=CATEGORIZATION_RESPONSE)
def test_upload_rejects_exact_duplicate_file(mock_categorize_ai, mock_extract_ai):
    first = _upload(filename="statement.pdf")
    assert first.status_code == 200

    second = _upload(filename="statement-renamed.pdf")
    assert second.status_code == 409
    assert "already uploaded" in second.json()["detail"]
    # The AI should never be called a second time for a byte-identical duplicate
    assert mock_extract_ai.call_count == 1

    db = TestSession()
    assert db.query(Statement).count() == 1
    db.close()


@patch("routes.upload.complete", return_value=EXTRACTION_RESPONSE)
@patch("services.categorizer.complete", return_value=CATEGORIZATION_RESPONSE)
def test_upload_allows_different_files(mock_categorize_ai, mock_extract_ai):
    first = _upload()
    assert first.status_code == 200

    different_bytes = MINIMAL_PDF_BYTES.replace(b"hello world", b"hello world!")
    second = client.post(
        "/api/upload",
        files={"file": ("statement2.pdf", different_bytes, "application/pdf")},
    )
    assert second.status_code == 200

    db = TestSession()
    assert db.query(Statement).count() == 2
    db.close()
