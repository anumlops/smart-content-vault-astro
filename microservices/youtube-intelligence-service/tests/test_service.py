from unittest.mock import MagicMock, patch

import pytest

from app.extractor.service import ExtractorError, YouTubeExtractor
from app.schemas.youtube import YouTubeData


class TestYouTubeExtractor:
    def _make_snippet(self, text: str, start: float, duration: float):
        s = MagicMock()
        s.text = text
        s.start = start
        s.duration = duration
        return s

    def _mock_transcript_api(self, return_value=None, side_effect=None):
        p = patch("app.extractor.transcript.YouTubeTranscriptApi")
        mock_cls = p.start()
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        if side_effect:
            mock_instance.fetch.side_effect = side_effect
        else:
            mock_instance.fetch.return_value = return_value or []
        return p

    def _make_http_mock(self, *, text="", url="https://www.youtube.com/watch?v=Pdp3p23P-TI", oembed_data=None):
        resp = MagicMock()
        resp.status_code = 200
        resp.text = text
        resp.url = url
        resp.headers = {"Content-Type": "text/html"}
        resp.raise_for_status = lambda: None
        resp.json.return_value = oembed_data or {
            "title": "",
            "author_name": "",
            "author_url": "",
            "thumbnail_url": "",
        }
        return resp

    def test_extract_success_with_transcript(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_get.return_value = self._make_http_mock(
                oembed_data={
                    "title": "Test Video",
                    "author_name": "Test Channel",
                    "author_url": "https://www.youtube.com/channel/UCtest",
                    "thumbnail_url": "https://i.ytimg.com/vi/test/hqdefault.jpg",
                }
            )

            transcript_patch = self._mock_transcript_api(
                return_value=[self._make_snippet("Hello world", 0.0, 1.5)]
            )

            extractor = YouTubeExtractor()
            result = extractor.extract("https://www.youtube.com/watch?v=Pdp3p23P-TI")

            transcript_patch.stop()

            assert isinstance(result, YouTubeData)
            assert result.platform == "youtube"
            assert result.video_id == "Pdp3p23P-TI"
            assert result.title == "Test Video"
            assert result.transcript is not None
            assert len(result.transcript) == 1

    def test_extract_success_without_transcript(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_get.return_value = self._make_http_mock()

            from youtube_transcript_api._errors import TranscriptsDisabled
            transcript_patch = self._mock_transcript_api(
                side_effect=TranscriptsDisabled("disabled")
            )

            extractor = YouTubeExtractor()
            result = extractor.extract("https://www.youtube.com/watch?v=Pdp3p23P-TI")

            transcript_patch.stop()

            assert isinstance(result, YouTubeData)
            assert result.video_id == "Pdp3p23P-TI"
            assert result.transcript is None

    def test_extract_invalid_url(self):
        extractor = YouTubeExtractor()
        with pytest.raises(ExtractorError, match="Not a YouTube URL"):
            extractor.extract("https://vimeo.com/12345")

    def test_extract_empty_url(self):
        extractor = YouTubeExtractor()
        with pytest.raises(ExtractorError, match="URL is empty"):
            extractor.extract("")

    def test_extract_short_url(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_get.return_value = self._make_http_mock(
                url="https://youtu.be/Pdp3p23P-TI",
            )

            transcript_patch = self._mock_transcript_api(return_value=[])

            extractor = YouTubeExtractor()
            result = extractor.extract("https://youtu.be/Pdp3p23P-TI")

            transcript_patch.stop()

            assert isinstance(result, YouTubeData)
            assert result.video_id == "Pdp3p23P-TI"
            assert result.canonical_url == "https://www.youtube.com/watch?v=Pdp3p23P-TI"
