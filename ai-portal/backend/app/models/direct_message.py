from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DirectMessage(Base):
    __tablename__ = "direct_messages"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content: str = Column(Text, nullable=False, default="")
    message_type: str = Column(String(20), default="text", nullable=False)
    image_url: str | None = Column(String(500), nullable=True)
    is_read: bool = Column(Boolean, default=False, nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    sender: "User" = relationship("User", foreign_keys=[sender_id])
    receiver: "User" = relationship("User", foreign_keys=[receiver_id])
