"""签到API"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.events import EventBus
from app.models import User
from app.models.checkin import CheckinRecord
from app.modules.checkin.schemas import (
    CheckinResponse,
    CheckinStatusResponse,
    CheckinCalendarResponse,
    CheckinCalendarItem,
    CheckinRankingResponse,
    CheckinRankingItem,
)
from app.services.point_service import point_service

router = APIRouter(tags=["签到"])

BONUS_RULES = {
    7: 10,
    30: 50,
    100: 200,
}


@router.post("/", response_model=CheckinResponse)
def do_checkin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    existing = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id,
        CheckinRecord.checkin_date == today,
    ).first()

    if existing:
        return CheckinResponse(
            success=False,
            message="今日已签到",
            points_awarded=0,
            continuous_days=existing.continuous_days,
        )

    yesterday = today - timedelta(days=1)
    yesterday_record = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id,
        CheckinRecord.checkin_date == yesterday,
    ).first()

    continuous_days = (yesterday_record.continuous_days + 1) if yesterday_record else 1

    bonus_points = 0
    for days, bonus in BONUS_RULES.items():
        if continuous_days == days:
            bonus_points = bonus
            break

    base_points = 5
    total_points = base_points + bonus_points

    record = CheckinRecord(
        user_id=current_user.id,
        checkin_date=today,
        continuous_days=continuous_days,
        points_awarded=total_points,
    )
    db.add(record)

    if hasattr(current_user, 'continuous_checkin_days'):
        current_user.continuous_checkin_days = continuous_days
    if hasattr(current_user, 'last_checkin_date'):
        current_user.last_checkin_date = today

    if not current_user.is_admin:
        point_service.award_points(db, current_user.id, "daily_checkin", "每日签到")
        if bonus_points > 0:
            point_service.award_points(db, current_user.id, "checkin_bonus", f"连续签到{continuous_days}天奖励")

    db.commit()

    EventBus.emit_sync("checkin.done", type('Payload', (), {'user_id': current_user.id, 'continuous_days': continuous_days})())

    return CheckinResponse(
        success=True,
        message="签到成功！",
        points_awarded=total_points,
        continuous_days=continuous_days,
        bonus_points=bonus_points,
    )


@router.get("/status", response_model=CheckinStatusResponse)
def get_checkin_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()
    existing = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id,
        CheckinRecord.checkin_date == today,
    ).first()

    return CheckinStatusResponse(
        is_checked_in=existing is not None,
        continuous_days=existing.continuous_days if existing else (current_user.continuous_checkin_days if hasattr(current_user, 'continuous_checkin_days') else 0),
        last_checkin_date=current_user.last_checkin_date if hasattr(current_user, 'last_checkin_date') else None,
    )


@router.get("/calendar", response_model=CheckinCalendarResponse)
def get_checkin_calendar(
    year: int = Query(...),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    import calendar
    _, days_in_month = calendar.monthrange(year, month)

    records = db.query(CheckinRecord).filter(
        CheckinRecord.user_id == current_user.id,
        func.strftime('%Y', CheckinRecord.checkin_date) == str(year),
        func.strftime('%m', CheckinRecord.checkin_date) == f'{month:02d}',
    ).all()

    checked_dates = {r.checkin_date for r in records}

    days = []
    for day in range(1, days_in_month + 1):
        d = date(year, month, day)
        days.append(CheckinCalendarItem(date=d, is_checked_in=d in checked_dates))

    return CheckinCalendarResponse(
        year=year,
        month=month,
        days=days,
        continuous_days=current_user.continuous_checkin_days if hasattr(current_user, 'continuous_checkin_days') else 0,
    )


@router.get("/ranking", response_model=CheckinRankingResponse)
def get_checkin_ranking(
    db: Session = Depends(get_db),
):
    users = db.query(User).filter(User.is_active == True).order_by(
        User.continuous_checkin_days.desc() if hasattr(User, 'continuous_checkin_days') else User.id
    ).limit(20).all()

    items = [
        CheckinRankingItem(
            user_id=u.id,
            username=u.username,
            nickname=u.nickname,
            avatar_url=u.avatar_url,
            continuous_days=u.continuous_checkin_days if hasattr(u, 'continuous_checkin_days') else 0,
        )
        for u in users
    ]

    return CheckinRankingResponse(items=items, total=len(items))
