from typing import Optional
from pydantic import BaseModel


class UploadResponse(BaseModel):
    statement_id: int
    transaction_count: int
    warnings: list[str]
