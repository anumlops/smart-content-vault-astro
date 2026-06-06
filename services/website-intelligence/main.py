"""
Website Intelligence Service — FastAPI server.
Runs alongside the Astro app to provide website content analysis.
"""

import json
import sys
import os
from pathlib import Path

# Add project root to path for module imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from src.modules.website import WebsiteProcessor

app = FastAPI(
    title="Smart Content Vault — Website Intelligence",
    description="Content extraction and analysis for website URLs",
    version="1.0.0",
)

processor = WebsiteProcessor()


class AnalyzeRequest(BaseModel):
    url: str


class AnalyzeResponse(BaseModel):
    url: str
    domain: str
    title: str | None = None
    summary: str | None = None
    category: str | None = None
    tags: list[str] = []
    key_takeaways: list[str] = []
    extracted_text: str | None = None
    error: str | None = None
    status: str = "completed"
    processed_at: str = ""


@app.get("/health")
async def health():
    return {"status": "ok", "service": "website-intelligence"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_website(request: AnalyzeRequest):
    try:
        result = await processor.process_url(request.url)

        return AnalyzeResponse(
            url=result.url,
            domain=result.domain,
            title=result.title,
            summary=result.summary,
            category=result.category.value if result.category else None,
            tags=result.tags,
            key_takeaways=result.key_takeaways,
            extracted_text=result.extracted_text,
            error=result.error,
            status=result.status.value,
            processed_at=result.processed_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/enrich", response_model=AnalyzeResponse)
async def enrich_content(request: AnalyzeRequest):
    """Alias for /analyze — integrates with existing pipeline naming."""
    return await analyze_website(request)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("WEBSITE_INTELLIGENCE_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
