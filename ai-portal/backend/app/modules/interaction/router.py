"""互动API - 点赞、收藏、分享"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.exceptions import NotFound
from app.core.events import EventBus
from app.models import User, Blog, Project, News, Product, Solution, Moment, Comment, UserLike, UserFavorite
from app.modules.interaction.schemas import (
    LikeStatusResponse,
    FavoriteStatusResponse,
    FavoriteItem,
    FavoriteListResponse,
)
from app.services.point_service import point_service
from app.modules.notification.router import create_notification

router = APIRouter(tags=["互动"])


def _get_like_count(db: Session, target_type: str, target_id: int) -> int:
    if target_type == "blog":
        blog = db.query(Blog).filter(Blog.id == target_id).first()
        return blog.likes_count if blog else 0
    elif target_type == "project":
        proj = db.query(Project).filter(Project.id == target_id).first()
        return proj.likes_count if proj else 0
    elif target_type == "moment":
        moment = db.query(Moment).filter(Moment.id == target_id).first()
        return moment.likes_count if moment else 0
    elif target_type == "comment":
        comment = db.query(Comment).filter(Comment.id == target_id).first()
        return comment.likes_count if comment else 0
    return 0


def _get_author_id(db: Session, target_type: str, target_id: int) -> int | None:
    if target_type == "blog":
        blog = db.query(Blog).filter(Blog.id == target_id).first()
        return blog.author_id if blog else None
    elif target_type == "project":
        proj = db.query(Project).filter(Project.id == target_id).first()
        return proj.author_id if proj else None
    elif target_type == "moment":
        moment = db.query(Moment).filter(Moment.id == target_id).first()
        return moment.user_id if moment else None
    elif target_type == "comment":
        comment = db.query(Comment).filter(Comment.id == target_id).first()
        return comment.user_id if comment else None
    return None


def _increment_like_count(db: Session, target_type: str, target_id: int):
    if target_type == "blog":
        db.query(Blog).filter(Blog.id == target_id).update({Blog.likes_count: Blog.likes_count + 1}, synchronize_session=False)
    elif target_type == "project":
        db.query(Project).filter(Project.id == target_id).update({Project.likes_count: Project.likes_count + 1}, synchronize_session=False)
    elif target_type == "moment":
        db.query(Moment).filter(Moment.id == target_id).update({Moment.likes_count: Moment.likes_count + 1}, synchronize_session=False)


def _decrement_like_count(db: Session, target_type: str, target_id: int):
    if target_type == "blog":
        db.query(Blog).filter(Blog.id == target_id).update({Blog.likes_count: func.max(Blog.likes_count - 1, 0)}, synchronize_session=False)
    elif target_type == "project":
        db.query(Project).filter(Project.id == target_id).update({Project.likes_count: func.max(Project.likes_count - 1, 0)}, synchronize_session=False)
    elif target_type == "moment":
        db.query(Moment).filter(Moment.id == target_id).update({Moment.likes_count: func.max(Moment.likes_count - 1, 0)}, synchronize_session=False)


def _increment_favorite_count(db: Session, target_type: str, target_id: int):
    if target_type == "blog":
        db.query(Blog).filter(Blog.id == target_id).update({Blog.favorites_count: Blog.favorites_count + 1}, synchronize_session=False)
    elif target_type == "project":
        db.query(Project).filter(Project.id == target_id).update({Project.favorites_count: Project.favorites_count + 1}, synchronize_session=False)


def _decrement_favorite_count(db: Session, target_type: str, target_id: int):
    if target_type == "blog":
        db.query(Blog).filter(Blog.id == target_id).update({Blog.favorites_count: func.max(Blog.favorites_count - 1, 0)}, synchronize_session=False)
    elif target_type == "project":
        db.query(Project).filter(Project.id == target_id).update({Project.favorites_count: func.max(Project.favorites_count - 1, 0)}, synchronize_session=False)


_TYPE_NAMES = {"blog": "博客", "project": "项目", "moment": "动态", "comment": "评论"}


@router.post("/like/{target_type}/{target_id}")
def toggle_like(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """点赞/取消点赞"""
    valid_types = ["blog", "project", "moment", "comment"]
    if target_type not in valid_types:
        raise NotFound("无效目标类型")

    existing = db.query(UserLike).filter(
        UserLike.user_id == current_user.id,
        UserLike.target_type == target_type,
        UserLike.target_id == target_id,
    ).first()

    if existing:
        db.delete(existing)
        _decrement_like_count(db, target_type, target_id)
        db.commit()
        return {"success": True, "liked": False, "likes_count": _get_like_count(db, target_type, target_id)}

    new_like = UserLike(user_id=current_user.id, target_type=target_type, target_id=target_id)
    db.add(new_like)
    _increment_like_count(db, target_type, target_id)
    db.commit()

    likes_count = _get_like_count(db, target_type, target_id)
    author_id = _get_author_id(db, target_type, target_id)
    if author_id and author_id != current_user.id:
        if not current_user.is_admin and point_service.check_daily_limit(db, author_id, "receive_like"):
            point_service.award_points(db, author_id, "receive_like", f"内容被点赞")
        create_notification(
            db, author_id, "like", "点赞通知",
            f"{current_user.nickname or current_user.username} 点赞了你的{_TYPE_NAMES.get(target_type, '内容')}",
            from_user_id=current_user.id,
            target_type=target_type, target_id=target_id,
        )

    EventBus.emit_sync("like.created", new_like)

    return {"success": True, "liked": True, "likes_count": likes_count}


@router.get("/like-status/{target_type}/{target_id}", response_model=LikeStatusResponse)
def get_like_status(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取点赞状态"""
    is_liked = db.query(UserLike).filter(
        UserLike.user_id == current_user.id,
        UserLike.target_type == target_type,
        UserLike.target_id == target_id,
    ).first() is not None
    return {"is_liked": is_liked, "likes_count": _get_like_count(db, target_type, target_id)}


