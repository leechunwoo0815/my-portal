"""博客版本历史模型"""
from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey


class BlogVersion(Base):
    __tablename__ = "blog_versions"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    blog_id: int = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False, index=True)
    version: int = Column(Integer, nullable=False)
    title: str = Column(String(200), nullable=False)
    content: str = Column(Text, nullable=False)
    summary: str | None = Column(Text, nullable=True)
    tags: str | None = Column(String(500), nullable=True)
    category: str | None = Column(String(50), nullable=True)
    editor_id: int | None = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
