"""签到模型"""
from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey
from app.core.database import Base
from app.models.user import utc_now


class CheckinRecord(Base):
    __tablename__ = "checkin_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    checkin_date = Column(Date, nullable=False)
    continuous_days = Column(Integer, default=1)
    points_awarded = Column(Integer, default=5)
    created_at = Column(DateTime, default=utc_now)
