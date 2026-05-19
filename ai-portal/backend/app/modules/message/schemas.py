"""私信模块 - 请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime


class MessageSendRequest(BaseModel):
    receiver_id: int
    content: str = Field(..., min_length=1, max_length=2000)


class MessageItem(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime
    sender_nickname: str | None
    sender_avatar: str | None
    sender_level: int


class ConversationItem(BaseModel):
    user_id: int
    username: str
    nickname: str | None
    avatar_url: str | None
    level: int
    bio: str | None
    last_message: str
    last_message_time: datetime
    unread_count: int
    relationship: str


class ConversationListResponse(BaseModel):
    total: int
    items: list[ConversationItem]
