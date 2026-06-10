from unittest.mock import patch

import pytest
import requests

from app.extractor.fetcher import Fetcher, FetcherError


class TestFetcher:
    def test_fetch_success(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_resp = requests.Response()
            mock_resp.status_code = 200
            mock_resp._content = b"<html><body>Hello</body></html>"
            mock_resp.headers = {"Content-Type": "text/html"}
            mock_resp.url = "https://www.youtube.com/watch?v=Pdp3p23P-TI"
            mock_get.return_value = mock_resp

            fetcher = Fetcher()
            result = fetcher.fetch("https://www.youtube.com/watch?v=Pdp3p23P-TI")

            assert result.status_code == 200
            assert "<html>" in result.html
            assert result.url == "https://www.youtube.com/watch?v=Pdp3p23P-TI"

    def test_fetch_failure(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Connection error")

            fetcher = Fetcher()
            with pytest.raises(FetcherError, match="Connection error"):
                fetcher.fetch("https://www.youtube.com/watch?v=Pdp3p23P-TI")

    def test_fetch_timeout(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

            fetcher = Fetcher(timeout=5)
            with pytest.raises(FetcherError, match="timed out"):
                fetcher.fetch("https://www.youtube.com/watch?v=Pdp3p23P-TI")

    def test_fetch_http_error(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_resp = requests.Response()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp

            fetcher = Fetcher()
            with pytest.raises(FetcherError):
                fetcher.fetch("https://www.youtube.com/watch?v=MISSING")

    def test_fetch_json_success(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_resp = requests.Response()
            mock_resp.status_code = 200
            mock_resp.headers = {"Content-Type": "application/json"}

            import json
            mock_resp._content = json.dumps({"title": "Test Video"}).encode()

            mock_get.return_value = mock_resp

            fetcher = Fetcher()
            result = fetcher.fetch_json("https://www.youtube.com/oembed?url=test&format=json")

            assert result == {"title": "Test Video"}

    def test_fetch_json_failure(self):
        with patch("app.extractor.fetcher.requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("JSON error")

            fetcher = Fetcher()
            with pytest.raises(FetcherError, match="JSON error"):
                fetcher.fetch_json("https://www.youtube.com/oembed?url=test")
