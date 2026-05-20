"""举报API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.deps import get_db, get_current_user, require_admin
from app.core.exceptions import NotFound, PermissionDenied, AlreadyExists
from app.models import User, Report, Comment, Blog, Moment, AuditLog
from app.modules.report.schemas import ReportCreate

router = APIRouter(tags=["举报"])


@router.post("")
def create_report(
    request: ReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """提交举报"""
    # 检查目标是否存在
    target_map = {
        "comment": Comment,
        "blog": Blog,
        "moment": Moment,
    }
    model = target_map.get(request.target_type)
    if model:
        target = db.query(model).filter(model.id == request.target_id).first()
        if not target:
            raise NotFound("举报目标不存在")

    # 防止重复举报
    existing = db.query(Report).filter(
        Report.reporter_id == current_user.id,
        Report.target_type == request.target_type,
        Report.target_id == request.target_id,
        Report.status == "pending",
    ).first()
    if existing:
        raise AlreadyExists("举报")

    report = Report(
        reporter_id=current_user.id,
        target_type=request.target_type,
        target_id=request.target_id,
        reason=request.reason,
        description=request.description,
    )
    db.add(report)
    db.commit()
    return {"message": "举报已提交，管理员会尽快处理"}


@router.get("/admin", response_model=dict)
def admin_list_reports(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    status: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """管理员查看举报列表"""
    query = db.query(Report)
    if status:
        query = query.filter(Report.status == status)
    query = query.order_by(Report.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()

    reporter_ids = {r.reporter_id for r in items if r.reporter_id}
    reporters = {}
    if reporter_ids:
        for u in db.query(User).filter(User.id.in_(reporter_ids)).all():
            reporters[u.id] = u.nickname or u.username

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": r.id,
            "reporter_id": r.reporter_id,
            "reporter_name": reporters.get(r.reporter_id, "匿名"),
            "target_type": r.target_type,
            "target_id": r.target_id,
            "reason": r.reason,
            "description": r.description,
            "status": r.status,
            "admin_note": r.admin_note,
            "created_at": str(r.created_at) if r.created_at else None,
        } for r in items],
    }


@router.put("/{report_id}/review")
def review_report(
    report_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """管理员审核举报"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise NotFound("举报")

    new_status = body.get("status", "reviewed")
    if new_status not in ("reviewed", "dismissed"):
        raise PermissionDenied("状态值无效")

    report.status = new_status
    report.admin_note = body.get("admin_note")
    report.reviewed_by = current_user.id
    report.reviewed_at = datetime.now(timezone.utc)

    db.add(AuditLog(
        admin_id=current_user.id,
        action="review_report",
        target_type="report",
        target_id=report_id,
        detail=f"举报审核: {new_status}",
    ))
    db.commit()
    return {"message": f"举报已{('处理' if new_status == 'reviewed' else '驳回')}"}
