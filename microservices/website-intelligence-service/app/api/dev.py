import logging
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl

from app.ai import AIService
from app.extractor import ExtractorService

from .dev_sessions import dev_sessions

logger = logging.getLogger(__name__)

router = APIRouter()

extractor = ExtractorService()
ai_service = AIService()

DEV_HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "dev.html")


class DevTestRequest(BaseModel):
    url: HttpUrl


class DevTestResponse(BaseModel):
    session_id: str
    title: str
    summary: str
    tags: list[str]
    word_count: int
    content_preview: str


class DevPublishResponse(BaseModel):
    success: bool
    message: str


class DevSessionsResponse(BaseModel):
    sessions: list[dict]


@router.get("/dev", response_class=HTMLResponse)
def dev_page():
    try:
        with open(DEV_HTML_PATH, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Dev page not found</h1>", status_code=404)


@router.post("/dev/test", response_model=DevTestResponse)
def dev_test(request: DevTestRequest):
    url_str = str(request.url)

    logger.info("Dev test: extracting %s", url_str)
    try:
        doc = extractor.extract(url_str)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Extraction failed: {e}")

    if not doc or not doc.content:
        raise HTTPException(status_code=422, detail="No content extracted")

    logger.info("Dev test: analyzing %s (%d words)", url_str, doc.word_count)
    try:
        analysis = ai_service.analyze(content=doc.content, title=doc.title)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {e}")

    session_id = dev_sessions.create(
        url=url_str,
        title=doc.title,
        summary=analysis["summary"],
        tags=analysis["tags"],
        content=doc.content,
    )

    content_preview = doc.content[:300] + ("..." if len(doc.content) > 300 else "")

    return DevTestResponse(
        session_id=session_id,
        title=doc.title,
        summary=analysis["summary"],
        tags=analysis["tags"],
        word_count=doc.word_count,
        content_preview=content_preview,
    )


@router.post("/dev/publish/{session_id}", response_model=DevPublishResponse)
def dev_publish(session_id: str):
    session = dev_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["published"]:
        return DevPublishResponse(success=False, message="Already published")

    success = dev_sessions.publish(session_id)
    if success:
        return DevPublishResponse(success=True, message="Published successfully")
    return DevPublishResponse(success=False, message="Failed to publish")


@router.get("/dev/sessions", response_model=DevSessionsResponse)
def dev_sessions_list():
    return DevSessionsResponse(sessions=dev_sessions.list_sessions())
