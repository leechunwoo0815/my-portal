"""互动模块 - 请求/响应模型"""
from pydantic import BaseModel
from datetime import datetime


class LikeStatusResponse(BaseModel):
    is_liked: bool
    likes_count: int


class FavoriteStatusResponse(BaseModel):
    is_favorited: bool
    favorites_count: int


class FavoriteItem(BaseModel):
    id: int
    target_type: str
    target_id: int
    created_at: datetime
    target_title: str | None = None
    target_cover: str | None = None


class FavoriteListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FavoriteItem]
