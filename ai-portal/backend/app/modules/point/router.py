"""积分API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import User, PointLog
from app.modules.point.schemas import (
    PointLogItem,
    PointLogListResponse,
    PointProgressResponse,
)
from app.services.point_service import point_service, LEVEL_TITLES

router = APIRouter(tags=["积分"])


@router.get("/logs", response_model=PointLogListResponse)
def list_point_logs(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取积分记录"""
    query = db.query(PointLog).filter(PointLog.user_id == current_user.id)
    total = query.count()
    logs = query.order_by(PointLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        {
            "id": log.id,
            "action": log.action,
            "points": log.points,
            "description": log.description,
            "created_at": log.created_at,
        }
        for log in logs
    ]

    return {"total": total, "page": page, "page_size": page_size, "items": items}


@router.get("/progress", response_model=PointProgressResponse)
def get_point_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """获取积分进度"""
    progress = point_service.get_level_progress(current_user.total_points)
    progress["total_points"] = current_user.total_points
    progress["level_title"] = LEVEL_TITLES.get(progress["level"], "未知")
    return progress


@router.get("/ranking")
def get_point_ranking(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """获取积分排行榜"""
    query = db.query(User).filter(User.is_active == True, User.is_admin == False)
    total = query.count()
    users = query.order_by(User.total_points.desc()).offset((page - 1) * page_size).limit(page_size).all()

    items = [
        {
            "user_id": u.id,
            "username": u.username,
            "nickname": u.nickname,
            "avatar_url": u.avatar_url,
            "level": u.level,
            "level_title": LEVEL_TITLES.get(u.level, "新手上路"),
            "total_points": u.total_points,
        }
        for u in users
    ]

    return {"total": total, "page": page, "page_size": page_size, "items": items}
