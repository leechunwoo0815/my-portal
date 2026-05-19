from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship


class Project(Base):
    __tablename__ = "projects"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title: str = Column(String(200), nullable=False)
    description: str = Column(Text, nullable=False)
    cover_image: str | None = Column(String(500), nullable=True)
    tech_stack: list | None = Column(JSON, nullable=True, default=list)
    category: str = Column(String(50), default="AI应用", nullable=False)
    content: str = Column(Text, nullable=False, default="")
    demo_url: str | None = Column(String(500), nullable=True)
    repo_url: str | None = Column(String(500), nullable=True)
    sort_order: int = Column(Integer, default=0, nullable=False)
    is_published: bool = Column(Boolean, default=True, nullable=False)
    author_id: int | None = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    likes_count: int = Column(Integer, default=0, nullable=False)
    shares_count: int = Column(Integer, default=0, nullable=False)
    favorites_count: int = Column(Integer, default=0, nullable=False)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    author = relationship("User", foreign_keys=[author_id], lazy="joined")
