from datetime import datetime, timezone
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship


class Solution(Base):
    __tablename__ = "solutions"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title: str = Column(String(200), nullable=False)
    slug: str | None = Column(String(200), unique=True, nullable=True, index=True)
    summary: str | None = Column(String(500), nullable=True)
    content: str = Column(Text, nullable=False)
    content_type: str = Column(String(20), default="markdown", nullable=False)
    cover_image: str | None = Column(String(500), nullable=True)
    category: str | None = Column(String(50), nullable=True)
    category_id: int | None = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    tags: str | None = Column(String(500), nullable=True)
    is_published: bool = Column(Boolean, default=False, nullable=False)
    status: str = Column(String(20), default="published", nullable=False, index=True)
    is_top: bool = Column(Boolean, default=False, nullable=False)
    is_original: bool = Column(Boolean, default=True, nullable=False)
    source_url: str | None = Column(String(500), nullable=True)
    edit_version: int = Column(Integer, default=1, nullable=False)
    view_count: int = Column(Integer, default=0, nullable=False)
    shares_count: int = Column(Integer, default=0, nullable=False)
    comments_count: int = Column(Integer, default=0, nullable=False)
    author_id: int | None = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    published_at: datetime | None = Column(DateTime, nullable=True)

    author = relationship("User", foreign_keys=[author_id], lazy="joined")
