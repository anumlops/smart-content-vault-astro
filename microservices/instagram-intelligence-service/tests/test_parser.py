import pytest

from app.extractor.parser import InstagramParser, ParserError


class TestInstagramParser:
    def test_valid_reel_url(self):
        url = "https://www.instagram.com/reel/DW8PkC0AZvb/"
        result = InstagramParser.validate(url)
        assert result == url

    def test_valid_reel_url_without_www(self):
        url = "https://instagram.com/reel/DW8PkC0AZvb/"
        result = InstagramParser.validate(url)
        assert result == url

    def test_valid_post_url(self):
        url = "https://www.instagram.com/p/CxYzAbCdEf/"
        result = InstagramParser.validate(url)
        assert result == url

    def test_valid_url_with_query_params(self):
        url = "https://www.instagram.com/reel/DW8PkC0AZvb/?utm_source=ig_web_copy_link"
        result = InstagramParser.validate(url)
        assert result == url

    def test_valid_url_without_scheme(self):
        url = "www.instagram.com/reel/DW8PkC0AZvb/"
        result = InstagramParser.validate(url)
        assert result.startswith("https://")

    def test_invalid_url_empty(self):
        with pytest.raises(ParserError, match="URL is empty"):
            InstagramParser.validate("")

    def test_invalid_url_non_instagram(self):
        with pytest.raises(ParserError, match="Not an Instagram URL"):
            InstagramParser.validate("https://youtube.com/watch?v=12345")

    def test_invalid_url_unsupported_format(self):
        with pytest.raises(ParserError, match="Unsupported Instagram URL format"):
            InstagramParser.validate("https://www.instagram.com/explore/")

    def test_invalid_url_just_domain(self):
        with pytest.raises(ParserError, match="Unsupported Instagram URL format"):
            InstagramParser.validate("https://www.instagram.com/")

    def test_get_content_id_reel(self):
        url = "https://www.instagram.com/reel/DW8PkC0AZvb/"
        assert InstagramParser.get_content_id(url) == "DW8PkC0AZvb"

    def test_get_content_id_post(self):
        url = "https://www.instagram.com/p/CxYzAbCdEf/"
        assert InstagramParser.get_content_id(url) == "CxYzAbCdEf"

    def test_get_content_id_invalid(self):
        url = "https://youtube.com/watch?v=12345"
        assert InstagramParser.get_content_id(url) is None
