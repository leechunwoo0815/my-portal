"""AI工具模块 - 请求/响应模型"""
from typing import Optional, Literal
from pydantic import BaseModel, Field


class PDFSummaryRequest(BaseModel):
    """PDF摘要请求"""
    file_path: str = Field(...)
    max_length: int = Field(default=500, ge=100, le=2000)


class PDFSummaryResponse(BaseModel):
    """PDF摘要响应"""
    summary: str
    page_count: int
    word_count: int


class MdToWordRequest(BaseModel):
    """Markdown转Word请求"""
    markdown: str = Field(..., min_length=1)
    filename: str = Field(default="document.docx", max_length=200)


class CodeExplainRequest(BaseModel):
    """代码解释请求"""
    code: str = Field(..., min_length=1)
    language: Optional[str] = Field(default=None)
    detail_level: Literal["brief", "detailed", "expert"] = Field(default="detailed")


class CodeExplainResponse(BaseModel):
    """代码解释响应"""
    explanation: str
    key_points: list[str]
    suggestions: Optional[list[str]]
