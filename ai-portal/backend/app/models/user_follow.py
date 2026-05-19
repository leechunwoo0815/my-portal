from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserFollow(Base):
    __tablename__ = "user_follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_user_follow_pair"),
    )
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    follower_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    follower_user: "User" = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )
    following_user: "User" = relationship(
        "User", foreign_keys=[following_id], back_populates="followers"
    )
