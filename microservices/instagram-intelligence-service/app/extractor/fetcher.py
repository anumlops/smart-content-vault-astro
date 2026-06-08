import logging

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class FetchResult:
    def __init__(self, html: str, url: str, status_code: int, headers: dict | None = None):
        self.html = html
        self.url = url
        self.status_code = status_code
        self.headers = headers or {}


class FetcherError(Exception):
    pass


class Fetcher:
    def __init__(self, timeout: int = 30, user_agent: str | None = None):
        self._timeout = timeout
        self._user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

    def fetch(self, url: str) -> FetchResult:
        logger.info("Fetch started: %s", url)

        try:
            resp = requests.get(
                url,
                timeout=self._timeout,
                headers={
                    "User-Agent": self._user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
                allow_redirects=True,
            )
            resp.raise_for_status()

            logger.info("Fetch completed: %s (status=%d)", url, resp.status_code)

            content_type = resp.headers.get("Content-Type", "")
            if "text/" not in content_type and "application/xhtml" not in content_type:
                logger.warning("Unexpected Content-Type: %s", content_type)

            return FetchResult(resp.text, resp.url, resp.status_code, dict(resp.headers))

        except RequestException as e:
            logger.error("Fetch failed: %s - %s", url, str(e))
            raise FetcherError(str(e)) from e
