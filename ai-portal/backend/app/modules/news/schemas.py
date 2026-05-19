from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.base import ContentBase, ContentCreate, ContentUpdate, PaginatedResponse, AuthorInfo

class NewsBase(ContentBase):
    pass

class NewsCreate(ContentCreate):
    pass

class NewsUpdate(ContentUpdate):
    pass

class NewsInDB(NewsBase):
    id: int
    author_id: int
    author: Optional[AuthorInfo] = None
    published_at: Optional[datetime] = None
    view_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NewsResponse(NewsInDB):
    pass

class NewsListResponse(PaginatedResponse[NewsResponse]):
    pass
