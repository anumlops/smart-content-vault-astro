import logging
import threading

from fastapi import APIRouter, HTTPException

from app.ai import AIService
from app.analyzer import ContentAnalyzer
from app.crawler import CrawlerService
from app.extractor import ExtractorService
from app.jobs import JobStatus
from app.jobs.manager import JobManager
from app.schemas import (
    AnalyzeLLMRequest,
    AnalyzeLLMResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    ExtractRequest,
    ExtractResponse,
    JobResponse,
    ProcessURLRequest,
    ProcessURLResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

crawler_service = CrawlerService()
content_extractor = ExtractorService()
analyzer = ContentAnalyzer()
ai_service = AIService()
job_manager = JobManager()


@router.post("/extract", response_model=ExtractResponse)
def extract_content(request: ExtractRequest):
    url_str = str(request.url)
    result = crawler_service.extract(url_str)

    if not result["success"]:
        raise HTTPException(
            status_code=422,
            detail=ExtractResponse(
                success=False,
                url=result["url"],
                domain=result["domain"],
                error=result["error"],
            ).model_dump(),
        )

    return ExtractResponse(
        success=True,
        url=result["url"],
        domain=result["domain"],
        title=result["title"],
        content=result["content"],
    )


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_content(request: AnalyzeRequest):
    result = analyzer.analyze(content=request.content, title=request.title)
    return AnalyzeResponse(**result)


@router.post("/analyze-llm", response_model=AnalyzeLLMResponse)
def analyze_llm(request: AnalyzeLLMRequest):
    result = ai_service.analyze(content=request.content, title=request.title)
    return AnalyzeLLMResponse(**result)


@router.post("/process-url", response_model=ProcessURLResponse)
def process_url(request: ProcessURLRequest):
    url_str = str(request.url)
    job = job_manager.create_job(url_str)
    thread = threading.Thread(target=_process_job, args=(job["job_id"], url_str), daemon=True)
    thread.start()
    logger.info("Background thread started for job %s", job["job_id"])
    return ProcessURLResponse(job_id=job["job_id"], status=job["status"])


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str):
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job)


def _process_job(job_id: str, url: str):
    logger.info("Job %s: processing URL %s", job_id, url)

    job_manager.update_status(job_id, JobStatus.EXTRACTING)
    try:
        doc = content_extractor.extract(url)
    except Exception as e:
        job_manager.fail(job_id, f"Extraction failed: {e}")
        return

    if not doc.content:
        job_manager.fail(job_id, "No content extracted from URL")
        return

    logger.info("Job %s: extraction complete (%d words)", job_id, doc.word_count)

    job_manager.update_status(job_id, JobStatus.ANALYZING)
    try:
        analysis = ai_service.analyze(content=doc.content, title=doc.title)
    except Exception as e:
        job_manager.fail(job_id, f"Analysis failed: {e}")
        return

    data = {
        "title": doc.title,
        "summary": analysis["summary"],
        "tags": analysis["tags"],
    }
    job_manager.complete(job_id, data)
    logger.info("Job %s: completed successfully", job_id)
