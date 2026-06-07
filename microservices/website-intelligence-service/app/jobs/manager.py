import logging
import threading
import uuid
from datetime import datetime, timezone

from .status import JobStatus

logger = logging.getLogger(__name__)


class JobManager:
    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create_job(self, url: str) -> dict:
        job_id = uuid.uuid4().hex[:12]
        job = {
            "job_id": job_id,
            "url": url,
            "status": JobStatus.PENDING,
            "data": None,
            "error": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._jobs[job_id] = job
        logger.info("Job %s created for URL: %s", job_id, url)
        return job

    def get_job(self, job_id: str) -> dict | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update_status(self, job_id: str, status: JobStatus, error: str | None = None):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job["status"] = status
                job["updated_at"] = datetime.now(timezone.utc).isoformat()
                if error:
                    job["error"] = error

    def complete(self, job_id: str, data: dict):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job["status"] = JobStatus.COMPLETED
                job["data"] = data
                job["updated_at"] = datetime.now(timezone.utc).isoformat()

    def fail(self, job_id: str, error: str):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job["status"] = JobStatus.FAILED
                job["error"] = error
                job["updated_at"] = datetime.now(timezone.utc).isoformat()
                logger.error("Job %s failed: %s", job_id, error)
