import re
from urllib.parse import urlparse
from datetime import datetime


def extract_domain(url: str) -> str:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return re.sub(r"^www\.", "", domain)
    except Exception:
        return url


def validate_url(url: str) -> bool:
    if not url or not url.strip():
        return False
    pattern = re.compile(
        r"^https?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(pattern.match(url.strip()))


def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    return f"{parsed.scheme}://{parsed.netloc}{path}"


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def format_timestamp(dt: datetime | None = None) -> str:
    if dt is None:
        dt = datetime.utcnow()
    return dt.isoformat()


def truncate_text(text: str, max_length: int = 500) -> str:
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."
