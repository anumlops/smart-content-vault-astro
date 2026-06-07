from readability import Document as ReadabilityDoc


class ReadabilityExtractor:
    def extract(self, html: str, url: str | None = None) -> str:
        if not html or not html.strip():
            return ""
        doc = ReadabilityDoc(html, url=url or "")
        summary = doc.summary()
        if not summary:
            return ""
        return str(summary)
