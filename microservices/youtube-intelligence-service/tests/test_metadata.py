from unittest.mock import MagicMock, patch

from app.extractor.fetcher import Fetcher
from app.extractor.metadata import MetadataExtractor


SAMPLE_PAGE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Test Video Title</title>
  <meta charset="utf-8" />
  <meta name="description" content="This is a meta description of the video" />
  <meta property="og:title" content="OG Video Title" />
  <meta property="og:description" content="OG video description here" />
  <meta property="og:image" content="https://i.ytimg.com/vi/Pdp3p23P-TI/maxresdefault.jpg" />
  <meta property="og:url" content="https://www.youtube.com/watch?v=Pdp3p23P-TI" />
  <link rel="canonical" href="https://www.youtube.com/watch?v=Pdp3p23P-TI" />
  <link itemprop="url" href="/channel/UC123456789" />
</head>
<body></body>
</html>"""

MINIMAL_PAGE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Just a Title</title>
</head>
<body></body>
</html>"""

EMPTY_PAGE_HTML = ""


class TestMetadataExtractor:
    def test_extract_all_fields(self):
        fetcher = MagicMock(spec=Fetcher)

        fetcher.fetch_json.return_value = {
            "title": "oEmbed Video Title",
            "author_name": "Test Channel",
            "author_url": "https://www.youtube.com/channel/UC123456789",
            "thumbnail_url": "https://i.ytimg.com/vi/Pdp3p23P-TI/hqdefault.jpg",
        }

        fetcher.fetch.return_value.html = SAMPLE_PAGE_HTML

        extractor = MetadataExtractor(fetcher, "https://www.youtube.com/watch?v=Pdp3p23P-TI", "Pdp3p23P-TI")
        result = extractor.extract_all()

        assert result["title"] == "oEmbed Video Title"
        assert result["description"] == "OG video description here"
        assert result["image"] == "https://i.ytimg.com/vi/Pdp3p23P-TI/hqdefault.jpg"
        assert result["canonical_url"] == "https://www.youtube.com/watch?v=Pdp3p23P-TI"
        assert result["channel_name"] == "Test Channel"
        assert result["channel_url"] == "https://www.youtube.com/channel/UC123456789"

    def test_extract_fallback_to_page_meta_when_oembed_fails(self):
        fetcher = MagicMock(spec=Fetcher)

        fetcher.fetch_json.side_effect = Exception("oEmbed failed")

        fetcher.fetch.return_value.html = SAMPLE_PAGE_HTML

        extractor = MetadataExtractor(fetcher, "https://www.youtube.com/watch?v=Pdp3p23P-TI", "Pdp3p23P-TI")
        result = extractor.extract_all()

        assert result["title"] == ""
        assert result["description"] == "OG video description here"
        assert result["image"] == "https://i.ytimg.com/vi/Pdp3p23P-TI/maxresdefault.jpg"

    def test_extract_minimal_html(self):
        fetcher = MagicMock(spec=Fetcher)

        fetcher.fetch_json.return_value = {
            "title": "oEmbed Title",
        }

        fetcher.fetch.return_value.html = MINIMAL_PAGE_HTML

        extractor = MetadataExtractor(fetcher, "https://www.youtube.com/watch?v=Pdp3p23P-TI", "Pdp3p23P-TI")
        result = extractor.extract_all()

        assert result["title"] == "oEmbed Title"
        assert result["description"] == ""
        assert result["image"] == "https://i.ytimg.com/vi/Pdp3p23P-TI/maxresdefault.jpg"
        assert result["canonical_url"] == "https://www.youtube.com/watch?v=Pdp3p23P-TI"

    def test_extract_empty_page_html(self):
        fetcher = MagicMock(spec=Fetcher)

        fetcher.fetch_json.return_value = {}

        fetcher.fetch.return_value.html = EMPTY_PAGE_HTML

        extractor = MetadataExtractor(fetcher, "https://www.youtube.com/watch?v=Pdp3p23P-TI", "Pdp3p23P-TI")
        result = extractor.extract_all()

        assert result["title"] == ""
        assert result["description"] == ""
        assert result["image"] == "https://i.ytimg.com/vi/Pdp3p23P-TI/maxresdefault.jpg"
        assert result["canonical_url"] == "https://www.youtube.com/watch?v=Pdp3p23P-TI"

    def test_extract_meta_description_fallback(self):
        fetcher = MagicMock(spec=Fetcher)

        html_no_og = """<!DOCTYPE html>
<html>
<head>
  <meta name="description" content="Fallback description from meta tag" />
</head>
<body></body>
</html>"""

        fetcher.fetch_json.return_value = {}
        fetcher.fetch.return_value.html = html_no_og

        extractor = MetadataExtractor(fetcher, "https://www.youtube.com/watch?v=Pdp3p23P-TI", "Pdp3p23P-TI")
        result = extractor.extract_all()

        assert result["description"] == "Fallback description from meta tag"
