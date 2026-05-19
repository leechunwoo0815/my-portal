from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.core.security import encrypt_api_key
from app.models import User, ApiKey
from app.modules.admin.schemas import ApiKeyCreate, ApiKeyUpdate, ApiKeyResponse
from app.services.llm_service import llm_service

router = APIRouter(tags=["后台管理"])


@router.get("", response_model=list[ApiKeyResponse])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[ApiKey]:
    return (
        db.query(ApiKey)
        .order_by(ApiKey.priority.desc(), ApiKey.created_at.desc())
        .all()
    )


@router.post("/models")
def fetch_models_from_api(
    api_key: str,
    base_url: str,
    provider: str,
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    model_list = llm_service.fetch_models_from_api(api_key, base_url, provider)
    return {"models": model_list}


@router.post("", response_model=ApiKeyResponse)
def create_api_key(
    request: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ApiKey:
    api_key = ApiKey(
        provider=request.provider,
        api_key_encrypted=encrypt_api_key(request.api_key),
        base_url=request.base_url,
        model_names=request.model_names or [],
        priority=request.priority,
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    return api_key


@router.put("/{key_id}", response_model=ApiKeyResponse)
def update_api_key(
    key_id: int,
    request: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> ApiKey:
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not api_key:
        raise NotFound("API密钥配置")
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "api_key" and value:
            setattr(api_key, "api_key_encrypted", encrypt_api_key(value))
        else:
            setattr(api_key, field, value)
    db.commit()
    db.refresh(api_key)
    return api_key


@router.delete("/{key_id}")
def delete_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, str]:
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not api_key:
        raise NotFound("API密钥配置")
    db.delete(api_key)
    db.commit()
    return {"message": "API密钥配置已删除"}
