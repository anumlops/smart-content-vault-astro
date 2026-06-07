import json

import pytest
from httpx import AsyncClient, ASGITransport

from app.analyzer.analyzer import (
    CATEGORIES,
    _classify_category,
    _extract_key_takeaways,
    _extract_tags,
    _extract_title,
    _generate_summary,
)
from app.main import app

SAMPLE_RAG = """
Retrieval-Augmented Generation (RAG) is a technique that enhances language model generation by incorporating external knowledge. This is typically done by retrieving relevant information from a large corpus.
RAG uses a vector database to find semantically similar documents. The retriever finds relevant contexts to condition the LLM.
A key advantage is that RAG prevents information overload and enhances result quality. The system uses an embedding model to convert text into vectors.
One important consideration is choosing the right chunk size. The chunking strategy directly impacts retrieval accuracy.
"""


class TestTitle:
    def test_uses_provided_title(self):
        assert _extract_title("some content", "My Title") == "My Title"

    def test_extracts_from_first_line(self):
        assert _extract_title("First Real Line\nmore text") == "First Real Line"

    def test_fallback_short_text(self):
        t = _extract_title("Short")
        assert t == "Short"


class TestSummary:
    def test_generates_summary_within_bounds(self):
        summary = _generate_summary(SAMPLE_RAG)
        assert 50 <= len(summary.split()) <= 200

    def test_empty_text(self):
        assert _generate_summary("") == ""


class TestCategory:
    def test_technology_keywords(self):
        text = "python api rest database algorithm framework kubernetes docker cloud deployment"
        assert _classify_category(text) == "Technology"

    def test_health_keywords(self):
        text = "health fitness exercise nutrition workout meditation sleep wellness"
        assert _classify_category(text) == "Health"

    def test_finance_keywords(self):
        text = "finance investment stock trading portfolio asset equity interest"
        assert _classify_category(text) == "Finance"

    def test_empty_text_fallsback(self):
        assert _classify_category("") == "Technology"

    def test_valid_categories(self):
        text = "python machine learning ai data science"
        cat = _classify_category(text)
        assert cat in CATEGORIES


class TestTags:
    def test_returns_relevant_tags(self):
        tags = _extract_tags(SAMPLE_RAG)
        assert len(tags) > 0
        assert all(isinstance(t, str) for t in tags)
        assert all(t.islower() for t in tags)
        assert len(tags) <= 10

    def test_no_duplicates(self):
        tags = _extract_tags(SAMPLE_RAG)
        assert len(tags) == len(set(tags))

    def test_empty_text(self):
        assert _extract_tags("") == []


class TestKeyTakeaways:
    def test_returns_key_sentences(self):
        takeaways = _extract_key_takeaways(SAMPLE_RAG)
        assert len(takeaways) > 0
        assert len(takeaways) <= 5

    def test_empty_text(self):
        assert _extract_key_takeaways("") == []


class TestAnalyzerAPI:
    @pytest.mark.asyncio
    async def test_analyze_endpoint(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/analyze",
                json={"content": SAMPLE_RAG, "title": "RAG Guide"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["title"] == "RAG Guide"
            assert data["category"] in CATEGORIES
            assert len(data["tags"]) <= 10
            assert len(data["key_takeaways"]) >= 1
            assert len(data["summary"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_without_title(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/analyze",
                json={"content": SAMPLE_RAG},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert len(data["title"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_empty_content(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/analyze",
                json={"content": ""},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["tags"] == []
            assert data["key_takeaways"] == []

    @pytest.mark.asyncio
    async def test_extract_and_analyze_together(self):
        from app.crawler import CrawlerService

        crawler = CrawlerService()
        with pytest.MonkeyPatch.context() as mp:
            def mock_extract(url):
                return {
                    "success": True,
                    "url": url,
                    "domain": "example.com",
                    "title": "Test Page",
                    "content": SAMPLE_RAG,
                    "error": None,
                }
            mp.setattr(crawler, "extract", mock_extract)
            result = crawler.extract("https://example.com")
            assert result["success"] is True
