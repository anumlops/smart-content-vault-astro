import logging
import time

from app.schemas.instagram import InstagramData

from .fetcher import Fetcher, FetcherError
from .metadata import MetadataExtractor
from .parser import InstagramParser, ParserError

logger = logging.getLogger(__name__)


class ExtractorError(Exception):
    pass


class InstagramExtractor:
    def __init__(self, timeout: int = 30):
        self._fetcher = Fetcher(timeout=timeout)

    def extract(self, url: str) -> InstagramData:
        start = time.time()

        try:
            url = InstagramParser.validate(url)
        except ParserError as e:
            raise ExtractorError(str(e)) from e

        logger.info("Processing URL: %s", url)

        try:
            fetch_result = self._fetcher.fetch(url)
        except FetcherError as e:
            raise ExtractorError(f"Failed to fetch URL: {e}") from e

        if not fetch_result.html or not fetch_result.html.strip():
            raise ExtractorError("No HTML content returned from URL")

        meta = MetadataExtractor(fetch_result.html, fetch_result.url)
        meta_data = meta.extract_all()

        data = InstagramData(
            url=url,
            canonical_url=meta_data["canonical_url"] or meta_data["url"] or url,
            title=meta_data["title"] or meta_data["page_title"] or "",
            description=(
                meta_data["description"]
                or meta_data["meta_description"]
                or ""
            ),
            thumbnail=meta_data["image"] or "",
        )

        elapsed = time.time() - start
        logger.info("Processing completed in %.2fs: %s", elapsed, url)

        return data
