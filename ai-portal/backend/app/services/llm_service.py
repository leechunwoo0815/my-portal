"""
大模型服务模块 - 通过 httpx 直连各家 OpenAI 兼容 API
支持流式输出、Token 统计、每日调用限制
"""

import logging
from datetime import datetime, timezone
from typing import AsyncGenerator, Optional, Any, Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decrypt_api_key
from app.models import ApiCallLog, ApiKey, Message, Conversation
from app.services.llm_client import LLMClient, PROVIDER_BASE_URLS

logger = logging.getLogger("ai-portal.llm")

# 模型显示名称
MODEL_DISPLAY_NAMES: dict[str, str] = {
    "deepseek-v4-flash": "DeepSeek V4 Flash",
    "deepseek-v4-pro": "DeepSeek V4 Pro",
    "glm-4-flash": "GLM-4-Flash",
    "glm-4": "GLM-4",
    "qwen-turbo": "通义千问 Turbo",
    "qwen-plus": "通义千问 Plus",
    "doubao-pro": "豆包 Pro",
    "doubao-lite": "豆包 Lite",
}


class LLMService:
    """大模型服务类 - 封装 httpx 直连调用逻辑"""

    def get_available_models(self, db: Optional[Session] = None) -> list[dict[str, Any]]:
        """获取当前可用的模型列表"""
        available: list[dict[str, Any]] = []
        seen: set[str] = set()

        if db is not None:
            try:
                keys = db.query(ApiKey).filter(
                    ApiKey.is_active == True,
                    ApiKey.api_key_encrypted.isnot(None),
                    ApiKey.api_key_encrypted != '',
                ).order_by(ApiKey.priority.desc()).all()

                for key in keys:
                    if not key.model_names:
                        continue
                    for model_id in key.model_names:
                        prefixed_id = f"{key.provider}:{model_id}"
                        if prefixed_id in seen:
                            continue
                        seen.add(prefixed_id)
                        display_name = MODEL_DISPLAY_NAMES.get(model_id, model_id)
                        available.append({
                            "id": prefixed_id,
                            "name": f"{key.provider} · {display_name}",
                            "provider": key.provider,
                            "description": f"{key.provider} · {display_name}",
                            "base_url": key.base_url or '',
                        })
            except Exception as e:
                logger.error("获取可用模型列表失败: %s", str(e))

        # env vars fallback
        env_keys = {
            "deepseek": settings.DEEPSEEK_API_KEY,
            "zhipu": settings.GLM_API_KEY,
            "qwen": settings.QWEN_API_KEY,
            "doubao": settings.DOUBAO_API_KEY,
        }
        for model_id, info in _MODEL_ENV_MAP.items():
            prefixed_id = f"{info['provider']}:{model_id}"
            if prefixed_id in seen:
                continue
            provider = info["provider"]
            api_key = env_keys.get(provider)
            if api_key and api_key.strip():
                seen.add(prefixed_id)
                display_name = MODEL_DISPLAY_NAMES.get(model_id, model_id)
                available.append({
                    "id": prefixed_id,
                    "name": f"{provider} · {display_name}",
                    "provider": provider,
                    "description": f"{display_name} - {provider}",
                })

        return available

    def check_daily_limit(self, db: Session, user_id: Optional[int] = None) -> bool:
        if user_id is not None:
            from app.models import User
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_admin:
                return True

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        count = db.query(ApiCallLog).filter(ApiCallLog.created_at >= today_start).count()
        return count < settings.DAILY_CHAT_LIMIT

    def stream_chat(
        self,
        db: Session,
        messages: list[dict[str, str]],
        model_id: str,
        system_prompt: Optional[str] = None,
        user_id: Optional[int] = None,
        abort_flag: Optional[Callable[[], bool]] = None,
    ):
        """流式聊天 - 通过 SSE 向前端推送 AI 回复"""
        if abort_flag is None:
            abort_flag = lambda: False

        if not self.check_daily_limit(db, user_id):
            logger.warning("每日调用次数已达上限: user_id=%s", user_id)
            yield self._format_sse({
                "type": "error",
                "content": f"今日调用次数已达上限（{settings.DAILY_CHAT_LIMIT}次），请明天再试",
            })
            return

        # 解析 provider:model_id
        raw_model_id = model_id
        db_provider = None
        db_api_key = None
        db_base_url = None

        if ":" in model_id:
            parts = model_id.split(":", 1)
            db_provider = parts[0]
            raw_model_id = parts[1]

        # 查找 API key
        if db is not None:
            try:
                q = db.query(ApiKey).filter(
                    ApiKey.is_active == True,
                    ApiKey.api_key_encrypted.isnot(None),
                    ApiKey.api_key_encrypted != '',
                )
                if db_provider:
                    q = q.filter(ApiKey.provider == db_provider)
                for key in q.order_by(ApiKey.priority.desc()).all():
                    if key.model_names and raw_model_id in key.model_names:
                        db_api_key = decrypt_api_key(key.api_key_encrypted)
                        db_base_url = key.base_url
                        db_provider = key.provider
                        break
            except Exception as e:
                logger.error("查询API密钥失败: %s", str(e))

        if db_api_key:
            provider = db_provider
            api_key = db_api_key
            base_url = db_base_url or PROVIDER_BASE_URLS.get(provider, "")
            api_model = raw_model_id
        else:
            env_keys = {
                "deepseek": settings.DEEPSEEK_API_KEY,
                "zhipu": settings.GLM_API_KEY,
                "qwen": settings.QWEN_API_KEY,
                "doubao": settings.DOUBAO_API_KEY,
            }
            env_urls = {
                "deepseek": settings.DEEPSEEK_BASE_URL,
                "zhipu": settings.GLM_BASE_URL,
                "qwen": settings.QWEN_BASE_URL,
                "doubao": settings.DOUBAO_BASE_URL,
            }
            model_config = _MODEL_ENV_MAP.get(raw_model_id)
            if not model_config:
                yield self._format_sse({"type": "error", "content": f"不支持的模型: {raw_model_id}"})
                return
            provider = model_config["provider"]
            api_key = env_keys.get(provider)
            if not api_key:
                yield self._format_sse({"type": "error", "content": f"{provider} 的API密钥未配置"})
                return
            base_url = env_urls.get(provider) or PROVIDER_BASE_URLS.get(provider, "")
            api_model = raw_model_id

        # 构建消息
        formatted_messages: list[dict[str, str]] = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        # 调用 LLM
        client = LLMClient(api_key=api_key, base_url=base_url, provider=provider)
        try:
            full_content = ""
            prompt_tokens = 0
            completion_tokens = 0
            total_tokens = 0

            try:
                for event in client.stream_chat(
                    messages=formatted_messages,
                    model=api_model,
                    max_tokens=settings.MAX_TOKENS_PER_REQUEST,
                    temperature=0.7,
                    timeout=30.0,
                ):
                    if abort_flag():
                        yield self._format_sse({"type": "error", "content": "generation_stopped"})
                        return

                    if event["type"] in ("thinking", "content"):
                        yield self._format_sse(event)
                        if event["type"] == "content":
                            full_content += event["content"]
                    elif event["type"] == "usage":
                        prompt_tokens = event["prompt_tokens"]
                        completion_tokens = event["completion_tokens"]
                        total_tokens = event["total_tokens"]

            except Exception as stream_error:
                error_msg = str(stream_error)
                if any(k in error_msg.lower() for k in ("timeout", "timed out", "connect")):
                    yield self._format_sse({"type": "error", "content": "请求超时，请检查网络连接后重试。"})
                    return
                raise

            yield self._format_sse({
                "type": "done",
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            })

            logger.info("LLM调用成功: model=%s, tokens=%d", model_id, total_tokens)

            self._log_api_call(
                db=db, provider=provider, model_name=model_id,
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                total_tokens=total_tokens, is_success=True,
                user_id=user_id,
            )

        except Exception as e:
            error_msg = str(e)
            yield self._format_sse({"type": "error", "content": f"模型调用失败: {error_msg}"})
            self._log_api_call(
                db=db, provider=provider, model_name=model_id,
                prompt_tokens=0, completion_tokens=0, total_tokens=0,
                is_success=False, error_message=error_msg,
                user_id=user_id,
            )

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model_id: str = "deepseek-v4-flash",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        db: Optional[Session] = None,
    ) -> str:
        """非流式聊天 - 直接返回完整回复"""
        raw_model_id = model_id
        db_provider = None
        if ":" in model_id:
            parts = model_id.split(":", 1)
            db_provider = parts[0]
            raw_model_id = parts[1]

        api_key = None
        base_url = None
        provider = None

        if db is not None:
            try:
                q = db.query(ApiKey).filter(
                    ApiKey.is_active == True,
                    ApiKey.api_key_encrypted.isnot(None),
                    ApiKey.api_key_encrypted != '',
                )
                if db_provider:
                    q = q.filter(ApiKey.provider == db_provider)
                for key in q.order_by(ApiKey.priority.desc()).all():
                    if key.model_names and raw_model_id in key.model_names:
                        api_key = decrypt_api_key(key.api_key_encrypted)
                        base_url = key.base_url
                        provider = key.provider
                        break
            except Exception as e:
                logger.error("查询API密钥失败: %s", str(e))

        if not api_key:
            env_keys = {
                "deepseek": settings.DEEPSEEK_API_KEY,
                "zhipu": settings.GLM_API_KEY,
                "qwen": settings.QWEN_API_KEY,
                "doubao": settings.DOUBAO_API_KEY,
            }
            model_config = _MODEL_ENV_MAP.get(raw_model_id)
            if not model_config:
                raise ValueError(f"不支持的模型: {raw_model_id}")

            provider = model_config["provider"]
            api_key = env_keys.get(provider)
            if not api_key:
                raise ValueError(f"{provider} 的API密钥未配置")

            base_url = PROVIDER_BASE_URLS.get(provider, "")
        formatted_messages: list[dict[str, str]] = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
        formatted_messages.extend(messages)

        client = LLMClient(api_key=api_key, base_url=base_url, provider=provider)
        result = client.chat_completion(
            messages=formatted_messages,
            model=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return result["content"]

    def fetch_models_from_api(self, api_key: str, base_url: str, provider: str) -> list[str]:
        """根据 API 密钥和 BaseURL 获取服务商支持的模型列表"""
        import httpx
        if not api_key or not base_url:
            return []
        base_url = base_url.rstrip("/")

        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            with httpx.Client(timeout=httpx.Timeout(15.0, connect=10.0), follow_redirects=True) as c:
                resp = c.get(f"{base_url}/models", headers=headers)
            if resp.status_code != 200:
                return []
            data = resp.json()
            if provider == "ollama":
                return [m.get("name", "") for m in data.get("models", []) if m.get("name")]
            elif provider == "gemini":
                return [m.get("name", "").replace("models/", "") for m in data.get("models", []) if m.get("name")]
            else:
                return [m.get("id", "") or m.get("name", "") for m in data.get("data", []) if m.get("id") or m.get("name")]
        except Exception as e:
            logger.error("获取模型列表失败: provider=%s, error=%s", provider, str(e))
            return []

    def count_tokens(self, text: str, model: str = "") -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 chars for English, 2 chars for Chinese)"""
        if not text:
            return 0
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        return chinese_chars * 2 + max(1, other_chars // 4)

    def _format_sse(self, data: dict[str, Any]) -> str:
        import json
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    def _log_api_call(self, db, provider, model_name, prompt_tokens, completion_tokens,
                       total_tokens, is_success, error_message=None, cost=None, user_id=None):
        if db is None:
            return
        try:
            log = ApiCallLog(
                provider=provider, model_name=model_name,
                prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
                total_tokens=total_tokens, cost=cost,
                is_success=is_success, error_message=error_message,
                user_id=user_id,
            )
            db.add(log)
            db.flush()
        except Exception as e:
            logger.error("记录API调用日志失败: %s", str(e))
            db.rollback()


# 环境变量 fallback 的模型映射
_MODEL_ENV_MAP: dict[str, dict[str, str]] = {
    "deepseek-v4-flash": {"provider": "deepseek"},
    "deepseek-v4-pro": {"provider": "deepseek"},
    "glm-4-flash": {"provider": "zhipu"},
    "glm-4": {"provider": "zhipu"},
    "qwen-turbo": {"provider": "qwen"},
    "qwen-plus": {"provider": "qwen"},
    "doubao-pro": {"provider": "doubao"},
    "doubao-lite": {"provider": "doubao"},
}

llm_service = LLMService()
