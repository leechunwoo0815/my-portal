"""内容举报模型"""
from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey


class Report(Base):
    __tablename__ = "reports"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    reporter_id: int = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    target_type: str = Column(String(20), nullable=False, index=True)  # comment/blog/moment/message
    target_id: int = Column(Integer, nullable=False, index=True)
    reason: str = Column(String(20), nullable=False)  # spam/abuse/illegal/other
    description: str | None = Column(Text, nullable=True)
    status: str = Column(String(20), default="pending", nullable=False, index=True)  # pending/reviewed/dismissed
    admin_note: str | None = Column(Text, nullable=True)
    reviewed_by: int | None = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    reviewed_at: datetime | None = Column(DateTime, nullable=True)
