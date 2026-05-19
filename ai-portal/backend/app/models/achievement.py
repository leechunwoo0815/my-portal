"""成就系统模型"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import utc_now


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    icon = Column(String(50), default="")
    category = Column(String(30), default="content")
    tier = Column(String(20), default="bronze")
    points = Column(Integer, default=0)
    condition_type = Column(String(30), default="count")
    condition_value = Column(Integer, default=1)
    is_secret = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=False, index=True)
    unlocked_at = Column(DateTime, default=utc_now)
    progress = Column(Integer, default=0)

    achievement = relationship("Achievement", back_populates="user_achievements")
