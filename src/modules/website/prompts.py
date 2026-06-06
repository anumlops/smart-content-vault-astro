"""
LLM prompts for website content analysis.
All prompts are centralized here for easy modification.
"""

WEBSITE_ANALYSIS_SYSTEM_PROMPT = """You are a precise content analyst. Analyze the provided article and return a structured JSON response.

Rules:
1. Choose exactly ONE category from the allowed list
2. Generate 5-10 highly relevant, searchable tags
3. Tags must be concise, lowercase, single words or short phrases
4. Key takeaways should be 2-5 concise bullet points (each 1-2 sentences)
5. Summary should be 2-3 sentences capturing the core message

Allowed categories:
- Technology
- Business
- Finance
- Productivity
- Education
- Career
- Marketing
- Health
- Entertainment
- Lifestyle

Return valid JSON only, no markdown, no code fences."""

WEBSITE_ANALYSIS_USER_PROMPT_TEMPLATE = """Analyze this content extracted from a website.

Title: {title}
Domain: {domain}
URL: {url}

Content:
{content}

Return a JSON object with exactly these fields:
- title: string (refined, clean title)
- summary: string (2-3 sentence summary)
- category: string (one from the allowed list)
- tags: string[] (5-10 concise tags)
- key_takeaways: string[] (2-5 key points)

JSON:"""


def build_analysis_prompt(
    title: str | None,
    domain: str,
    url: str,
    content: str,
) -> tuple[str, str]:
    user_prompt = WEBSITE_ANALYSIS_USER_PROMPT_TEMPLATE.format(
        title=title or "Untitled",
        domain=domain,
        url=url,
        content=content[:8000],
    )
    return WEBSITE_ANALYSIS_SYSTEM_PROMPT, user_prompt
