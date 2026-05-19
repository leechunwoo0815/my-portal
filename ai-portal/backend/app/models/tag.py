from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, DateTime


class Tag(Base):
    __tablename__ = "tags"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(50), unique=True, nullable=False, index=True)
    slug: str = Column(String(50), unique=True, nullable=False, index=True)
    usage_count: int = Column(Integer, default=0, nullable=False)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
