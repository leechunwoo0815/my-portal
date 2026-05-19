from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, require_admin
from app.models import User, Project, Blog, Conversation, Message, ApiCallLog, Comment
from app.modules.admin.schemas import DashboardStats, SystemMonitor
from app.services.monitor import get_system_metrics, get_system_info, get_process_info

router = APIRouter(tags=["后台管理"])


@router.get("", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, int]:
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0, tzinfo=None
    )
    today_calls = db.query(ApiCallLog).filter(ApiCallLog.created_at >= today_start).count()
    today_tokens = (
        db.query(func.sum(ApiCallLog.total_tokens))
        .filter(ApiCallLog.created_at >= today_start)
        .scalar() or 0
    )
    return {
        "total_conversations": db.query(Conversation).count(),
        "total_messages": db.query(Message).count(),
        "total_projects": db.query(Project).count(),
        "total_blogs": db.query(Blog).count(),
        "total_comments": db.query(Comment).count(),
        "today_api_calls": today_calls,
        "today_token_usage": int(today_tokens),
        "total_users": db.query(User).count(),
    }


@router.get("/monitor", response_model=SystemMonitor)
def get_system_monitor(
    current_user: User = Depends(require_admin),
) -> SystemMonitor:
    return get_system_metrics()


@router.get("/monitor/info")
def get_system_information(
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    return get_system_info()


@router.get("/monitor/process")
def get_backend_process_info(
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    import os
    return get_process_info(pid=os.getpid())
