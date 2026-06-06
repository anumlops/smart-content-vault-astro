"""
Website Intelligence Service.
Orchestrates crawling and analysis of website content.
"""

from datetime import datetime

from src.modules.shared.types import (
    ContentSource,
    ContentProcessor,
    ContentCategory,
    EnrichmentStatus,
    ProcessingResult,
)
from src.modules.shared.utils import validate_url, extract_domain, normalize_url
from .crawler import WebsiteCrawler
from .analyzer import WebsiteAnalyzer


class WebsiteProcessor(ContentProcessor):
    """
    Full website content processor.
    Implements the ContentProcessor interface for website URLs.
    """

    source_type = "website"

    def __init__(self):
        self.crawler = WebsiteCrawler()
        self.analyzer = WebsiteAnalyzer()

    def can_handle(self, url: str) -> bool:
        return self.crawler.can_handle(url)

    async def extract(self, url: str) -> ContentSource:
        if not validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        website_content = self.crawler.extract(url)

        return ContentSource(
            url=website_content.url,
            content_type="website",
            raw_html=website_content.html,
            extracted_text=website_content.text,
            metadata={
                "title": website_content.title,
                "domain": website_content.domain,
                **website_content.metadata,
            },
        )

    async def analyze(self, source: ContentSource) -> ProcessingResult:
        from .schemas import WebsiteContent

        website_content = WebsiteContent(
            url=source.url,
            domain=source.metadata.get("domain", extract_domain(source.url)),
            title=source.metadata.get("title"),
            html=source.raw_html,
            text=source.extracted_text,
            metadata=source.metadata,
        )

        analysis = await self.analyzer.analyze(website_content)

        if analysis.error:
            return ProcessingResult(
                url=source.url,
                domain=extract_domain(source.url),
                title=analysis.title or source.metadata.get("title"),
                summary=None,
                category=None,
                tags=[],
                key_takeaways=[],
                extracted_text=source.extracted_text,
                raw_content=source.raw_html,
                error=analysis.error,
                status=EnrichmentStatus.FAILED,
            )

        try:
            category = ContentCategory(analysis.category) if analysis.category else None
        except ValueError:
            category = None

        return ProcessingResult(
            url=source.url,
            domain=extract_domain(source.url),
            title=analysis.title or source.metadata.get("title"),
            summary=analysis.summary,
            category=category,
            tags=analysis.tags or [],
            key_takeaways=analysis.key_takeaways or [],
            extracted_text=source.extracted_text,
            raw_content=source.raw_html,
            status=EnrichmentStatus.COMPLETED,
            processed_at=datetime.utcnow().isoformat(),
        )

    async def process_url(self, url: str) -> ProcessingResult:
        try:
            source = await self.extract(url)
            result = await self.analyze(source)
            return result
        except ValueError as e:
            return ProcessingResult(
                url=url,
                domain=extract_domain(url),
                title=None,
                summary=None,
                category=None,
                tags=[],
                key_takeaways=[],
                extracted_text=None,
                raw_content=None,
                error=str(e),
                status=EnrichmentStatus.FAILED,
            )
        except Exception as e:
            return ProcessingResult(
                url=url,
                domain=extract_domain(url),
                title=None,
                summary=None,
                category=None,
                tags=[],
                key_takeaways=[],
                extracted_text=None,
                raw_content=None,
                error=f"Processing failed: {str(e)}",
                status=EnrichmentStatus.FAILED,
            )
