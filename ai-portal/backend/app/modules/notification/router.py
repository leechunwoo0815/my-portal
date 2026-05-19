"""通知API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import User, Notification
from app.modules.notification.schemas import (
    NotificationItem,
    NotificationListResponse,
)

router = APIRouter(tags=["通知"])


def create_notification(
    db: Session,
    user_id: int,
    notif_type: str,
    title: str,
    content: str = None,
    from_user_id: int = None,
    target_type: str = None,
    target_id: int = None,
) -> Notification:
    """创建通知（内部函数）"""
    notif = Notification(
        user_id=user_id,
        type=notif_type,
        title=title,
        content=content,
        from_user_id=from_user_id,
        target_type=target_type,
        target_id=target_id,
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


@router.get("", response_model=NotificationListResponse)
def list_notifications(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    notif_type: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取通知列表"""
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if notif_type:
        query = query.filter(Notification.type == notif_type)

    total = query.count()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()

    notifications = query.order_by(Notification.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    user_ids = {n.from_user_id for n in notifications if n.from_user_id}
    users = {u.id: u for u in db.query(User).filter(User.id.in_(user_ids)).all()} if user_ids else {}

    items = []
    for n in notifications:
        from_user = users.get(n.from_user_id)
        items.append({
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "from_user_id": n.from_user_id,
            "from_username": from_user.username if from_user else None,
            "from_nickname": from_user.nickname if from_user else None,
            "from_avatar": from_user.avatar_url if from_user else None,
            "from_level": from_user.level if from_user else 1,
            "target_type": n.target_type,
            "target_id": n.target_id,
            "is_read": n.is_read,
            "created_at": n.created_at,
        })

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "unread_count": unread_count,
        "items": items,
    }


@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """标记单条通知已读"""
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if notif:
        notif.is_read = True
        db.commit()
    return {"message": "已标记已读"}


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """全部标记已读"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "全部已标记已读"}


@router.get("/unread-count")
def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取未读通知数"""
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).count()
    return {"unread_count": count}
