"""Integral service - unified handling of integral rewards, deductions, and level calculations"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import User, PointLog

# Integral rule constants
POINT_RULES = {
    # Earn points
    "daily_login": {"points": 5, "daily_limit": 1, "description": "Daily login"},
    "publish_blog": {"points": 20, "daily_limit": 5, "description": "Publish blog"},
    "publish_project": {"points": 15, "daily_limit": 3, "description": "Publish project"},
    "publish_moment": {"points": 5, "daily_limit": 10, "description": "Publish moment"},
    "post_comment": {"points": 3, "daily_limit": 20, "description": "Post comment"},
    "receive_like": {"points": 5, "daily_limit": 50, "description": "Receive like"},
    "receive_favorite": {"points": 10, "daily_limit": 20, "description": "Receive favorite"},
    "receive_follow": {"points": 10, "daily_limit": 30, "description": "Receive follow"},
    "share_content": {"points": 5, "daily_limit": 10, "description": "Share content"},
    "complete_profile": {"points": 1, "daily_limit": 1, "description": "Complete profile"},
    # Deduct points
    "content_deleted": {"points": -20, "daily_limit": 0, "description": "Content deleted"},
    "comment_deleted": {"points": -10, "daily_limit": 0, "description": "Comment deleted"},
}

# Level thresholds
LEVEL_THRESHOLDS = [0, 100, 300, 900, 1500, 3000, 5000, 10000, 20000, 50000]

LEVEL_TITLES = {
    1: "新手上路",
    2: "初学乍练",
    3: "渐入佳境",
    4: "融会贯通",
    5: "出类拔萃",
    6: "技术大牛",
    7: "领域专家",
    8: "一代宗师",
    9: "传奇人物",
    10: "至尊王者",
    999: "管理员",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class PointService:
    def get_level(self, total_points: int) -> int:
        """Calculate level based on total points (max level 10)"""
        level = 1
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if total_points >= threshold:
                level = i + 1
        return level

    def get_level_title(self, level: int) -> str:
        """Get level title"""
        return LEVEL_TITLES.get(level, "Unknown")

    def get_level_progress(self, total_points: int) -> dict:
        """Get level progress information"""
        level = self.get_level(total_points)
        if level >= 10:
            return {
                "level": level,
                "current_points": total_points,
                "next_threshold": None,
                "progress": 100,
            }

        current_threshold = LEVEL_THRESHOLDS[level - 1]
        next_threshold = LEVEL_THRESHOLDS[level]
        progress = int((total_points - current_threshold) / (next_threshold - current_threshold) * 100)
        return {
            "level": level,
            "current_points": total_points,
            "current_threshold": current_threshold,
            "next_threshold": next_threshold,
            "points_needed": next_threshold - total_points,
            "progress": min(progress, 100),
        }

    def check_daily_limit(self, db: Session, user_id: int, action: str) -> bool:
        """Check if daily limit is reached for an action, return True if not reached"""
        if action not in POINT_RULES:
            return True

        rule = POINT_RULES[action]
        if rule["daily_limit"] == 0:
            return True

        today_start = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        count = db.query(PointLog).filter(
            PointLog.user_id == user_id,
            PointLog.action == action,
            PointLog.created_at >= today_start,
        ).count()

        return count < rule["daily_limit"]

    def award_points(
        self,
        db: Session,
        user_id: int,
        action: str,
        description: Optional[str] = None,
    ) -> Optional[dict]:
        """Award points, return point change info or None (limit reached/admin)"""
        if action not in POINT_RULES:
            return None

        rule = POINT_RULES[action]
        if rule["points"] <= 0:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if user.is_admin:
            return None

        if not self.check_daily_limit(db, user_id, action):
            return None

        point_change = rule["points"]
        user.points += point_change
        user.total_points += point_change

        new_level = self.get_level(user.total_points)
        level_changed = new_level != user.level
        user.level = new_level

        point_log = PointLog(
            user_id=user_id,
            action=action,
            points=point_change,
            description=description or rule["description"],
        )
        db.add(point_log)
        db.commit()

        return {
            "points_change": point_change,
            "current_points": user.points,
            "total_points": user.total_points,
            "level": user.level,
            "level_changed": level_changed,
            "action_description": rule["description"],
        }

    def deduct_points(
        self,
        db: Session,
        user_id: int,
        action: str,
        description: Optional[str] = None,
    ) -> Optional[dict]:
        """Deduct points, return point change info or None (user not found/admin)"""
        if action not in POINT_RULES:
            return None

        rule = POINT_RULES[action]
        if rule["points"] >= 0:
            return None

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if user.is_admin:
            return None

        point_change = rule["points"]
        user.points = max(0, user.points + point_change)
        user.level = self.get_level(user.total_points)

        point_log = PointLog(
            user_id=user_id,
            action=action,
            points=point_change,
            description=description or rule["description"],
        )
        db.add(point_log)
        db.commit()

        return {
            "points_change": point_change,
            "current_points": user.points,
            "total_points": user.total_points,
            "level": user.level,
            "action_description": rule["description"],
        }

    def sync_user_level(self, db: Session, user: User) -> None:
        """Synchronize user level based on total_points (admin level 999 unchanged)"""
        if user.is_admin:
            return
        user.level = self.get_level(user.total_points)
        db.commit()


point_service = PointService()
