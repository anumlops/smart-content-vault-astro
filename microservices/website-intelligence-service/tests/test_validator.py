import pytest

from app.ai.validator import ValidationError, validate_analysis_response


class TestValidateAnalysisResponse:
    def test_valid_response(self):
        data = {
            "summary": "A concise summary of the content.",
            "tags": ["technology", "ai", "python", "machine-learning", "data"],
        }
        result = validate_analysis_response(data)
        assert result["summary"] == data["summary"]
        assert result["tags"] == data["tags"]

    def test_not_a_dict(self):
        with pytest.raises(ValidationError, match="not a JSON object"):
            validate_analysis_response("string")

    def test_missing_summary(self):
        with pytest.raises(ValidationError, match="Missing 'summary'"):
            validate_analysis_response({"tags": []})

    def test_empty_summary(self):
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_analysis_response({"summary": "", "tags": ["a", "b", "c", "d", "e"]})

    def test_summary_too_long(self):
        summary = "word " * 501
        with pytest.raises(ValidationError, match="exceeds 500 words"):
            validate_analysis_response({"summary": summary, "tags": ["a", "b", "c", "d", "e"]})

    def test_missing_tags(self):
        with pytest.raises(ValidationError, match="Missing 'tags'"):
            validate_analysis_response({"summary": "hello"})

    def test_tags_not_array(self):
        with pytest.raises(ValidationError, match="must be an array"):
            validate_analysis_response({"summary": "hello", "tags": "not-array"})

    def test_wrong_number_of_tags(self):
        with pytest.raises(ValidationError, match="exactly 5"):
            validate_analysis_response({"summary": "hello", "tags": ["a", "b", "c"]})

    def test_duplicate_tags(self):
        with pytest.raises(ValidationError, match="duplicates"):
            validate_analysis_response({
                "summary": "hello",
                "tags": ["tag1", "tag1", "tag2", "tag3", "tag4"],
            })

    def test_tag_not_lowercase(self):
        with pytest.raises(ValidationError, match="not lowercase"):
            validate_analysis_response({
                "summary": "hello",
                "tags": ["Tag1", "tag2", "tag3", "tag4", "tag5"],
            })

    def test_empty_tag_string(self):
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_analysis_response({
                "summary": "hello",
                "tags": ["tag1", "", "tag3", "tag4", "tag5"],
            })

    def test_summary_edge_500_words(self):
        summary = "word " * 500
        data = {"summary": summary.strip(), "tags": ["a", "b", "c", "d", "e"]}
        result = validate_analysis_response(data)
        assert len(result["summary"].split()) == 500
