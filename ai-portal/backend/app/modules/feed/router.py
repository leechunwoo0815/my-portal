"""动态流API - 关注用户的内容动态"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import User, Blog, Moment, Comment, UserFollow
from app.modules.feed.schemas import FeedItem, FeedListResponse

router = APIRouter(tags=["动态流"])


def _get_comments_count_map(db: Session, target_type: str, target_ids: list[int]) -> dict[int, int]:
    if not target_ids:
        return {}
    rows = db.query(Comment.target_id, func.count(Comment.id)).filter(
        Comment.target_type == target_type, Comment.target_id.in_(target_ids)
    ).group_by(Comment.target_id).all()
    return {r[0]: r[1] for r in rows}


@router.get("/", response_model=FeedListResponse)
def get_following_feed(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    following_ids = [f.following_id for f in db.query(UserFollow).filter(UserFollow.follower_id == current_user.id).all()]
    if not following_ids:
        return FeedListResponse(items=[], total=0, page=page)

    items = []
    blogs = db.query(Blog).filter(Blog.author_id.in_(following_ids), Blog.is_published == True).order_by(desc(Blog.created_at)).all()
    blog_ids = [b.id for b in blogs]
    blog_comments_map = _get_comments_count_map(db, "blog", blog_ids)
    for b in blogs:
        author = b.author
        items.append(FeedItem(
            id=b.id, content_type="blog", title=b.title, content=None,
            summary=b.content[:100] if b.content else None,
            author_id=author.id if author else None,
            author_name=author.nickname or author.username if author else None,
            author_avatar=author.avatar_url if author else None,
            author_level=author.level if author else 1,
            created_at=b.created_at, likes_count=b.likes_count or 0,
            comments_count=blog_comments_map.get(b.id, 0),
        ))

    moments = db.query(Moment).filter(Moment.user_id.in_(following_ids)).order_by(desc(Moment.created_at)).all()
    moment_ids = [m.id for m in moments]
    moment_comments_map = _get_comments_count_map(db, "moment", moment_ids)
    for m in moments:
        author = m.author
        items.append(FeedItem(
            id=m.id, content_type="moment", title=None, content=m.content,
            summary=m.content[:100] if m.content else None,
            author_id=author.id if author else None,
            author_name=author.nickname or author.username if author else None,
            author_avatar=author.avatar_url if author else None,
            author_level=author.level if author else 1,
            created_at=m.created_at, likes_count=m.likes_count or 0,
            comments_count=moment_comments_map.get(m.id, 0),
        ))

    items.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    start = (page - 1) * page_size
    paged = items[start:start + page_size]
    return FeedListResponse(items=paged, total=len(items), page=page)


@router.get("/all", response_model=FeedListResponse)
def get_all_feed(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    items = []
    blogs = db.query(Blog).filter(Blog.is_published == True).order_by(desc(Blog.created_at)).limit(50).all()
    blog_ids = [b.id for b in blogs]
    blog_comments_map = _get_comments_count_map(db, "blog", blog_ids)
    for b in blogs:
        author = b.author
        items.append(FeedItem(
            id=b.id, content_type="blog", title=b.title, content=None,
            summary=b.content[:100] if b.content else None,
            author_id=author.id if author else None,
            author_name=author.nickname or author.username if author else None,
            author_avatar=author.avatar_url if author else None,
            author_level=author.level if author else 1,
            created_at=b.created_at, likes_count=b.likes_count or 0,
            comments_count=blog_comments_map.get(b.id, 0),
        ))

    moments = db.query(Moment).order_by(desc(Moment.created_at)).limit(50).all()
    moment_ids = [m.id for m in moments]
    moment_comments_map = _get_comments_count_map(db, "moment", moment_ids)
    for m in moments:
        author = m.author
        items.append(FeedItem(
            id=m.id, content_type="moment", title=None, content=m.content,
            summary=m.content[:100] if m.content else None,
            author_id=author.id if author else None,
            author_name=author.nickname or author.username if author else None,
            author_avatar=author.avatar_url if author else None,
            author_level=author.level if author else 1,
            created_at=m.created_at, likes_count=m.likes_count or 0,
            comments_count=moment_comments_map.get(m.id, 0),
        ))

    items.sort(key=lambda x: x.created_at or datetime.min, reverse=True)
    start = (page - 1) * page_size
    paged = items[start:start + page_size]
    return FeedListResponse(items=paged, total=len(items), page=page)
