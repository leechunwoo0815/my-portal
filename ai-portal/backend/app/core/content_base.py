from typing import TypeVar, Type, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.events import EventBus
from app.models import Comment, UserLike, UserFavorite, ContentTag

T = TypeVar("T")


class ContentCRUD:
    def __init__(self, model_class: Type[T], event_prefix: str):
        self.model = model_class
        self.event_prefix = event_prefix

    def get(self, db: Session, obj_id: int) -> T | None:
        return db.query(self.model).filter(self.model.id == obj_id).first()

    def get_or_404(self, db: Session, obj_id: int, detail: str = "内容不存在") -> T:
        obj = self.get(db, obj_id)
        if not obj:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        return obj

    def list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        filters: dict | None = None,
        order_by: Any = None,
    ) -> tuple[list[T], int]:
        query = db.query(self.model)
        if filters:
            for field, value in filters.items():
                if value is not None:
                    col = getattr(self.model, field, None)
                    if col is not None:
                        if isinstance(value, list):
                            query = query.filter(col.in_(value))
                        else:
                            query = query.filter(col == value)
        total = query.count()
        if order_by is not None:
            query = query.order_by(order_by)
        else:
            query = query.order_by(self.model.id.desc())
        items = query.offset(skip).limit(limit).all()
        return items, total

    async def create(self, db: Session, data: BaseModel, user_id: int) -> T:
        dump = data.model_dump()
        obj = self.model(**dump, author_id=user_id)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        await EventBus.emit(f"{self.event_prefix}.created", obj)
        return obj

    async def update(self, db: Session, obj: T, data: BaseModel) -> T:
        update_data = data.model_dump(exclude_unset=True)
        if "edit_version" in update_data and hasattr(obj, "edit_version"):
            if update_data["edit_version"] != obj.edit_version:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="内容已被他人修改，请刷新后重试",
                )
        for field, value in update_data.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        if hasattr(obj, "edit_version"):
            obj.edit_version = (obj.edit_version or 0) + 1
        db.commit()
        db.refresh(obj)
        return obj

    async def delete(self, db: Session, obj_id: int, target_type: str) -> None:
        obj = self.get_or_404(db, obj_id)
        db.query(Comment).filter(
            Comment.target_type == target_type, Comment.target_id == obj_id
        ).delete(synchronize_session=False)
        db.query(UserLike).filter(
            UserLike.target_type == target_type, UserLike.target_id == obj_id
        ).delete(synchronize_session=False)
        db.query(UserFavorite).filter(
            UserFavorite.target_type == target_type, UserFavorite.target_id == obj_id
        ).delete(synchronize_session=False)
        db.query(ContentTag).filter(
            ContentTag.target_type == target_type, ContentTag.target_id == obj_id
        ).delete(synchronize_session=False)
        db.delete(obj)
        db.commit()
        await EventBus.emit(f"{self.event_prefix}.deleted", obj)

    async def publish(self, db: Session, obj_id: int) -> T:
        from app.models.user import utc_now
        obj = self.get_or_404(db, obj_id)
        obj.status = "published"
        obj.is_published = True
        obj.published_at = utc_now()
        db.commit()
        db.refresh(obj)
        await EventBus.emit(f"{self.event_prefix}.published", obj)
        return obj

    def make_list_response(self, items: list, total: int, page: int, page_size: int) -> dict:
        total_pages = (total + page_size - 1) // page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items,
        }
