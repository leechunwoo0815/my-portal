"""聊天模块 - 请求/响应模型"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """发送消息请求"""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: Optional[int] = Field(default=None)
    model: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)


class ChatMessageResponse(BaseModel):
    """单条消息响应"""
    model_config = {"from_attributes": True}
    id: int
    role: Literal["user", "assistant", "system"]
    content: str
    model_name: Optional[str]
    token_count: Optional[int]
    thinking: Optional[str] = None
    duration: Optional[int] = None
    created_at: datetime


class ConversationResponse(BaseModel):
    """会话响应"""
    model_config = {"from_attributes": True}
    id: int
    title: str
    model_name: str
    system_prompt: Optional[str]
    is_archived: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None


class ConversationCreateRequest(BaseModel):
    """创建会话请求"""
    title: Optional[str] = Field(default="新会话", max_length=200)
    model: Optional[str] = Field(default=None)
    system_prompt: Optional[str] = Field(default=None)


class ConversationUpdateRequest(BaseModel):
    """更新会话请求"""
    title: Optional[str] = Field(default=None, max_length=200)
    is_archived: Optional[bool] = Field(default=None)


class ModelInfo(BaseModel):
    """模型信息"""
    model_config = {"extra": "allow"}
    id: str
    name: str
    provider: str
    description: Optional[str] = None
