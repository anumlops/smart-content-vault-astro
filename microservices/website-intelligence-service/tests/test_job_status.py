import pytest

from app.jobs.status import JobStatus


class TestJobStatus:
    def test_has_all_statuses(self):
        assert JobStatus.PENDING == "PENDING"
        assert JobStatus.EXTRACTING == "EXTRACTING"
        assert JobStatus.ANALYZING == "ANALYZING"
        assert JobStatus.COMPLETED == "COMPLETED"
        assert JobStatus.FAILED == "FAILED"

    def test_valid_transition_values(self):
        statuses = {s.value for s in JobStatus}
        assert statuses == {"PENDING", "EXTRACTING", "ANALYZING", "COMPLETED", "FAILED"}
