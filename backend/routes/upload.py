import json
import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database import Statement, Transaction, get_db
from models import UploadResponse
from services.ai_client import complete
from services.categorizer import categorize
from services.pdf_extractor import extract_text
from services.prompt_loader import extraction_system_prompt, extraction_user_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["upload"])


def _parse_ai_response(raw: str) -> dict:
    """Extract JSON from the AI response, tolerating markdown code fences."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


def _confidence_to_float(value: str | None) -> float | None:
    mapping = {"high": 1.0, "medium": 0.6, "low": 0.3}
    if value is None:
        return None
    return mapping.get(str(value).lower())


@router.post("/upload", response_model=UploadResponse)
async def upload_statement(file: UploadFile, db: Session = Depends(get_db)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        if not (file.filename or "").lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    raw_bytes = await file.read()

    import io
    extraction = extract_text(io.BytesIO(raw_bytes))
    if not extraction.get("full_text"):
        error = extraction.get("error", "No text could be extracted from the PDF")
        raise HTTPException(status_code=422, detail=error)

    full_text = extraction["full_text"]

    try:
        ai_raw = complete(extraction_system_prompt(), extraction_user_prompt(full_text))
        ai_data = _parse_ai_response(ai_raw)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("AI extraction failed: %s", exc)
        raise HTTPException(status_code=502, detail=f"AI extraction returned invalid JSON: {exc}")

    # Derive statement_month from period_start or first transaction date
    statement_month = None
    period_start = ai_data.get("period_start")
    if period_start and len(period_start) >= 7:
        statement_month = period_start[:7]
    elif ai_data.get("transactions"):
        first_date = ai_data["transactions"][0].get("date", "")
        if len(first_date) >= 7:
            statement_month = first_date[:7]

    statement = Statement(
        filename=file.filename or "upload.pdf",
        bank_name=ai_data.get("institution"),
        statement_month=statement_month,
        account_last4=ai_data.get("account_last4"),
        account_type=ai_data.get("account_type"),
        raw_text=full_text,
    )
    db.add(statement)
    db.flush()  # get statement.id before committing

    transactions = ai_data.get("transactions") or []
    for tx in transactions:
        db.add(Transaction(
            statement_id=statement.id,
            date=tx.get("date", ""),
            description=tx.get("description", ""),
            amount=float(tx.get("amount") or 0),
            type=tx.get("type", "debit"),
            is_internal_transfer=1 if tx.get("is_internal_transfer") else 0,
            confidence=_confidence_to_float(tx.get("confidence")),
        ))

    db.commit()

    cat_result = categorize(statement.id, db)

    warnings = (ai_data.get("warnings") or []) + cat_result["warnings"]
    return UploadResponse(
        statement_id=statement.id,
        transaction_count=len(transactions),
        new_map_entries=cat_result["new_map_entries"],
        warnings=warnings,
    )
