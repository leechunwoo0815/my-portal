from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Notification(Base):
    __tablename__ = "notifications"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: str = Column(String(20), nullable=False)
    title: str = Column(String(200), nullable=False)
    content: str = Column(Text, nullable=True)
    from_user_id: int | None = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    target_type: str | None = Column(String(20), nullable=True)
    target_id: int | None = Column(Integer, nullable=True)
    is_read: bool = Column(Boolean, default=False, nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    user: "User" = relationship("User", foreign_keys=[user_id], back_populates="notifications")
    from_user: "User" = relationship("User", foreign_keys=[from_user_id])
