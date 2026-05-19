from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship


class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(100), nullable=False)
    description: str | None = Column(Text, nullable=True)
    category: str = Column(String(50), default="通用", nullable=False)
    document_count: int = Column(Integer, default=0, nullable=False)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    documents: list["KnowledgeDocument"] = relationship(
        "KnowledgeDocument", back_populates="knowledge_base", cascade="all, delete-orphan"
    )


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    knowledge_base_id: int = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    filename: str = Column(String(255), nullable=False)
    file_type: str = Column(String(20), nullable=False)
    chunk_count: int = Column(Integer, default=0, nullable=False)
    file_size: int = Column(Integer, default=0, nullable=False)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    knowledge_base: "KnowledgeBase" = relationship("KnowledgeBase", back_populates="documents")
