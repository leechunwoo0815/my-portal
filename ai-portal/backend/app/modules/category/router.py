from typing import Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.deps import get_db, require_admin
from app.models import Category
from app.modules.category.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse

router = APIRouter(tags=["分类管理"])


@router.get("/", response_model=CategoryListResponse)
def list_categories(
    module_type: str = "",
    page: int = 1,
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    query = db.query(Category)
    if module_type:
        query = query.filter(Category.module_type == module_type)
    query = query.order_by(Category.sort_order.asc(), Category.id.asc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"total": total, "items": items}


@router.get("/tree", response_model=list[CategoryResponse])
def list_categories_tree(
    module_type: str = "",
    db: Session = Depends(get_db),
) -> list[Category]:
    query = db.query(Category)
    if module_type:
        query = query.filter(Category.module_type == module_type)
    return query.order_by(Category.sort_order.asc(), Category.id.asc()).all()


@router.post("/", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> Category:
    cat = Category(**data.model_dump())
    db.add(cat)
    try:
        db.commit()
        db.refresh(cat)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="分类slug已存在")
    return cat


@router.put("/{cat_id}", response_model=CategoryResponse)
def update_category(
    cat_id: int,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> Category:
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    try:
        db.commit()
        db.refresh(cat)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="分类slug已存在")
    return cat


@router.delete("/{cat_id}")
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> dict[str, str]:
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    db.delete(cat)
    db.commit()
    return {"message": "分类已删除"}
