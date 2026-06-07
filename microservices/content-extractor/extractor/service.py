import os
from datetime import datetime, timezone

from schemas.document import ExtractedDocument, Metadata

from .cleaner import Cleaner
from .fetcher import Fetcher, FetcherError
from .metadata import MetadataExtractor
from .readability import ReadabilityExtractor


class ExtractorError(Exception):
    pass


class ContentExtractorService:
    def __init__(self, output_dir: str | None = None):
        self._fetcher = Fetcher()
        self._readability = ReadabilityExtractor()
        self._cleaner = Cleaner()
        self._output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "extracted"
        )
        os.makedirs(self._output_dir, exist_ok=True)

    def extract(self, url: str) -> ExtractedDocument:
        if not url or not url.startswith(("http://", "https://")):
            raise ExtractorError("Invalid URL. Must start with http:// or https://")

        try:
            fetch_result = self._fetcher.fetch(url)
        except FetcherError as e:
            raise ExtractorError(f"Failed to fetch URL: {e}") from e

        if not fetch_result.html:
            raise ExtractorError("No HTML content returned from URL")

        meta = MetadataExtractor(fetch_result.html, fetch_result.url)
        meta_data = meta.extract_all()

        raw_content = self._readability.extract(fetch_result.html, fetch_result.url)
        if not raw_content:
            raise ExtractorError("Readability could not extract any content from the page")

        content = self._cleaner.clean(raw_content)
        if not content:
            raise ExtractorError("Content cleaning produced empty result")

        word_count = len(content.split())

        doc = ExtractedDocument(
            url=meta_data["url"],
            canonical_url=meta_data["canonical_url"],
            domain=meta_data["domain"],
            title=meta_data["title"],
            description=meta_data["description"],
            author=meta_data["author"],
            published_date=meta_data["published_date"],
            language=meta_data["language"],
            content=content,
            word_count=word_count,
            extracted_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            metadata=Metadata(
                og_title=meta_data["og_title"],
                og_description=meta_data["og_description"],
                og_image=meta_data["og_image"],
            ),
        )

        self._save(doc)
        return doc

    def _save(self, doc: ExtractedDocument) -> str:
        safe_domain = doc.domain.replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_domain}_{timestamp}.json"
        filepath = os.path.join(self._output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(doc.model_dump_json(indent=2))
        return filepath
