"""积分模块 - 请求/响应模型"""
from pydantic import BaseModel
from datetime import datetime


class PointLogItem(BaseModel):
    id: int
    action: str
    points: int
    description: str | None
    created_at: datetime


class PointLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[PointLogItem]


class PointProgressResponse(BaseModel):
    level: int
    current_points: int
    total_points: int
    current_threshold: int | None
    next_threshold: int | None
    points_needed: int | None
    progress: int
    level_title: str
