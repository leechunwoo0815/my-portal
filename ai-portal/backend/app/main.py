"""
FastAPI应用入口 - 创建应用实例、自动发现路由、配置中间件
生产环境禁用Swagger UI，内存优化优先
"""

import os
import re
import time
import uuid
import importlib
import pkgutil
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base
from app.core.security import get_password_hash
from app.core.exceptions import AppException
from app.core.logging_config import setup_logging
from app.models import User

# 初始化日志系统
setup_logging(debug=settings.DEBUG)
logger = logging.getLogger("ai-portal")


# ============================================================
# 生命周期管理
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动中...")
    Base.metadata.create_all(bind=engine)

    from sqlalchemy.orm import Session
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        admin = db.query(User).filter(
            User.username == settings.ADMIN_USERNAME
        ).first()

        if not admin:
            if settings.ADMIN_PASSWORD.startswith("TODO:"):
                logger.warning("管理员密码未修改，请修改.env文件中的ADMIN_PASSWORD")

            admin = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.commit()
            logger.info("默认管理员已创建: %s", settings.ADMIN_USERNAME)
        else:
            logger.info("管理员账号已存在: %s", settings.ADMIN_USERNAME)
    except Exception as e:
        logger.error("初始化管理员失败: %s", e, exc_info=True)
        db.rollback()
    finally:
        db.close()

    # 自动发现并导入所有模块的模型（确保表被创建）
    import app.modules as modules_pkg
    loaded = []
    for _, module_name, _ in pkgutil.iter_modules(modules_pkg.__path__):
        try:
            m = importlib.import_module(f"app.modules.{module_name}.models")
            loaded.append(module_name)
        except ImportError:
            pass
    if loaded:
        logger.info("已加载模块模型: %s", ", ".join(loaded))

    # 确保目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.BACKUP_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

    if settings.SECRET_KEY == "change-me-in-production-use-a-strong-random-key":
        logger.warning("⚠️ 使用默认SECRET_KEY，请在.env中设置随机密钥！")
    if settings.ADMIN_PASSWORD == "admin123":
        logger.warning("⚠️ 使用默认管理员密码，请在.env中修改ADMIN_PASSWORD！")

    from app.core.event_handlers import register_event_handlers
    register_event_handlers()

    try:
        from app.services.achievement_service import achievement_service
        db2 = SessionLocal()
        achievement_service.seed_achievements(db2)
        db2.close()
        logger.info("成就种子数据已初始化")
    except Exception as e:
        logger.warning("成就种子初始化跳过: %s", e)

    logger.info("%s v%s 启动成功", settings.APP_NAME, settings.APP_VERSION)
    logger.info("调试模式: %s, 数据库: %s", settings.DEBUG, re.sub(r"://([^@]+)@", "://***@", settings.DATABASE_URL))

    yield

    logger.info("应用正在关闭...")
    engine.dispose()


# ============================================================
# 创建FastAPI应用实例
# ============================================================
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI技术门户后端API - 大模型聊天、RAG知识库、AI工具集",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================
# 请求日志中间件
# ============================================================
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    if request.headers.get("content-length"):
        if int(request.headers["content-length"]) > 50 * 1024 * 1024:
            return JSONResponse(status_code=413, content={"detail": "请求体过大"})
    return await call_next(request)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    method = request.method
    path = request.url.path
    query = request.url.query
    full_path = f"{path}?{query}" if query else path
    client_ip = request.client.host if request.client else "unknown"
    request_id = getattr(request.state, "request_id", "-")

    response = await call_next(request)

    elapsed = (time.time() - start) * 1000
    status_code = response.status_code
    level = logging.WARNING if status_code >= 400 else logging.INFO
    logger.log(level, "%s %s | %d | %.0fms | %s | req=%s", method, full_path, status_code, elapsed, client_ip, request_id)

    return response


# ============================================================
# CORS中间件配置
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    max_age=600,
)

# 静态文件服务（上传的图片）
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ============================================================
# 自动发现并注册API路由
# 新增模块只需在 modules/ 下创建目录即可，无需修改此文件
# ============================================================
def _auto_register_routers(app: FastAPI) -> None:
    registered: list[str] = []
    import app.modules as modules_pkg

    for _, module_name, _ in pkgutil.iter_modules(modules_pkg.__path__):
        try:
            router_module = importlib.import_module(
                f"app.modules.{module_name}.router"
            )
            if hasattr(router_module, "router"):
                prefix = f"/api/v1/{module_name}"
                app.include_router(router_module.router, prefix=prefix)
                registered.append(f"/api/v1/{module_name} -> {module_name}")
        except Exception as e:
            logger.error("模块路由加载失败: %s - %s", module_name, e, exc_info=True)
            registered.append(f"{module_name}: {e}")

    logger.info("注册路由模块: %s", ", ".join(registered))


_auto_register_routers(app)


# ============================================================
# 健康检查端点
# ============================================================
@app.get("/health", tags=["健康检查"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": settings.APP_VERSION}


# ============================================================
# 全局异常处理
# ============================================================
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    logger.warning("业务异常: %s %s | code=%s message=%s",
                   request.method, request.url.path, exc.code, exc.message)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("未捕获异常: %s %s | %s",
                 request.method, request.url.path, str(exc), exc_info=True)
    detail = str(exc) if settings.DEBUG else "服务器内部错误"
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )


# ============================================================
# 根路径
# ============================================================
@app.get("/", tags=["根路径"])
def root() -> dict[str, str | None]:
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else None,
    }
