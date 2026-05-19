from datetime import datetime
from app.core.database import Base
from app.models.user import utc_now
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship


class ContentTag(Base):
    __tablename__ = "content_tags"
    __table_args__ = (
        UniqueConstraint("tag_id", "target_type", "target_id", name="uq_content_tag"),
    )
    __allow_unmapped__ = True

    id: int = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tag_id: int = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False, index=True)
    target_type: str = Column(String(20), nullable=False, index=True)
    target_id: int = Column(Integer, nullable=False, index=True)
    created_at: datetime = Column(DateTime, default=utc_now, nullable=False)

    tag = relationship("Tag")
