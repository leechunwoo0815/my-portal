from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username: str = Column(String(50), unique=True, nullable=False, index=True)
    slug: str | None = Column(String(50), unique=True, nullable=True, index=True)
    email: str = Column(String(100), unique=True, nullable=True)
    hashed_password: str = Column(String(255), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_admin: bool = Column(Boolean, default=False, nullable=False)
    role: str = Column(String(20), default="user", nullable=False)
    status: str = Column(String(20), default="active", nullable=False)
    avatar_url: str | None = Column(String(255), nullable=True)
    nickname: str | None = Column(String(50), nullable=True)
    bio: str | None = Column(String(500), nullable=True)
    level: int = Column(Integer, default=1, nullable=False)
    points: int = Column(Integer, default=0, nullable=False)
    total_points: int = Column(Integer, default=0, nullable=False)
    blog_count: int = Column(Integer, default=0, nullable=False)
    like_count: int = Column(Integer, default=0, nullable=False)
    followers_count: int = Column(Integer, default=0, nullable=False)
    following_count: int = Column(Integer, default=0, nullable=False)
    gender: str | None = Column(String(10), nullable=True)
    location: str | None = Column(String(100), nullable=True)
    website: str | None = Column(String(255), nullable=True)
    github: str | None = Column(String(255), nullable=True)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    conversations: list["Conversation"] = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    followers: list["UserFollow"] = relationship(
        "UserFollow", foreign_keys="UserFollow.following_id", back_populates="following_user", cascade="all, delete-orphan"
    )
    following: list["UserFollow"] = relationship(
        "UserFollow", foreign_keys="UserFollow.follower_id", back_populates="follower_user", cascade="all, delete-orphan"
    )
    notifications: list["Notification"] = relationship(
        "Notification", foreign_keys="Notification.user_id", back_populates="user", cascade="all, delete-orphan"
    )
    likes: list["UserLike"] = relationship("UserLike", back_populates="user", cascade="all, delete-orphan")
    favorites: list["UserFavorite"] = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    moments: list["Moment"] = relationship("Moment", back_populates="author", cascade="all, delete-orphan")
    point_logs: list["PointLog"] = relationship("PointLog", back_populates="user", cascade="all, delete-orphan")
