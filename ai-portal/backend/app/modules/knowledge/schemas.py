"""知识库模块 - 请求/响应模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    category: str = Field(default="通用")


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    model_config = {"from_attributes": True}
    id: int
    name: str
    description: Optional[str]
    category: str
    document_count: int
    created_at: datetime
    updated_at: datetime


class DocumentResponse(BaseModel):
    """文档响应"""
    model_config = {"from_attributes": True}
    id: int
    knowledge_base_id: int
    filename: str
    file_type: str
    chunk_count: int
    file_size: int
    created_at: datetime


class RAGQueryRequest(BaseModel):
    """RAG问答请求"""
    question: str = Field(..., min_length=1, max_length=2000)
    knowledge_base_id: Optional[int] = Field(default=None)
    top_k: int = Field(default=5, ge=1, le=20)


class RAGSource(BaseModel):
    """RAG引用来源"""
    document_id: int
    filename: str
    content: str
    score: float


class RAGQueryResponse(BaseModel):
    """RAG问答响应"""
    answer: str
    sources: list[RAGSource]
    model_used: str
