"""成就检查服务"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Achievement, UserAchievement, Blog, Comment, UserLike, UserFollow, Moment, UserFavorite, User
from app.services.point_service import point_service

logger = logging.getLogger(__name__)

ACHIEVEMENT_SEEDS = [
    {"code": "first_blog", "name": "初出茅庐", "description": "发布首篇博客", "icon": "✍️", "category": "content", "tier": "bronze", "points": 10, "condition_type": "count", "condition_value": 1},
    {"code": "blog_5", "name": "笔耕不辍", "description": "发布5篇博客", "icon": "📝", "category": "content", "tier": "silver", "points": 30, "condition_type": "count", "condition_value": 5},
    {"code": "blog_20", "name": "技术大牛", "description": "发布20篇博客", "icon": "🏆", "category": "content", "tier": "gold", "points": 100, "condition_type": "count", "condition_value": 20},
    {"code": "blog_50", "name": "传道授业", "description": "发布50篇博客", "icon": "👑", "category": "content", "tier": "diamond", "points": 300, "condition_type": "count", "condition_value": 50},
    {"code": "first_comment", "name": "互动新人", "description": "发表首条评论", "icon": "💬", "category": "social", "tier": "bronze", "points": 5, "condition_type": "count", "condition_value": 1},
    {"code": "comment_50", "name": "评论区大佬", "description": "发表50条评论", "icon": "🗣️", "category": "social", "tier": "silver", "points": 50, "condition_type": "count", "condition_value": 50},
    {"code": "like_10", "name": "初获认可", "description": "获得10个赞", "icon": "👍", "category": "social", "tier": "bronze", "points": 10, "condition_type": "accumulation", "condition_value": 10},
    {"code": "like_100", "name": "人气之星", "description": "获得100个赞", "icon": "⭐", "category": "social", "tier": "gold", "points": 100, "condition_type": "accumulation", "condition_value": 100},
    {"code": "like_1000", "name": "万众瞩目", "description": "获得1000个赞", "icon": "🌟", "category": "social", "tier": "diamond", "points": 500, "condition_type": "accumulation", "condition_value": 1000},
    {"code": "follower_10", "name": "小有名气", "description": "10人关注", "icon": "👥", "category": "social", "tier": "bronze", "points": 10, "condition_type": "count", "condition_value": 10},
    {"code": "follower_100", "name": "技术网红", "description": "100人关注", "icon": "🔥", "category": "social", "tier": "gold", "points": 100, "condition_type": "count", "condition_value": 100},
    {"code": "checkin_7", "name": "坚持一周", "description": "连续签到7天", "icon": "📅", "category": "contribution", "tier": "bronze", "points": 15, "condition_type": "count", "condition_value": 7},
    {"code": "checkin_30", "name": "月度全勤", "description": "连续签到30天", "icon": "📆", "category": "contribution", "tier": "silver", "points": 50, "condition_type": "count", "condition_value": 30},
    {"code": "checkin_100", "name": "百日修行", "description": "连续签到100天", "icon": "🧘", "category": "contribution", "tier": "diamond", "points": 300, "condition_type": "count", "condition_value": 100},
    {"code": "favorite_10", "name": "收藏达人", "description": "收藏10篇内容", "icon": "🔖", "category": "contribution", "tier": "bronze", "points": 10, "condition_type": "count", "condition_value": 10},
    {"code": "moment_10", "name": "动态达人", "description": "发布10条动态", "icon": "💭", "category": "content", "tier": "bronze", "points": 10, "condition_type": "count", "condition_value": 10},
    {"code": "early_adopter", "name": "早期用户", "description": "注册前100名", "icon": "🚀", "category": "special", "tier": "gold", "points": 50, "condition_type": "special", "condition_value": 100},
    {"code": "profile_complete", "name": "完美档案", "description": "完善个人资料", "icon": "📋", "category": "contribution", "tier": "bronze", "points": 10, "condition_type": "special", "condition_value": 1},
    {"code": "share_10", "name": "传播之星", "description": "分享10次", "icon": "🔗", "category": "contribution", "tier": "bronze", "points": 10, "condition_type": "count", "condition_value": 10},
    {"code": "all_categories", "name": "全能作者", "description": "在所有分类发布过", "icon": "🌈", "category": "special", "tier": "diamond", "points": 200, "condition_type": "special", "condition_value": 1},
]


class AchievementService:
    def seed_achievements(self, db: Session):
        for seed in ACHIEVEMENT_SEEDS:
            existing = db.query(Achievement).filter(Achievement.code == seed["code"]).first()
            if not existing:
                ach = Achievement(**seed)
                db.add(ach)
        db.commit()

    def check_all(self, db: Session, user_id: int) -> list[dict]:
        newly_unlocked = []
        achievements = db.query(Achievement).all()
        user_achs = db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
        unlocked_codes = set()

        for ua in user_achs:
            ach = db.query(Achievement).filter(Achievement.id == ua.achievement_id).first()
            if ach:
                unlocked_codes.add(ach.code)

        for ach in achievements:
            if ach.code in unlocked_codes:
                continue

            progress = self._get_progress(db, user_id, ach)
            if progress >= ach.condition_value:
                ua = UserAchievement(user_id=user_id, achievement_id=ach.id, progress=progress)
                db.add(ua)
                if not db.query(User).filter(User.id == user_id).first().is_admin:
                    point_service.award_points(db, user_id, "achievement_unlock", f"解锁成就: {ach.name}")
                newly_unlocked.append({"code": ach.code, "name": ach.name, "icon": ach.icon, "tier": ach.tier})
            elif progress > 0:
                existing_ua = db.query(UserAchievement).filter(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == ach.id,
                ).first()
                if existing_ua:
                    existing_ua.progress = progress

        db.commit()
        return newly_unlocked

    def _get_progress(self, db: Session, user_id: int, ach: Achievement) -> int:
        code = ach.code

        if code.startswith("blog_"):
            count = db.query(func.count(Blog.id)).filter(Blog.author_id == user_id).scalar() or 0
            return count
        elif code == "first_blog":
            return db.query(func.count(Blog.id)).filter(Blog.author_id == user_id).scalar() or 0
        elif code.startswith("comment_"):
            return db.query(func.count(Comment.id)).filter(Comment.user_id == user_id).scalar() or 0
        elif code == "first_comment":
            return db.query(func.count(Comment.id)).filter(Comment.user_id == user_id).scalar() or 0
        elif code.startswith("like_"):
            return db.query(func.sum(Blog.likes_count)).filter(Blog.author_id == user_id).scalar() or 0
        elif code.startswith("follower_"):
            return db.query(func.count(UserFollow.id)).filter(UserFollow.following_id == user_id).scalar() or 0
        elif code.startswith("checkin_"):
            user = db.query(User).filter(User.id == user_id).first()
            return user.continuous_checkin_days if user and hasattr(user, 'continuous_checkin_days') else 0
        elif code.startswith("favorite_"):
            return db.query(func.count(UserFavorite.id)).filter(UserFavorite.user_id == user_id).scalar() or 0
        elif code.startswith("moment_"):
            return db.query(func.count(Moment.id)).filter(Moment.user_id == user_id).scalar() or 0
        elif code == "early_adopter":
            rank = db.query(func.count(User.id)).filter(User.id <= user_id).scalar() or 999
            return 1 if rank <= ach.condition_value else 0
        elif code == "profile_complete":
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.nickname and user.bio and user.avatar_url:
                return 1
            return 0
        elif code == "share_10":
            return 0
        elif code == "all_categories":
            cats = db.query(Blog.category).filter(Blog.author_id == user_id, Blog.category != None).distinct().count()
            all_cats = db.query(Blog.category).filter(Blog.category != None).distinct().count()
            return 1 if all_cats > 0 and cats >= all_cats else 0
        return 0


achievement_service = AchievementService()
