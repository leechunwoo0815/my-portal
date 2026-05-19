"""评论模块 - Schema 定义"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    emoji: Optional[str] = Field(default=None, max_length=10)
    parent_id: Optional[int] = Field(default=None)
    author_name: Optional[str] = Field(default=None, max_length=50)  # 仅游客使用


class CommentResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    target_type: str
    target_id: int
    parent_id: Optional[int]
    author_name: str
    content: str
    emoji: Optional[str]
    likes_count: int
    created_at: datetime
    replies: list["CommentResponse"] = []


CommentResponse.model_rebuild()