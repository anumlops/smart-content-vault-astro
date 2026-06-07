from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.crawler import CrawlerService, ContentExtractor
from app.main import app


class TestContentExtractor:
    def test_extract_domain(self):
        assert ContentExtractor.extract_domain("https://www.example.com/path") == "www.example.com"
        assert ContentExtractor.extract_domain("https://example.com") == "example.com"

    def test_clean_content(self):
        assert ContentExtractor.clean_content("  hello world  ") == "hello world"
        assert ContentExtractor.clean_content("") == ""
        assert ContentExtractor.clean_content(None) == ""


class TestCrawlerService:
    def test_extract_success(self):
        service = CrawlerService()
        with patch("app.crawler.crawler.ContentExtractor.extract_from_url") as mock_extract:
            mock_extract.return_value = ("Main content of the page.", "Page Title")
            result = service.extract("https://example.com")
            assert result["success"] is True
            assert result["url"] == "https://example.com"
            assert result["domain"] == "example.com"
            assert result["title"] == "Page Title"
            assert "Main content" in result["content"]

    def test_extract_fetch_failure(self):
        service = CrawlerService()
        with patch("app.crawler.crawler.ContentExtractor.extract_from_url") as mock_extract:
            mock_extract.return_value = (None, None)
            result = service.extract("https://unreachable.example.com")
            assert result["success"] is False
            assert result["error"] is not None

    def test_extract_empty_content(self):
        service = CrawlerService()
        with patch("app.crawler.crawler.ContentExtractor.extract_from_url") as mock_extract:
            mock_extract.return_value = ("   ", "Title")
            result = service.extract("https://example.com")
            assert result["success"] is False
            assert "No readable content" in result["error"]

    def test_extract_exception(self):
        service = CrawlerService()
        with patch("app.crawler.crawler.ContentExtractor.extract_from_url") as mock_extract:
            mock_extract.side_effect = Exception("Connection timeout")
            result = service.extract("https://example.com")
            assert result["success"] is False
            assert "Connection timeout" in result["error"]


class TestAPI:
    @pytest.mark.asyncio
    async def test_health(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_extract_invalid_url(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/extract", json={"url": "not-a-valid-url"})
            assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_extract_empty_url(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/extract", json={"url": ""})
            assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_extract_empty_body(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/v1/extract", json={})
            assert resp.status_code == 422
