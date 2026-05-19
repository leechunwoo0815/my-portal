"""博客API路由 - 博客文章CRUD"""
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.crud import CRUDBase
from app.core.deps import get_db, get_current_user, require_admin
from app.core.exceptions import NotFound, PermissionDenied
from app.core.events import EventBus
from app.models import Blog, User
from app.models import Comment, UserLike, UserFavorite
from app.modules.blog.schemas import (
    BlogCreate,
    BlogUpdate,
    BlogResponse,
    BlogListResponse,
)
from app.services.point_service import point_service

router = APIRouter(tags=["博客"])
crud = CRUDBase(Blog)


@router.get("/posts", response_model=BlogListResponse)
def list_blogs(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: str = "",
    tag: str = "",
    keyword: str = "",
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取博客列表（公开接口）"""
    from sqlalchemy import or_
    query = db.query(Blog).filter(Blog.is_published == True)
    if category:
        query = query.filter(Blog.category == category)
    if tag:
        query = query.filter(Blog.tags.contains(tag))
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(Blog.title.like(pattern), Blog.summary.like(pattern), Blog.tags.like(pattern)))
    total = query.count()
    items = query.order_by(Blog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}


@router.get("/posts/{blog_id}", response_model=BlogResponse)
def get_blog(blog_id: int, db: Session = Depends(get_db)) -> Blog:
    """获取博客详情（公开接口）"""
    blog = crud.get_or_404(db, blog_id, "博客不存在")
    if not blog.is_published:
        raise NotFound("博客")
    db.query(Blog).filter(Blog.id == blog_id).update({Blog.view_count: Blog.view_count + 1}, synchronize_session=False)
    db.commit()
    db.refresh(blog)
    return blog


@router.post("/posts", response_model=BlogResponse)
def create_blog(
    request: BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Blog:
    """创建博客（LV3+ 或管理员）"""
    if not current_user.is_admin and current_user.level < 3:
        raise PermissionDenied("LV3及以上才能发布博客")
    blog = Blog(**request.model_dump())
    blog.author_id = current_user.id
    db.add(blog)
    db.commit()
    db.refresh(blog)
    if not current_user.is_admin and point_service.check_daily_limit(db, current_user.id, "publish_blog"):
        point_service.award_points(db, current_user.id, "publish_blog", "发布博客")
    EventBus.emit_sync("blog.created", blog)
    if blog.is_published:
        EventBus.emit_sync("blog.published", blog)
    return blog


@router.put("/posts/{blog_id}", response_model=BlogResponse)
def update_blog(
    blog_id: int,
    request: BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Blog:
    """更新博客（作者或管理员）"""
    blog = crud.get_or_404(db, blog_id, "博客不存在")
    if not current_user.is_admin and blog.author_id != current_user.id:
        raise PermissionDenied("无权编辑该博客")
    return crud.update(db, blog, request)


@router.delete("/posts/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """删除博客（作者或管理员）"""
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise NotFound("博客")
    if not current_user.is_admin and blog.author_id != current_user.id:
        raise PermissionDenied("无权删除该博客")
    db.query(Comment).filter(Comment.target_type == "blog", Comment.target_id == blog_id).delete(synchronize_session=False)
    db.query(UserLike).filter(UserLike.target_type == "blog", UserLike.target_id == blog_id).delete(synchronize_session=False)
    db.query(UserFavorite).filter(UserFavorite.target_type == "blog", UserFavorite.target_id == blog_id).delete(synchronize_session=False)
    db.delete(blog)
    db.commit()
    EventBus.emit_sync("blog.deleted", blog)
    return {"message": "博客已删除"}


@router.get("/admin/posts", response_model=BlogListResponse)
def admin_list_blogs(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    author_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    """博客管理列表：管理员看全部，可按作者筛选"""
    query = db.query(Blog)
    if author_id is not None:
        query = query.filter(Blog.author_id == author_id)
    query = query.order_by(Blog.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}
