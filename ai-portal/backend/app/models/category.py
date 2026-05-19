from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Category(Base):
    __tablename__ = "categories"
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name: str = Column(String(50), nullable=False)
    slug: str = Column(String(50), unique=True, nullable=False, index=True)
    module_type: str = Column(String(20), nullable=False, index=True)
    parent_id: int | None = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    sort_order: int = Column(Integer, default=0, nullable=False)
    icon: str | None = Column(String(100), nullable=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)
    updated_at: datetime = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    parent = relationship("Category", remote_side=[id], foreign_keys=[parent_id])
