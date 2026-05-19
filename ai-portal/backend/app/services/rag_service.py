"""
RAG服务模块 - 检索增强生成
文档上传、分块、向量化、检索问答
使用ChromaDB内存模式+持久化，384维向量
"""

import os
import hashlib
import logging
from typing import Optional, Any
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger("ai-portal.rag")


# ============================================================
# 文本分块工具函数
# ============================================================
def split_text(text: str, chunk_size: int = 512, chunk_overlap: int = 64) -> list[str]:
    """
    将长文本按固定大小分块，带重叠

    Args:
        text: 原始文本
        chunk_size: 每个块的最大字符数
        chunk_overlap: 相邻块之间的重叠字符数

    Returns:
        文本块列表
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks: list[str] = []
    start: int = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        # 下一个块的起始位置 = 当前结束位置 - 重叠大小
        start = end - chunk_overlap
        # 防止死循环：如果重叠太大导致start不前进
        if start >= end:
            start = end

    return chunks


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    从文件中提取纯文本内容

    Args:
        file_path: 文件路径
        file_type: 文件类型（pdf/docx/md/txt）

    Returns:
        提取的纯文本
    """
    text: str = ""
    try:
        if file_type == "pdf":
            # 使用PyMuPDF提取PDF文本
            import fitz
            doc = fitz.open(file_path)
            for page in doc:
                text += page.get_text()
            doc.close()

        elif file_type == "docx":
            # 使用python-docx提取Word文本
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paragraphs)

        elif file_type in ("md", "txt", "markdown"):
            # Markdown/纯文本直接读取
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

        else:
            text = f"[不支持的文件类型: {file_type}]"

    except Exception as e:
        text = f"[文件解析失败: {str(e)}]"

    return text


