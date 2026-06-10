from unittest.mock import MagicMock, patch

import pytest

from app.extractor.transcript import TranscriptExtractor, TranscriptError
from app.schemas.youtube import TranscriptSegment


def _make_snippet(text: str, start: float, duration: float):
    s = MagicMock()
    s.text = text
    s.start = start
    s.duration = duration
    return s


class TestTranscriptExtractor:
    def test_extract_success(self):
        with patch("app.extractor.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_instance = MagicMock()
            mock_api_cls.return_value = mock_instance
            mock_instance.fetch.return_value = [
                _make_snippet("Hello world", 0.0, 1.5),
                _make_snippet("This is a test", 1.5, 2.0),
            ]

            result = TranscriptExtractor.extract("Pdp3p23P-TI")

            assert len(result) == 2
            assert isinstance(result[0], TranscriptSegment)
            assert result[0].text == "Hello world"
            assert result[0].start == 0.0
            assert result[0].duration == 1.5
            assert result[1].text == "This is a test"

    def test_extract_transcripts_disabled(self):
        with patch("app.extractor.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_instance = MagicMock()
            mock_api_cls.return_value = mock_instance
            from youtube_transcript_api._errors import TranscriptsDisabled
            mock_instance.fetch.side_effect = TranscriptsDisabled("disabled")

            with pytest.raises(TranscriptError, match="Transcripts are disabled"):
                TranscriptExtractor.extract("Pdp3p23P-TI")

    def test_extract_no_transcript_found(self):
        with patch("app.extractor.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_instance = MagicMock()
            mock_api_cls.return_value = mock_instance
            from youtube_transcript_api._errors import NoTranscriptFound
            from youtube_transcript_api._transcripts import TranscriptList
            mock_instance.fetch.side_effect = NoTranscriptFound(
                "Pdp3p23P-TI", ["en"], MagicMock(spec=TranscriptList)
            )

            with pytest.raises(TranscriptError, match="No transcript available"):
                TranscriptExtractor.extract("Pdp3p23P-TI")

    def test_extract_video_unavailable(self):
        with patch("app.extractor.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_instance = MagicMock()
            mock_api_cls.return_value = mock_instance
            from youtube_transcript_api._errors import VideoUnavailable
            mock_instance.fetch.side_effect = VideoUnavailable("unavailable")

            with pytest.raises(TranscriptError, match="Video is unavailable"):
                TranscriptExtractor.extract("Pdp3p23P-TI")

    def test_extract_generic_error(self):
        with patch("app.extractor.transcript.YouTubeTranscriptApi") as mock_api_cls:
            mock_instance = MagicMock()
            mock_api_cls.return_value = mock_instance
            mock_instance.fetch.side_effect = Exception("Something went wrong")

            with pytest.raises(TranscriptError, match="Transcript error"):
                TranscriptExtractor.extract("Pdp3p23P-TI")
