# Content Extractor

Extract clean, structured, AI-ready content from any website using Mozilla Readability (Firefox Reader Mode engine).

## Pipeline

```
URL
 ↓
fetcher.py ──── requests + BS4 ──→ raw HTML
 ↓
metadata.py ── OG / meta / JSON-LD ──→ metadata dict
 ↓
readability.py ── readability-lxml (Mozilla port) ──→ cleaned HTML
 ↓
cleaner.py ──── normalize, strip, preserve structure ──→ clean text
 ↓
service.py ──── orchestrator → {AI-ready JSON} → data/extracted/<domain>_<ts>.json
```

## Quick Start

```bash
cd content-extractor
pip install -r requirements.txt
python -c "
from extractor import ContentExtractorService
svc = ContentExtractorService()
doc = svc.extract('https://example.com/article')
print(doc.model_dump_json(indent=2))
"
```

## Output Format

Saved to `data/extracted/<domain>_<timestamp>.json`

```json
{
  "source_type": "website",
  "url": "https://example.com/article",
  "canonical_url": "https://example.com/article",
  "domain": "example.com",
  "title": "Article Title",
  "description": "Article description",
  "author": "Author Name",
  "published_date": "2024-01-15T10:00:00Z",
  "language": "en",
  "content": "Clean article text...\n\nWith paragraph separation.\n\n# Heading preserved",
  "word_count": 1240,
  "extracted_at": "2024-01-15T12:00:00Z",
  "metadata": {
    "og_title": "OG Title",
    "og_description": "OG Description",
    "og_image": "https://example.com/image.jpg"
  }
}
```

## AI Consumption

The `content` field is already clean and normalized. Pass it directly to any AI pipeline:

```python
from analyzer import ContentAnalyzer
from extractor import ContentExtractorService

svc = ContentExtractorService()
doc = svc.extract("https://example.com/article")

ai = ContentAnalyzer()
result = ai.analyze(content=doc.content, title=doc.title)
```

No preprocessing required. No HTML, navigation, ads, or styling.

## Project Structure

```
content-extractor/
├── extractor/
│   ├── __init__.py
│   ├── fetcher.py       # HTTP fetch via requests
│   ├── metadata.py      # OG, meta tags, JSON-LD
│   ├── readability.py   # Mozilla Readability wrapper
│   ├── cleaner.py       # Content normalization
│   └── service.py       # Pipeline orchestrator
├── schemas/
│   ├── __init__.py
│   └── document.py      # Pydantic models
├── data/
│   └── extracted/       # Saved JSON outputs
├── tests/
├── requirements.txt
└── README.md
```

## Testing

```bash
pytest tests/ -v
```
