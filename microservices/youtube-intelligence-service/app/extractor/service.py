import logging
import time

from app.schemas.youtube import YouTubeData

from .fetcher import Fetcher, FetcherError
from .metadata import MetadataExtractor
from .parser import YouTubeParser, ParserError
from .transcript import TranscriptExtractor, TranscriptError

logger = logging.getLogger(__name__)


class ExtractorError(Exception):
    pass


class YouTubeExtractor:
    def __init__(self, timeout: int = 30):
        self._fetcher = Fetcher(timeout=timeout)

    def extract(self, url: str) -> YouTubeData:
        start = time.time()

        try:
            url = YouTubeParser.validate(url)
        except ParserError as e:
            raise ExtractorError(str(e)) from e

        video_id = YouTubeParser.get_video_id(url)
        if not video_id:
            raise ExtractorError(f"Cannot extract video ID from: {url}")

        watch_url = YouTubeParser.to_watch_url(url)

        logger.info("Processing YouTube video: %s (video_id=%s)", url, video_id)

        meta = MetadataExtractor(self._fetcher, watch_url, video_id)
        meta_data = meta.extract_all()

        transcript = None
        try:
            transcript = TranscriptExtractor.extract(video_id)
        except TranscriptError as e:
            logger.info("Transcript not available for %s: %s", video_id, e)

        data = YouTubeData(
            url=url,
            canonical_url=meta_data["canonical_url"] or url,
            title=meta_data["title"] or "",
            description=meta_data["description"] or "",
            thumbnail=meta_data["image"] or "",
            channel_name=meta_data["channel_name"] or "",
            channel_url=meta_data["channel_url"] or "",
            video_id=video_id,
            transcript=transcript,
        )

        elapsed = time.time() - start
        logger.info("Processing completed in %.2fs: %s", elapsed, url)

        return data
