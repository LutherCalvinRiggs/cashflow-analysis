from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import Category, Transaction, get_db
from models import CategoryOut, TransactionOut, TransactionPage

router = APIRouter(prefix="/api", tags=["transactions"])


@router.get("/transactions", response_model=TransactionPage)
def list_transactions(
    category: str | None = Query(None),
    type: str | None = Query(None, pattern="^(debit|credit)$"),
    date_from: str | None = Query(None, description="YYYY-MM-DD"),
    date_to: str | None = Query(None, description="YYYY-MM-DD"),
    statement_id: int | None = Query(None),
    exclude_transfers: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(Transaction)

    if category:
        q = q.filter(Transaction.category == category)
    if type:
        q = q.filter(Transaction.type == type)
    if date_from:
        q = q.filter(Transaction.date >= date_from)
    if date_to:
        q = q.filter(Transaction.date <= date_to)
    if statement_id:
        q = q.filter(Transaction.statement_id == statement_id)
    if exclude_transfers:
        q = q.filter(Transaction.is_internal_transfer == 0)

    total = q.count()
    items = (
        q.order_by(Transaction.date.desc(), Transaction.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    pages = max(1, (total + page_size - 1) // page_size)

    return TransactionPage(
        items=[
            TransactionOut(
                **{c.key: getattr(tx, c.key) for c in Transaction.__table__.columns
                   if c.key != "is_internal_transfer"},
                is_internal_transfer=bool(tx.is_internal_transfer),
            )
            for tx in items
        ],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()
