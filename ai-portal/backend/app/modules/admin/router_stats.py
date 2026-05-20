from datetime import datetime, timezone, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, require_admin
from app.models import User, Project, Blog, Conversation, Message, ApiCallLog, Comment, News, Product, Solution, Moment, UserLike, UserFavorite, CheckinRecord
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


@router.get("/charts")
def get_chart_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    """一次性返回所有图表数据"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

    # 1. 7 天 API 调用趋势
    trend_labels = []
    trend_data = []
    for i in range(6, -1, -1):
        day_start = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
        day_end = day_start + timedelta(days=1)
        count = db.query(ApiCallLog).filter(
            ApiCallLog.created_at >= day_start,
            ApiCallLog.created_at < day_end,
        ).count()
        trend_labels.append(day_start.strftime("%m-%d"))
        trend_data.append(count)

    # 2. 模型使用分布
    model_rows = (
        db.query(ApiCallLog.model_name, func.count(ApiCallLog.id))
        .group_by(ApiCallLog.model_name)
        .order_by(func.count(ApiCallLog.id).desc())
        .limit(6)
        .all()
    )
    model_data = [{"name": name or "未知", "value": cnt} for name, cnt in model_rows]
    # 如果没有任何数据，返回空列表
    if not model_data:
        model_data = [{"name": "暂无数据", "value": 0}]

    # 3. 内容发布统计
    content_stats = {
        "博客": db.query(Blog).filter(Blog.is_published == True).count(),
        "资讯": db.query(News).filter(News.is_published == True).count(),
        "产品": db.query(Product).filter(Product.is_published == True).count(),
        "方案": db.query(Solution).filter(Solution.is_published == True).count(),
        "项目": db.query(Project).filter(Project.is_published == True).count(),
    }
    content_labels = list(content_stats.keys())
    content_data = list(content_stats.values())

    # 4. 用户活跃度（全平台汇总）
    total_comments = db.query(Comment).count()
    total_likes = db.query(UserLike).count()
    total_favorites = db.query(UserFavorite).count()
    total_checkins = db.query(CheckinRecord).count()
    total_moments = db.query(Moment).count()
    total_blogs = db.query(Blog).count()
    user_count = max(db.query(User).count(), 1)

    # 归一化到 0-100 范围（每用户平均值 * 系数）
    activity_data = [
        min(100, total_blogs * 10 // user_count),
        min(100, total_comments * 5 // user_count),
        min(100, total_likes * 2 // user_count),
        min(100, total_favorites * 3 // user_count),
        min(100, total_checkins * 3 // user_count),
        min(100, total_moments * 5 // user_count),
    ]
    activity_indicators = ["博客", "评论", "点赞", "收藏", "签到", "动态"]

    return {
        "trend": {"labels": trend_labels, "data": trend_data},
        "models": model_data,
        "content": {"labels": content_labels, "data": content_data},
        "activity": {"indicators": activity_indicators, "data": activity_data},
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
