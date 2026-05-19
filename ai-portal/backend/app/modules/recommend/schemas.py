"""推荐模块 - 响应模型"""
from pydantic import BaseModel
from datetime import datetime


class RecommendItem(BaseModel):
    id: int
    title: str
    summary: str | None
    category: str | None
    tags: str | None
    cover_image: str | None
    author_name: str | None
    view_count: int
    likes_count: int
    created_at: datetime | None
    content_type: str
    score: float = 0


class RecommendListResponse(BaseModel):
    items: list[RecommendItem]
    total: int


class TrendingTag(BaseModel):
    name: str
    count: int


class TrendingTagResponse(BaseModel):
    tags: list[TrendingTag]
