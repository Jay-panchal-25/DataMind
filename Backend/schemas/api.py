from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    type: str
    content: Any


class UploadResponse(BaseModel):
    session_id: str
    message: str
    columns: list[str]
    rows: int
    stats: Any
    insights: Any
    summary: str
    report: Any
    quality: Any


class DatasetResponse(BaseModel):
    page: int
    total_pages: int
    columns: list[str]
    data: list[dict[str, Any]]
    stats: Any = None
    report: Any = None
    quality: Any = None
