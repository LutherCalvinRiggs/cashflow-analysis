from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import Category, Transaction, get_db
from models import CategoryCreate, CategoryOut, CategoryUpdate, CategoryUpdateResponse, TransactionOut, TransactionPage
from services.merchant_mapper import find_matching_transactions, find_related_entry, upsert_entry

router = APIRouter(prefix="/api", tags=["transactions"])

# Rotated through for user-created categories so they don't all render identically gray.
_NEW_CATEGORY_COLORS = [
    "#f59e0b", "#ec4899", "#06b6d4", "#ef4444", "#14b8a6",
    "#6366f1", "#84cc16", "#f97316", "#f43f5e", "#8b5cf6",
]


@router.get("/transactions", response_model=TransactionPage)
def list_transactions(
    category: str | None = Query(None),
    type: str | None = Query(None, pattern="^(debit|credit)$"),
    date_from: str | None = Query(None, description="YYYY-MM-DD"),
    date_to: str | None = Query(None, description="YYYY-MM-DD"),
    year: str | None = Query(None, pattern="^\\d{4}$"),
    month: str | None = Query(None, pattern="^\\d{2}$"),
    statement_id: int | None = Query(None),
    exclude_transfers: bool = Query(False),
    sort: str = Query("desc", pattern="^(asc|desc)$"),
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
    if year and month:
        q = q.filter(Transaction.date.like(f"{year}-{month}-%"))
    elif year:
        q = q.filter(Transaction.date.like(f"{year}-%"))
    if statement_id:
        q = q.filter(Transaction.statement_id == statement_id)
    if exclude_transfers:
        q = q.filter(Transaction.is_internal_transfer == 0)

    total = q.count()
    order = (Transaction.date.asc(), Transaction.id.asc()) if sort == "asc" else (Transaction.date.desc(), Transaction.id.desc())
    items = (
        q.order_by(*order)
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


@router.get("/transactions/periods", response_model=list[str])
def list_transaction_periods(db: Session = Depends(get_db)):
    """Distinct YYYY-MM periods with at least one transaction, most recent first.

    Used to populate the ledger's year/month filters with only real options.
    """
    dates = [d for (d,) in db.query(Transaction.date).distinct().all() if d and len(d) >= 7]
    return sorted({d[:7] for d in dates}, reverse=True)


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()


@router.post("/categories", response_model=CategoryOut)
def create_category(body: CategoryCreate, db: Session = Depends(get_db)):
    """Create a category, or return the existing one if the name's already taken.

    Idempotent by design — this backs an inline "create a category" input embedded
    in the transaction category-edit flow, where "create X" should just succeed
    and be usable immediately whether or not X already exists, not force the
    caller to handle a 409.
    """
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Category name cannot be empty")

    existing = db.query(Category).filter(Category.name == name).first()
    if existing:
        return existing

    color = _NEW_CATEGORY_COLORS[db.query(Category).count() % len(_NEW_CATEGORY_COLORS)]
    category = Category(name=name, description=f"User-created category: {name}", color=color)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


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
