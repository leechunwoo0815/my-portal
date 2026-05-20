"""刷新令牌模型 - 用于 refresh_token 的服务端存储和吊销"""
from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: int = Column(Integer, nullable=False, index=True)
    token_hash: str = Column(String(64), unique=True, nullable=False, index=True)
    expires_at: datetime = Column(DateTime(timezone=True), nullable=False)
    revoked: bool = Column(Boolean, default=False, nullable=False, index=True)
    created_at: datetime = Column(DateTime(timezone=True), default=utc_now, nullable=False)
