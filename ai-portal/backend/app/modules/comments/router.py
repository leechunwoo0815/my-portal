from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session
import json

from app.core.events import EventBus

from app.core.deps import get_db, get_current_user, get_optional_current_user
from app.core.exceptions import NotFound, PermissionDenied
from app.core.moderation import contains_sensitive
from app.models import Comment, User
from app.modules.comments.schemas import CommentCreate
import random
import string

router = APIRouter(tags=["评论"])


def _get_client_ip(request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/{comment_id}/like")
def like_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    ip = _get_client_ip(request) if request else "unknown"

    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise NotFound("评论")

    liked_ips = json.loads(comment.liked_ips or "[]")
    if ip in liked_ips:
        liked_ips.remove(ip)
        comment.liked_ips = json.dumps(liked_ips)
        db.query(Comment).filter(Comment.id == comment_id).update({Comment.likes_count: func.max(Comment.likes_count - 1, 0)}, synchronize_session=False)
        db.commit()
        db.refresh(comment)
        return {"likes_count": comment.likes_count, "liked": False}

    liked_ips.append(ip)
    comment.liked_ips = json.dumps(liked_ips)
    db.query(Comment).filter(Comment.id == comment_id).update({Comment.likes_count: Comment.likes_count + 1}, synchronize_session=False)
    db.commit()
    db.refresh(comment)

    return {"likes_count": comment.likes_count, "liked": True}


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise NotFound("评论")
    if comment.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权删除该评论")

    def _collect_ids(cid: int, depth: int = 0) -> list[int]:
        if depth > 10:
            return [cid]
        ids = [cid]
        for child in db.query(Comment).filter(Comment.parent_id == cid).all():
            ids += _collect_ids(child.id, depth + 1)
        return ids

    all_ids = _collect_ids(comment_id)
    db.query(Comment).filter(Comment.id.in_(all_ids)).delete(synchronize_session=False)
    db.commit()
    return {"message": f"已删除 {len(all_ids)} 条评论（含回复）"}


@router.get("/{target_type}/{target_id}")
def list_comments(
    target_type: str,
    target_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
):
    ip = _get_client_ip(request) if request else "unknown"
    all_comments = (
        db.query(Comment)
        .filter(Comment.target_type == target_type, Comment.target_id == target_id, Comment.status != "hidden")
        .order_by(Comment.created_at.desc())
        .all()
    )

    liked_ips_set = set()
    comment_map = {}
    for c in all_comments:
        ips = json.loads(c.liked_ips or "[]")
        liked = ip in ips
        if liked:
            liked_ips_set.add(c.id)
        display_name = c.user.nickname or c.user.username if c.user else c.author_name
        comment_map[c.id] = {
            "id": c.id,
            "target_type": c.target_type,
            "target_id": c.target_id,
            "parent_id": c.parent_id,
            "user_id": c.user_id,
            "author_name": display_name,
            "avatar_url": c.user.avatar_url if c.user else None,
            "level": c.user.level if c.user else 1,
            "content": c.content,
            "emoji": c.emoji,
            "likes_count": c.likes_count,
            "liked": liked,
            "created_at": c.created_at,
            "replies": [],
        }

    def _fill_replies(entry):
        for r in entry.get("replies", []):
            if r["id"] in liked_ips_set:
                r["liked"] = True
            _fill_replies(r)

    roots = []
    for c in all_comments:
        entry = comment_map[c.id]
        if c.parent_id and c.parent_id in comment_map:
            comment_map[c.parent_id]["replies"].append(entry)
        elif c.parent_id is None:
            roots.append(entry)
        else:
            roots.append(entry)

    for root in roots:
        _fill_replies(root)

    return roots


def _generate_guest_name() -> str:
    """生成随机游客名"""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    return f"游客{suffix}"


@router.post("/{target_type}/{target_id}")
def create_comment(
    target_type: str,
    target_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
):
    if current_user:
        # 已登录用户：使用注册用户名，禁止自定义
        author_name = current_user.nickname or current_user.username
        user_id = current_user.id
    else:
        # 游客：自动生成昵称，也可接受前端传入（但会被覆盖）
        author_name = _generate_guest_name()
        user_id = None

    content_clean = data.content.strip()
    status = "flagged" if contains_sensitive(content_clean) else "visible"

    comment = Comment(
        target_type=target_type,
        target_id=target_id,
        parent_id=data.parent_id,
        user_id=user_id,
        author_name=author_name,
        content=content_clean,
        emoji=data.emoji,
        likes_count=0,
        liked_ips="[]",
        status=status,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    EventBus.emit_sync("comment.created", comment)

    return {
        "id": comment.id,
        "target_type": comment.target_type,
        "target_id": comment.target_id,
        "parent_id": comment.parent_id,
        "user_id": comment.user_id,
        "author_name": comment.author_name,
        "avatar_url": current_user.avatar_url if current_user else None,
        "level": current_user.level if current_user else 1,
        "content": comment.content,
        "emoji": comment.emoji,
        "likes_count": 0,
        "liked": False,
        "created_at": comment.created_at,
        "replies": [],
    }
