"""专栏/系列模型"""
from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Series(Base):
    __tablename__ = "series"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title: str = Column(String(200), nullable=False)
    description: str | None = Column(Text, nullable=True)
    cover_image: str | None = Column(String(500), nullable=True)
    author_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    is_public: bool = Column(Boolean, default=True, nullable=False)
    articles_count: int = Column(Integer, default=0, nullable=False)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    author = relationship("User", foreign_keys=[author_id], lazy="joined")


class SeriesArticle(Base):
    __tablename__ = "series_articles"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    series_id: int = Column(Integer, ForeignKey("series.id", ondelete="CASCADE"), nullable=False, index=True)
    blog_id: int = Column(Integer, ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False, index=True)
    order: int = Column(Integer, default=0, nullable=False)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    series = relationship("Series", foreign_keys=[series_id])
    blog = relationship("Blog", foreign_keys=[blog_id], lazy="joined")
