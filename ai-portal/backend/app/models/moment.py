from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Moment(Base):
    __tablename__ = "moments"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: str = Column(Text, nullable=False)
    images: list | None = Column(JSON, nullable=True, default=list)
    moment_type: str = Column(String(20), default="original", nullable=False)
    original_id: int | None = Column(Integer, ForeignKey("moments.id", ondelete="CASCADE"), nullable=True)
    likes_count: int = Column(Integer, default=0, nullable=False)
    shares_count: int = Column(Integer, default=0, nullable=False)
    comments_count: int = Column(Integer, default=0, nullable=False)
    is_public: bool = Column(Boolean, default=True, nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    author: "User" = relationship("User", back_populates="moments")
    original: "Moment" = relationship("Moment", remote_side=[id], foreign_keys=[original_id])
