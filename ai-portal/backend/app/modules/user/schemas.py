"""用户主页模块 - 请求/响应模型"""
from pydantic import BaseModel
from datetime import datetime


class UserProfilePublic(BaseModel):
    user_id: int
    username: str
    nickname: str | None
    avatar_url: str | None
    bio: str | None
    level: int
    level_title: str
    points: int
    total_points: int
    followers_count: int
    following_count: int
    friends_count: int
    is_following: bool
    is_followed_by: bool
    is_mutual: bool
    gender: str | None
    location: str | None
    website: str | None
    github: str | None
    created_at: datetime


class UserBlogItem(BaseModel):
    id: int
    title: str
    summary: str | None
    cover_image: str | None
    category: str
    tags: list[str]
    view_count: int
    likes_count: int
    favorites_count: int
    created_at: datetime


class UserBlogList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UserBlogItem]


class UserProjectItem(BaseModel):
    id: int
    title: str
    description: str | None
    cover_image: str | None
    category: str
    tech_stack: list[str]
    likes_count: int
    favorites_count: int
    created_at: datetime


class UserProjectList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UserProjectItem]
