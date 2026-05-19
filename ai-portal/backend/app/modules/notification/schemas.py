"""通知模块 - 请求/响应模型"""
from pydantic import BaseModel
from datetime import datetime


class NotificationItem(BaseModel):
    id: int
    type: str
    title: str
    content: str | None
    from_user_id: int | None
    from_username: str | None
    from_nickname: str | None
    from_avatar: str | None
    from_level: int
    target_type: str | None
    target_id: int | None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    unread_count: int
    items: list[NotificationItem]
