"""动态API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_optional_current_user
from app.core.exceptions import NotFound, PermissionDenied
from app.models import User, Moment, UserLike, UserFavorite, Comment, UserFollow
from app.modules.moment.schemas import (
    MomentCreate,
    MomentUpdate,
    MomentItem,
    MomentListResponse,
    RepostRequest,
)
from app.services.point_service import point_service, LEVEL_TITLES

router = APIRouter(tags=["动态"])


def _build_moment_response(db: Session, moment: Moment, current_user_id: int | None = None, users: dict = None, likes: set = None, favorites: set = None, comments_count_map: dict = None, depth: int = 0) -> dict:
    author = (users or {}).get(moment.user_id) or db.query(User).filter(User.id == moment.user_id).first()
    is_liked = moment.id in likes if likes is not None else False
    is_favorited = moment.id in favorites if favorites is not None else False
    if current_user_id and likes is None:
        is_liked = db.query(UserLike).filter(
            UserLike.user_id == current_user_id,
            UserLike.target_type == "moment",
            UserLike.target_id == moment.id,
        ).first() is not None
    if current_user_id and favorites is None:
        is_favorited = db.query(UserFavorite).filter(
            UserFavorite.user_id == current_user_id,
            UserFavorite.target_type == "moment",
            UserFavorite.target_id == moment.id,
        ).first() is not None

    if comments_count_map is not None:
        actual_comments_count = comments_count_map.get(moment.id, 0)
    else:
        actual_comments_count = db.query(Comment).filter(
            Comment.target_type == "moment", Comment.target_id == moment.id
        ).count()

    original_moment = None
    if moment.original_id:
        if depth > 5:
            original_moment = None
        else:
            orig = db.query(Moment).filter(Moment.id == moment.original_id).first()
            if orig:
                original_moment = _build_moment_response(db, orig, None, depth=depth + 1)

    return {
        "id": moment.id,
        "user_id": moment.user_id,
        "content": moment.content,
        "images": moment.images or [],
        "moment_type": moment.moment_type,
        "original_id": moment.original_id,
        "likes_count": moment.likes_count,
        "comments_count": actual_comments_count,
        "is_public": moment.is_public,
        "is_liked": is_liked,
        "is_favorited": is_favorited,
        "created_at": moment.created_at,
        "author": {
            "user_id": author.id if author else 0,
            "username": author.username if author else "",
            "nickname": author.nickname if author else None,
            "avatar_url": author.avatar_url if author else None,
            "level": author.level if author else 1,
            "level_title": LEVEL_TITLES.get(author.level, "新手上路") if author else "新手上路",
        } if author else None,
        "original": original_moment,
    }


@router.post("", response_model=MomentItem)
def create_moment(
    request: MomentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """发布动态"""
    if current_user.level < 2 and not current_user.is_admin:
        raise PermissionDenied("LV2及以上才能发布动态")

    moment = Moment(
        user_id=current_user.id,
        content=request.content.strip(),
        images=request.images or [],
        moment_type="original",
        is_public=request.is_public,
    )
    db.add(moment)
    db.commit()
    db.refresh(moment)

    if not current_user.is_admin and point_service.check_daily_limit(db, current_user.id, "publish_moment"):
        point_service.award_points(db, current_user.id, "publish_moment", "发布动态")

    return _build_moment_response(db, moment, current_user.id)


@router.get("", response_model=MomentListResponse)
def list_moments(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取动态列表"""
    query = db.query(Moment).filter(Moment.is_public == True)
    total = query.count()
    moments = query.order_by(Moment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    uid = current_user.id if current_user else None
    user_ids = {m.user_id for m in moments}
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    moment_ids = [m.id for m in moments]
    likes_set = {l.target_id for l in db.query(UserLike).filter(UserLike.target_type == "moment", UserLike.target_id.in_(moment_ids), UserLike.user_id == uid).all()} if uid and moment_ids else set()
    favs_set = {f.target_id for f in db.query(UserFavorite).filter(UserFavorite.target_type == "moment", UserFavorite.target_id.in_(moment_ids), UserFavorite.user_id == uid).all()} if uid and moment_ids else set()
    comments_count_map = {}
    if moment_ids:
        rows = db.query(Comment.target_id, func.count(Comment.id)).filter(
            Comment.target_type == "moment", Comment.target_id.in_(moment_ids)
        ).group_by(Comment.target_id).all()
        comments_count_map = {r[0]: r[1] for r in rows}
    items = [_build_moment_response(db, m, uid, users_map, likes_set, favs_set, comments_count_map) for m in moments]
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/following", response_model=MomentListResponse)
def list_following_moments(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取关注用户的动态"""
    following_ids = [f.following_id for f in db.query(UserFollow).filter(UserFollow.follower_id == current_user.id).all()]
    if not following_ids:
        return {"total": 0, "page": page, "page_size": page_size, "items": []}
    query = db.query(Moment).filter(Moment.is_public == True, Moment.user_id.in_(following_ids))
    total = query.count()
    moments = query.order_by(Moment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    uid = current_user.id
    user_ids = {m.user_id for m in moments}
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    moment_ids = [m.id for m in moments]
    likes_set = {l.target_id for l in db.query(UserLike).filter(UserLike.target_type == "moment", UserLike.target_id.in_(moment_ids), UserLike.user_id == uid).all()} if moment_ids else set()
    favs_set = {f.target_id for f in db.query(UserFavorite).filter(UserFavorite.target_type == "moment", UserFavorite.target_id.in_(moment_ids), UserFavorite.user_id == uid).all()} if moment_ids else set()
    comments_count_map = {}
    if moment_ids:
        rows = db.query(Comment.target_id, func.count(Comment.id)).filter(
            Comment.target_type == "moment", Comment.target_id.in_(moment_ids)
        ).group_by(Comment.target_id).all()
        comments_count_map = {r[0]: r[1] for r in rows}
    items = [_build_moment_response(db, m, uid, users_map, likes_set, favs_set, comments_count_map) for m in moments]
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/my", response_model=MomentListResponse)
def list_my_moments(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取我的动态"""
    query = db.query(Moment).filter(Moment.user_id == current_user.id)
    total = query.count()
    moments = query.order_by(Moment.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    user_ids = {m.user_id for m in moments}
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}
    moment_ids = [m.id for m in moments]
    likes_set = {l.target_id for l in db.query(UserLike).filter(UserLike.target_type == "moment", UserLike.target_id.in_(moment_ids), UserLike.user_id == current_user.id).all()} if moment_ids else set()
    favs_set = {f.target_id for f in db.query(UserFavorite).filter(UserFavorite.target_type == "moment", UserFavorite.target_id.in_(moment_ids), UserFavorite.user_id == current_user.id).all()} if moment_ids else set()
    comments_count_map = {}
    if moment_ids:
        rows = db.query(Comment.target_id, func.count(Comment.id)).filter(
            Comment.target_type == "moment", Comment.target_id.in_(moment_ids)
        ).group_by(Comment.target_id).all()
        comments_count_map = {r[0]: r[1] for r in rows}
    items = [_build_moment_response(db, m, current_user.id, users_map, likes_set, favs_set, comments_count_map) for m in moments]
    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/{moment_id}", response_model=MomentItem)
def get_moment(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> dict:
    """获取动态详情"""
    moment = db.query(Moment).filter(Moment.id == moment_id).first()
    if not moment:
        raise NotFound("动态")
    if not moment.is_public and (not current_user or current_user.id != moment.user_id):
        raise NotFound("动态")
    return _build_moment_response(db, moment, current_user.id if current_user else None)


@router.delete("/{moment_id}")
def delete_moment(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """删除动态"""
    moment = db.query(Moment).filter(Moment.id == moment_id).first()
    if not moment:
        raise NotFound("动态")
    if moment.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权删除该动态")
    db.query(Comment).filter(Comment.target_type == "moment", Comment.target_id == moment_id).delete(synchronize_session=False)
    db.query(UserLike).filter(UserLike.target_type == "moment", UserLike.target_id == moment_id).delete(synchronize_session=False)
    db.query(UserFavorite).filter(UserFavorite.target_type == "moment", UserFavorite.target_id == moment_id).delete(synchronize_session=False)
    db.delete(moment)
    db.commit()
    return {"message": "动态已删除"}


@router.put("/{moment_id}", response_model=MomentItem)
def update_moment(
    moment_id: int,
    request: MomentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """修改动态"""
    moment = db.query(Moment).filter(Moment.id == moment_id).first()
    if not moment:
        raise NotFound("动态")
    if moment.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权修改该动态")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(moment, field, value)
    db.commit()
    db.refresh(moment)
    return _build_moment_response(db, moment, current_user.id)


@router.post("/{moment_id}/like")
def like_moment(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """点赞/取消点赞动态"""
    moment = db.query(Moment).filter(Moment.id == moment_id).first()
    if not moment:
        raise NotFound("动态")

    existing = db.query(UserLike).filter(
        UserLike.user_id == current_user.id,
        UserLike.target_type == "moment",
        UserLike.target_id == moment_id,
    ).first()

    if existing:
        db.delete(existing)
        db.query(Moment).filter(Moment.id == moment_id).update({Moment.likes_count: func.max(Moment.likes_count - 1, 0)}, synchronize_session=False)
        db.commit()
        db.refresh(moment)
        return {"liked": False, "likes_count": moment.likes_count}

    new_like = UserLike(user_id=current_user.id, target_type="moment", target_id=moment_id)
    db.add(new_like)
    db.query(Moment).filter(Moment.id == moment_id).update({Moment.likes_count: Moment.likes_count + 1}, synchronize_session=False)
    db.commit()
    db.refresh(moment)

    if moment.user_id != current_user.id:
        if not current_user.is_admin and point_service.check_daily_limit(db, moment.user_id, "receive_like"):
            point_service.award_points(db, moment.user_id, "receive_like", f"动态被 {current_user.username} 点赞")
        from app.modules.notification.router import create_notification
        create_notification(
            db, moment.user_id, "like", "点赞通知",
            f"{current_user.nickname or current_user.username} 点赞了你的动态",
            from_user_id=current_user.id,
            target_type="moment", target_id=moment_id,
        )

    return {"liked": True, "likes_count": moment.likes_count}


@router.post("/{moment_id}/repost", response_model=MomentItem)
def repost_moment(
    moment_id: int,
    request: RepostRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """转发动态"""
    original = db.query(Moment).filter(Moment.id == moment_id).first()
    if not original:
        raise NotFound("原动态")
    if not original.is_public:
        raise PermissionDenied("该动态不可转发")

    content = request.content.strip() if request.content else ""

    new_moment = Moment(
        user_id=current_user.id,
        content=content,
        images=[],
        moment_type="repost",
        original_id=moment_id,
        is_public=True,
    )
    db.add(new_moment)

    db.commit()
    db.refresh(new_moment)

    if not current_user.is_admin and point_service.check_daily_limit(db, current_user.id, "publish_moment"):
        point_service.award_points(db, current_user.id, "publish_moment", "转发动态")

    return _build_moment_response(db, new_moment, current_user.id)
