from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import Category, Transaction, get_db
from models import CategoryOut, CategoryUpdate, CategoryUpdateResponse, TransactionOut, TransactionPage
from services.merchant_mapper import find_matching_transactions, find_related_entry, upsert_entry

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


@router.patch("/transactions/{transaction_id}/category", response_model=CategoryUpdateResponse)
def update_transaction_category(transaction_id: int, body: CategoryUpdate, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if not db.query(Category).filter(Category.name == body.category).first():
        raise HTTPException(status_code=400, detail=f"Unknown category: {body.category}")

    # Reuse the merchant's existing canonical pattern if one exists, rather than falling
    # back to this single transaction's full normalized description (which usually carries
    # a unique trailing reference number and would fragment the merchant into its own group).
    related = find_related_entry(tx.description, db)
    suggested_key = related.pattern if related else None

    # Persist as a user override — always wins over AI, never downgraded (see upsert_entry)
    entry, _ = upsert_entry(
        description=tx.description,
        suggested_key=suggested_key,
        category=body.category,
        confidence=1.0,
        source="user",
        db=db,
    )

    # Apply retroactively to every transaction this merchant pattern matches,
    # not just the one the user clicked on.
    matches = find_matching_transactions(entry.pattern, db)
    for match in matches:
        match.category = body.category
        match.confidence = 1.0

    db.commit()

    return CategoryUpdateResponse(updated_count=len(matches), category=body.category, pattern=entry.pattern)
