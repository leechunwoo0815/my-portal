"""知识库API路由 - 知识库管理、文档上传、RAG问答"""
import os
import shutil
import uuid
from typing import Any
from pathlib import Path

from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_current_user, require_admin
from app.core.exceptions import NotFound, FileError, FileTooLarge
from app.models import KnowledgeBase, KnowledgeDocument, User
from app.modules.knowledge.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    DocumentResponse,
    RAGQueryRequest,
    RAGQueryResponse,
)
from app.services.rag_service import rag_service
from app.services.llm_service import llm_service

router = APIRouter(tags=["知识库"])

ALLOWED_FILE_TYPES = {"pdf", "docx", "md", "txt", "markdown"}


def _get_file_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def _save_upload_file(upload_file: UploadFile, dest_dir: str) -> str:
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    safe_filename = os.path.basename(upload_file.filename)
    name, ext = os.path.splitext(safe_filename)
    safe_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = os.path.join(dest_dir, safe_filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return file_path


@router.get("/bases", response_model=list[KnowledgeBaseResponse])
def list_knowledge_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[KnowledgeBase]:
    """获取知识库列表"""
    return db.query(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()).all()


@router.post("/bases", response_model=KnowledgeBaseResponse)
def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> KnowledgeBase:
    """创建知识库（管理员）"""
    kb = KnowledgeBase(**request.model_dump())
    db.add(kb)
    db.commit()
    db.refresh(kb)
    return kb


@router.put("/bases/{kb_id}", response_model=KnowledgeBaseResponse)
def update_knowledge_base(
    kb_id: int,
    request: KnowledgeBaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> KnowledgeBase:
    """更新知识库（管理员）"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise NotFound("知识库")
    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(kb, field, value)
    db.commit()
    db.refresh(kb)
    return kb


@router.delete("/bases/{kb_id}")
def delete_knowledge_base(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, str]:
    """删除知识库及其所有文档（管理员）"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise NotFound("知识库")
    for doc in kb.documents:
        file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        rag_service.delete_document(doc.extra_data.get("doc_hash", ""))
    db.delete(kb)
    db.commit()
    return {"message": "知识库已删除"}


@router.post("/bases/{kb_id}/documents")
def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, Any]:
    """上传文档到知识库（管理员）"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise NotFound("知识库")

    file_ext = _get_file_extension(file.filename)
    if file_ext not in ALLOWED_FILE_TYPES:
        raise FileError(f"不支持的文件类型: {file_ext}")

    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise FileTooLarge(settings.MAX_UPLOAD_SIZE // (1024*1024))

    file_path = _save_upload_file(file, settings.UPLOAD_DIR)
    result = rag_service.upload_document(
        db=db,
        knowledge_base_id=kb_id,
        file_path=file_path,
        filename=file.filename,
        file_type=file_ext,
    )

    if not result.get("success"):
        if os.path.exists(file_path):
            os.remove(file_path)
        raise FileError(result.get("error", "文档处理失败"))

    doc = KnowledgeDocument(
        knowledge_base_id=kb_id,
        filename=file.filename,
        file_type=file_ext,
        chunk_count=result["chunk_count"],
        file_size=file_size,
        extra_data={"doc_hash": result["doc_hash"], "file_path": file_path},
    )
    db.add(doc)
    db.flush()
    kb.document_count = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.knowledge_base_id == kb_id
    ).count()
    db.commit()
    db.refresh(doc)

    return {
        "success": True,
        "document_id": doc.id,
        "filename": file.filename,
        "chunk_count": result["chunk_count"],
        "file_size": file_size,
    }


@router.get("/bases/{kb_id}/documents", response_model=list[DocumentResponse])
def list_documents(
    kb_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> list[KnowledgeDocument]:
    """获取知识库中的文档列表"""
    return (
        db.query(KnowledgeDocument)
        .filter(KnowledgeDocument.knowledge_base_id == kb_id)
        .order_by(KnowledgeDocument.created_at.desc())
        .all()
    )


@router.delete("/bases/{kb_id}/documents/{doc_id}")
def delete_document(
    kb_id: int,
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict[str, str]:
    """删除知识库中的文档（管理员）"""
    doc = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.id == doc_id,
        KnowledgeDocument.knowledge_base_id == kb_id,
    ).first()
    if not doc:
        raise NotFound("文档")

    file_path = doc.extra_data.get("file_path") if doc.extra_data else None
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
    doc_hash = doc.extra_data.get("doc_hash", "") if doc.extra_data else ""
    if doc_hash:
        rag_service.delete_document(doc_hash)

    db.delete(doc)
    db.commit()
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if kb:
        kb.document_count = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.knowledge_base_id == kb_id
        ).count()
        db.commit()
    return {"message": "文档已删除"}


@router.post("/bases/{kb_id}/query", response_model=RAGQueryResponse)
def query_knowledge_base(
    kb_id: int,
    request: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """RAG问答 - 基于知识库内容回答问题"""
    kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
    if not kb:
        raise NotFound("知识库")

    retrieval_result = rag_service.query(
        question=request.question,
        knowledge_base_id=kb_id,
        top_k=request.top_k,
    )
    if not retrieval_result.get("success"):
        raise FileError(retrieval_result.get("error", "检索失败"))

    sources = retrieval_result.get("sources", [])
    context = retrieval_result.get("context", "")
    if not sources:
        return RAGQueryResponse(
            answer="未在知识库中找到相关内容，请尝试上传相关文档或调整问题。",
            sources=[],
            model_used="",
        )

    # 使用 LLMService 非流式调用，统一走调用限制和日志
    rag_prompt = (
        f"你是智慧城市领域的专业助手。请基于以下参考资料回答问题。\n\n"
        f"如果参考资料中没有答案，请明确说明。\n\n"
        f"参考资料：\n{context}\n\n"
        f"问题：{request.question}\n\n"
        f"回答："
    )

    try:
        answer = llm_service.chat_completion(
            messages=[{"role": "user", "content": rag_prompt}],
            model_id=settings.DEFAULT_MODEL,
            temperature=0.3,
            max_tokens=2048,
            db=db,
        )
        model_used = settings.DEFAULT_MODEL
    except Exception as e:
        answer = "生成回答时出错，请稍后重试"
        model_used = ""

    formatted_sources = [
        {
            "document_id": i,
            "filename": s["filename"],
            "content": s["content"][:200] + "..." if len(s["content"]) > 200 else s["content"],
            "score": s["score"],
        }
        for i, s in enumerate(sources)
    ]

    return RAGQueryResponse(
        answer=answer,
        sources=formatted_sources,
        model_used=model_used,
    )
