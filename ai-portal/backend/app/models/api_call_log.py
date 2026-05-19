from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, JSON, Index, ForeignKey


class ApiCallLog(Base):
    __tablename__ = "api_call_logs"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int | None = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    provider: str = Column(String(50), nullable=False, index=True)
    model_name: str = Column(String(100), nullable=False, index=True)
    prompt_tokens: int = Column(Integer, default=0, nullable=False)
    completion_tokens: int = Column(Integer, default=0, nullable=False)
    total_tokens: int = Column(Integer, default=0, nullable=False)
    cost: float | None = Column(Float, nullable=True)
    is_success: bool = Column(Boolean, default=True, nullable=False)
    error_message: str | None = Column(Text, nullable=True)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    __table_args__ = (Index("idx_log_provider_created", "provider", "created_at"),)
