from html import parser as html_parser
from urllib.parse import urlparse

import trafilatura


class _TitleExtractor(html_parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self._in_title = False
        self.title = None

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and self.title is None:
            self.title = data.strip()


class ContentExtractor:
    @staticmethod
    def extract_domain(url: str) -> str:
        return urlparse(url).netloc

    @staticmethod
    def extract_from_url(url: str) -> tuple[str | None, str | None]:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            return None, None
        doc = trafilatura.bare_extraction(downloaded)
        if doc is None:
            return None, None
        text = doc.text if hasattr(doc, "text") else None
        title = doc.title if hasattr(doc, "title") else None
        if not title:
            parser = _TitleExtractor()
            parser.feed(downloaded)
            title = parser.title
        if text is None:
            text = trafilatura.extract(
                downloaded,
                output_format="txt",
                include_tables=False,
                include_images=False,
                include_links=False,
                favor_recall=False,
            )
        return text, title

    @staticmethod
    def extract_from_html(html: str) -> tuple[str | None, str | None]:
        result = trafilatura.extract(
            html,
            output_format="txt",
            include_tables=False,
            include_images=False,
            include_links=False,
            favor_recall=False,
        )
        return result, None

    @staticmethod
    def clean_content(text: str) -> str:
        if not text:
            return ""
        return text.strip()
