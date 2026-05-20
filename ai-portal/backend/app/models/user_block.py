"""用户拉黑模型"""
from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint


class UserBlock(Base):
    __tablename__ = "user_blocks"
    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_user_block_pair"),
    )
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    blocker_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    blocked_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
