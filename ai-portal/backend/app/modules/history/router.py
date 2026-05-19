"""阅读历史API路由"""
from typing import Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import User, Blog, News
from app.models.history import ReadingHistory

router = APIRouter(tags=["阅读历史"])

CONTENT_MODELS = {
    "blog": Blog,
    "news": News,
}


@router.post("/")
def record_read(
    content_type: str,
    content_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """记录阅读历史"""
    existing = db.query(ReadingHistory).filter(
        ReadingHistory.user_id == user.id,
        ReadingHistory.content_type == content_type,
        ReadingHistory.content_id == content_id,
    ).first()
    if existing:
        from datetime import datetime
        existing.read_at = datetime.utcnow()
    else:
        record = ReadingHistory(
            user_id=user.id,
            content_type=content_type,
            content_id=content_id,
        )
        db.add(record)
        count = db.query(ReadingHistory).filter(ReadingHistory.user_id == user.id).count()
        if count > 500:
            oldest = db.query(ReadingHistory).filter(
                ReadingHistory.user_id == user.id
            ).order_by(ReadingHistory.read_at.asc()).limit(count - 500).all()
            for r in oldest:
                db.delete(r)
    db.commit()
    return {"message": "ok"}


@router.get("/")
def list_history(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    content_type: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """获取阅读历史"""
    query = db.query(ReadingHistory).filter(ReadingHistory.user_id == user.id)
    if content_type:
        query = query.filter(ReadingHistory.content_type == content_type)
    total = query.count()
    items = query.order_by(ReadingHistory.read_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    result = []
    for item in items:
        model = CONTENT_MODELS.get(item.content_type)
        title = None
        if model:
            obj = db.query(model).filter(model.id == item.content_id).first()
            if obj:
                title = getattr(obj, 'title', None)
        result.append({
            "id": item.id,
            "content_type": item.content_type,
            "content_id": item.content_id,
            "content_title": title,
            "read_at": item.read_at,
        })

    return {"total": total, "page": page, "page_size": page_size, "items": result}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(
    content_type: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    """清空阅读历史"""
    query = db.query(ReadingHistory).filter(ReadingHistory.user_id == user.id)
    if content_type:
        query = query.filter(ReadingHistory.content_type == content_type)
    query.delete()
    db.commit()
