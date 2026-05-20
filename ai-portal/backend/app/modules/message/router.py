"""私信API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.deps import get_db, get_current_user
from app.core.exceptions import NotFound, PermissionDenied
from app.models import User, DirectMessage, UserFollow
from app.modules.message.schemas import (
    MessageSendRequest,
    MessageItem,
    ConversationListResponse,
)
from app.modules.notification.router import create_notification

router = APIRouter(tags=["私信"])


def _get_relationship_label(db: Session, user_id: int, other_id: int) -> str:
    """判断与对方的关系状态"""
    i_follow_him = db.query(UserFollow).filter(
        UserFollow.follower_id == user_id,
        UserFollow.following_id == other_id,
    ).first() is not None
    he_follows_me = db.query(UserFollow).filter(
        UserFollow.follower_id == other_id,
        UserFollow.following_id == user_id,
    ).first() is not None

    if i_follow_him and he_follows_me:
        return "互相关注"
    elif i_follow_him:
        return "我关注的人"
    elif he_follows_me:
        return "关注你的人"
    else:
        return "陌生人"


@router.post("/send")
def send_message(
    request: MessageSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """发送私信"""
    if request.receiver_id == current_user.id:
        raise PermissionDenied("不能给自己发私信")

    receiver = db.query(User).filter(User.id == request.receiver_id).first()
    if not receiver:
        raise NotFound("用户")
    if not receiver.is_active:
        raise PermissionDenied("该用户已被禁用")

    # 校验：文本消息必须有内容，图片消息必须有 image_url
    if request.message_type == "image":
        if not request.image_url:
            raise PermissionDenied("图片消息必须包含 image_url")
    else:
        if not request.content.strip():
            raise PermissionDenied("消息内容不能为空")

    message = DirectMessage(
        sender_id=current_user.id,
        receiver_id=request.receiver_id,
        content=request.content.strip() if request.content else "",
        message_type=request.message_type,
        image_url=request.image_url,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    create_notification(
        db, request.receiver_id, "message", "新私信",
        f"你收到 {current_user.nickname or current_user.username} 的私信",
        from_user_id=current_user.id,
    )

    return {"id": message.id, "created_at": message.created_at}


@router.get("/conversations", response_model=ConversationListResponse)
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取会话列表"""
    sent = db.query(DirectMessage.sender_id).filter(DirectMessage.sender_id == current_user.id).distinct().all()
    received = db.query(DirectMessage.receiver_id).filter(DirectMessage.receiver_id == current_user.id).distinct().all()
    partner_ids = list(set([s[0] for s in sent] + [r[0] for r in received]))

    from sqlalchemy import func as sqlfunc

    users_map = {u.id: u for u in db.query(User).filter(User.id.in_(partner_ids)).all()} if partner_ids else {}

    uid = current_user.id
    last_msgs = {}
    for pid in partner_ids:
        msg = db.query(DirectMessage).filter(
            or_(
                (DirectMessage.sender_id == uid) & (DirectMessage.receiver_id == pid),
                (DirectMessage.sender_id == pid) & (DirectMessage.receiver_id == uid),
            )
        ).order_by(DirectMessage.created_at.desc()).first()
        if msg:
            last_msgs[pid] = msg

    unread_counts = dict(
        db.query(DirectMessage.sender_id, sqlfunc.count(DirectMessage.id))
        .filter(DirectMessage.receiver_id == uid, DirectMessage.is_read == False, DirectMessage.sender_id.in_(partner_ids))
        .group_by(DirectMessage.sender_id)
        .all()
    )

    conversations = []
    for pid in partner_ids:
        partner = users_map.get(pid)
        if not partner:
            continue

        last_msg = last_msgs.get(pid)

        conversations.append({
            "user_id": partner.id,
            "username": partner.username,
            "nickname": partner.nickname,
            "avatar_url": partner.avatar_url,
            "level": partner.level,
            "bio": partner.bio,
            "last_message": "[图片]" if last_msg and last_msg.message_type == "image" else (last_msg.content[:50] if last_msg else ""),
            "last_message_time": last_msg.created_at if last_msg else partner.created_at,
            "unread_count": unread_counts.get(pid, 0),
            "relationship": _get_relationship_label(db, current_user.id, pid),
        })

    conversations.sort(key=lambda x: x["last_message_time"], reverse=True)
    return {"total": len(conversations), "items": conversations}


@router.get("/conversations/{user_id}", response_model=list[MessageItem])
def get_conversation_messages(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list:
    """获取与某用户的消息历史"""
    partner = db.query(User).filter(User.id == user_id).first()
    if not partner:
        raise NotFound("用户")

    messages = db.query(DirectMessage).filter(
        or_(
            (DirectMessage.sender_id == current_user.id) & (DirectMessage.receiver_id == user_id),
            (DirectMessage.sender_id == user_id) & (DirectMessage.receiver_id == current_user.id),
        )
    ).order_by(DirectMessage.created_at.asc()).all()

    result = []
    sender_ids = {m.sender_id for m in messages}
    senders = {u.id: u for u in db.query(User).filter(User.id.in_(sender_ids)).all()} if sender_ids else {}
    for m in messages:
        sender = senders.get(m.sender_id)
        result.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "message_type": m.message_type,
            "image_url": m.image_url,
            "is_read": m.is_read,
            "created_at": m.created_at,
            "sender_nickname": sender.nickname if sender else None,
            "sender_avatar": sender.avatar_url if sender else None,
            "sender_level": sender.level if sender else 1,
        })

    db.query(DirectMessage).filter(
        DirectMessage.sender_id == user_id,
        DirectMessage.receiver_id == current_user.id,
        DirectMessage.is_read == False,
    ).update({"is_read": True})
    db.commit()

    return result


@router.put("/read/{user_id}")
def mark_messages_read(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """标记与某用户的私信已读"""
    db.query(DirectMessage).filter(
        DirectMessage.sender_id == user_id,
        DirectMessage.receiver_id == current_user.id,
        DirectMessage.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "已标记已读"}


@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取未读私信数"""
    count = db.query(DirectMessage).filter(
        DirectMessage.receiver_id == current_user.id,
        DirectMessage.is_read == False,
    ).count()
    return {"unread_count": count}
