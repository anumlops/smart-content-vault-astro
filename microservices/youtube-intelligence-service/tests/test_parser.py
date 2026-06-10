import pytest

from app.extractor.parser import YouTubeParser, ParserError


class TestYouTubeParser:
    def test_valid_watch_url(self):
        url = "https://www.youtube.com/watch?v=Pdp3p23P-TI"
        result = YouTubeParser.validate(url)
        assert result == url

    def test_valid_watch_url_without_www(self):
        url = "https://youtube.com/watch?v=Pdp3p23P-TI"
        result = YouTubeParser.validate(url)
        assert result == url

    def test_valid_short_url(self):
        url = "https://youtu.be/Pdp3p23P-TI"
        result = YouTubeParser.validate(url)
        assert result == url

    def test_valid_embed_url(self):
        url = "https://www.youtube.com/embed/Pdp3p23P-TI"
        result = YouTubeParser.validate(url)
        assert result == url

    def test_valid_shorts_url(self):
        url = "https://www.youtube.com/shorts/Pdp3p23P-TI"
        result = YouTubeParser.validate(url)
        assert result == url

    def test_valid_url_with_params(self):
        url = "https://www.youtube.com/watch?v=Pdp3p23P-TI&t=30s&list=PLabc123"
        result = YouTubeParser.validate(url)
        assert result == url

    def test_valid_url_without_scheme(self):
        url = "www.youtube.com/watch?v=Pdp3p23P-TI"
        result = YouTubeParser.validate(url)
        assert result.startswith("https://")

    def test_valid_mobile_url(self):
        url = "https://m.youtube.com/watch?v=Pdp3p23P-TI"
        result = YouTubeParser.validate(url)
        assert result == url

    def test_invalid_url_empty(self):
        with pytest.raises(ParserError, match="URL is empty"):
            YouTubeParser.validate("")

    def test_invalid_url_non_youtube(self):
        with pytest.raises(ParserError, match="Not a YouTube URL"):
            YouTubeParser.validate("https://vimeo.com/12345")

    def test_invalid_url_unsupported_format(self):
        with pytest.raises(ParserError, match="Unsupported YouTube URL format"):
            YouTubeParser.validate("https://www.youtube.com/feed/trending")

    def test_invalid_url_just_domain(self):
        with pytest.raises(ParserError, match="Unsupported YouTube URL format"):
            YouTubeParser.validate("https://www.youtube.com/")

    def test_get_video_id_watch(self):
        assert YouTubeParser.get_video_id("https://www.youtube.com/watch?v=Pdp3p23P-TI") == "Pdp3p23P-TI"

    def test_get_video_id_short(self):
        assert YouTubeParser.get_video_id("https://youtu.be/Pdp3p23P-TI") == "Pdp3p23P-TI"

    def test_get_video_id_embed(self):
        assert YouTubeParser.get_video_id("https://www.youtube.com/embed/Pdp3p23P-TI") == "Pdp3p23P-TI"

    def test_get_video_id_shorts(self):
        assert YouTubeParser.get_video_id("https://www.youtube.com/shorts/Pdp3p23P-TI") == "Pdp3p23P-TI"

    def test_get_video_id_with_params(self):
        assert YouTubeParser.get_video_id("https://www.youtube.com/watch?v=Pdp3p23P-TI&t=30s") == "Pdp3p23P-TI"

    def test_get_video_id_invalid(self):
        assert YouTubeParser.get_video_id("https://vimeo.com/12345") is None

    def test_to_watch_url_from_short(self):
        result = YouTubeParser.to_watch_url("https://youtu.be/Pdp3p23P-TI")
        assert result == "https://www.youtube.com/watch?v=Pdp3p23P-TI"

    def test_to_watch_url_from_embed(self):
        result = YouTubeParser.to_watch_url("https://www.youtube.com/embed/Pdp3p23P-TI")
        assert result == "https://www.youtube.com/watch?v=Pdp3p23P-TI"

    def test_to_watch_url_from_shorts(self):
        result = YouTubeParser.to_watch_url("https://www.youtube.com/shorts/Pdp3p23P-TI")
        assert result == "https://www.youtube.com/watch?v=Pdp3p23P-TI"

    def test_to_watch_url_invalid(self):
        with pytest.raises(ParserError, match="Cannot extract video ID"):
            YouTubeParser.to_watch_url("https://www.youtube.com/")
