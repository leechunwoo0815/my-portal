"""用户主页API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_optional_current_user
from app.core.exceptions import NotFound
from app.models import User, Blog, Project, Moment, UserFollow
from app.modules.user.schemas import (
    UserProfilePublic,
    UserBlogItem,
    UserBlogList,
    UserProjectItem,
    UserProjectList,
)
from app.modules.moment.schemas import MomentListResponse
from app.modules.moment.router import _build_moment_response
from app.services.point_service import LEVEL_TITLES

router = APIRouter(tags=["用户主页"])


def _build_user_profile(db: Session, user_id: int, current_user_id: int | None = None) -> dict:
    """构建用户公开资料"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")

    is_following = False
    is_followed_by = False
    if current_user_id:
        is_following = db.query(UserFollow).filter(
            UserFollow.follower_id == current_user_id,
            UserFollow.following_id == user_id,
        ).first() is not None
        is_followed_by = db.query(UserFollow).filter(
            UserFollow.follower_id == user_id,
            UserFollow.following_id == current_user_id,
        ).first() is not None

    # Count mutual follows (friends)
    friends_count = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id,
        UserFollow.following_id.in_(
            db.query(UserFollow.follower_id).filter(UserFollow.following_id == user_id)
        ),
    ).count()

    return {
        "user_id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "level": user.level,
        "level_title": LEVEL_TITLES.get(user.level, "新手上路"),
        "points": user.points,
        "total_points": user.total_points,
        "followers_count": user.followers_count,
        "following_count": user.following_count,
        "friends_count": friends_count,
        "is_following": is_following,
        "is_followed_by": is_followed_by,
        "is_mutual": is_following and is_followed_by,
        "gender": user.gender,
        "location": user.location,
        "website": user.website,
        "github": user.github,
        "created_at": user.created_at,
    }


@router.get("/{user_id}", response_model=UserProfilePublic)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取用户公开资料"""
    return _build_user_profile(db, user_id, current_user.id if current_user else None)


@router.get("/{user_id}/blogs", response_model=UserBlogList)
def get_user_blogs(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """获取用户的博客列表"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")

    query = db.query(Blog).filter(Blog.author_id == user_id, Blog.is_published == True)
    total = query.count()
    blogs = query.order_by(Blog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for blog in blogs:
        items.append({
            "id": blog.id,
            "title": blog.title,
            "summary": blog.summary,
            "cover_image": blog.cover_image,
            "category": blog.category,
            "tags": (blog.tags or "").split(",") if blog.tags else [],
            "view_count": blog.view_count,
            "likes_count": blog.likes_count,
            "favorites_count": blog.favorites_count,
            "created_at": blog.created_at,
        })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{user_id}/projects", response_model=UserProjectList)
def get_user_projects(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """获取用户的项目列表"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")

    query = db.query(Project).filter(Project.author_id == user_id, Project.is_published == True)
    total = query.count()
    projects = query.order_by(Project.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for proj in projects:
        items.append({
            "id": proj.id,
            "title": proj.title,
            "description": proj.description,
            "cover_image": proj.cover_image,
            "category": proj.category,
            "tech_stack": proj.tech_stack or [],
            "likes_count": proj.likes_count,
            "favorites_count": proj.favorites_count,
            "created_at": proj.created_at,
        })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{user_id}/moments", response_model=MomentListResponse)
def get_user_moments(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取用户的动态列表"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")

    query = db.query(Moment).filter(Moment.user_id == user_id)
    if not current_user or current_user.id != user_id:
        query = query.filter(Moment.is_public == True)

    total = query.count()
    moments = query.order_by(Moment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = [_build_moment_response(db, m, current_user.id if current_user else None) for m in moments]
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{user_id}/followers")
def get_user_followers(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """获取粉丝列表"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")

    query = db.query(UserFollow).filter(UserFollow.following_id == user_id)
    total = query.count()
    follows = query.order_by(UserFollow.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    follower_ids = [f.follower_id for f in follows]
    followers = db.query(User).filter(User.id.in_(follower_ids)).all() if follower_ids else []
    follower_map = {u.id: u for u in followers}

    items = []
    for f in follows:
        u = follower_map.get(f.follower_id)
        if u:
            items.append({
                "user_id": u.id,
                "username": u.username,
                "nickname": u.nickname,
                "avatar_url": u.avatar_url,
                "level": u.level,
                "bio": u.bio,
                "created_at": f.created_at,
            })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{user_id}/following")
def get_user_following(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """获取关注列表"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")

    query = db.query(UserFollow).filter(UserFollow.follower_id == user_id)
    total = query.count()
    follows = query.order_by(UserFollow.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    following_ids = [f.following_id for f in follows]
    following_users = db.query(User).filter(User.id.in_(following_ids)).all() if following_ids else []
    following_map = {u.id: u for u in following_users}

    items = []
    for f in follows:
        u = following_map.get(f.following_id)
        if u:
            items.append({
                "user_id": u.id,
                "username": u.username,
                "nickname": u.nickname,
                "avatar_url": u.avatar_url,
                "level": u.level,
                "bio": u.bio,
                "created_at": f.created_at,
            })

    return {"total": total, "page": page, "page_size": page_size, "items": items}
