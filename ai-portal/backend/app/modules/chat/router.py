"""聊天API路由 - 会话管理、发送消息（SSE流式）、模型列表"""
import asyncio
import json
import logging
import threading
from typing import Any, AsyncGenerator

import fastapi

logger = logging.getLogger("ai-portal")

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models import Conversation, Message, User
from app.modules.chat.schemas import (
    ChatRequest,
    ConversationResponse,
    ConversationCreateRequest,
    ConversationUpdateRequest,
    ChatMessageResponse,
    ModelInfo,
)
from app.services.llm_service import llm_service
from app.core.exceptions import NotFound, PermissionDenied, AlreadyExists

router = APIRouter(tags=["聊天"])
limiter = Limiter(key_func=get_remote_address)

# cancel_by_convId: {conversation_id -> threading.Event}
_cancel_events: dict[int, threading.Event] = {}
_cancel_lock = threading.Lock()


def _save_assistant_message(db: Session, conversation_id: int, model: str, full_content: str, thinking_content: str) -> None:
    """保存 AI 回复消息到数据库（正常结束/中断断连都调用）"""
    from app.models import utc_now

    try:
        if full_content:
            clean = full_content
            t0 = full_content.find('<thinking>')
            t1 = full_content.find('</thinking>')
            if t0 != -1 and t1 != -1 and t1 > t0:
                if not thinking_content:
                    thinking_content = full_content[t0+10:t1].strip()
                clean = (full_content[:t0] + full_content[t1+12:]).strip()
            else:
                clean = full_content.strip()
        else:
            clean = ""

        if not clean and not thinking_content:
            return

        token_count = llm_service.count_tokens(clean, model) if clean else 0
        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=clean or "",
            model_name=model,
            token_count=token_count,
            thinking=thinking_content if thinking_content else None,
            duration=None,
        )
        db.add(ai_message)
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation:
            conversation.updated_at = utc_now()
        db.commit()
    except Exception as e:
        logger.error("保存AI回复失败: conversation_id=%d, error=%s", conversation_id, str(e))
        db.rollback()


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Conversation]:
    """获取当前用户的所有会话列表（已置顶优先）"""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.is_pinned.desc(), Conversation.updated_at.desc())
        .all()
    )
    from sqlalchemy import func as sqlfunc
    message_counts = dict(
        db.query(Message.conversation_id, sqlfunc.count(Message.id))
        .filter(Message.conversation_id.in_([c.id for c in conversations]))
        .group_by(Message.conversation_id)
        .all()
    )
    for conv in conversations:
        conv.message_count = message_counts.get(conv.id, 0)
    return conversations


