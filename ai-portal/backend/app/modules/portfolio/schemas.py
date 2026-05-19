"""作品集模块 - 请求/响应模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.base import AuthorInfo


class ProjectCreate(BaseModel):
    """创建项目请求"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    cover_image: Optional[str] = None
    tech_stack: Optional[list[str]] = Field(default=None)
    category: str = Field(default="AI应用")
    content: str = Field(..., min_length=1)
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    sort_order: int = Field(default=0)
    is_published: bool = Field(default=True)


class ProjectUpdate(BaseModel):
    """更新项目请求"""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    cover_image: Optional[str] = None
    tech_stack: Optional[list[str]] = None
    category: Optional[str] = None
    content: Optional[str] = None
    demo_url: Optional[str] = None
    repo_url: Optional[str] = None
    sort_order: Optional[int] = None
    is_published: Optional[bool] = None


class ProjectResponse(BaseModel):
    """项目响应"""
    model_config = {"from_attributes": True}
    id: int
    title: str
    description: str
    cover_image: Optional[str]
    tech_stack: Optional[list]
    category: str
    content: str
    demo_url: Optional[str]
    repo_url: Optional[str]
    sort_order: int
    is_published: bool
    author_id: Optional[int] = None
    author: Optional[AuthorInfo] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: datetime


class ProjectListResponse(BaseModel):
    """项目列表响应"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[ProjectResponse]
