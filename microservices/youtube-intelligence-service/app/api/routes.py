import logging

from fastapi import APIRouter, HTTPException

from app.extractor import ExtractorError, YouTubeExtractor
from app.schemas.youtube import ExtractRequest, ExtractResponse

logger = logging.getLogger(__name__)

router = APIRouter()
extractor = YouTubeExtractor()


@router.post("/extract", response_model=ExtractResponse)
def extract_content(request: ExtractRequest):
    url = request.url.strip()

    if not url:
        raise HTTPException(
            status_code=422,
            detail=ExtractResponse(success=False, error="URL is required").model_dump(),
        )

    try:
        data = extractor.extract(url)
        return ExtractResponse(success=True, data=data)
    except ExtractorError as e:
        logger.error("Extraction failed for %s: %s", url, str(e))
        raise HTTPException(
            status_code=422,
            detail=ExtractResponse(success=False, error=str(e)).model_dump(),
        )
    except Exception as e:
        logger.exception("Unexpected error for %s", url)
        raise HTTPException(
            status_code=500,
            detail=ExtractResponse(success=False, error=f"Internal error: {str(e)}").model_dump(),
        )