@router.post("/conversations/{conversation_id}/pin")
def pin_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """置顶会话（最多5个）"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise NotFound("会话")
    if conv.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权操作")

    pinned_count = db.query(Conversation).filter(
        Conversation.user_id == current_user.id,
        Conversation.is_pinned == True,
    ).count()
    if pinned_count >= 5:
        raise AlreadyExists("置顶会话（最多5个）")

    conv.is_pinned = True
    db.commit()
    return {"message": "已置顶"}


@router.post("/conversations/{conversation_id}/unpin")
def unpin_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """取消置顶"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise NotFound("会话")
    if conv.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权操作")

    conv.is_pinned = False
    db.commit()
    return {"message": "已取消置顶"}


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Conversation:
    """创建新聊天会话"""
    available = llm_service.get_available_models(db=db)
    model = request.model or (available[0]["id"] if available else "deepseek-chat")
    conversation = Conversation(
        title=request.title or "新会话",
        model_name=model,
        system_prompt=request.system_prompt,
        user_id=current_user.id,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    conversation.message_count = 0
    return conversation


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: int,
    request: ConversationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Conversation:
    """更新会话信息"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise NotFound("会话")
    if conversation.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权访问该会话")

    if request.title is not None:
        conversation.title = request.title
    if request.is_archived is not None:
        conversation.is_archived = request.is_archived
    db.commit()
    db.refresh(conversation)
    return conversation


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """删除会话及其所有消息"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise NotFound("会话")
    if conversation.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权访问该会话")
    db.delete(conversation)
    db.commit()
    return {"message": "会话已删除"}


@router.get("/conversations/{conversation_id}/messages", response_model=list[ChatMessageResponse])
def get_messages(
    conversation_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Message]:
    """获取会话的所有消息"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise NotFound("会话")
    if conversation.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权访问该会话")
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .all()
    )


@router.post("/completions/cancel/{conversation_id}")
def cancel_completion(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """主动停止指定会话的生成（设置Event让流提前退出）"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    if not conversation:
        raise NotFound("会话")
    if conversation.user_id != current_user.id and not current_user.is_admin:
        raise PermissionDenied("无权访问该会话")

    with _cancel_lock:
        ev = _cancel_events.get(conversation_id)
        if ev is None:
            ev = threading.Event()
            _cancel_events[conversation_id] = ev
        ev.set()
    return {"message": "cancel requested"}


@router.post("/completions")
@limiter.limit("30/minute")
async def chat_completions(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送消息并获取AI回复（SSE流式响应）"""
    from app.models import utc_now

    conversation_id = chat_request.conversation_id
    if conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if not conversation:
            raise NotFound("会话")
        if conversation.user_id != current_user.id and not current_user.is_admin:
            raise PermissionDenied("无权访问该会话")
    else:
        available = llm_service.get_available_models(db=db)
        model = chat_request.model or (available[0]["id"] if available else "deepseek-chat")
        conversation = Conversation(
            title=chat_request.message[:30] + "..." if len(chat_request.message) > 30 else chat_request.message,
            model_name=model,
            system_prompt=chat_request.system_prompt,
            user_id=current_user.id,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id

    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=chat_request.message,
        model_name=chat_request.model,
    )
    db.add(user_message)
    db.commit()

    history_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(50)
        .all()
    )
    history_messages.reverse()
    messages_for_llm = [
        {"role": msg.role, "content": msg.content}
        for msg in history_messages
    ]

    model = chat_request.model or conversation.model_name or "deepseek-chat"
    system_prompt = chat_request.system_prompt or conversation.system_prompt

    # 为本次会话创建 cancel Event
    cancel_event = threading.Event()
    with _cancel_lock:
        _cancel_events[conversation_id] = cancel_event

    async def event_generator() -> AsyncGenerator[str, None]:
        nonlocal conversation_id, model
        logger.info(f"[stream] Starting stream for conversation_id={conversation_id}, model={model}")
        full_content = ""
        thinking_content = ""
        loop = asyncio.get_event_loop()
        sync_gen = llm_service.stream_chat(
            db=db,
            messages=messages_for_llm,
            model_id=model,
            system_prompt=system_prompt,
            user_id=current_user.id,
            abort_flag=lambda: cancel_event.is_set(),
        )

        def _next_safe():
            try:
                return next(sync_gen), False
            except StopIteration:
                return None, True
            except Exception as e:
                logger.error("流式生成异常: %s", str(e))
                return None, True

        try:
            while True:
                if cancel_event.is_set():
                    yield f'data: {json.dumps({"type": "error", "content": "generation_stopped"})}\n\n'
                    break
                item, done = await loop.run_in_executor(None, _next_safe)
                if done or cancel_event.is_set():
                    logger.info(f"[stream] Generator done, cancel={cancel_event.is_set()}")
                    break
                logger.debug(f"[stream] Yielding item: {item[:80] if item else 'empty'}")
                yield item
                try:
                    data = json.loads(item.replace("data: ", "").strip())
                    if data.get("type") == "thinking":
                        thinking_content += data.get("content", "")
                    elif data.get("type") == "content":
                        full_content += data.get("content", "")
                except Exception:
                    pass
        except asyncio.CancelledError:
            # 客户端断连（取消/切换会话），不再 yield，直接落到保存逻辑
            pass
        except Exception as e:
            try:
                yield f'data: {json.dumps({"type": "error", "content": str(e)})}\n\n'
            except Exception:
                pass

        # 无论正常结束还是异常断连，都要保存消息
        _save_assistant_message(db, conversation_id, model, full_content, thinking_content)

        # 清理 cancel Event
        with _cancel_lock:
            _cancel_events.pop(conversation_id, None)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked",
        },
    )


@router.get("/models", response_model=list[ModelInfo])
def get_models(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """获取当前可用的模型列表"""
    return llm_service.get_available_models(db=db)