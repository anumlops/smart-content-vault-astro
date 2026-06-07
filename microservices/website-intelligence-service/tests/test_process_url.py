from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


class TestProcessURL:
    @pytest.mark.asyncio
    async def test_process_url_returns_job_id(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/process-url",
                json={"url": "https://example.com/article"},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "job_id" in data
            assert data["status"] in ("PENDING", "EXTRACTING")

    @pytest.mark.asyncio
    async def test_process_url_invalid_url(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/process-url",
                json={"url": "not-a-url"},
            )
            assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_process_url_empty_body(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/v1/process-url",
                json={},
            )
            assert resp.status_code == 422


class TestGetJob:
    @pytest.mark.asyncio
    async def test_get_job_returns_status(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_resp = await client.post(
                "/api/v1/process-url",
                json={"url": "https://example.com/article"},
            )
            job_id = create_resp.json()["job_id"]
            get_resp = await client.get(f"/api/v1/jobs/{job_id}")
            assert get_resp.status_code == 200
            data = get_resp.json()
            assert data["job_id"] == job_id
            assert data["status"] in ("PENDING", "EXTRACTING", "ANALYZING", "COMPLETED", "FAILED")

    @pytest.mark.asyncio
    async def test_get_job_not_found(self):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/v1/jobs/nonexistent")
            assert resp.status_code == 404
