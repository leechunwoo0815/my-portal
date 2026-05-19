from typing import Any, Callable
from collections import defaultdict
import asyncio
import logging

logger = logging.getLogger(__name__)


class EventBus:
    _handlers: dict[str, list[Callable]] = defaultdict(list)

    @classmethod
    def on(cls, event_name: str, handler: Callable) -> None:
        cls._handlers[event_name].append(handler)

    @classmethod
    def off(cls, event_name: str, handler: Callable) -> None:
        if event_name in cls._handlers:
            cls._handlers[event_name] = [
                h for h in cls._handlers[event_name] if h != handler
            ]

    @classmethod
    async def emit(cls, event_name: str, payload: Any = None) -> None:
        handlers = cls._handlers.get(event_name, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                logger.error(f"Event handler error for '{event_name}': {e}")

    @classmethod
    def emit_sync(cls, event_name: str, payload: Any = None) -> None:
        handlers = cls._handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Sync event handler error for '{event_name}': {e}")

    @classmethod
    def clear(cls) -> None:
        cls._handlers.clear()


EVENTS = {
    "blog.published": "博客发布",
    "blog.created": "博客创建",
    "blog.deleted": "博客删除",
    "news.published": "新闻发布",
    "news.created": "新闻创建",
    "news.deleted": "新闻删除",
    "product.published": "产品发布",
    "product.created": "产品创建",
    "product.deleted": "产品删除",
    "solution.published": "方案发布",
    "solution.created": "方案创建",
    "solution.deleted": "方案删除",
    "comment.created": "评论创建",
    "comment.deleted": "评论删除",
    "like.created": "点赞",
    "like.deleted": "取消点赞",
    "favorite.created": "收藏",
    "favorite.deleted": "取消收藏",
    "user.registered": "用户注册",
    "user.followed": "关注用户",
    "user.unfollowed": "取消关注",
    "moment.created": "动态创建",
    "moment.deleted": "动态删除",
}
