from typing import Any

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.models import User, SystemConfig

router = APIRouter(tags=["后台管理"])


@router.get("")
def list_system_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[dict[str, Any]]:
    configs = db.query(SystemConfig).order_by(SystemConfig.key).all()
    return [
        {
            "id": c.id,
            "key": c.key,
            "value": c.value,
            "description": c.description,
            "updated_at": c.updated_at,
        }
        for c in configs
    ]


@router.put("/{key}")
def update_system_config(
    key: str,
    value: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, str]:
    config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not config:
        raise NotFound("配置项")
    config.value = value
    db.commit()
    return {"message": "配置已更新"}
