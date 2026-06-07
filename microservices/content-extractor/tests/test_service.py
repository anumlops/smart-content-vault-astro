import pytest

from extractor.service import ContentExtractorService, ExtractorError


class TestService:
    def test_invalid_url_raises(self):
        svc = ContentExtractorService()
        with pytest.raises(ExtractorError, match="Invalid URL"):
            svc.extract("not-a-url")

    def test_empty_url_raises(self):
        svc = ContentExtractorService()
        with pytest.raises(ExtractorError, match="Invalid URL"):
            svc.extract("")

    def test_ftp_url_raises(self):
        svc = ContentExtractorService()
        with pytest.raises(ExtractorError, match="Invalid URL"):
            svc.extract("ftp://example.com")
