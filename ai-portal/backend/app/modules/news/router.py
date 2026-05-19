from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime, timezone
from app.core.deps import get_db, require_admin
from app.core.exceptions import NotFound
from app.modules.news.schemas import NewsCreate, NewsUpdate, NewsResponse, NewsListResponse
from app.models import News, Comment, UserLike, UserFavorite
from sqlalchemy import func, desc

router = APIRouter(tags=["新闻"])

@router.post("/", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
def create_news(news: NewsCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """创建新闻"""
    db_news = News(
        title=news.title,
        summary=news.summary,
        content=news.content,
        content_type=news.content_type,
        cover_image=news.cover_image,
        category=news.category,
        tags=news.tags,
        is_published=news.is_published,
        author_id=current_user.id
    )
    if news.is_published:
        db_news.published_at = datetime.now(timezone.utc)
    
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news

@router.get("/", response_model=NewsListResponse)
def list_news(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy import or_
    query = db.query(News).filter(News.is_published == True)
    if category:
        query = query.filter(News.category == category)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(News.title.like(pattern), News.summary.like(pattern), News.tags.like(pattern)))
    total = query.count()
    items = query.order_by(desc(News.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}

@router.get("/admin", response_model=NewsListResponse)
def admin_list_news(
    page: int = 1,
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    author_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    query = db.query(News)
    if category:
        query = query.filter(News.category == category)
    if author_id:
        query = query.filter(News.author_id == author_id)
    total = query.count()
    items = query.order_by(desc(News.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size
    return {"total": total, "page": page, "page_size": page_size, "total_pages": total_pages, "items": items}

@router.get("/{news_id}", response_model=NewsResponse)
def get_news(news_id: int, db: Session = Depends(get_db)):
    """获取新闻详情"""
    news = db.query(News).filter(News.id == news_id, News.is_published == True).first()
    if not news:
        raise NotFound("新闻")
    db.query(News).filter(News.id == news_id).update({News.view_count: News.view_count + 1}, synchronize_session=False)
    db.commit()
    db.refresh(news)
    return news

@router.put("/{news_id}", response_model=NewsResponse)
def update_news(news_id: int, news: NewsUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """更新新闻"""
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise NotFound("新闻")
    
    update_data = news.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_news, field, value)
    
    # 如果发布状态从false变为true，设置发布时间
    if 'is_published' in update_data and update_data['is_published'] and not db_news.published_at:
        db_news.published_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_news)
    return db_news

@router.delete("/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    """删除新闻"""
    db_news = db.query(News).filter(News.id == news_id).first()
    if not db_news:
        raise NotFound("新闻")
    db.query(Comment).filter(Comment.target_type == "news", Comment.target_id == news_id).delete(synchronize_session=False)
    db.query(UserLike).filter(UserLike.target_type == "news", UserLike.target_id == news_id).delete(synchronize_session=False)
    db.query(UserFavorite).filter(UserFavorite.target_type == "news", UserFavorite.target_id == news_id).delete(synchronize_session=False)
    db.delete(db_news)
    db.commit()
    return {"message": "新闻已删除"}
