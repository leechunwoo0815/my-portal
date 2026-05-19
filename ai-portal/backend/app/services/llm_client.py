"""
OpenAI-compatible HTTP client for LLM providers.
Replaces litellm with direct httpx calls to DeepSeek / Zhipu / Qwen / Doubao.
All these providers use the same OpenAI chat completion API format.
"""

import json
import logging
import httpx
from typing import Generator, Any, Optional

logger = logging.getLogger("ai-portal.llm.client")


# Provider → base URL mapping
PROVIDER_BASE_URLS: dict[str, str] = {
    "deepseek": "https://api.deepseek.com",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "doubao": "https://ark.cn-beijing.volces.com/api/v3",
    "silicon": "https://api.siliconflow.cn/v1",
    "custom": "",  # user-provided base URL
}


class LLMClient:
    """Lightweight OpenAI-compatible chat client using httpx."""

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        provider: str = "deepseek",
    ):
        self.api_key = api_key
        self.base_url = (base_url or PROVIDER_BASE_URLS.get(provider, "")).rstrip("/")
        self.provider = provider

        # SiliconFlow uses openai/ prefix model names
        if provider in ("silicon", "custom"):
            self.supports_reasoning = False
        else:
            self.supports_reasoning = True

    def _get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

    def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Stream chat completion via SSE.
        Yields dicts with either {"delta": ..., "type": "content"|"thinking"|"usage"}
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
            "stream_options": {"include_usage": True},
        }

        with httpx.Client(timeout=httpx.Timeout(timeout, connect=10.0)) as client:
            logger.debug("LLM请求: provider=%s, model=%s, url=%s", self.provider, model, url)
            with client.stream("POST", url, json=payload, headers=self._get_headers()) as resp:
                resp.raise_for_status()

                for line in resp.iter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = data.get("choices", [])
                    if not choices:
                        continue

                    delta = choices[0].get("delta", {})

                    # reasoning_content (DeepSeek reasoning)
                    reasoning = delta.get("reasoning_content")
                    if reasoning:
                        yield {"type": "thinking", "content": reasoning}

                    # content
                    content = delta.get("content")
                    if content:
                        yield {"type": "content", "content": content}

                    # usage (in the last chunk)
                    usage = data.get("usage")
                    if usage:
                        yield {
                            "type": "usage",
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0),
                        }

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        """
        Non-streaming chat completion.
        Returns {"content": ..., "usage": {...}}
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        with httpx.Client(timeout=httpx.Timeout(timeout, connect=10.0)) as client:
            logger.debug("LLM请求: provider=%s, model=%s, url=%s", self.provider, model, url)
            resp = client.post(url, json=payload, headers=self._get_headers())
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        content = choice.get("message", {}).get("content", "") or ""
        usage = data.get("usage", {})
        return {
            "content": content,
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
        }
