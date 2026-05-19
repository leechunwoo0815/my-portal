"""专栏API路由"""
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.crud import CRUDBase
from app.core.deps import get_db, get_current_user, get_optional_current_user
from app.core.exceptions import NotFound, PermissionDenied
from app.models import User, Blog
from app.models.series import Series, SeriesArticle
from app.modules.series.schemas import (
    SeriesCreate, SeriesUpdate, SeriesArticleAdd,
    SeriesResponse, SeriesListResponse,
)

router = APIRouter(tags=["专栏"])
crud = CRUDBase(Series)


@router.get("/", response_model=SeriesListResponse)
def list_series(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    author_id: int = 0,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """获取专栏列表"""
    filters = {}
    if author_id:
        filters["author_id"] = author_id
    else:
        filters["is_public"] = True
    items, total = crud.list(db, skip=(page - 1) * page_size, limit=page_size, filters=filters, order_by=Series.created_at.desc())
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}


@router.get("/{series_id}")
def get_series(series_id: int, db: Session = Depends(get_db)) -> dict:
    """获取专栏详情"""
    series = crud.get_or_404(db, series_id, "专栏不存在")
    articles = db.query(SeriesArticle).filter(SeriesArticle.series_id == series_id).order_by(SeriesArticle.order).all()
    article_list = []
    for sa in articles:
        blog = db.query(Blog).filter(Blog.id == sa.blog_id).first()
        if blog:
            article_list.append({
                "id": blog.id, "title": blog.title, "summary": blog.summary,
                "cover_image": blog.cover_image, "view_count": blog.view_count,
                "likes_count": blog.likes_count, "created_at": blog.created_at,
                "order": sa.order,
            })
    return {**SeriesResponse.model_validate(series).model_dump(), "articles": article_list}


@router.post("/", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED)
def create_series(
    data: SeriesCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Series:
    """创建专栏"""
    series = Series(**data.model_dump(), author_id=user.id)
    db.add(series)
    db.commit()
    db.refresh(series)
    return series


@router.put("/{series_id}", response_model=SeriesResponse)
def update_series(
    series_id: int,
    data: SeriesUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Series:
    """更新专栏"""
    series = crud.get_or_404(db, series_id, "专栏不存在")
    if series.author_id != user.id:
        raise PermissionDenied()
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(series, key, value)
    db.commit()
    db.refresh(series)
    return series


@router.delete("/{series_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_series(
    series_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """删除专栏"""
    series = crud.get_or_404(db, series_id, "专栏不存在")
    if series.author_id != user.id:
        raise PermissionDenied()
    db.query(SeriesArticle).filter(SeriesArticle.series_id == series_id).delete()
    db.delete(series)
    db.commit()


@router.post("/{series_id}/articles")
def add_article(
    series_id: int,
    data: SeriesArticleAdd,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """添加文章到专栏"""
    series = crud.get_or_404(db, series_id, "专栏不存在")
    if series.author_id != user.id:
        raise PermissionDenied()
    existing = db.query(SeriesArticle).filter(
        SeriesArticle.series_id == series_id, SeriesArticle.blog_id == data.blog_id
    ).first()
    if existing:
        return {"message": "文章已在专栏中"}
    sa = SeriesArticle(series_id=series_id, blog_id=data.blog_id, order=data.order)
    db.add(sa)
    series.articles_count = db.query(SeriesArticle).filter(SeriesArticle.series_id == series_id).count() + 1
    db.commit()
    return {"message": "添加成功"}


@router.delete("/{series_id}/articles/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_article(
    series_id: int,
    blog_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """从专栏移除文章"""
    series = crud.get_or_404(db, series_id, "专栏不存在")
    if series.author_id != user.id:
        raise PermissionDenied()
    db.query(SeriesArticle).filter(
        SeriesArticle.series_id == series_id, SeriesArticle.blog_id == blog_id
    ).delete()
    series.articles_count = db.query(SeriesArticle).filter(SeriesArticle.series_id == series_id).count()
    db.commit()
