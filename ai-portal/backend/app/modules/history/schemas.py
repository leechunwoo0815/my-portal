"""阅读历史 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class HistoryRecord(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    content_type: str
    content_id: int
    content_title: Optional[str] = None
    read_at: datetime


class HistoryListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[HistoryRecord]
