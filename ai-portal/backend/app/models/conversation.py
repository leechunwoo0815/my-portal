from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship


class Conversation(Base):
    __tablename__ = "conversations"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title: str = Column(String(200), default="新会话", nullable=False)
    model_name: str = Column(String(100), nullable=False)
    system_prompt: str | None = Column(Text, nullable=True)
    is_archived: bool = Column(Boolean, default=False, nullable=False)
    is_pinned: bool = Column(Boolean, default=False, nullable=False)
    user_id: int | None = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user: "User | None" = relationship("User", back_populates="conversations")
    messages: list["Message"] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
