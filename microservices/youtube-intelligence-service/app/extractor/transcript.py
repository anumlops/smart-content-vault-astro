import logging

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from app.schemas.youtube import TranscriptSegment

logger = logging.getLogger(__name__)


class TranscriptError(Exception):
    pass


class TranscriptExtractor:
    @classmethod
    def extract(cls, video_id: str) -> list[TranscriptSegment]:
        logger.info("Transcript extraction started: %s", video_id)

        try:
            api = YouTubeTranscriptApi()
            raw = api.fetch(video_id)
        except TranscriptsDisabled:
            logger.info("Transcripts disabled for video: %s", video_id)
            raise TranscriptError("Transcripts are disabled for this video")
        except NoTranscriptFound:
            logger.info("No transcript found for video: %s", video_id)
            raise TranscriptError("No transcript available for this video")
        except VideoUnavailable:
            logger.info("Video unavailable: %s", video_id)
            raise TranscriptError("Video is unavailable")
        except Exception as e:
            logger.error("Transcript extraction failed for %s: %s", video_id, str(e))
            raise TranscriptError(f"Transcript error: {str(e)}") from e

        segments = [
            TranscriptSegment(text=item.text, start=item.start, duration=item.duration)
            for item in raw
        ]

        logger.info(
            "Transcript extraction completed: %s (%d segments)",
            video_id,
            len(segments),
        )

        return segments
