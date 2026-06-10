import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_WATCH_PATTERN = re.compile(
    r"^(https?:\/\/)?((www|m)\.)?youtube\.com\/watch\?v=[a-zA-Z0-9_-]+"
)
YOUTUBE_SHORTS_PATTERN = re.compile(
    r"^(https?:\/\/)?((www|m)\.)?youtube\.com\/shorts\/[a-zA-Z0-9_-]+"
)
YOUTUBE_EMBED_PATTERN = re.compile(
    r"^(https?:\/\/)?((www|m)\.)?youtube\.com\/embed\/[a-zA-Z0-9_-]+"
)
YOUTUBE_SHORT_PATTERN = re.compile(
    r"^(https?:\/\/)?youtu\.be\/[a-zA-Z0-9_-]+"
)


class ParserError(Exception):
    pass


class YouTubeParser:
    VALID_HOSTS = {
        "youtube.com", "www.youtube.com",
        "youtu.be", "www.youtu.be",
        "m.youtube.com",
    }

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
            raise ParserError(f"Not a YouTube URL: {url}")

        if (
            YOUTUBE_WATCH_PATTERN.match(url)
            or YOUTUBE_SHORTS_PATTERN.match(url)
            or YOUTUBE_EMBED_PATTERN.match(url)
            or YOUTUBE_SHORT_PATTERN.match(url)
        ):
            return url

        raise ParserError(f"Unsupported YouTube URL format: {url}")

    @classmethod
    def get_video_id(cls, url: str) -> str | None:
        parsed = urlparse(url)
        hostname = parsed.hostname or ""

        if hostname in ("youtu.be", "www.youtu.be"):
            return parsed.path.lstrip("/").split("/")[0] if parsed.path else None

        if hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
            path = parsed.path
            if path.startswith("/watch"):
                params = parse_qs(parsed.query)
                return params.get("v", [None])[0]
            if path.startswith("/shorts/"):
                return path.split("/shorts/")[1].split("/")[0] if "/shorts/" in path else None
            if path.startswith("/embed/"):
                return path.split("/embed/")[1].split("/")[0] if "/embed/" in path else None

        return None

    @classmethod
    def to_watch_url(cls, url: str) -> str:
        video_id = cls.get_video_id(url)
        if not video_id:
            raise ParserError(f"Cannot extract video ID from: {url}")
        return f"https://www.youtube.com/watch?v={video_id}"
