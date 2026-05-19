from pydantic import BaseModel


class SearchQuery(BaseModel):
    keyword: str
    target_types: list[str] | None = None
    page: int = 1
    page_size: int = 20


class SearchResultItem(BaseModel):
    id: int
    title: str
    summary: str | None = None
    target_type: str
    author_name: str | None = None
    created_at: str | None = None


class SearchResponse(BaseModel):
    total: int = 0
    page: int = 1
    page_size: int = 20
    items: list[SearchResultItem] = []
