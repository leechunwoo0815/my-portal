from pydantic import BaseModel


class SearchResultItem(BaseModel):
    id: int
    title: str
    summary: str | None = None
    target_type: str
    author_name: str | None = None
    cover_image: str | None = None
    category: str | None = None
    tags: str | None = None
    likes_count: int = 0
    view_count: int = 0
    created_at: str | None = None


class SearchResponse(BaseModel):
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0
    items: list[SearchResultItem] = []
