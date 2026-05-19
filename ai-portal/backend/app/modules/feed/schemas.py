"""动态流 - 响应模型"""
from pydantic import BaseModel
from datetime import datetime


class FeedItem(BaseModel):
    id: int
    content_type: str
    title: str | None
    content: str | None
    summary: str | None
    author_id: int | None = None
    author_name: str | None
    author_avatar: str | None
    author_level: int = 1
    created_at: datetime | None
    likes_count: int = 0
    comments_count: int = 0


class FeedListResponse(BaseModel):
    items: list[FeedItem]
    total: int
    page: int
