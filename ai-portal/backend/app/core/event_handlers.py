"""
事件订阅注册 - 连接 EventBus 与各业务模块
MD 要求：blog.published → 积分+通知, user.registered → 欢迎通知, like.created → 通知
"""
import logging
from app.core.events import EventBus
from app.core.database import SessionLocal
from app.services.point_service import point_service

logger = logging.getLogger(__name__)


def _get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def on_blog_published(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'author_id') and payload.author_id:
            point_service.award_points(db, payload.author_id, "publish_blog", "发布博客")
            from app.models import Notification
            from app.models.user import utc_now
            followers = db.query(Notification).filter(
                Notification.type == "follow",
            ).first()
            if not followers:
                pass
        db.close()
    except Exception as e:
        logger.error(f"on_blog_published error: {e}")


def on_news_published(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'author_id') and payload.author_id:
            point_service.award_points(db, payload.author_id, "publish_blog", "发布新闻")
        db.close()
    except Exception as e:
        logger.error(f"on_news_published error: {e}")


def on_project_published(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'author_id') and payload.author_id:
            point_service.award_points(db, payload.author_id, "publish_project", "发布项目")
        db.close()
    except Exception as e:
        logger.error(f"on_project_published error: {e}")


def on_moment_created(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'author_id') and payload.author_id:
            point_service.award_points(db, payload.author_id, "publish_moment", "发布动态")
        db.close()
    except Exception as e:
        logger.error(f"on_moment_created error: {e}")


def on_comment_created(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'user_id') and payload.user_id:
            point_service.award_points(db, payload.user_id, "post_comment", "发表评论")
            if hasattr(payload, 'target_type') and hasattr(payload, 'target_id'):
                from app.models import Notification, Blog, News, Product, Solution
                target_model_map = {
                    "blog": Blog, "news": News, "product": Product, "solution": Solution,
                }
                model_cls = target_model_map.get(payload.target_type)
                if model_cls:
                    target = db.query(model_cls).filter(model_cls.id == payload.target_id).first()
                    if target and target.author_id != payload.user_id:
                        notif = Notification(
                            user_id=target.author_id,
                            type="comment",
                            title="收到新评论",
                            content=f"你的{payload.target_type}收到了一条新评论",
                            from_user_id=payload.user_id,
                            target_type=payload.target_type,
                            target_id=payload.target_id,
                        )
                        db.add(notif)
                        db.commit()
        db.close()
    except Exception as e:
        logger.error(f"on_comment_created error: {e}")


def on_like_created(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'user_id') and hasattr(payload, 'target_type') and hasattr(payload, 'target_id'):
            point_service.award_points(db, payload.user_id, "receive_like", "获得点赞")
            from app.models import Notification, Blog, News, Product, Solution, Moment
            target_model_map = {
                "blog": Blog, "news": News, "product": Product, "solution": Solution, "moment": Moment,
            }
            model_cls = target_model_map.get(payload.target_type)
            if model_cls:
                target = db.query(model_cls).filter(model_cls.id == payload.target_id).first()
                if target and hasattr(target, 'author_id') and target.author_id != payload.user_id:
                    notif = Notification(
                        user_id=target.author_id,
                        type="like",
                        title="收到点赞",
                        content=f"你的{payload.target_type}被点赞了",
                        from_user_id=payload.user_id,
                        target_type=payload.target_type,
                        target_id=payload.target_id,
                    )
                    db.add(notif)
                    db.commit()
        db.close()
    except Exception as e:
        logger.error(f"on_like_created error: {e}")


def on_favorite_created(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'user_id') and hasattr(payload, 'target_type') and hasattr(payload, 'target_id'):
            point_service.award_points(db, payload.user_id, "receive_favorite", "获得收藏")
            from app.models import Notification, Blog, News, Product, Solution
            target_model_map = {
                "blog": Blog, "news": News, "product": Product, "solution": Solution,
            }
            model_cls = target_model_map.get(payload.target_type)
            if model_cls:
                target = db.query(model_cls).filter(model_cls.id == payload.target_id).first()
                if target and hasattr(target, 'author_id') and target.author_id != payload.user_id:
                    notif = Notification(
                        user_id=target.author_id,
                        type="favorite",
                        title="收到收藏",
                        content=f"你的{payload.target_type}被收藏了",
                        from_user_id=payload.user_id,
                        target_type=payload.target_type,
                        target_id=payload.target_id,
                    )
                    db.add(notif)
                    db.commit()
        db.close()
    except Exception as e:
        logger.error(f"on_favorite_created error: {e}")


def on_user_followed(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'following_id'):
            point_service.award_points(db, payload.following_id, "receive_follow", "获得关注")
            from app.models import Notification
            follower_id = getattr(payload, 'follower_id', None)
            notif = Notification(
                user_id=payload.following_id,
                type="follow",
                title="新粉丝",
                content="有人关注了你",
                from_user_id=follower_id,
            )
            db.add(notif)
            db.commit()
        db.close()
    except Exception as e:
        logger.error(f"on_user_followed error: {e}")


def on_user_registered(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'id'):
            from app.models import Notification
            notif = Notification(
                user_id=payload.id,
                type="system",
                title="欢迎加入",
                content="欢迎注册 AI 技术门户！开始你的技术之旅吧。",
            )
            db.add(notif)
            db.commit()
        db.close()
    except Exception as e:
        logger.error(f"on_user_registered error: {e}")


def on_content_deleted(payload):
    try:
        db = _get_db()
        if payload and hasattr(payload, 'author_id') and payload.author_id:
            point_service.deduct_points(db, payload.author_id, "content_deleted", "内容被删除")
        db.close()
    except Exception as e:
        logger.error(f"on_content_deleted error: {e}")


def register_event_handlers():
    EventBus.on("blog.published", on_blog_published)
    EventBus.on("blog.created", on_blog_published)
    EventBus.on("blog.deleted", on_content_deleted)
    EventBus.on("news.published", on_news_published)
    EventBus.on("news.created", on_news_published)
    EventBus.on("news.deleted", on_content_deleted)
    EventBus.on("product.published", on_project_published)
    EventBus.on("product.created", on_project_published)
    EventBus.on("product.deleted", on_content_deleted)
    EventBus.on("solution.published", on_project_published)
    EventBus.on("solution.created", on_project_published)
    EventBus.on("solution.deleted", on_content_deleted)
    EventBus.on("moment.created", on_moment_created)
    EventBus.on("moment.deleted", on_content_deleted)
    EventBus.on("comment.created", on_comment_created)
    EventBus.on("like.created", on_like_created)
    EventBus.on("favorite.created", on_favorite_created)
    EventBus.on("user.registered", on_user_registered)
    EventBus.on("user.followed", on_user_followed)
    logger.info("Event handlers registered successfully")
