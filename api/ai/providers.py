import json
import logging
import os

import httpx

from .prompts import ANALYSIS_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"

KIMI_MODEL = "moonshotai/kimi-k2.6"
DEEPSEEK_MODEL = "deepseek/deepseek-chat"


class LLMError(Exception):
    pass


class RateLimitError(LLMError):
    pass


class TimeoutError(LLMError):
    pass


class InvalidResponseError(LLMError):
    pass


def _build_prompt(content: str, title: str | None = None) -> str:
    text = content[:50000]
    prompt = ANALYSIS_PROMPT_TEMPLATE.format(content=text)
    if title:
        prompt += f"\n\nThe page title is: {title}"
    return prompt


def _parse_llm_response(raw: str) -> dict | None:
    text = raw.strip()
    if text.startswith("```json"):
        text = text.split("```json", 1)[1]
        if "```" in text:
            text = text.split("```", 1)[0]
    elif text.startswith("```"):
        text = text.split("```", 1)[1]
        if "```" in text:
            text = text.split("```", 1)[0]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def call_llm(content: str, title: str | None = None, model: str | None = None) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        raise LLMError("OPENROUTER_API_KEY not set")

    model_name = model or os.getenv("OPENROUTER_MODEL") or os.getenv("LLM_MODEL") or DEEPSEEK_MODEL
    prompt = _build_prompt(content, title)

    logger.info("Calling %s via OpenRouter", model_name)

    try:
        resp = httpx.post(
            OPENROUTER_BASE,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.1,
            },
            timeout=45,
        )
    except httpx.TimeoutException:
        raise TimeoutError(f"Request to {model_name} timed out")
    except httpx.RequestError as e:
        raise LLMError(f"Request to {model_name} failed: {e}")

    if resp.status_code == 429:
        raise RateLimitError(f"Rate limited on {model_name}")
    if resp.status_code != 200:
        raise LLMError(
            f"{model_name} returned HTTP {resp.status_code}: {resp.text[:200]}"
        )

    try:
        data = resp.json()
        choice = data["choices"][0]
        msg = choice["message"]
        raw = msg.get("content") or msg.get("reasoning") or ""
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise InvalidResponseError(f"Unexpected response format: {e}")

    if not raw:
        raise InvalidResponseError("Empty response from model")

    parsed = _parse_llm_response(raw)
    if parsed is None:
        raise InvalidResponseError("Failed to parse JSON from model response")

    return parsed
