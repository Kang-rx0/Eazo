# 模型调用封装（文档十二：所有模型调用经过本模块，带 1 次重试和 30s 超时）。
# chat：Agent 主循环用；embed：RAG 用；vision：食物照片识别用。
import base64
import logging
import time

from openai import OpenAI

from . import config

logger = logging.getLogger(__name__)

_client = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL,
            timeout=30,
        )
    return _client


def chat(messages: list[dict], tools: list[dict] | None = None):
    """调 chat 模型，返回 choices[0].message。失败重试 1 次，再失败抛异常（调用方兜底）。"""
    kwargs = {"model": config.CHAT_MODEL, "messages": messages}
    if tools:
        kwargs["tools"] = tools
    for attempt in range(2):
        try:
            start = time.perf_counter()
            resp = get_client().chat.completions.create(**kwargs)
            msg = resp.choices[0].message
            called = [tc.function.name for tc in (msg.tool_calls or [])]
            logger.info(
                "llm_call model=%s tools=%s 耗时=%.1fs",
                config.CHAT_MODEL, called or "无(最终输出)", time.perf_counter() - start,
            )
            return msg
        except Exception:
            if attempt == 0:
                logger.warning("chat 调用失败，重试第1次", exc_info=True)
                time.sleep(1)
            else:
                logger.error("chat 调用重试后仍失败", exc_info=True)
                raise


def vision(image_bytes: bytes, prompt: str, mime: str = "image/jpeg") -> str:
    """视觉模型识别图片，返回文本。失败重试 1 次，再失败抛异常（调用方兜底）。"""
    b64 = base64.b64encode(image_bytes).decode()
    messages = [{
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": prompt},
        ],
    }]
    for attempt in range(2):
        try:
            start = time.perf_counter()
            resp = get_client().chat.completions.create(
                model=config.VISION_MODEL, messages=messages
            )
            logger.info(
                "llm_call model=%s vision 耗时=%.1fs",
                config.VISION_MODEL, time.perf_counter() - start,
            )
            return resp.choices[0].message.content
        except Exception:
            if attempt == 0:
                logger.warning("vision 调用失败，重试第1次", exc_info=True)
                time.sleep(1)
            else:
                logger.error("vision 调用重试后仍失败", exc_info=True)
                raise


def embed(texts: list[str]) -> list[list[float]]:
    """文本向量化。失败重试 1 次，再失败抛异常（调用方决定兜底）。"""
    for attempt in range(2):
        try:
            start = time.perf_counter()
            resp = get_client().embeddings.create(
                model=config.EMBED_MODEL, input=texts
            )
            logger.info(
                "llm_call model=%s 条数=%d 耗时=%.1fs",
                config.EMBED_MODEL, len(texts), time.perf_counter() - start,
            )
            # 按 index 排序，保证与输入顺序一致
            return [d.embedding for d in sorted(resp.data, key=lambda d: d.index)]
        except Exception:
            if attempt == 0:
                logger.warning("embed 调用失败，重试第1次", exc_info=True)
                time.sleep(1)
            else:
                logger.error("embed 调用重试后仍失败", exc_info=True)
                raise
