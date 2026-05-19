"""动态模块 - 请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime


class MomentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="动态内容")
    images: list[str] | None = Field(default_factory=list, description="图片URL列表")
    is_public: bool = Field(default=True, description="是否公开")


class MomentUpdate(BaseModel):
    content: str | None = Field(None, min_length=1, max_length=1000)
    images: list[str] | None = None
    is_public: bool | None = None


class MomentAuthor(BaseModel):
    user_id: int
    username: str
    nickname: str | None
    avatar_url: str | None
    level: int
    level_title: str


class MomentItem(BaseModel):
    id: int
    user_id: int
    content: str
    images: list[str]
    moment_type: str
    original_id: int | None
    likes_count: int
    comments_count: int
    is_public: bool
    is_liked: bool
    is_favorited: bool
    created_at: datetime
    author: MomentAuthor
    original: "MomentItem | None" = None


class MomentListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[MomentItem]


class RepostRequest(BaseModel):
    content: str = Field(default="", max_length=500, description="转发时的评论")


MomentItem.model_rebuild()
