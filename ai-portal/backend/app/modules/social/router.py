"""社交关系API - 关注/粉丝"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_optional_current_user
from app.core.exceptions import NotFound, PermissionDenied
from app.core.events import EventBus
from app.models import User, UserFollow
from app.modules.social.schemas import (
    FollowResponse,
    FollowerListResponse,
    FollowStatusResponse,
)
from app.services.point_service import point_service
from app.modules.notification.router import create_notification

router = APIRouter(tags=["社交"])


@router.post("/follow/{user_id}", response_model=FollowResponse)
def follow_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """关注/取消关注用户"""
    if user_id == current_user.id:
        raise PermissionDenied("不能关注自己")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise NotFound("用户")
    if not target_user.is_active:
        raise PermissionDenied("该用户已被禁用")

    existing = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id,
    ).first()

    if existing:
        db.delete(existing)
        db.query(User).filter(User.id == current_user.id).update({User.following_count: func.max(User.following_count - 1, 0)}, synchronize_session=False)
        db.query(User).filter(User.id == user_id).update({User.followers_count: func.max(User.followers_count - 1, 0)}, synchronize_session=False)
        db.commit()
        db.refresh(current_user)
        db.refresh(target_user)
        return {
            "is_following": False,
            "followers_count": target_user.followers_count,
            "following_count": current_user.following_count,
        }

    new_follow = UserFollow(follower_id=current_user.id, following_id=user_id)
    db.add(new_follow)
    db.query(User).filter(User.id == current_user.id).update({User.following_count: User.following_count + 1}, synchronize_session=False)
    db.query(User).filter(User.id == user_id).update({User.followers_count: User.followers_count + 1}, synchronize_session=False)
    db.commit()
    db.refresh(current_user)
    db.refresh(target_user)

    if point_service.check_daily_limit(db, target_user.id, "receive_follow"):
        point_service.award_points(db, target_user.id, "receive_follow", f"被 {current_user.username} 关注")

    create_notification(
        db, user_id, "follow", "新关注者",
        f"{current_user.nickname or current_user.username} 关注了你",
        from_user_id=current_user.id,
    )

    EventBus.emit_sync("user.followed", new_follow)

    return {
        "is_following": True,
        "followers_count": target_user.followers_count,
        "following_count": current_user.following_count,
    }


@router.get("/followers/{user_id}", response_model=FollowerListResponse)
def list_followers(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取粉丝列表"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise NotFound("用户")

    query = db.query(UserFollow).filter(UserFollow.following_id == user_id)
    total = query.count()
    follows = query.order_by(UserFollow.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    follower_ids = [f.follower_id for f in follows]
    followers = db.query(User).filter(User.id.in_(follower_ids)).all() if follower_ids else []
    follower_map = {u.id: u for u in followers}

    # is_following_me: does this follower also follow user_id back? (relative to profile owner)
    owner_following_ids = set()
    owner_follows = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id,
        UserFollow.following_id.in_(follower_ids),
    ).all() if follower_ids else []
    owner_following_ids = {f.following_id for f in owner_follows}

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
                "is_following_me": u.id in owner_following_ids,
                "created_at": f.created_at,
            })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/following/{user_id}", response_model=FollowerListResponse)
def list_following(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取关注列表"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise NotFound("用户")

    query = db.query(UserFollow).filter(UserFollow.follower_id == user_id)
    total = query.count()
    follows = query.order_by(UserFollow.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    following_ids = [f.following_id for f in follows]
    following_users = db.query(User).filter(User.id.in_(following_ids)).all() if following_ids else []
    following_map = {u.id: u for u in following_users}

    # is_following_me: does this person also follow user_id back? (relative to profile owner)
    owner_follower_ids = set()
    owner_followers = db.query(UserFollow).filter(
        UserFollow.follower_id.in_(following_ids),
        UserFollow.following_id == user_id,
    ).all() if following_ids else []
    owner_follower_ids = {f.follower_id for f in owner_followers}

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
                "is_following_me": u.id in owner_follower_ids,
                "created_at": f.created_at,
            })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/friends/{user_id}", response_model=FollowerListResponse)
def list_friends(
    user_id: int,
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取好友列表（互相关注）"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise NotFound("用户")

    # Find users that target_user follows
    following_ids_q = db.query(UserFollow.following_id).filter(UserFollow.follower_id == user_id)
    # Find mutual: those who also follow target_user
    query = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id,
        UserFollow.following_id.in_(
            db.query(UserFollow.follower_id).filter(UserFollow.following_id == user_id)
        ),
    )
    total = query.count()
    follows = query.order_by(UserFollow.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    friend_ids = [f.following_id for f in follows]
    friends = db.query(User).filter(User.id.in_(friend_ids)).all() if friend_ids else []
    friend_map = {u.id: u for u in friends}

    # Friends are mutual follows, so is_following_me is always True
    items = []
    for f in follows:
        u = friend_map.get(f.following_id)
        if u:
            items.append({
                "user_id": u.id,
                "username": u.username,
                "nickname": u.nickname,
                "avatar_url": u.avatar_url,
                "level": u.level,
                "bio": u.bio,
                "is_following_me": True,
                "created_at": f.created_at,
            })

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.post("/remove-follower/{user_id}")
def remove_follower(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """移除粉丝"""
    follow = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id,
        UserFollow.following_id == current_user.id,
    ).first()
    if not follow:
        raise NotFound("关注关系")

    db.delete(follow)
    db.query(User).filter(User.id == user_id).update({User.following_count: func.max(User.following_count - 1, 0)}, synchronize_session=False)
    db.query(User).filter(User.id == current_user.id).update({User.followers_count: func.max(User.followers_count - 1, 0)}, synchronize_session=False)
    db.commit()
    return {"message": "已移除该粉丝"}


@router.get("/follow-status/{user_id}", response_model=FollowStatusResponse)
def get_follow_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取关注关系状态"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise NotFound("用户")

    if not current_user:
        return {
            "is_following": False,
            "is_followed_by": False,
            "is_mutual": False,
            "followers_count": target_user.followers_count,
            "following_count": target_user.following_count,
        }

    i_follow_him = db.query(UserFollow).filter(
        UserFollow.follower_id == current_user.id,
        UserFollow.following_id == user_id,
    ).first() is not None

    he_follows_me = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id,
        UserFollow.following_id == current_user.id,
    ).first() is not None

    return {
        "is_following": i_follow_him,
        "is_followed_by": he_follows_me,
        "is_mutual": i_follow_him and he_follows_me,
        "followers_count": target_user.followers_count,
        "following_count": target_user.following_count,
    }
