from fastapi import APIRouter

from app.modules.admin.router_stats import router as stats_router
from app.modules.admin.router_apikeys import router as apikeys_router
from app.modules.admin.router_logs import router as logs_router
from app.modules.admin.router_configs import router as configs_router
from app.modules.admin.router_comments import router as comments_router
from app.modules.admin.router_users import router as users_router
from app.modules.admin.router_moments import router as moments_router

router = APIRouter(tags=["后台管理"])

router.include_router(stats_router, prefix="/stats")
router.include_router(apikeys_router, prefix="/api-keys")
router.include_router(logs_router, prefix="/api-logs")
router.include_router(configs_router, prefix="/configs")
router.include_router(comments_router, prefix="/comments")
router.include_router(users_router, prefix="/users")
router.include_router(moments_router, prefix="/moments")
