from app.jobs.manager import JobManager
from app.jobs.status import JobStatus


class TestJobManager:
    def test_create_job(self):
        mgr = JobManager()
        job = mgr.create_job("https://example.com")
        assert job["status"] == JobStatus.PENDING
        assert job["url"] == "https://example.com"
        assert job["job_id"] is not None
        assert job["data"] is None
        assert job["error"] is None

    def test_get_job_returns_none_for_missing(self):
        mgr = JobManager()
        assert mgr.get_job("nonexistent") is None

    def test_get_job_returns_job(self):
        mgr = JobManager()
        created = mgr.create_job("https://example.com")
        fetched = mgr.get_job(created["job_id"])
        assert fetched == created

    def test_update_status(self):
        mgr = JobManager()
        job = mgr.create_job("https://example.com")
        mgr.update_status(job["job_id"], JobStatus.EXTRACTING)
        updated = mgr.get_job(job["job_id"])
        assert updated["status"] == JobStatus.EXTRACTING

    def test_complete(self):
        mgr = JobManager()
        job = mgr.create_job("https://example.com")
        data = {"title": "Test", "summary": "Sum", "tags": ["a", "b", "c", "d", "e"]}
        mgr.complete(job["job_id"], data)
        updated = mgr.get_job(job["job_id"])
        assert updated["status"] == JobStatus.COMPLETED
        assert updated["data"] == data

    def test_fail(self):
        mgr = JobManager()
        job = mgr.create_job("https://example.com")
        mgr.fail(job["job_id"], "Something went wrong")
        updated = mgr.get_job(job["job_id"])
        assert updated["status"] == JobStatus.FAILED
        assert updated["error"] == "Something went wrong"

    def test_multiple_jobs(self):
        mgr = JobManager()
        j1 = mgr.create_job("https://a.com")
        j2 = mgr.create_job("https://b.com")
        assert j1["job_id"] != j2["job_id"]
        assert mgr.get_job(j1["job_id"])["url"] == "https://a.com"
        assert mgr.get_job(j2["job_id"])["url"] == "https://b.com"

    def test_update_status_with_error(self):
        mgr = JobManager()
        job = mgr.create_job("https://example.com")
        mgr.update_status(job["job_id"], JobStatus.FAILED, error="error msg")
        updated = mgr.get_job(job["job_id"])
        assert updated["status"] == JobStatus.FAILED
        assert updated["error"] == "error msg"
