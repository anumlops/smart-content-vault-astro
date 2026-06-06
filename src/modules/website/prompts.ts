export const SYSTEM_PROMPT = `You are a precise content analyst. Analyze the provided article and return a structured JSON response.

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

Return valid JSON only, no markdown, no code fences.`

export function buildUserPrompt(
  title: string | null,
  domain: string,
  url: string,
  content: string
): string {
  return `Analyze this content extracted from a website.

Title: ${title || 'Untitled'}
Domain: ${domain}
URL: ${url}

Content:
${content.slice(0, 8000)}

Return a JSON object with exactly these fields:
- title: string (refined, clean title)
- summary: string (2-3 sentence summary)
- category: string (one from the allowed list)
- tags: string[] (5-10 concise tags)
- key_takeaways: string[] (2-5 key points)

JSON:`
}
