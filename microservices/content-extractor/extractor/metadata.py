import json
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup


class MetadataExtractor:
    def __init__(self, html: str, url: str):
        self._soup = BeautifulSoup(html, "lxml")
        self._url = url
        self._domain = urlparse(url).netloc

    def extract_all(self) -> dict:
        return {
            "url": self._url,
            "domain": self._domain,
            "canonical_url": self._extract_canonical(),
            "title": self._extract_title(),
            "description": self._extract_description(),
            "author": self._extract_author(),
            "published_date": self._extract_published_date(),
            "language": self._extract_language(),
            "og_title": self._extract_og("title"),
            "og_description": self._extract_og("description"),
            "og_image": self._extract_og("image"),
        }

    def _extract_canonical(self) -> str:
        tag = self._soup.find("link", rel="canonical")
        if tag and tag.get("href"):
            return tag["href"]
        return self._url

    def _extract_title(self) -> str:
        og = self._extract_og("title")
        if og:
            return og
        tag = self._soup.find("title")
        if tag and tag.string:
            return tag.string.strip()
        return ""

    def _extract_description(self) -> str:
        og = self._extract_og("description")
        if og:
            return og
        tag = self._soup.find("meta", attrs={"name": "description"})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return ""

    def _extract_og(self, key: str) -> str:
        tag = self._soup.find("meta", property=re.compile(rf"^og:{key}$", re.I))
        if not tag:
            tag = self._soup.find("meta", attrs={"name": re.compile(rf"^og:{key}$", re.I)})
        if tag and tag.get("content"):
            return tag["content"].strip()
        return ""

    def _extract_author(self) -> str:
        selectors = [
            {"attrs": {"name": "author"}},
            {"attrs": {"property": "article:author"}},
            {"attrs": {"name": "twitter:creator"}},
            {"itemprop": "author"},
        ]
        for sel in selectors:
            tag = self._soup.find("meta", **sel)
            if tag and tag.get("content"):
                return tag["content"].strip()
        scripts = self._soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string) if script.string else {}
                author = self._find_in_jsonld(data, "author")
                if author:
                    return author
            except (json.JSONDecodeError, AttributeError):
                continue
        return ""

    def _extract_published_date(self) -> str:
        selectors = [
            {"attrs": {"property": "article:published_time"}},
            {"attrs": {"name": "article:published_time"}},
            {"attrs": {"name": "date"}},
            {"itemprop": "datePublished"},
        ]
        for sel in selectors:
            tag = self._soup.find("meta", **sel)
            if tag and tag.get("content"):
                return tag["content"].strip()
        scripts = self._soup.find_all("script", type="application/ld+json")
        for script in scripts:
            try:
                data = json.loads(script.string) if script.string else {}
                date = self._find_in_jsonld(data, "datePublished")
                if date:
                    return date
            except (json.JSONDecodeError, AttributeError):
                continue
        return ""

    def _extract_language(self) -> str:
        html_tag = self._soup.find("html")
        if html_tag and html_tag.get("lang"):
            return html_tag["lang"].strip()
        meta = self._soup.find("meta", attrs={"http-equiv": "Content-Language"})
        if meta and meta.get("content"):
            return meta["content"].strip()
        return ""

    def _find_in_jsonld(self, data: dict | list, key: str) -> str | None:
        if isinstance(data, dict):
            if key in data:
                val = data[key]
                if isinstance(val, str):
                    return val
                if isinstance(val, dict) and "name" in val:
                    return val["name"]
            for v in data.values():
                if isinstance(v, (dict, list)):
                    result = self._find_in_jsonld(v, key)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_in_jsonld(item, key)
                if result:
                    return result
        return None
