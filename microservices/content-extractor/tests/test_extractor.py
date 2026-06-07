import pytest

from extractor.cleaner import Cleaner
from extractor.fetcher import Fetcher, FetcherError
from extractor.metadata import MetadataExtractor
from extractor.readability import ReadabilityExtractor


class TestFetcher:
    def test_invalid_url_raises(self):
        f = Fetcher()
        with pytest.raises(FetcherError):
            f.fetch("not-a-url")


SAMPLE_HTML = """
<html lang="en">
<head>
  <title>Test Article</title>
  <meta name="description" content="A test article">
  <meta property="og:title" content="OG Test Article">
  <meta property="og:description" content="OG description">
  <meta property="og:image" content="https://example.com/image.jpg">
  <meta name="author" content="John Doe">
  <meta property="article:published_time" content="2024-01-15T10:00:00Z">
  <link rel="canonical" href="https://example.com/canonical">
</head>
<body>
  <nav>Navigation</nav>
  <article>
    <h1>Test Article</h1>
    <p>This is the first paragraph of the article. It contains meaningful content.</p>
    <p>This is the second paragraph with more information.</p>
    <ul>
      <li>List item one</li>
      <li>List item two</li>
    </ul>
  </article>
  <footer>Footer content</footer>
</body>
</html>
"""


class TestMetadataExtractor:
    def test_extracts_title(self):
        m = MetadataExtractor(SAMPLE_HTML, "https://example.com")
        data = m.extract_all()
        assert data["title"] == "OG Test Article"

    def test_extracts_domain(self):
        m = MetadataExtractor(SAMPLE_HTML, "https://example.com/page")
        data = m.extract_all()
        assert data["domain"] == "example.com"

    def test_extracts_canonical(self):
        m = MetadataExtractor(SAMPLE_HTML, "https://example.com/page")
        data = m.extract_all()
        assert data["canonical_url"] == "https://example.com/canonical"

    def test_extracts_og_tags(self):
        m = MetadataExtractor(SAMPLE_HTML, "https://example.com")
        data = m.extract_all()
        assert data["og_title"] == "OG Test Article"
        assert data["og_description"] == "OG description"
        assert data["og_image"] == "https://example.com/image.jpg"

    def test_extracts_author(self):
        m = MetadataExtractor(SAMPLE_HTML, "https://example.com")
        data = m.extract_all()
        assert data["author"] == "John Doe"

    def test_extracts_published_date(self):
        m = MetadataExtractor(SAMPLE_HTML, "https://example.com")
        data = m.extract_all()
        assert data["published_date"] == "2024-01-15T10:00:00Z"

    def test_extracts_language(self):
        m = MetadataExtractor(SAMPLE_HTML, "https://example.com")
        data = m.extract_all()
        assert data["language"] == "en"

    def test_no_metadata_fallsback_gracefully(self):
        html = "<html><body><p>Hello</p></body></html>"
        m = MetadataExtractor(html, "https://example.com")
        data = m.extract_all()
        assert data["title"] == ""
        assert data["author"] == ""
        assert data["published_date"] == ""


SAMPLE_READABLE = """
<html><body>
  <nav>Nav links</nav>
  <div id="content">
    <h1>Main Title</h1>
    <p>First paragraph with some content.</p>
    <p>Second paragraph with more text.</p>
  </div>
  <footer>Footer links here</footer>
</body></html>
"""


class TestReadabilityExtractor:
    def test_extracts_main_content(self):
        r = ReadabilityExtractor()
        result = r.extract(SAMPLE_READABLE, "https://example.com")
        assert result is not None
        assert "Main Title" in result or "First paragraph" in result

    def test_empty_html_returns_empty(self):
        r = ReadabilityExtractor()
        assert r.extract("") == ""
        assert r.extract("   ") == ""


class TestCleaner:
    def test_removes_script_and_style(self):
        html = '<p>Hello</p><script>alert(1)</script><style>.c{}</style>'
        c = Cleaner()
        result = c.clean(html)
        assert "Hello" in result
        assert "alert" not in result

    def test_preserves_headings(self):
        html = '<h1>Title</h1><h2>Subtitle</h2><p>Text</p>'
        c = Cleaner()
        result = c.clean(html)
        assert "# Title" in result
        assert "## Subtitle" in result

    def test_preserves_list_items(self):
        html = '<ul><li>One</li><li>Two</li></ul>'
        c = Cleaner()
        result = c.clean(html)
        assert "- One" in result
        assert "- Two" in result

    def test_empty_input(self):
        c = Cleaner()
        assert c.clean("") == ""
        assert c.clean(None) == ""
