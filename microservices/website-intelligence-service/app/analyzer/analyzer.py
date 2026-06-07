import re
from collections import Counter

CATEGORIES = [
    "Technology", "Business", "Finance", "Productivity",
    "Education", "Career", "Marketing", "Health",
    "Entertainment", "Lifestyle",
]

STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "can", "could", "may", "might", "shall", "should", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very", "just",
    "because", "also", "if", "then", "else", "this", "that", "these", "those",
    "it", "its", "you", "your", "we", "our", "they", "them", "their", "what",
    "which", "who", "whom", "whose", "i", "me", "my", "he", "him", "his",
    "she", "her", "hers",
}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Technology": [
        "software", "hardware", "api", "database", "algorithm", "programming",
        "code", "python", "javascript", "web", "app", "cloud", "server",
        "data", "model", "ai", "machine learning", "deep learning", "neural",
        "blockchain", "cybersecurity", "devops", "docker", "kubernetes",
        "framework", "library", "frontend", "backend", "full stack", "api",
        "rest", "graphql", "microservice", "container", "deployment",
        "algorithm", "compute", "storage", "network", "encryption",
    ],
    "Business": [
        "business", "company", "startup", "entrepreneur", "management",
        "strategy", "revenue", "growth", "scale", "market", "customer",
        "product", "service", "b2b", "b2c", "saas", "leadership",
        "innovation", "disruption", "pivot", "acquisition", "merger",
        "enterprise", "stakeholder", "partnership", "supply chain",
    ],
    "Finance": [
        "finance", "investment", "stock", "bond", "crypto", "bitcoin",
        "trading", "portfolio", "asset", "equity", "debt", "interest",
        "inflation", "dividend", "mutual fund", "etf", "retirement",
        "banking", "loan", "mortgage", "credit", "tax", "insurance",
        "wealth", "financial planning", "budget", "saving",
    ],
    "Productivity": [
        "productivity", "time management", "workflow", "automation",
        "efficiency", "focus", "task", "todo", "calendar", "schedule",
        "habit", "routine", "gtd", "getting things done", "pomodoro",
        "deep work", "organization", "prioritize", "deadline",
        "tool", "system", "process", "optimize", "streamline",
    ],
    "Education": [
        "education", "learning", "course", "class", "tutorial", "lesson",
        "study", "student", "teacher", "professor", "school", "university",
        "degree", "certification", "skill", "knowledge", "training",
        "workshop", "lecture", "curriculum", "syllabus", "homework",
        "exam", "grade", "academic", "research", "science",
    ],
    "Career": [
        "career", "job", "resume", "interview", "salary", "promotion",
        "hire", "recruit", "layoff", "remote", "freelance", "contract",
        "full-time", "part-time", "internship", "mentor", "networking",
        "linkedin", "portfolio", "skill development", "career change",
        "work-life balance", "job search", "offer", "negotiation",
    ],
    "Marketing": [
        "marketing", "seo", "social media", "content", "brand", "advertising",
        "campaign", "conversion", "lead", "funnel", "analytics", "growth",
        "engagement", "audience", "influencer", "email marketing",
        "landing page", "cta", "ppc", "google ads", "facebook ads",
        "copywriting", "storytelling", "positioning", "market research",
    ],
    "Health": [
        "health", "fitness", "exercise", "workout", "nutrition", "diet",
        "mental health", "meditation", "yoga", "sleep", "stress",
        "wellness", "doctor", "medical", "disease", "symptom",
        "treatment", "therapy", "medicine", "vitamin", "supplement",
        "weight loss", "muscle", "cardio", "strength", "immunity",
    ],
    "Entertainment": [
        "movie", "film", "music", "game", "gaming", "tv", "show",
        "streaming", "netflix", "youtube", "tiktok", "instagram",
        "celebrity", "actor", "singer", "concert", "tour", "album",
        "review", "trailer", "anime", "comic", "book", "novel",
        "fiction", "fantasy", "sci-fi", "comedy", "drama",
    ],
    "Lifestyle": [
        "lifestyle", "travel", "food", "recipe", "fashion", "beauty",
        "home", "decor", "garden", "pet", "relationship", "family",
        "parenting", "wedding", "gift", "minimalism", "sustainable",
        "vegan", "organic", "hobby", "diy", "craft", "photography",
    ],
}


def _tokenize(text: str) -> list[str]:
    text = text.lower()
    tokens = re.findall(r"[a-z0-9+#]+(?:[-'][a-z0-9]+)*", text)
    return [t for t in tokens if t not in STOP_WORDS and len(t) > 2]


def _multi_word_keywords(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    count = 0
    for kw in keywords:
        if " " in kw:
            count += text_lower.count(kw)
    return count


def _classify_category(text: str) -> str:
    if not text:
        return "Technology"
    tokens = _tokenize(text)
    scores: dict[str, float] = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = 0.0
        single_words = [kw for kw in keywords if " " not in kw]
        multi_words = [kw for kw in keywords if " " in kw]
        if single_words:
            token_counts = Counter(tokens)
            for word in single_words:
                score += token_counts.get(word, 0)
        score += _multi_word_keywords(text, multi_words) * 2
        scores[cat] = score
    return max(scores, key=scores.get)


def _generate_summary(text: str, max_words: int = 200, min_words: int = 100) -> str:
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    summary_parts = []
    word_count = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        sentence_words = len(sentence.split())
        if word_count + sentence_words > max_words:
            break
        summary_parts.append(sentence)
        word_count += sentence_words
        if word_count >= min_words:
            break
    summary = " ".join(summary_parts)
    if word_count < min_words and summary_parts:
        summary = " ".join(summary_parts)
    if not summary:
        summary = text[:500]
    return summary.strip()


def _extract_title(text: str, provided_title: str | None = None) -> str:
    if provided_title:
        return provided_title
    lines = text.strip().split("\n")
    for line in lines:
        line = line.strip().strip("#")
        line = line.strip()
        if line and len(line) > 10:
            return line
    words = text.split()
    if words:
        return " ".join(words[:10]) + ("..." if len(words) > 10 else "")
    return "Untitled"


def _extract_tags(text: str) -> list[str]:
    if not text:
        return []
    tokens = _tokenize(text)
    if not tokens:
        return []
    counter = Counter(tokens)
    common = counter.most_common(30)
    filtered = [word for word, count in common if count > 1 and len(word) > 2]
    return filtered[:10]


def _extract_key_takeaways(text: str) -> list[str]:
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    scored = []
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 40:
            continue
        lower = s.lower()
        score = 0
        indicators = [
            "key", "important", "significant", "critical", "essential",
            "crucial", "notable", "fundamental", "vital", "must",
            "always", "never", "best", "worst", "top", "should",
            "need to", "remember", "conclusion", "summary", "therefore",
            "in short", "overall", "primary", "main", "core",
        ]
        for ind in indicators:
            if ind in lower:
                score += 1
        if score > 0:
            scored.append((score, s))
    scored.sort(key=lambda x: -x[0])
    takeaways = [s for _, s in scored[:5]]
    if not takeaways:
        long_sentences = [s for s in sentences if len(s.split()) > 15]
        takeaways = long_sentences[:3]
    return takeaways


class ContentAnalyzer:
    def analyze(self, content: str, title: str | None = None) -> dict:
        import app.analyzer.llm_backend as llm

        if llm.is_available():
            llm_result = llm.analyze(content, title)
            if llm_result is not None:
                return llm_result

        return {
            "title": _extract_title(content, title),
            "summary": _generate_summary(content),
            "category": _classify_category(content),
            "tags": _extract_tags(content),
            "key_takeaways": _extract_key_takeaways(content),
        }
