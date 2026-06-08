import logging
import re

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class MetadataExtractor:
    def __init__(self, html: str, url: str):
        self._soup = BeautifulSoup(html, "html.parser")
        self._url = url

    def extract_all(self) -> dict:
        logger.info("Metadata extraction started")

        result = {
            "title": self._extract_title(),
            "description": self._extract_description(),
            "image": self._extract_image(),
            "url": self._extract_url(),
            "canonical_url": self._extract_canonical(),
            "meta_description": self._extract_meta_description(),
            "page_title": self._extract_page_title(),
        }

        missing = [k for k, v in result.items() if not v]
        if missing:
            logger.info("Missing metadata fields: %s", missing)

        logger.info("Metadata extraction completed")
        return result

    def _extract_og(self, key: str) -> str:
        tag = self._soup.find("meta", property=re.compile(rf"^og:{key}$", re.I))
        if not tag:
            tag = self._soup.find("meta", attrs={"name": re.compile(rf"^og:{key}$", re.I)})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return ""

    def _extract_title(self) -> str:
        return self._extract_og("title")

    def _extract_description(self) -> str:
        return self._extract_og("description")

    def _extract_image(self) -> str:
        return self._extract_og("image")

    def _extract_url(self) -> str:
        og_url = self._extract_og("url")
        if og_url:
            return og_url
        return self._url

    def _extract_canonical(self) -> str:
        tag = self._soup.find("link", rel="canonical")
        if tag and tag.get("href"):
            return tag["href"].strip()
        return ""

    def _extract_meta_description(self) -> str:
        tag = self._soup.find("meta", attrs={"name": "description"})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return ""

    def _extract_page_title(self) -> str:
        tag = self._soup.find("title")
        if tag and tag.string:
            return tag.string.strip()
        return ""
