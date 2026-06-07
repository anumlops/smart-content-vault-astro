ANALYSIS_PROMPT_TEMPLATE = """You are a content analysis engine.

Analyze the provided content.

Generate:

1. Summary under 500 words.
2. Exactly 5 relevant tags.

Tag Rules:

- lowercase
- concise
- searchable
- no duplicates

Return ONLY valid JSON.

Required Format:

{{
  "summary": "",
  "tags": []
}}

Content:

{content}"""
