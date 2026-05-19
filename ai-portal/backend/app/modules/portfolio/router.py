"""作品集API路由 - 项目CRUD"""
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, require_admin
from app.core.exceptions import NotFound, PermissionDenied
from app.models import Project, User
from app.models import Comment, UserLike, UserFavorite
from app.modules.portfolio.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectListResponse,
)
from app.services.point_service import point_service

router = APIRouter(tags=["作品集"])


@router.get("/projects", response_model=ProjectListResponse)
def list_projects(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: str = "",
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """获取项目列表（公开接口）"""
    query = db.query(Project).filter(Project.is_published == True)
    if category:
        query = query.filter(Project.category == category)
    query = query.order_by(Project.sort_order.asc(), Project.created_at.desc())
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    projects = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": projects,
    }


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    """获取项目详情（公开接口）"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.is_published == True,
    ).first()
    if not project:
        raise NotFound("项目")
    return project


@router.post("/projects", response_model=ProjectResponse)
def create_project(
    request: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    """创建项目（LV4+ 或管理员）"""
    if not current_user.is_admin and current_user.level < 4:
        raise PermissionDenied("LV4及以上才能发布项目")
    project = Project(**request.model_dump(), author_id=current_user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    if not current_user.is_admin and point_service.check_daily_limit(db, current_user.id, "publish_project"):
        point_service.award_points(db, current_user.id, "publish_project", "发布项目")
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    request: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Project:
    """更新项目（作者或管理员）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFound("项目")
    if not current_user.is_admin and project.author_id != current_user.id:
        raise PermissionDenied("无权编辑该项目")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """删除项目（作者或管理员）"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise NotFound("项目")
    if not current_user.is_admin and project.author_id != current_user.id:
        raise PermissionDenied("无权删除该项目")
    db.query(Comment).filter(Comment.target_type == "project", Comment.target_id == project_id).delete(synchronize_session=False)
    db.query(UserLike).filter(UserLike.target_type == "project", UserLike.target_id == project_id).delete(synchronize_session=False)
    db.query(UserFavorite).filter(UserFavorite.target_type == "project", UserFavorite.target_id == project_id).delete(synchronize_session=False)
    db.delete(project)
    db.commit()
    return {"message": "项目已删除"}


@router.get("/admin/projects", response_model=ProjectListResponse)
def admin_list_projects(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    author_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    """项目管理列表：管理员看全部，可按作者筛选"""
    query = db.query(Project)
    if author_id is not None:
        query = query.filter(Project.author_id == author_id)
    query = query.order_by(Project.sort_order.asc(), Project.created_at.desc())
    total = query.count()
    total_pages = (total + page_size - 1) // page_size
    projects = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": projects,
    }
