import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    pass


def validate_analysis_response(data: dict) -> dict:
    if not isinstance(data, dict):
        raise ValidationError("Response is not a JSON object")

    if "summary" not in data:
        raise ValidationError("Missing 'summary' field")
    summary = data["summary"]
    if not isinstance(summary, str) or not summary.strip():
        raise ValidationError("'summary' must be a non-empty string")
    word_count = len(summary.split())
    if word_count > 500:
        raise ValidationError(f"'summary' exceeds 500 words ({word_count})")

    if "tags" not in data:
        raise ValidationError("Missing 'tags' field")
    tags = data["tags"]
    if not isinstance(tags, list):
        raise ValidationError("'tags' must be an array")

    if len(tags) != 5:
        raise ValidationError(f"'tags' must have exactly 5 items, got {len(tags)}")

    if len(set(tags)) != len(tags):
        raise ValidationError("'tags' contain duplicates")

    for i, tag in enumerate(tags):
        if not isinstance(tag, str) or not tag.strip():
            raise ValidationError(f"Tag at index {i} is not a non-empty string")
        if tag != tag.lower():
            raise ValidationError(f"Tag '{tag}' is not lowercase")

    return {"summary": summary.strip(), "tags": tags}
