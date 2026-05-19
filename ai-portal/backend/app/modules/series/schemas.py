"""专栏模块 Schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class SeriesCreate(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    is_public: bool = True


class SeriesUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    is_public: Optional[bool] = None


class SeriesArticleAdd(BaseModel):
    blog_id: int
    order: int = 0


class SeriesResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    author_id: int
    is_public: bool = True
    articles_count: int = 0
    created_at: datetime
    updated_at: datetime


class SeriesListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[SeriesResponse]
