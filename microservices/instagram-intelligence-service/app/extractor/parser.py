import re
from urllib.parse import urlparse


INSTAGRAM_REEL_PATTERN = re.compile(
    r"^(https?:\/\/)?(www\.)?instagram\.com\/reel\/[a-zA-Z0-9_-]+\/?(\?.*)?$"
)
INSTAGRAM_POST_PATTERN = re.compile(
    r"^(https?:\/\/)?(www\.)?instagram\.com\/p\/[a-zA-Z0-9_-]+\/?(\?.*)?$"
)


class ParserError(Exception):
    pass


class InstagramParser:
    VALID_HOSTS = {"instagram.com", "www.instagram.com"}

    @classmethod
    def validate(cls, url: str) -> str:
        if not url or not url.strip():
            raise ParserError("URL is empty")

        url = url.strip()

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        if hostname not in cls.VALID_HOSTS:
            raise ParserError(f"Not an Instagram URL: {url}")

        if INSTAGRAM_REEL_PATTERN.match(url) or INSTAGRAM_POST_PATTERN.match(url):
            return url

        raise ParserError(f"Unsupported Instagram URL format: {url}")

    @classmethod
    def get_content_id(cls, url: str) -> str | None:
        match = re.search(r"/(reel|p)/([a-zA-Z0-9_-]+)", url)
        if match:
            return match.group(2)
        return None
