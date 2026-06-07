from app.extractor_core.service import ContentExtractorService, ExtractorError

__all__ = ["ExtractorService", "ExtractorError"]


class ExtractorService:
    def __init__(self):
        self._inner = ContentExtractorService()

    def extract(self, url: str):
        return self._inner.extract(url)
