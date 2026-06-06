"""
Instagram Content Processor — PLACEHOLDER

This module is a placeholder for future Instagram content processing.
It defines the interface that will be implemented later.

To implement:
1. Use an Instagram scraper or API client to extract post/reel data
2. Implement the ContentProcessor protocol from src.modules.shared.types
3. Add Instagram-specific analysis (image caption, comments)
4. Register in the unified content ingestion system
"""

from src.modules.shared.types import ContentProcessor


class InstagramProcessor(ContentProcessor):
    """Placeholder for Instagram content processing."""

    source_type = "instagram"

    def can_handle(self, url: str) -> bool:
        return "instagram.com" in url.lower()

    async def extract(self, url: str):
        raise NotImplementedError("Instagram processing not yet implemented")

    async def analyze(self, content):
        raise NotImplementedError("Instagram processing not yet implemented")
