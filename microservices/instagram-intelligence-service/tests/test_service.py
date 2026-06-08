from unittest.mock import patch

import pytest

from app.extractor.service import ExtractorError, InstagramExtractor
from app.schemas.instagram import InstagramData


SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Instagram Post</title>
  <meta charset="utf-8" />
  <meta property="og:title" content="OG Title Here" />
  <meta property="og:description" content="OG Description Here" />
  <meta property="og:image" content="https://scontent.cdninstagram.com/og-image.jpg" />
  <meta property="og:url" content="https://www.instagram.com/reel/DW8PkC0AZvb/" />
  <link rel="canonical" href="https://www.instagram.com/reel/DW8PkC0AZvb/" />
</head>
<body></body>
</html>"""


class TestInstagramExtractor:
    def test_extract_success(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_resp = type("Resp", (), {
                "status_code": 200,
                "text": SAMPLE_HTML,
                "url": "https://www.instagram.com/reel/DW8PkC0AZvb/",
                "headers": {"Content-Type": "text/html"},
            })()

            def raise_for_status():
                pass

            mock_resp.raise_for_status = raise_for_status
            mock_get.return_value = mock_resp

            extractor = InstagramExtractor()
            result = extractor.extract("https://www.instagram.com/reel/DW8PkC0AZvb/")

            assert isinstance(result, InstagramData)
            assert result.platform == "instagram"
            assert result.title == "OG Title Here"
            assert result.description == "OG Description Here"
            assert result.thumbnail == "https://scontent.cdninstagram.com/og-image.jpg"
            assert result.canonical_url == "https://www.instagram.com/reel/DW8PkC0AZvb/"

    def test_extract_invalid_url(self):
        extractor = InstagramExtractor()
        with pytest.raises(ExtractorError, match="Not an Instagram URL"):
            extractor.extract("https://youtube.com/watch?v=12345")

    def test_extract_empty_url(self):
        extractor = InstagramExtractor()
        with pytest.raises(ExtractorError, match="URL is empty"):
            extractor.extract("")
