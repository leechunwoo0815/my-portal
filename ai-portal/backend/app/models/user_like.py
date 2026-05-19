from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserLike(Base):
    __tablename__ = "user_likes"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_like"),
    )
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type: str = Column(String(20), nullable=False, index=True)
    target_id: int = Column(Integer, nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    user: "User" = relationship("User", back_populates="likes")
