"""审计日志模型 - 记录管理员操作"""
from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    admin_id: int = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: str = Column(String(50), nullable=False)  # delete_comment, hide_comment, ban_user, etc.
    target_type: str = Column(String(50), nullable=False)  # comment, blog, user, etc.
    target_id: int = Column(Integer, nullable=True)
    detail: str | None = Column(Text, nullable=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
