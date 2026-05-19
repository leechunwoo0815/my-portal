from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime, timezone
from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.modules.solutions.schemas import SolutionCreate, SolutionUpdate, SolutionResponse, SolutionListResponse
from app.models import Solution, Comment, UserLike, UserFavorite
from sqlalchemy import func, desc

router = APIRouter(tags=["解决方案"])

@router.post("/", response_model=SolutionResponse, status_code=status.HTTP_201_CREATED)
def create_solution(solution: SolutionCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """创建解决方案"""
    db_solution = Solution(
        title=solution.title,
        summary=solution.summary,
        content=solution.content,
        content_type=solution.content_type,
        cover_image=solution.cover_image,
        category=solution.category,
        tags=solution.tags,
        is_published=solution.is_published,
        author_id=current_user.id
    )
    if solution.is_published:
        db_solution.published_at = datetime.now(timezone.utc)
    
    db.add(db_solution)
    db.commit()
    db.refresh(db_solution)
    return db_solution

@router.get("/", response_model=SolutionListResponse)
def list_solutions(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy import or_
    query = db.query(Solution).filter(Solution.is_published == True)
    if category:
        query = query.filter(Solution.category == category)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(Solution.title.like(pattern), Solution.summary.like(pattern), Solution.tags.like(pattern)))
    total = query.count()
    items = query.order_by(desc(Solution.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}

@router.get("/admin", response_model=SolutionListResponse)
def admin_list_solutions(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    author_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    query = db.query(Solution)
    if category:
        query = query.filter(Solution.category == category)
    if author_id:
        query = query.filter(Solution.author_id == author_id)
    total = query.count()
    items = query.order_by(desc(Solution.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}

@router.get("/{solution_id}", response_model=SolutionResponse)
def get_solution(solution_id: int, db: Session = Depends(get_db)):
    """获取解决方案详情"""
    solution = db.query(Solution).filter(Solution.id == solution_id, Solution.is_published == True).first()
    if not solution:
        raise NotFound("解决方案")
    db.query(Solution).filter(Solution.id == solution_id).update({Solution.view_count: Solution.view_count + 1}, synchronize_session=False)
    db.commit()
    db.refresh(solution)
    return solution

@router.put("/{solution_id}", response_model=SolutionResponse)
def update_solution(solution_id: int, solution: SolutionUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """更新解决方案"""
    db_solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not db_solution:
        raise NotFound("解决方案")
    
    update_data = solution.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_solution, field, value)
    
    # 如果发布状态从false变为true，设置发布时间
    if 'is_published' in update_data and update_data['is_published'] and not db_solution.published_at:
        db_solution.published_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_solution)
    return db_solution

@router.delete("/{solution_id}")
def delete_solution(solution_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """删除解决方案"""
    db_solution = db.query(Solution).filter(Solution.id == solution_id).first()
    if not db_solution:
        raise NotFound("解决方案")
    db.query(Comment).filter(Comment.target_type == "solution", Comment.target_id == solution_id).delete(synchronize_session=False)
    db.query(UserLike).filter(UserLike.target_type == "solution", UserLike.target_id == solution_id).delete(synchronize_session=False)
    db.query(UserFavorite).filter(UserFavorite.target_type == "solution", UserFavorite.target_id == solution_id).delete(synchronize_session=False)
    db.delete(db_solution)
    db.commit()
    return {"message": "解决方案已删除"}
