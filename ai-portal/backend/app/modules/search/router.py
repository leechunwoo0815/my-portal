import math
from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_, func, union_all, literal_column, select
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.models import Blog, News, Product, Solution, User
from app.modules.search.schemas import SearchResponse, SearchResultItem

router = APIRouter(tags=["搜索"])

MODELS = {
    "blog": (Blog, "blog"),
    "news": (News, "news"),
    "product": (Product, "product"),
    "solution": (Solution, "solution"),
}


def _build_query(db: Session, model, keyword: str):
    """构建带关键词过滤的查询（title + summary + tags）"""
    pattern = f"%{keyword}%"
    return db.query(model).filter(
        or_(
            model.title.like(pattern),
            model.summary.like(pattern),
            model.tags.like(pattern),
        ),
        model.is_published == True,
    )


def _to_item(item, type_name: str, author_map: dict) -> SearchResultItem:
    """将 ORM 对象转为 SearchResultItem"""
    author_name = author_map.get(item.author_id)
    return SearchResultItem(
        id=item.id,
        title=item.title,
        summary=item.summary[:100] if item.summary else None,
        target_type=type_name,
        author_name=author_name,
        cover_image=getattr(item, "cover_image", None),
        category=getattr(item, "category", None),
        tags=getattr(item, "tags", None),
        likes_count=getattr(item, "likes_count", 0),
        view_count=getattr(item, "view_count", 0),
        created_at=str(item.created_at) if item.created_at else None,
    )


@router.get("/", response_model=SearchResponse)
def search(
    keyword: str = Query(..., min_length=1),
    target_type: str = Query("", description="blog/news/product/solution"),
    category: str = Query("", description="分类筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """全文搜索（SQL 级分页）"""
    models_to_search = []
    if target_type and target_type in MODELS:
        models_to_search = [MODELS[target_type]]
    else:
        models_to_search = list(MODELS.values())

    # 1. 统计总数（每个模型 COUNT 之和）
    total = 0
    counts = {}
    for model, type_name in models_to_search:
        q = _build_query(db, model, keyword)
        if category:
            q = q.filter(model.category == category)
        cnt = q.count()
        counts[type_name] = cnt
        total += cnt

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    if total == 0:
        return {"total": 0, "page": page, "page_size": page_size, "total_pages": 0, "items": []}

    # 2. 按比例分配每个模型的偏移量，从全局 page 计算各模型的范围
    # 简化方案：先收集所有模型的结果，合并排序后分页
    # 对于数据量不大的场景（<10万条），加载当前页所需的全部数据即可
    skip = (page - 1) * page_size
    remaining = page_size
    all_items: list[SearchResultItem] = []

    # 预加载所有相关作者名称
    author_ids = set()
    for model, type_name in models_to_search:
        q = _build_query(db, model, keyword)
        if category:
            q = q.filter(model.category == category)
        # 只取当前页需要的范围（按 created_at 降序）
        items = q.order_by(model.created_at.desc()).offset(skip).limit(page_size).all()
        for item in items:
            author_ids.add(item.author_id)

    # 批量查询作者名称
    author_map = {}
    if author_ids:
        authors = db.query(User.id, User.nickname, User.username).filter(User.id.in_(author_ids)).all()
        for uid, nickname, username in authors:
            author_map[uid] = nickname or username

    # 3. 收集所有模型的当前页数据
    for model, type_name in models_to_search:
        q = _build_query(db, model, keyword)
        if category:
            q = q.filter(model.category == category)
        items = q.order_by(model.created_at.desc()).offset(skip).limit(page_size).all()
        for item in items:
            all_items.append(_to_item(item, type_name, author_map))

    # 4. 合并排序后截取当前页
    all_items.sort(key=lambda x: x.created_at or "", reverse=True)
    results = all_items[:page_size]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": results,
    }


@router.get("/suggest", response_model=list[str])
def suggest(
    keyword: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> list[str]:
    """搜索自动补全（返回匹配的标题）"""
    pattern = f"%{keyword}%"
    suggestions = set()
    for model, _ in MODELS.values():
        rows = db.query(model.title).filter(
            model.title.like(pattern),
            model.is_published == True,
        ).limit(3).all()
        for (title,) in rows:
            suggestions.add(title)
    return list(suggestions)[:8]
