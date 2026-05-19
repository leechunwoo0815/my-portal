"""认证模块 - 请求/响应模型"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=72)
    remember_me: bool = Field(default=False)


class TokenResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str = Field(default="bearer")
    expires_in: int


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., max_length=100)
    new_password: str = Field(..., min_length=6, max_length=100)


class UserResponse(BaseModel):
    """用户信息响应"""
    model_config = {"from_attributes": True}
    id: int
    username: str
    email: str | None
    is_active: bool
    is_admin: bool
    avatar_url: str | None


class RegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class RegisterResponse(BaseModel):
    """注册成功响应"""
    id: int
    username: str
    email: str
    level: int
    message: str = "注册成功，请登录"


class UserProfileResponse(BaseModel):
    """用户详细资料响应"""
    model_config = {"from_attributes": True}
    id: int
    username: str
    email: str | None
    nickname: str | None
    bio: str | None
    avatar_url: str | None
    level: int
    points: int
    total_points: int
    followers_count: int
    following_count: int
    gender: str | None
    location: str | None
    website: str | None
    github: str | None
    is_admin: bool
    is_active: bool
    created_at: datetime
    level_title: str = Field(default="新手上路", description="等级称号")


class ProfileUpdateRequest(BaseModel):
    """个人资料修改请求"""
    nickname: str | None = Field(None, min_length=1, max_length=50)
    bio: str | None = Field(None, min_length=1, max_length=500)
    avatar_url: str | None = Field(None, max_length=255)
    gender: str | None = Field(None, min_length=1, max_length=10)
    location: str | None = Field(None, max_length=100)
    website: str | None = Field(None, max_length=255)
    github: str | None = Field(None, max_length=255)
