from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime, timezone
from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.models import Product, Comment, UserLike, UserFavorite
from sqlalchemy import func, desc

router = APIRouter(tags=["产品"])

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """创建产品"""
    db_product = Product(
        title=product.title,
        summary=product.summary,
        content=product.content,
        content_type=product.content_type,
        cover_image=product.cover_image,
        category=product.category,
        tags=product.tags,
        is_published=product.is_published,
        author_id=current_user.id
    )
    if product.is_published:
        db_product.published_at = datetime.now(timezone.utc)
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=ProductListResponse)
def list_products(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy import or_
    query = db.query(Product).filter(Product.is_published == True)
    if category:
        query = query.filter(Product.category == category)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(Product.title.like(pattern), Product.summary.like(pattern), Product.tags.like(pattern)))
    total = query.count()
    items = query.order_by(desc(Product.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}

@router.get("/admin", response_model=ProductListResponse)
def admin_list_products(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    author_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if author_id:
        query = query.filter(Product.author_id == author_id)
    total = query.count()
    items = query.order_by(desc(Product.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """获取产品详情"""
    product = db.query(Product).filter(Product.id == product_id, Product.is_published == True).first()
    if not product:
        raise NotFound("产品")
    db.query(Product).filter(Product.id == product_id).update({Product.view_count: Product.view_count + 1}, synchronize_session=False)
    db.commit()
    db.refresh(product)
    return product

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """更新产品"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise NotFound("产品")
    
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    # 如果发布状态从false变为true，设置发布时间
    if 'is_published' in update_data and update_data['is_published'] and not db_product.published_at:
        db_product.published_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_product)
    return db_product

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """删除产品"""
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        raise NotFound("产品")
    db.query(Comment).filter(Comment.target_type == "product", Comment.target_id == product_id).delete(synchronize_session=False)
    db.query(UserLike).filter(UserLike.target_type == "product", UserLike.target_id == product_id).delete(synchronize_session=False)
    db.query(UserFavorite).filter(UserFavorite.target_type == "product", UserFavorite.target_id == product_id).delete(synchronize_session=False)
    db.delete(db_product)
    db.commit()
    return {"message": "产品已删除"}
