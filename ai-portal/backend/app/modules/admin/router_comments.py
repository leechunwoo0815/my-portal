from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.models import User, Comment, AuditLog

router = APIRouter(tags=["后台管理"])


@router.get("")
def admin_list_comments(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    status: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = db.query(Comment)
    if user_id is not None:
        query = query.filter(Comment.user_id == user_id)
    if status:
        query = query.filter(Comment.status == status)
    query = query.order_by(Comment.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    parent_ids = {c.parent_id for c in items if c.parent_id}
    parents = {}
    if parent_ids:
        for p in db.query(Comment).filter(Comment.id.in_(parent_ids)).all():
            parents[p.id] = {"author_name": p.author_name, "content": p.content[:80]}

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": c.id,
                "target_type": c.target_type,
                "target_id": c.target_id,
                "parent_id": c.parent_id,
                "parent": parents.get(c.parent_id),
                "user_id": c.user_id,
                "author_name": c.author_name,
                "avatar_url": c.user.avatar_url if c.user else None,
                "level": c.user.level if c.user else 1,
                "content": c.content,
                "emoji": c.emoji,
                "likes_count": c.likes_count,
                "status": c.status,
                "created_at": c.created_at,
            }
            for c in items
        ],
    }


@router.delete("/{comment_id}")
def admin_delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise NotFound("评论")

    def _collect_ids(cid: int, depth: int = 0) -> list[int]:
        if depth > 10:
            return [cid]
        ids = [cid]
        for child in db.query(Comment).filter(Comment.parent_id == cid).all():
            ids += _collect_ids(child.id, depth + 1)
        return ids

    all_ids = _collect_ids(comment_id)
    db.query(Comment).filter(Comment.id.in_(all_ids)).delete(synchronize_session=False)
    db.add(AuditLog(admin_id=current_user.id, action="delete_comment", target_type="comment", target_id=comment_id, detail=f"删除 {len(all_ids)} 条评论"))
    db.commit()
    return {"message": f"已删除 {len(all_ids)} 条评论（含回复）"}


@router.put("/{comment_id}/status")
def admin_update_comment_status(
    comment_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """修改评论状态（visible/hidden/flagged）"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise NotFound("评论")
    new_status = body.get("status", "visible")
    if new_status not in ("visible", "hidden", "flagged"):
        from app.core.exceptions import BadRequest
        raise BadRequest("状态值无效，必须是 visible/hidden/flagged")
    comment.status = new_status
    db.add(AuditLog(admin_id=current_user.id, action="moderate_comment", target_type="comment", target_id=comment_id, detail=f"状态变更为 {new_status}"))
    db.commit()
    return {"message": f"评论状态已更新为 {new_status}", "status": new_status}
