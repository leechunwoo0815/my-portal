"""推荐API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_optional_current_user
from app.models import User, Blog, News, Product, Solution
from app.modules.recommend.schemas import (
    RecommendItem,
    RecommendListResponse,
    TrendingTag,
    TrendingTagResponse,
)

router = APIRouter(tags=["推荐"])


def _calculate_score(item, user=None):
    score = 0
    score += (item.view_count or 0) * 0.1
    score += (getattr(item, 'likes_count', 0) or 0) * 2.0
    score += (getattr(item, 'favorites_count', 0) or 0) * 3.0
    score += (getattr(item, 'comments_count', 0) or 0) * 1.5
    from datetime import datetime, timedelta
    if hasattr(item, 'created_at') and item.created_at:
        hours = (datetime.utcnow() - item.created_at).total_seconds() / 3600
        if hours < 24:
            score += 5 * (1 - hours / 24)
    return round(score, 2)


def _item_to_recommend(item, content_type, score=0):
    author_name = None
    if hasattr(item, 'author') and item.author:
        author_name = item.author.nickname or item.author.username
    return RecommendItem(
        id=item.id,
        title=item.title,
        summary=getattr(item, 'summary', None) or (item.content[:100] if item.content else None),
        category=getattr(item, 'category', None),
        tags=getattr(item, 'tags', None),
        cover_image=getattr(item, 'cover_image', None),
        author_name=author_name,
        view_count=item.view_count or 0,
        likes_count=getattr(item, 'likes_count', 0) or 0,
        created_at=item.created_at,
        content_type=content_type,
        score=score,
    )


@router.get("/feed", response_model=RecommendListResponse)
def get_recommend_feed(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    items = []
    blogs = db.query(Blog).filter(Blog.is_published == True).all()
    for b in blogs:
        score = _calculate_score(b, current_user)
        items.append((_item_to_recommend(b, "blog", score), score))
    news = db.query(News).filter(News.is_published == True).all()
    for n in news:
        score = _calculate_score(n, current_user)
        items.append((_item_to_recommend(n, "news", score), score))
    products = db.query(Product).filter(Product.is_published == True).all()
    for p in products:
        score = _calculate_score(p, current_user)
        items.append((_item_to_recommend(p, "product", score), score))
    items.sort(key=lambda x: x[1], reverse=True)
    start = (page - 1) * page_size
    paged = items[start:start + page_size]
    return RecommendListResponse(items=[i[0] for i in paged], total=len(items))


@router.get("/hot", response_model=RecommendListResponse)
def get_hot_content(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items = []
    blogs = db.query(Blog).filter(Blog.is_published == True).order_by(desc(Blog.view_count)).limit(50).all()
    for b in blogs:
        items.append(_item_to_recommend(b, "blog", _calculate_score(b)))
    news = db.query(News).filter(News.is_published == True).order_by(desc(News.view_count)).limit(20).all()
    for n in news:
        items.append(_item_to_recommend(n, "news", _calculate_score(n)))
    items.sort(key=lambda x: x.score, reverse=True)
    start = (page - 1) * page_size
    paged = items[start:start + page_size]
    return RecommendListResponse(items=paged, total=len(items))


@router.get("/related/{content_type}/{content_id}", response_model=RecommendListResponse)
def get_related_content(
    content_type: str,
    content_id: int,
    page_size: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    model_map = {"blog": Blog, "news": News, "product": Product, "solution": Solution}
    model = model_map.get(content_type)
    if not model:
        return RecommendListResponse(items=[], total=0)
    source = db.query(model).filter(model.id == content_id).first()
    if not source:
        return RecommendListResponse(items=[], total=0)
    query = db.query(model).filter(model.id != content_id, model.is_published == True)
    if hasattr(source, 'category') and source.category:
        query = query.filter(model.category == source.category)
    related = query.order_by(desc(model.view_count)).limit(page_size).all()
    items = [_item_to_recommend(r, content_type, _calculate_score(r)) for r in related]
    return RecommendListResponse(items=items, total=len(items))


@router.get("/trending-tags", response_model=TrendingTagResponse)
def get_trending_tags(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    tags = {}
    for model_cls, ct in [(Blog, "blog"), (News, "news")]:
        rows = db.query(model_cls.tags).filter(model_cls.is_published == True, model_cls.tags != None).limit(100).all()
        for row in rows:
            if row.tags:
                for tag in row.tags.split(','):
                    tag = tag.strip()
                    if tag:
                        tags[tag] = tags.get(tag, 0) + 1
    sorted_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:limit]
    return TrendingTagResponse(tags=[TrendingTag(name=t[0], count=t[1]) for t in sorted_tags])
