from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional
from datetime import datetime

T = TypeVar("T")


class AuthorInfo(BaseModel):
    """作者信息"""
    model_config = {"from_attributes": True}
    id: int
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    level: int = 1


class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[T]

class ContentBase(BaseModel):
    title: str = Field(..., max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str
    content_type: str = Field(default="markdown", pattern="^(markdown|html|richtext)$")
    cover_image: str | None = None
    category: str | None = Field(default=None, max_length=50)
    tags: str | None = None
    is_published: bool = False

class ContentCreate(ContentBase):
    pass

class ContentUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str | None = None
    content_type: str | None = Field(default=None, pattern="^(markdown|html|richtext)$")
    cover_image: str | None = None
    category: str | None = None
    tags: str | None = None
    is_published: bool | None = None
