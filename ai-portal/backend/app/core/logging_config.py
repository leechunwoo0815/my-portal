"""
结构化日志配置模块
提供统一的日志格式、输出目标和日志级别管理
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone

from app.core.config import settings


def setup_logging(debug: bool = False) -> None:
    log_level_str = settings.LOG_LEVEL.upper() if hasattr(settings, 'LOG_LEVEL') else None
    if log_level_str:
        level = getattr(logging, log_level_str, logging.DEBUG if debug else logging.INFO)
    else:
        level = logging.DEBUG if debug else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout if debug else sys.stderr)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, "backend.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(handler)
    root.propagate = False

    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.setLevel(logging.DEBUG if debug else logging.WARNING)
    sql_logger.handlers.clear()
    sql_logger.addHandler(file_handler)
    sql_logger.addHandler(handler)
    sql_logger.propagate = False

    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        u_logger = logging.getLogger(name)
        u_logger.handlers.clear()
        u_logger.addHandler(file_handler)
        u_logger.addHandler(handler)
        u_logger.setLevel(logging.INFO if debug else logging.WARNING)
        u_logger.propagate = False

    for name in ("httpx", "httpcore", "chromadb", "urllib3"):
        lib = logging.getLogger(name)
        lib.setLevel(logging.WARNING)
        lib.propagate = False

    logger = logging.getLogger("ai-portal")
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False
    logger.info("日志系统初始化完成" if debug else "日志系统初始化（生产模式）")
