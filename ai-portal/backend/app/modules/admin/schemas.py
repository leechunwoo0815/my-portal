"""后台管理模块 - 请求/响应模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_conversations: int
    total_messages: int
    total_projects: int
    total_blogs: int
    total_comments: int = 0
    today_api_calls: int
    today_token_usage: int
    total_users: int


class SystemMonitor(BaseModel):
    """系统监控数据"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    timestamp: datetime


class ApiKeyCreate(BaseModel):
    """创建API密钥请求"""
    provider: str = Field(..., min_length=1, max_length=50)
    api_key: str = Field(..., min_length=1, max_length=500)
    base_url: Optional[str] = None
    model_names: Optional[list[str]] = Field(default=None)
    priority: int = Field(default=0, ge=0)


class ApiKeyUpdate(BaseModel):
    """更新API密钥请求"""
    provider: Optional[str] = Field(default=None, max_length=50)
    api_key: Optional[str] = Field(default=None, max_length=500)
    base_url: Optional[str] = None
    model_names: Optional[list[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class ApiKeyResponse(BaseModel):
    """API密钥响应（隐藏真实密钥）"""
    model_config = {"from_attributes": True}
    id: int
    provider: str
    base_url: Optional[str]
    model_names: Optional[list]
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: datetime


class ApiCallLogResponse(BaseModel):
    """API调用日志响应"""
    model_config = {"from_attributes": True}
    id: int
    provider: str
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: Optional[float]
    is_success: bool
    error_message: Optional[str]
    created_at: datetime


class ApiLogListResponse(BaseModel):
    """API日志列表响应"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[ApiCallLogResponse]


class UserAdminItem(BaseModel):
    """管理员用户列表项"""
    model_config = {"from_attributes": True}
    id: int
    username: str
    email: str | None
    nickname: str | None
    avatar_url: str | None
    level: int
    points: int
    total_points: int
    followers_count: int
    following_count: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    comment_count: int = 0


class UserAdminCreate(BaseModel):
    """管理员创建用户"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=100)
    password: str = Field(..., min_length=6, max_length=100)
    nickname: str | None = Field(default=None, max_length=50)
    level: int = Field(default=1, ge=1, le=999)
    is_admin: bool = False


class UserAdminUpdate(BaseModel):
    """管理员修改用户信息"""
    is_active: bool | None = None
    is_admin: bool | None = None
    level: int | None = Field(None, ge=1, le=999)
    points: int | None = Field(None, ge=0)
    nickname: str | None = Field(default=None, max_length=50)
    bio: str | None = Field(default=None, max_length=500)


class UserAdminListResponse(BaseModel):
    """管理员用户列表响应"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[UserAdminItem]
