"""举报模块 - 请求/响应模型"""
from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    target_type: str = Field(..., pattern="^(comment|blog|moment|message)$")
    target_id: int
    reason: str = Field(..., pattern="^(spam|abuse|illegal|other)$")
    description: str | None = Field(None, max_length=500)
