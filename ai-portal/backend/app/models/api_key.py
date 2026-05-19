from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON


class ApiKey(Base):
    __tablename__ = "api_keys"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    provider: str = Column(String(50), nullable=False, index=True)
    api_key_encrypted: str = Column(String(500), nullable=False)
    base_url: str | None = Column(String(500), nullable=True)
    model_names: list | None = Column(JSON, nullable=True, default=list)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    priority: int = Column(Integer, default=0, nullable=False)
    extra_data: dict | None = Column(JSON, nullable=True, default=dict)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
