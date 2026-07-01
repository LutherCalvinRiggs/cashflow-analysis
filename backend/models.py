from pydantic import BaseModel


class UploadResponse(BaseModel):
    statement_id: int
    transaction_count: int
    new_map_entries: int
    warnings: list[str]
