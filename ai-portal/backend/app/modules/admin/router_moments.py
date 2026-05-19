from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.models import User, Moment, Comment, UserLike, UserFavorite

router = APIRouter(tags=["后台管理"])


@router.get("")
def admin_list_moments(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """动态管理列表：管理员看全部，可按用户筛选"""
    query = db.query(Moment)
    if user_id is not None:
        query = query.filter(Moment.user_id == user_id)
    query = query.order_by(Moment.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    # 批量查询用户信息
    user_ids = {m.user_id for m in items}
    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": m.id,
                "user_id": m.user_id,
                "content": m.content,
                "images": m.images or [],
                "moment_type": m.moment_type,
                "likes_count": m.likes_count,
                "comments_count": m.comments_count,
                "is_public": m.is_public,
                "created_at": m.created_at,
                "author": {
                    "user_id": users_map[m.user_id].id,
                    "username": users_map[m.user_id].username,
                    "nickname": users_map[m.user_id].nickname,
                    "avatar_url": users_map[m.user_id].avatar_url,
                    "level": users_map[m.user_id].level,
                } if m.user_id in users_map else None,
            }
            for m in items
        ],
    }


@router.delete("/{moment_id}")
def admin_delete_moment(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """管理员删除动态"""
    moment = db.query(Moment).filter(Moment.id == moment_id).first()
    if not moment:
        raise NotFound("动态")

    # 删除关联数据
    db.query(Comment).filter(Comment.target_type == "moment", Comment.target_id == moment_id).delete(synchronize_session=False)
    db.query(UserLike).filter(UserLike.target_type == "moment", UserLike.target_id == moment_id).delete(synchronize_session=False)
    db.query(UserFavorite).filter(UserFavorite.target_type == "moment", UserFavorite.target_id == moment_id).delete(synchronize_session=False)
    db.delete(moment)
    db.commit()
    return {"message": "动态已删除"}
