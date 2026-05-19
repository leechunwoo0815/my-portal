from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.models import User, ApiCallLog
from app.modules.admin.schemas import ApiLogListResponse

router = APIRouter(tags=["后台管理"])


@router.get("", response_model=ApiLogListResponse)
def list_api_logs(
    page: int = 1,
    page_size: int = Query(50, ge=1, le=100),
    provider: str = "",
    model_name: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    query = db.query(ApiCallLog)
    if provider:
        query = query.filter(ApiCallLog.provider == provider)
    if model_name:
        query = query.filter(ApiCallLog.model_name == model_name)
    query = query.order_by(ApiCallLog.created_at.desc())
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    logs = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": logs,
    }
