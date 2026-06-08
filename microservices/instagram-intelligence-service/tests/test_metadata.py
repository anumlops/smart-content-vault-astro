from app.extractor.metadata import MetadataExtractor


SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Instagram Post Title</title>
  <meta charset="utf-8" />
  <meta name="description" content="Meta description content" />
  <meta property="og:title" content="OG Title Here" />
  <meta property="og:description" content="OG Description Here" />
  <meta property="og:image" content="https://scontent.cdninstagram.com/v/t51.2885-15/og-image.jpg" />
  <meta property="og:url" content="https://www.instagram.com/reel/DW8PkC0AZvb/" />
  <link rel="canonical" href="https://www.instagram.com/reel/DW8PkC0AZvb/" />
</head>
<body></body>
</html>"""

MINIMAL_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Just a Title</title>
</head>
<body></body>
</html>"""

EMPTY_HTML = ""


class TestMetadataExtractor:
    def test_extract_all_fields(self):
        extractor = MetadataExtractor(SAMPLE_HTML, "https://www.instagram.com/reel/DW8PkC0AZvb/")
        result = extractor.extract_all()

        assert result["title"] == "OG Title Here"
        assert result["description"] == "OG Description Here"
        assert result["image"] == "https://scontent.cdninstagram.com/v/t51.2885-15/og-image.jpg"
        assert result["url"] == "https://www.instagram.com/reel/DW8PkC0AZvb/"
        assert result["canonical_url"] == "https://www.instagram.com/reel/DW8PkC0AZvb/"
        assert result["meta_description"] == "Meta description content"
        assert result["page_title"] == "Instagram Post Title"

    def test_extract_minimal(self):
        extractor = MetadataExtractor(MINIMAL_HTML, "https://www.instagram.com/p/CxYzAbCdEf/")
        result = extractor.extract_all()

        assert result["title"] == ""
        assert result["description"] == ""
        assert result["image"] == ""
        assert result["url"] == "https://www.instagram.com/p/CxYzAbCdEf/"
        assert result["canonical_url"] == ""
        assert result["meta_description"] == ""
        assert result["page_title"] == "Just a Title"

    def test_extract_empty_html(self):
        extractor = MetadataExtractor(EMPTY_HTML, "https://www.instagram.com/reel/DW8PkC0AZvb/")
        result = extractor.extract_all()

        assert result["title"] == ""
        assert result["description"] == ""
        assert result["image"] == ""
        assert result["url"] == "https://www.instagram.com/reel/DW8PkC0AZvb/"
