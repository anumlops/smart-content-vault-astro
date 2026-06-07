from .extractor import ContentExtractor


class CrawlerService:
    def __init__(self, timeout: int = 30):
        self._timeout = timeout

    def extract(self, url: str) -> dict:
        domain = ContentExtractor.extract_domain(url)

        try:
            content, title = ContentExtractor.extract_from_url(url)
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "domain": domain,
                "title": None,
                "content": None,
                "error": str(e),
            }

        if content is None:
            return {
                "success": False,
                "url": url,
                "domain": domain,
                "title": None,
                "content": None,
                "error": "Failed to fetch or extract content from URL",
            }

        content = ContentExtractor.clean_content(content)

        if not content:
            return {
                "success": False,
                "url": url,
                "domain": domain,
                "title": title,
                "content": None,
                "error": "No readable content extracted from page",
            }

        return {
            "success": True,
            "url": url,
            "domain": domain,
            "title": title,
            "content": content,
            "error": None,
        }
