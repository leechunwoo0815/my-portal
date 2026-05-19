"""博客模块 - 请求/响应模型，统一继承 ContentBase 体系"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.base import ContentBase, ContentCreate, ContentUpdate, PaginatedResponse, AuthorInfo


class BlogBase(ContentBase):
    """博客基础字段，继承 ContentBase(title, content, content_type, summary, cover_image, category, tags, is_published)"""
    pass


class BlogCreate(ContentCreate):
    """创建博客，继承 ContentCreate"""
    pass


class BlogUpdate(ContentUpdate):
    """更新博客，继承 ContentUpdate"""
    pass


class BlogResponse(BaseModel):
    """博客响应"""
    model_config = {"from_attributes": True}
    id: int
    title: str
    content: str
    content_type: str = "markdown"
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[str] = None
    category: str = "技术"
    is_published: bool = True
    view_count: int = 0
    author_id: Optional[int] = None
    author: Optional[AuthorInfo] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: datetime


class BlogListResponse(PaginatedResponse[BlogResponse]):
    """博客列表响应"""
    pass