class RAGService:
    """
    RAG服务类 - 文档管理与检索问答
    使用ChromaDB作为向量存储，sentence-transformers生成嵌入
    """

    def __init__(self) -> None:
        """初始化RAG服务，延迟加载重量级依赖"""
        self._chroma_client: Any = None
        self._embedding_function: Any = None
        self._collection: Any = None

    def _init_chroma(self) -> None:
        """初始化ChromaDB客户端（延迟加载，缺失时优雅降级）"""
        if self._chroma_client is not None:
            return

        try:
            import chromadb
            from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
        except ImportError:
            logger.warning("chromadb 未安装，RAG知识库功能不可用")
            self._chroma_client = False  # 标记为不可用
            return

        # 确保持久化目录存在
        persist_dir = Path(settings.CHROMA_PERSIST_DIR)
        persist_dir.mkdir(parents=True, exist_ok=True)

        # 创建ChromaDB客户端（内存模式+持久化）
        self._chroma_client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=chromadb.Settings(
                anonymized_telemetry=False,  # 禁用遥测，保护隐私
            ),
        )

        # 使用轻量级嵌入模型（384维，内存占用小）
        self._embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )

        # 获取或创建集合
        self._collection = self._chroma_client.get_or_create_collection(
            name="knowledge_base",
            embedding_function=self._embedding_function,
            metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
        )

    def _check_chroma(self) -> bool:
        """检查ChromaDB是否可用"""
        self._init_chroma()
        return self._chroma_client is not False

    def upload_document(
        self,
        db: Session,
        knowledge_base_id: int,
        file_path: str,
        filename: str,
        file_type: str,
    ) -> dict[str, Any]:
        """
        上传文档并进行向量化处理

        Args:
            db: 数据库会话
            knowledge_base_id: 所属知识库ID
            file_path: 上传后的文件路径
            filename: 原始文件名
            file_type: 文件类型

        Returns:
            处理结果，包含chunk_count等信息
        """
        if not self._check_chroma():
            return {"success": False, "error": "RAG知识库功能不可用：chromadb 未安装。请执行 pip install chromadb"}

        # 1. 提取文本
        text = extract_text_from_file(file_path, file_type)
        if not text or text.startswith("["):
            return {"success": False, "error": text}

        # 2. 文本分块
        chunks = split_text(
            text,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        if not chunks:
            return {"success": False, "error": "文档内容为空"}

        # 3. 生成唯一文档ID
        doc_hash = hashlib.md5(f"{knowledge_base_id}:{filename}".encode()).hexdigest()

        # 4. 准备ChromaDB数据
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_hash}_{i}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "knowledge_base_id": knowledge_base_id,
                "filename": filename,
                "file_type": file_type,
                "chunk_index": i,
                "doc_hash": doc_hash,
            })

        # 5. 添加到ChromaDB
        try:
            self._collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as e:
            return {"success": False, "error": f"向量化失败: {str(e)}"}

        # 6. 更新知识库文档计数
        from app.models import KnowledgeBase as KBModel
        from app.models import KnowledgeDocument as KDDoc
        kb = db.query(KBModel).filter(KBModel.id == knowledge_base_id).first()
        if kb:
            kb.document_count = (
                db.query(KDDoc)
                .filter(KDDoc.knowledge_base_id == knowledge_base_id)
                .count() + 1
            )
            db.commit()

        return {
            "success": True,
            "chunk_count": len(chunks),
            "doc_hash": doc_hash,
            "filename": filename,
        }

    def query(
        self,
        question: str,
        knowledge_base_id: Optional[int] = None,
        top_k: int = 5,
    ) -> dict[str, Any]:
        """
        RAG问答 - 检索相关文档并返回结果

        Args:
            question: 用户问题
            knowledge_base_id: 指定知识库ID，None则搜索全部
            top_k: 返回最相关的top_k个结果

        Returns:
            包含检索结果和引用来源的字典
        """
        if not self._check_chroma():
            return {"success": False, "error": "RAG知识库功能不可用：chromadb 未安装", "sources": []}

        # 1. 构建过滤条件
        where_filter: Optional[dict] = None
        if knowledge_base_id is not None:
            where_filter = {"knowledge_base_id": knowledge_base_id}

        # 2. 执行向量检索
        try:
            results = self._collection.query(
                query_texts=[question],
                n_results=top_k,
                where=where_filter,
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"检索失败: {str(e)}",
                "sources": [],
            }

        # 3. 解析结果
        sources: list[dict[str, Any]] = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 1.0
                # 余弦距离转相似度分数（0-1，1表示最相似）
                score = round(1.0 - distance, 4)
                sources.append({
                    "content": doc,
                    "filename": metadata.get("filename", "未知文件"),
                    "file_type": metadata.get("file_type", ""),
                    "score": score,
                })

        # 4. 构建上下文
        context = "\n\n".join(
            f"[来源: {s['filename']}]\n{s['content']}"
            for s in sources
        )

        return {
            "success": True,
            "context": context,
            "sources": sources,
            "question": question,
        }

    def delete_document(self, doc_hash: str) -> bool:
        """
        删除文档及其所有chunk

        Args:
            doc_hash: 文档哈希标识

        Returns:
            bool: 是否删除成功
        """
        if not self._check_chroma():
            return False

        try:
            # 删除所有以doc_hash开头的chunk
            self._collection.delete(
                where={"doc_hash": doc_hash},
            )
            return True
        except Exception as e:
            logger.error("删除文档失败: doc_hash=%s, error=%s", doc_hash, str(e))
            return False

    def list_documents(self, knowledge_base_id: Optional[int] = None) -> list[dict[str, Any]]:
        """
        列出知识库中的所有文档

        Args:
            knowledge_base_id: 知识库ID

        Returns:
            文档列表
        """
        if not self._check_chroma():
            return []

        where_filter: Optional[dict] = None
        if knowledge_base_id is not None:
            where_filter = {"knowledge_base_id": knowledge_base_id}

        try:
            results = self._collection.get(
                where=where_filter,
                limit=1000,
            )
        except Exception as e:
            logger.error("列出文档失败: %s", str(e))
            return []

        # 去重：按doc_hash聚合
        docs_map: dict[str, dict] = {}
        if results and results["metadatas"]:
            for metadata in results["metadatas"]:
                doc_hash = metadata.get("doc_hash", "")
                if doc_hash not in docs_map:
                    docs_map[doc_hash] = {
                        "doc_hash": doc_hash,
                        "filename": metadata.get("filename", ""),
                        "file_type": metadata.get("file_type", ""),
                        "knowledge_base_id": metadata.get("knowledge_base_id", 0),
                    }

        return list(docs_map.values())


# 全局RAG服务单例
rag_service = RAGService()
