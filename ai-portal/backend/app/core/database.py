"""
数据库引擎与会话工厂模块
使用SQLAlchemy声明式基类，SQLite启用WAL模式
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# 创建数据库引擎
# SQLite需要check_same_thread=False以支持多线程FastAPI
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # SQL 日志由 logging_config 模块控制
    pool_pre_ping=True,
)


# SQLite WAL模式自动启用
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection: object, connection_record: object) -> None:
    """
    SQLite连接建立时自动设置WAL模式
    WAL模式允许读写并发，显著提升SQLite性能
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy声明式基类，所有模型继承此类"""
    pass