@router.post("/favorite/{target_type}/{target_id}")
def toggle_favorite(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """收藏/取消收藏"""
    valid_types = ["blog", "project"]
    if target_type not in valid_types:
        raise NotFound("仅支持收藏 blog 和 project")

    existing = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.target_type == target_type,
        UserFavorite.target_id == target_id,
    ).first()

    if existing:
        db.delete(existing)
        _decrement_favorite_count(db, target_type, target_id)
        db.commit()
        fav_count = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).count()
        return {"success": True, "favorited": False, "favorites_count": fav_count}

    new_fav = UserFavorite(user_id=current_user.id, target_type=target_type, target_id=target_id)
    db.add(new_fav)
    _increment_favorite_count(db, target_type, target_id)
    db.commit()

    author_id = _get_author_id(db, target_type, target_id)
    if author_id and author_id != current_user.id:
        if not current_user.is_admin and point_service.check_daily_limit(db, author_id, "receive_favorite"):
            point_service.award_points(db, author_id, "receive_favorite", "内容被收藏")
        create_notification(
            db, author_id, "favorite", "收藏通知",
            f"{current_user.nickname or current_user.username} 收藏了你的{_TYPE_NAMES.get(target_type, '内容')}",
            from_user_id=current_user.id,
            target_type=target_type, target_id=target_id,
        )

    fav_count = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id).count()

    EventBus.emit_sync("favorite.created", new_fav)

    return {"success": True, "favorited": True, "favorites_count": fav_count}


@router.get("/favorite-status/{target_type}/{target_id}", response_model=FavoriteStatusResponse)
def get_favorite_status(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取收藏状态"""
    is_favorited = db.query(UserFavorite).filter(
        UserFavorite.user_id == current_user.id,
        UserFavorite.target_type == target_type,
        UserFavorite.target_id == target_id,
    ).first() is not None
    favorites_count = db.query(UserFavorite).filter(UserFavorite.target_type == target_type, UserFavorite.target_id == target_id).count()
    return {"is_favorited": is_favorited, "favorites_count": favorites_count}


@router.get("/favorites", response_model=FavoriteListResponse)
def list_my_favorites(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取我的收藏"""
    query = db.query(UserFavorite).filter(UserFavorite.user_id == current_user.id)
    total = query.count()
    favorites = query.order_by(UserFavorite.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for fav in favorites:
        target_title = None
        target_cover = None
        if fav.target_type == "blog":
            blog = db.query(Blog).filter(Blog.id == fav.target_id).first()
            target_title = blog.title if blog else "（已删除）"
            target_cover = blog.cover_image if blog else None
        elif fav.target_type == "project":
            proj = db.query(Project).filter(Project.id == fav.target_id).first()
            target_title = proj.title if proj else "（已删除）"
            target_cover = proj.cover_image if proj else None

        items.append({
            "id": fav.id,
            "target_type": fav.target_type,
            "target_id": fav.target_id,
            "created_at": fav.created_at,
            "target_title": target_title,
            "target_cover": target_cover,
        })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("/share/{target_type}/{target_id}")
def share_content(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """分享内容"""
    valid_types = {"blog", "project", "news", "product", "solution", "moment"}
    if target_type not in valid_types:
        raise NotFound("无效的目标类型")
    if target_type == "blog":
        db.query(Blog).filter(Blog.id == target_id).update({Blog.shares_count: Blog.shares_count + 1}, synchronize_session=False)
    elif target_type == "project":
        db.query(Project).filter(Project.id == target_id).update({Project.shares_count: Project.shares_count + 1}, synchronize_session=False)
    elif target_type == "news":
        db.query(News).filter(News.id == target_id).update({News.shares_count: News.shares_count + 1}, synchronize_session=False)
    elif target_type == "product":
        db.query(Product).filter(Product.id == target_id).update({Product.shares_count: Product.shares_count + 1}, synchronize_session=False)
    elif target_type == "solution":
        db.query(Solution).filter(Solution.id == target_id).update({Solution.shares_count: Solution.shares_count + 1}, synchronize_session=False)

    db.commit()

    author_id = _get_author_id(db, target_type, target_id)
    if author_id and author_id != current_user.id:
        if not current_user.is_admin and point_service.check_daily_limit(db, author_id, "share_content"):
            point_service.award_points(db, author_id, "share_content", "内容被分享")

    if not current_user.is_admin and point_service.check_daily_limit(db, current_user.id, "share_content"):
        point_service.award_points(db, current_user.id, "share_content", "分享内容")

    return {"success": True, "message": "分享成功"}
