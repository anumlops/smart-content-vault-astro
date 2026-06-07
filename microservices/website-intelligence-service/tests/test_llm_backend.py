import json
import os
from unittest.mock import patch

import pytest

from app.analyzer import llm_backend


class TestParseLLMResponse:
    def test_parses_clean_json(self):
        result = llm_backend._parse_llm_response('{"title": "Test"}')
        assert result == {"title": "Test"}

    def test_parses_json_with_code_fence(self):
        text = '```json\n{"title": "Test"}\n```'
        result = llm_backend._parse_llm_response(text)
        assert result == {"title": "Test"}

    def test_parses_code_fence_no_lang(self):
        text = '```\n{"title": "Test"}\n```'
        result = llm_backend._parse_llm_response(text)
        assert result == {"title": "Test"}

    def test_invalid_json_returns_none(self):
        result = llm_backend._parse_llm_response("not json")
        assert result is None


class TestIsAvailable:
    def test_returns_true_when_key_set(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
            assert llm_backend.is_available() is True

    def test_returns_false_when_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            assert llm_backend.is_available() is False


class TestAnalyze:
    def test_returns_none_when_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            assert llm_backend.analyze("content") is None

    def test_returns_result_on_success(self):
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "title": "RAG Guide",
                        "summary": "A summary.",
                        "category": "Technology",
                        "tags": ["rag", "ai"],
                        "key_takeaways": ["Key point 1"],
                    })
                }
            }]
        }
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
            with patch("app.analyzer.llm_backend.httpx.post") as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = mock_response
                result = llm_backend.analyze("test content")
                assert result is not None
                assert result["title"] == "RAG Guide"
                assert result["category"] == "Technology"

    def test_returns_none_on_api_error(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
            with patch("app.analyzer.llm_backend.httpx.post") as mock_post:
                mock_post.return_value.status_code = 429
                result = llm_backend.analyze("test content")
                assert result is None


class TestAnalyzerIntegration:
    def test_uses_llm_when_available(self):
        """ContentAnalyzer should use LLM backend when key is set"""
        from app.analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer()
        mock_response = {
            "choices": [{
                "message": {
                    "content": json.dumps({
                        "title": "LLM Title",
                        "summary": "LLM summary.",
                        "category": "Health",
                        "tags": ["test"],
                        "key_takeaways": ["Takeaway 1"],
                    })
                }
            }]
        }
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "sk-test"}):
            with patch("app.analyzer.llm_backend.httpx.post") as mock_post:
                mock_post.return_value.status_code = 200
                mock_post.return_value.json.return_value = mock_response
                result = analyzer.analyze("content", "title")
                assert result["title"] == "LLM Title"
                assert result["category"] == "Health"

    def test_falls_back_to_rule_based(self):
        """ContentAnalyzer should fall back to rule-based when LLM unavailable"""
        from app.analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer()
        with patch.dict(os.environ, {}, clear=True):
            result = analyzer.analyze("Python machine learning API database framework data data data")
            assert result["category"] == "Technology"
            assert len(result["tags"]) > 0
