from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Text, DateTime


class SystemConfig(Base):
    __tablename__ = "system_configs"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key: str = Column(String(100), unique=True, nullable=False, index=True)
    value: str = Column(Text, nullable=False)
    description: str | None = Column(String(255), nullable=True)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
