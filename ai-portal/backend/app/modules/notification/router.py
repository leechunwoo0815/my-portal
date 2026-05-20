"""通知API"""
import json
import asyncio
import logging
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import decode_access_token
from app.models import User, Notification
from app.modules.notification.schemas import (
    NotificationItem,
    NotificationListResponse,
)

logger = logging.getLogger("ai-portal.notification")

router = APIRouter(tags=["通知"])

# ---- WebSocket 连接管理器 ----
class ConnectionManager:
    def __init__(self):
        self._connections: dict[int, list[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self._connections.setdefault(user_id, []).append(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        conns = self._connections.get(user_id, [])
        if ws in conns:
            conns.remove(ws)
        if not conns:
            self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, data: dict):
        conns = self._connections.get(user_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

manager = ConnectionManager()


def push_notification(user_id: int, notif_data: dict):
    """异步推送通知到 WebSocket（在同步上下文中调用）"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(manager.send_to_user(user_id, notif_data))
        else:
            loop.run_until_complete(manager.send_to_user(user_id, notif_data))
    except RuntimeError:
        pass  # 没有事件循环时跳过


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

    # WebSocket 实时推送
    push_notification(user_id, {
        "type": "notification",
        "data": {
            "id": notif.id,
            "type": notif.type,
            "title": notif.title,
            "content": notif.content,
            "is_read": False,
        },
    })

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


@router.websocket("/ws")
async def notification_ws(websocket: WebSocket):
    """WebSocket 实时通知推送
    连接时通过 query 参数传 token: /api/v1/notification/ws?token=xxx
    """
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="缺少 token")
        return

    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=4001, reason="token 无效")
        return

    user_id_str = payload.get("sub")
    try:
        user_id = int(user_id_str)
    except (TypeError, ValueError):
        await websocket.close(code=4001, reason="token 格式错误")
        return

    await manager.connect(user_id, websocket)
    logger.info("WebSocket 通知连接: user_id=%d", user_id)
    try:
        while True:
            # 保持连接，接收心跳
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(user_id, websocket)
        logger.info("WebSocket 通知断开: user_id=%d", user_id)
