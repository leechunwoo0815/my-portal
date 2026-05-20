"""私信模块 - 请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime


class MessageSendRequest(BaseModel):
    receiver_id: int
    content: str = Field(default="", max_length=2000)
    message_type: str = Field(default="text", pattern="^(text|image)$")
    image_url: str | None = Field(None, max_length=500)


class MessageItem(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    message_type: str = "text"
    image_url: str | None = None
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
