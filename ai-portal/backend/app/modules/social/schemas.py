"""社交关系模块 - 请求/响应模型"""
from pydantic import BaseModel
from datetime import datetime


class FollowResponse(BaseModel):
    is_following: bool
    followers_count: int
    following_count: int


class FollowerItem(BaseModel):
    user_id: int
    username: str
    nickname: str | None
    avatar_url: str | None
    level: int
    bio: str | None
    is_following_me: bool
    created_at: datetime


class FollowerListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[FollowerItem]


class FollowStatusResponse(BaseModel):
    is_following: bool
    is_followed_by: bool
    is_mutual: bool
    followers_count: int
    following_count: int
