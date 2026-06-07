import pytest
from pydantic import ValidationError

from schemas.document import ExtractedDocument, Metadata


class TestExtractedDocument:
    def test_default_values(self):
        doc = ExtractedDocument(url="https://example.com", domain="example.com", content="Hello")
        assert doc.source_type == "website"
        assert doc.word_count == 0
        assert doc.metadata.og_title == ""

    def test_word_count_calculated(self):
        doc = ExtractedDocument(
            url="https://example.com",
            domain="example.com",
            content="one two three four five",
            word_count=5,
        )
        assert doc.word_count == 5

    def test_requires_url_domain_content(self):
        with pytest.raises(ValidationError):
            ExtractedDocument()
