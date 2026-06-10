import logging
import re

from bs4 import BeautifulSoup

from .fetcher import Fetcher

logger = logging.getLogger(__name__)


class MetadataExtractor:
    OEMBED_URL = "https://www.youtube.com/oembed"

    def __init__(self, fetcher: Fetcher, watch_url: str, video_id: str):
        self._fetcher = fetcher
        self._watch_url = watch_url
        self._video_id = video_id

    def extract_all(self) -> dict:
        logger.info("YouTube metadata extraction started: %s", self._video_id)

        oembed = self._fetch_oembed()

        page_html = self._fetch_page()

        result = {
            "title": oembed.get("title", ""),
            "description": self._extract_description(page_html),
            "image": self._extract_best_thumbnail(oembed),
            "canonical_url": self._watch_url,
            "channel_name": oembed.get("author_name", ""),
            "channel_url": (
                f"https://www.youtube.com{page_channel_path}"
                if (page_channel_path := self._extract_channel_path(page_html))
                else oembed.get("author_url", "")
            ),
        }

        missing = [k for k, v in result.items() if not v]
        if missing:
            logger.info("Missing metadata fields: %s", missing)

        logger.info("YouTube metadata extraction completed")
        return result

    def _fetch_oembed(self) -> dict:
        oembed_full_url = f"{self.OEMBED_URL}?url={self._watch_url}&format=json"
        try:
            return self._fetcher.fetch_json(oembed_full_url)
        except Exception as e:
            logger.warning("oEmbed fetch failed: %s", e)
            return {}

    def _fetch_page(self) -> str:
        try:
            result = self._fetcher.fetch(self._watch_url)
            return result.html
        except Exception as e:
            logger.warning("Page fetch failed: %s", e)
            return ""

    def _extract_description(self, html: str) -> str:
        if not html:
            return ""
        soup = BeautifulSoup(html, "html.parser")

        og_desc = soup.find("meta", property=re.compile(r"^og:description$", re.I))
        if og_desc and og_desc.get("content"):
            return og_desc["content"].strip()

        meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
        if meta_desc and meta_desc.get("content"):
            return meta_desc["content"].strip()

        return ""

    def _extract_best_thumbnail(self, oembed: dict) -> str:
        oembed_thumb = oembed.get("thumbnail_url", "")
        if oembed_thumb:
            return oembed_thumb

        return f"https://i.ytimg.com/vi/{self._video_id}/maxresdefault.jpg"

    def _extract_channel_path(self, html: str) -> str | None:
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")

        channel_link = soup.find("link", attrs={"itemprop": "url"})
        if channel_link and channel_link.get("href"):
            return channel_link["href"].strip()

        return None
