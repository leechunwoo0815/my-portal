from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship


class Comment(Base):
    __tablename__ = "comments"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    target_type: str = Column(String(20), nullable=False, index=True)
    target_id: int = Column(Integer, nullable=False, index=True)
    parent_id: int | None = Column(Integer, nullable=True, index=True)
    user_id: int | None = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    author_name: str = Column(String(50), nullable=False)
    content: str = Column(Text, nullable=False)
    emoji: str | None = Column(String(10), nullable=True)
    likes_count: int = Column(Integer, default=0, nullable=False)
    liked_ips: str | None = Column(Text, nullable=True)  # Stored as JSON string
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    # 关联到用户表，获取头像和等级
    user = relationship("User", foreign_keys=[user_id], lazy="joined")
