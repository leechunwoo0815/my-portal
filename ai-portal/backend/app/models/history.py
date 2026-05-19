"""阅读历史模型"""
from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index


class ReadingHistory(Base):
    __tablename__ = "reading_history"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type: str = Column(String(20), nullable=False)  # blog, news, product, solution
    content_id: int = Column(Integer, nullable=False)
    read_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    __table_args__ = (
        Index("ix_history_user_read", "user_id", "read_at"),
    )
