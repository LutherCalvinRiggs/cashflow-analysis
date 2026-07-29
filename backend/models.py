from pydantic import BaseModel


class UploadResponse(BaseModel):
    statement_id: int
    transaction_count: int
    new_map_entries: int
    warnings: list[str]


class TransactionOut(BaseModel):
    id: int
    statement_id: int
    date: str
    description: str
    amount: float
    type: str
    category: str | None
    confidence: float | None
    notes: str | None
    is_internal_transfer: bool

    class Config:
        from_attributes = True


class TransactionPage(BaseModel):
    items: list[TransactionOut]
    total: int
    page: int
    page_size: int
    pages: int


class CategoryOut(BaseModel):
    id: int
    name: str
    description: str
    color: str

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    category: str


class CategoryUpdateResponse(BaseModel):
    updated_count: int
    category: str
    pattern: str
