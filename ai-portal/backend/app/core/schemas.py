from datetime import datetime
from pydantic import BaseModel, Field


class ContentBase(BaseModel):
    title: str = Field(max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str
    content_type: str = Field(default="markdown", max_length=20)
    cover_image: str | None = Field(default=None, max_length=500)
    category: str = Field(default="技术", max_length=50)
    category_id: int | None = None
    is_original: bool = True
    source_url: str | None = None
    is_published: bool = True
    status: str = Field(default="published", pattern="^(draft|published|archived)$")


class ContentCreate(ContentBase):
    pass


class ContentUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    summary: str | None = None
    content: str | None = None
    content_type: str | None = None
    cover_image: str | None = None
    category: str | None = None
    category_id: int | None = None
    is_original: bool | None = None
    source_url: str | None = None
    is_published: bool | None = None
    status: str | None = Field(default=None, pattern="^(draft|published|archived)$")
    edit_version: int | None = None


class UserBrief(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    avatar_url: str | None = None
    level: int = 1

    model_config = {"from_attributes": True}


class ContentResponse(BaseModel):
    id: int
    title: str
    slug: str | None = None
    summary: str | None = None
    content: str
    content_type: str = "markdown"
    cover_image: str | None = None
    category: str | None = None
    category_id: int | None = None
    is_published: bool = True
    status: str = "published"
    is_top: bool = False
    is_original: bool = True
    source_url: str | None = None
    edit_version: int = 1
    author_id: int | None = None
    author: UserBrief | None = None
    view_count: int = 0
    likes_count: int = 0
    favorites_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    published_at: datetime | None = None

    model_config = {"from_attributes": True}


class ContentListResponse(BaseModel):
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    items: list[ContentResponse] = []
