from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship


class Message(Base):
    __tablename__ = "messages"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id: int = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role: str = Column(String(20), nullable=False)
    content: str = Column(Text, nullable=False)
    model_name: str | None = Column(String(100), nullable=True)
    token_count: int | None = Column(Integer, nullable=True)
    thinking: str | None = Column(Text, nullable=True)
    duration: int | None = Column(Integer, nullable=True)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    conversation: "Conversation" = relationship("Conversation", back_populates="messages")

    __table_args__ = (Index("idx_message_conv_created", "conversation_id", "created_at"),)
