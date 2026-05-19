from fastapi import APIRouter, Depends, Query
from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound, PermissionDenied, AlreadyExists
from app.core.security import get_password_hash
from app.models import User, UserFollow, Comment
from app.modules.admin.schemas import UserAdminItem, UserAdminCreate, UserAdminUpdate, UserAdminListResponse

router = APIRouter(tags=["后台管理"])


@router.post("", response_model=UserAdminItem)
def admin_create_user(
    request: UserAdminCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    """管理员创建用户"""
    existing = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    if existing:
        raise AlreadyExists("用户名或邮箱")
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=get_password_hash(request.password),
        nickname=request.nickname,
        level=request.level or 1,
        is_admin=request.is_admin or False,
        is_active=True,
        points=0,
        total_points=0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("", response_model=UserAdminListResponse)
def admin_list_users(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    query = db.query(User)
    if keyword:
        query = query.filter(
            (User.username.contains(keyword)) |
            (User.email.contains(keyword)) |
            (User.nickname.contains(keyword))
        )
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    # 批量查询评论数
    user_ids = [u.id for u in users]
    comment_counts = {}
    if user_ids:
        for uid, count in db.query(Comment.user_id, sqlfunc.count(Comment.id)).filter(Comment.user_id.in_(user_ids)).group_by(Comment.user_id).all():
            comment_counts[uid] = count
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "nickname": u.nickname,
                "avatar_url": u.avatar_url,
                "level": u.level,
                "points": u.points,
                "total_points": u.total_points,
                "followers_count": u.followers_count,
                "following_count": u.following_count,
                "is_active": u.is_active,
                "is_admin": u.is_admin,
                "created_at": u.created_at,
                "comment_count": comment_counts.get(u.id, 0),
            }
            for u in users
        ],
    }


@router.put("/{user_id}", response_model=UserAdminItem)
def admin_update_user(
    user_id: int,
    request: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")
    if user_id == current_user.id and request.is_active is False:
        raise PermissionDenied("不能禁用自己的账号")
    if user.is_admin and request.is_admin is False:
        raise PermissionDenied("不能撤销管理员权限")

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    if user_id == current_user.id:
        raise PermissionDenied("不能删除自己")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFound("用户")
    if user.is_admin:
        raise PermissionDenied("不能删除管理员")
    follower_ids = [f.follower_id for f in db.query(UserFollow).filter(UserFollow.following_id == user_id).all()]
    if follower_ids:
        db.query(User).filter(User.id.in_(follower_ids)).update({User.following_count: User.following_count - 1}, synchronize_session=False)
    following_ids = [f.following_id for f in db.query(UserFollow).filter(UserFollow.follower_id == user_id).all()]
    if following_ids:
        db.query(User).filter(User.id.in_(following_ids)).update({User.followers_count: User.followers_count - 1}, synchronize_session=False)
    db.delete(user)
    db.commit()
    return {"message": "用户已删除"}
