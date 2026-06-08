from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


class TestExtractEndpoint:
    @pytest.mark.asyncio
    async def test_extract_success(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_resp = type("Resp", (), {
                "status_code": 200,
                "text": '<html><head><meta property="og:title" content="Test Reel" /></head></html>',
                "url": "https://www.instagram.com/reel/DW8PkC0AZvb/",
                "headers": {"Content-Type": "text/html"},
            })()
            mock_resp.raise_for_status = lambda: None
            mock_get.return_value = mock_resp

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post(
                    "/api/v1/extract",
                    json={"url": "https://www.instagram.com/reel/DW8PkC0AZvb/"},
                )
                assert resp.status_code == 200
                data = resp.json()
                assert data["success"] is True
                assert data["data"]["title"] == "Test Reel"
                assert data["data"]["platform"] == "instagram"

    @pytest.mark.asyncio
    async def test_extract_invalid_url(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/extract",
                json={"url": "https://youtube.com/watch?v=12345"},
            )
            assert resp.status_code == 422
            data = resp.json()
            assert data["detail"]["success"] is False

    @pytest.mark.asyncio
    async def test_extract_empty_url(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/extract",
                json={"url": ""},
            )
            assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            assert resp.json() == {"status": "ok"}
