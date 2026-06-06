"""
Website content analyzer using LLM.
Generates summary, category, tags, and key takeaways.
"""

import json
import os
from typing import Any

import httpx

from src.modules.shared.constants import (
    VALID_CATEGORIES,
    TAG_MIN_COUNT,
    TAG_MAX_COUNT,
)
from .prompts import build_analysis_prompt
from .schemas import WebsiteAnalysis, WebsiteContent


class WebsiteAnalyzer:
    """Analyzes website content using a configurable LLM provider."""

    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.api_url = os.getenv(
            "LLM_API_URL",
            "https://api.openai.com/v1/chat/completions",
        )
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.api_key:
            return self._fallback_analysis(system_prompt, user_prompt)

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.3,
                        "max_tokens": 1000,
                        "response_format": {"type": "json_object"},
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return self._fallback_analysis(system_prompt, user_prompt, str(e))

    def _fallback_analysis(
        self,
        system_prompt: str,
        user_prompt: str,
        error: str | None = None,
    ) -> str | None:
        """Simple keyword-based fallback when LLM is unavailable."""
        import re

        content = user_prompt
        title_match = re.search(r"Title: (.+)", content)
        title = title_match.group(1).strip() if title_match else "Untitled"

        domain_match = re.search(r"Domain: (.+)", content)
        domain = domain_match.group(1).strip() if domain_match else ""

        category = "Technology"
        for cat in VALID_CATEGORIES:
            if cat.lower() in content.lower():
                category = cat
                break

        words = re.findall(r"\b[A-Z][a-z]{2,}\b", content[:2000])
        tags = list(dict.fromkeys(w.lower() for w in words))[:TAG_MIN_COUNT]
        if len(tags) < TAG_MIN_COUNT:
            tags = [domain.split(".")[0]] if domain else ["website"]
            tags.extend(["technology", "article"])

        fallback = {
            "title": title,
            "summary": "Content analysis unavailable. Basic metadata extracted.",
            "category": category,
            "tags": tags[:TAG_MAX_COUNT],
            "key_takeaways": ["Content could not be fully analyzed by AI."],
        }
        return json.dumps(fallback)

    def _parse_response(self, raw: str | None) -> dict[str, Any]:
        if not raw:
            return self._empty_result()

        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0]

        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            return self._empty_result()

        return result

    def _empty_result(self) -> dict[str, Any]:
        return {
            "title": None,
            "summary": None,
            "category": None,
            "tags": [],
            "key_takeaways": [],
        }

    def _validate_result(self, result: dict[str, Any]) -> dict[str, Any]:
        if result.get("category") and result["category"] not in VALID_CATEGORIES:
            result["category"] = "Technology"

        tags = result.get("tags", [])
        if isinstance(tags, list):
            tags = list(dict.fromkeys(t.lower().strip() for t in tags if t))
            result["tags"] = tags[:TAG_MAX_COUNT]

        takeaways = result.get("key_takeaways", [])
        if isinstance(takeaways, list):
            result["key_takeaways"] = [t.strip() for t in takeaways if t.strip()]

        return result

    async def analyze(self, content: WebsiteContent) -> WebsiteAnalysis:
        if content.error and not content.text:
            return WebsiteAnalysis(
                title=content.title,
                error=content.error,
                category=None,
                tags=[],
                key_takeaways=[],
            )

        system_prompt, user_prompt = build_analysis_prompt(
            title=content.title,
            domain=content.domain,
            url=content.url,
            content=content.text or "",
        )

        raw_response = self._call_llm(system_prompt, user_prompt)
        parsed = self._parse_response(raw_response)
        validated = self._validate_result(parsed)

        return WebsiteAnalysis(
            title=validated.get("title") or content.title,
            summary=validated.get("summary"),
            category=validated.get("category"),
            tags=validated.get("tags", []),
            key_takeaways=validated.get("key_takeaways", []),
        )
