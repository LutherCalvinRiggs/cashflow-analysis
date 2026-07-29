import json
import re
from datetime import datetime
from pathlib import Path

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Statement(Base):
    __tablename__ = "statements"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    bank_name = Column(String, nullable=True)
    statement_month = Column(String, nullable=True)  # "YYYY-MM"
    account_last4 = Column(String, nullable=True)
    account_type = Column(String, nullable=True)     # "checking" | "savings" | "credit" | "unknown"
    raw_text = Column(Text, nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("statements.id"), nullable=False)
    date = Column(String, nullable=False)          # "YYYY-MM-DD"
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)          # "debit" | "credit"
    is_internal_transfer = Column(Integer, default=0)  # 0/1 boolean
    category = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)


class MonthlyStat(Base):
    __tablename__ = "monthly_stats"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, nullable=False, unique=True)  # "YYYY-MM"
    total_income = Column(Float, default=0.0)
    total_spending = Column(Float, default=0.0)
    net = Column(Float, default=0.0)
    category_breakdown = Column(JSON, nullable=True)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    color = Column(String, nullable=False)


class MerchantMap(Base):
    __tablename__ = "merchant_map"

    id = Column(Integer, primary_key=True, index=True)
    pattern = Column(String, nullable=False, unique=True)   # normalized key, e.g. "foodcellar lic"
    display_name = Column(String, nullable=False)           # original description for display
    category = Column(String, nullable=False)
    confidence = Column(Float, nullable=False, default=0.6)
    source = Column(String, nullable=False, default="ai")   # "ai" | "user"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_categories(db: Session) -> None:
    if db.query(Category).count() > 0:
        return
    categories_file = Path(__file__).parent.parent / "docs" / "CATEGORIES.md"
    raw = categories_file.read_text()
    match = re.search(r"```json\s*(\[.*?\])\s*```", raw, re.DOTALL)
    if not match:
        return
    for item in json.loads(match.group(1)):
        db.add(Category(name=item["name"], description=item["description"], color=item["color"]))
    db.commit()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        _seed_categories(db)
    finally:
        db.close()
