from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


class TestExtractEndpoint:
    @pytest.mark.asyncio
    async def test_extract_success(self):
        with (
            patch("app.extractor.fetcher.requests.get") as mock_get,
            patch("app.extractor.transcript.YouTubeTranscriptApi") as mock_api_cls,
        ):
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = ""
            mock_resp.url = "https://www.youtube.com/watch?v=Pdp3p23P-TI"
            mock_resp.headers = {"Content-Type": "text/html"}
            mock_resp.raise_for_status = lambda: None
            mock_resp.json.return_value = {
                "title": "",
                "author_name": "",
                "author_url": "",
                "thumbnail_url": "",
            }
            mock_get.return_value = mock_resp

            mock_instance = MagicMock()
            mock_api_cls.return_value = mock_instance
            mock_instance.fetch.return_value = []

            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                resp = await client.post(
                    "/api/v1/extract",
                    json={"url": "https://www.youtube.com/watch?v=Pdp3p23P-TI"},
                )
                assert resp.status_code == 200
                data = resp.json()
                assert data["success"] is True
                assert data["data"]["platform"] == "youtube"
                assert data["data"]["video_id"] == "Pdp3p23P-TI"

    @pytest.mark.asyncio
    async def test_extract_invalid_url(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            resp = await client.post(
                "/api/v1/extract",
                json={"url": "https://vimeo.com/12345"},
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
