from pydantic import BaseModel, Field
from datetime import datetime


class TagCreate(BaseModel):
    name: str = Field(max_length=50)
    slug: str = Field(max_length=50)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    slug: str | None = Field(default=None, max_length=50)


class TagResponse(BaseModel):
    id: int
    name: str
    slug: str
    usage_count: int = 0
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class TagListResponse(BaseModel):
    total: int = 0
    items: list[TagResponse] = []
