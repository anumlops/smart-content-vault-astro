import json
import os

import httpx

OPENROUTER_BASE = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "moonshotai/kimi-k2.6"

ANALYSIS_PROMPT = """You are a content intelligence engine. Analyze the extracted website content.

Return ONLY valid JSON.

Required format:
{{
  "title": "",
  "summary": "",
  "category": "",
  "tags": [],
  "key_takeaways": []
}}

Allowed categories: Technology, Business, Finance, Productivity, Education, Career, Marketing, Health, Entertainment, Lifestyle

Tag rules: lowercase, no duplicates, max 10, search friendly.

Content:
{content}"""


def is_available() -> bool:
    return bool(os.getenv("OPENROUTER_API_KEY"))


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


def analyze(content: str, title: str | None = None) -> dict | None:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return None

    prompt_text = ANALYSIS_PROMPT.format(content=content[:50000])
    if title:
        prompt_text += f"\n\nThe page title is: {title}"

    try:
        resp = httpx.post(
            OPENROUTER_BASE,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
                "messages": [{"role": "user", "content": prompt_text}],
                "max_tokens": 2000,
                "temperature": 0.1,
            },
            timeout=120,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        choice = data["choices"][0]
        msg = choice["message"]
        raw = msg.get("content") or msg.get("reasoning") or ""
        if not raw:
            return None

        return _parse_llm_response(raw)

    except Exception:
        return None
