"""成就模块 - 请求/响应模型"""
from pydantic import BaseModel
from datetime import datetime


class AchievementResponse(BaseModel):
    id: int
    code: str
    name: str
    description: str | None
    icon: str | None
    category: str
    tier: str
    points: int
    condition_type: str
    condition_value: int
    is_secret: bool
    is_unlocked: bool = False
    progress: int = 0
    unlocked_at: datetime | None

    class Config:
        from_attributes = True


class AchievementListResponse(BaseModel):
    total: int
    items: list[AchievementResponse]
    unlocked_count: int
    total_points: int
