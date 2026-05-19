from pydantic import BaseModel, Field
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str = Field(max_length=50)
    slug: str = Field(max_length=50)
    module_type: str = Field(max_length=20)
    parent_id: int | None = None
    sort_order: int = 0
    icon: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=50)
    slug: str | None = Field(default=None, max_length=50)
    module_type: str | None = Field(default=None, max_length=20)
    parent_id: int | None = None
    sort_order: int | None = None
    icon: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    module_type: str
    parent_id: int | None = None
    sort_order: int = 0
    icon: str | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class CategoryListResponse(BaseModel):
    total: int = 0
    items: list[CategoryResponse] = []
