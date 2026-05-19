"""成就API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import User, Achievement, UserAchievement
from app.modules.achievement.schemas import AchievementResponse, AchievementListResponse

router = APIRouter(tags=["成就"])


@router.get("/", response_model=AchievementListResponse)
def list_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    all_achievements = db.query(Achievement).order_by(Achievement.category, Achievement.tier).all()
    user_achs = db.query(UserAchievement).filter(UserAchievement.user_id == current_user.id).all()
    user_ach_map = {ua.achievement_id: ua for ua in user_achs}

    items = []
    unlocked_count = 0
    total_points = 0
    for ach in all_achievements:
        ua = user_ach_map.get(ach.id)
        is_unlocked = ua is not None
        if is_unlocked:
            unlocked_count += 1
            total_points += ach.points
        items.append(AchievementResponse(
            id=ach.id,
            code=ach.code,
            name=ach.name if (is_unlocked or not ach.is_secret) else "???",
            description=ach.description if (is_unlocked or not ach.is_secret) else "隐藏成就",
            icon=ach.icon if (is_unlocked or not ach.is_secret) else "🔒",
            category=ach.category,
            tier=ach.tier,
            points=ach.points,
            condition_type=ach.condition_type,
            condition_value=ach.condition_value,
            is_secret=ach.is_secret,
            is_unlocked=is_unlocked,
            progress=ua.progress if ua else 0,
            unlocked_at=ua.unlocked_at if ua else None,
        ))

    return AchievementListResponse(
        total=len(items),
        items=items,
        unlocked_count=unlocked_count,
        total_points=total_points,
    )


@router.get("/my", response_model=AchievementListResponse)
def get_my_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return list_achievements(db, current_user)


@router.get("/{code}", response_model=AchievementResponse)
def get_achievement(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ach = db.query(Achievement).filter(Achievement.code == code).first()
    if not ach:
        from app.core.exceptions import NotFound
        raise NotFound("成就不存在")

    ua = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id,
        UserAchievement.achievement_id == ach.id,
    ).first()

    is_unlocked = ua is not None
    return AchievementResponse(
        id=ach.id,
        code=ach.code,
        name=ach.name if (is_unlocked or not ach.is_secret) else "???",
        description=ach.description if (is_unlocked or not ach.is_secret) else "隐藏成就",
        icon=ach.icon if (is_unlocked or not ach.is_secret) else "🔒",
        category=ach.category,
        tier=ach.tier,
        points=ach.points,
        condition_type=ach.condition_type,
        condition_value=ach.condition_value,
        is_secret=ach.is_secret,
        is_unlocked=is_unlocked,
        progress=ua.progress if ua else 0,
        unlocked_at=ua.unlocked_at if ua else None,
    )


@router.post("/check")
def check_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services.achievement_service import achievement_service
    newly_unlocked = achievement_service.check_all(db, current_user.id)
    return {"newly_unlocked": len(newly_unlocked), "achievements": newly_unlocked}
