from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PointLog(Base):
    __tablename__ = "point_logs"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: str = Column(String(30), nullable=False)
    points: int = Column(Integer, nullable=False)
    description: str = Column(String(200), nullable=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    user: "User" = relationship("User", back_populates="point_logs")
