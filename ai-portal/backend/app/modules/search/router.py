from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models import Blog, News, Product, Solution
from app.modules.search.schemas import SearchResponse, SearchResultItem

router = APIRouter(tags=["搜索"])


@router.get("/", response_model=SearchResponse)
def search(
    keyword: str = Query(..., min_length=1),
    target_type: str = Query("", description="blog/news/product/solution"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    results: list[SearchResultItem] = []
    total = 0
    skip = (page - 1) * page_size

    model_map = {
        "blog": (Blog, "blog"),
        "news": (News, "news"),
        "product": (Product, "product"),
        "solution": (Solution, "solution"),
    }

    search_models = []
    if target_type and target_type in model_map:
        search_models = [model_map[target_type]]
    else:
        search_models = list(model_map.values())

    all_items = []
    for model, type_name in search_models:
        query = db.query(model).filter(
            or_(
                model.title.contains(keyword),
                model.summary.contains(keyword),
            ),
            model.is_published == True,
        )
        for item in query.all():
            author_name = None
            if hasattr(item, "author") and item.author:
                author_name = item.author.nickname or item.author.username
            all_items.append(SearchResultItem(
                id=item.id,
                title=item.title,
                summary=item.summary[:100] if item.summary else None,
                target_type=type_name,
                author_name=author_name,
                created_at=str(item.created_at) if item.created_at else None,
            ))

    total = len(all_items)
    results = all_items[skip:skip + page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": results,
    }
