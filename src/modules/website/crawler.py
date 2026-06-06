"""
Website content crawler using Trafilatura.
Extracts clean article content from any website URL.
"""

import trafilatura
from trafilatura.settings import use_config

from src.modules.shared.utils import extract_domain, validate_url
from .schemas import WebsiteContent


class WebsiteCrawler:
    """Extracts clean content from website URLs using Trafilatura."""

    def __init__(self):
        self.config = use_config()
        self.config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")

    def can_handle(self, url: str) -> bool:
        return validate_url(url)

    def extract(self, url: str) -> WebsiteContent:
        if not validate_url(url):
            raise ValueError(f"Invalid URL: {url}")

        domain = extract_domain(url)

        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return WebsiteContent(
                url=url,
                domain=domain,
                error="Failed to download page content",
            )

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            include_images=False,
            include_links=False,
            output_format="txt",
            with_metadata=True,
        )

        title = trafilatura.extract(
            downloaded,
            output_format="txt",
            include_formatting=False,
            include_links=False,
            include_images=False,
            with_metadata=True,
        )

        metadata = {}
        try:
            meta = trafilatura.extract_metadata(downloaded)
            if meta:
                metadata = {
                    "author": meta.get("author"),
                    "date": meta.get("date"),
                    "site_name": meta.get("sitename"),
                    "description": meta.get("description"),
                }
        except Exception:
            pass

        page_title = title.split("\n")[0].strip() if title else None

        if not text or len(text.strip()) < 50:
            return WebsiteContent(
                url=url,
                domain=domain,
                title=page_title,
                html=downloaded,
                text=text.strip() if text else None,
                metadata=metadata,
                error="Insufficient content extracted",
            )

        return WebsiteContent(
            url=url,
            domain=domain,
            title=page_title,
            html=downloaded,
            text=text.strip(),
            metadata=metadata,
        )
