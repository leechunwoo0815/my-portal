from typing import Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_admin
from app.models import Tag
from app.modules.tag.schemas import TagCreate, TagUpdate, TagResponse, TagListResponse

router = APIRouter(tags=["标签管理"])


@router.get("/", response_model=TagListResponse)
def list_tags(
    page: int = 1,
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Tag).order_by(Tag.usage_count.desc(), Tag.id.asc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": items}


@router.get("/popular", response_model=list[TagResponse])
def list_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Tag]:
    return db.query(Tag).order_by(Tag.usage_count.desc()).limit(limit).all()


@router.post("/", response_model=TagResponse)
def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> Tag:
    tag = Tag(**data.model_dump())
    db.add(tag)
    try:
        db.commit()
        db.refresh(tag)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="标签名或slug已存在")
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    data: TagUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> Tag:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(tag, k, v)
    try:
        db.commit()
        db.refresh(tag)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="标签名或slug已存在")
    return tag


@router.delete("/{tag_id}")
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> dict[str, str]:
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    db.delete(tag)
    db.commit()
    return {"message": "标签已删除"}
