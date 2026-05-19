from typing import Type, TypeVar, Generic, Optional, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel

from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.core.deps import get_db, get_current_user, require_admin
from app.core.exceptions import PermissionDenied

T = TypeVar("T")


class CRUDBase(Generic[T]):

    def __init__(self, model: Type[T]):
        self.model = model

    def get(self, db: Session, obj_id: int) -> Optional[T]:
        return db.query(self.model).filter(self.model.id == obj_id).first()

    def get_or_404(self, db: Session, obj_id: int, detail: str = "记录不存在") -> T:
        obj = self.get(db, obj_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        return obj

    def list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[dict] = None,
        order_by: Optional[Any] = None,
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

    def create(self, db: Session, obj_in: BaseModel | dict, **extra_fields) -> T:
        data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in
        if extra_fields:
            data.update(extra_fields)
        db_obj = self.model(**data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: T, obj_in: BaseModel | dict) -> T:
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, "model_dump") else obj_in
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, obj_id: int) -> bool:
        obj = self.get(db, obj_id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

    def cascade_delete(self, db: Session, id: int, target_type: str) -> None:
        from app.models import Comment, UserLike, UserFavorite
        obj = self.get_or_404(db, id)
        db.query(Comment).filter(Comment.target_type == target_type, Comment.target_id == id).delete(synchronize_session=False)
        db.query(UserLike).filter(UserLike.target_type == target_type, UserLike.target_id == id).delete(synchronize_session=False)
        db.query(UserFavorite).filter(UserFavorite.target_type == target_type, UserFavorite.target_id == id).delete(synchronize_session=False)
        db.delete(obj)
        db.commit()


class CRUDRouterFactory:

    def __init__(
        self,
        model: Type,
        create_schema: Type[BaseModel],
        update_schema: Type[BaseModel],
        response_schema: Type[BaseModel],
        list_response_schema: Type[BaseModel],
        target_type: str,
        prefix: str = "",
        tags: list[str] = [],
        require_auth_create: bool = True,
        require_auth_list: bool = False,
        require_admin_delete: bool = True,
    ):
        self.crud = CRUDBase(model)
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.response_schema = response_schema
        self.list_response_schema = list_response_schema
        self.target_type = target_type
        self.router = APIRouter(prefix=prefix, tags=tags)
        self._register_routes()

    def _register_routes(self):
        @self.router.get("/", response_model=self.list_response_schema)
        def list_items(
            page: int = 1,
            page_size: int = Query(20, ge=1, le=100),
            db: Session = Depends(get_db),
        ):
            total = db.query(self.model).count()
            items = db.query(self.model).order_by(self.model.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
            total_pages = (total + page_size - 1) // page_size
            return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}

        @self.router.get("/{item_id}", response_model=self.response_schema)
        def get_item(item_id: int, db: Session = Depends(get_db)):
            return self.crud.get_or_404(db, item_id)

        @self.router.post("/", response_model=self.response_schema)
        def create_item(
            data: self.create_schema,
            db: Session = Depends(get_db),
            current_user=Depends(get_current_user),
        ):
            obj = self.model(**data.model_dump())
            obj.author_id = current_user.id
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj

        @self.router.put("/{item_id}", response_model=self.response_schema)
        def update_item(
            item_id: int,
            data: self.update_schema,
            db: Session = Depends(get_db),
            current_user=Depends(get_current_user),
        ):
            obj = self.crud.get_or_404(db, item_id)
            if obj.author_id and obj.author_id != current_user.id and not current_user.is_admin:
                raise PermissionDenied("无权修改此内容")
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(obj, field, value)
            db.commit()
            db.refresh(obj)
            return obj

        @self.router.delete("/{item_id}")
        def delete_item(
            item_id: int,
            db: Session = Depends(get_db),
            current_user=Depends(require_admin),
        ):
            self.crud.cascade_delete(db, item_id, self.target_type)
            return {"message": "已删除"}