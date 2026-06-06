# Website Intelligence Module

Extracts and analyzes content from any website URL using Trafilatura + LLM.

## Architecture

```
URL → WebsiteCrawler (Trafilatura) → WebsiteAnalyzer (LLM) → ProcessingResult
```

## Files

| File | Purpose |
|------|---------|
| `crawler.py` | Extracts clean article content using Trafilatura |
| `analyzer.py` | Sends content to LLM for summary, category, tags, takeaways |
| `prompts.py` | Centralized LLM prompt templates |
| `schemas.py` | Website-specific data classes |
| `service.py` | Main `WebsiteProcessor` implementing the `ContentProcessor` interface |

## Usage

```python
from src.modules.website import WebsiteProcessor

processor = WebsiteProcessor()
result = await processor.process_url("https://example.com/article")
print(result.summary)
print(result.category)
print(result.tags)
```

## Adding a New Content Source

1. Create folder `src/modules/<source>/`
2. Implement `ContentProcessor` protocol (see `src/modules/shared/types.py`)
3. Create `__init__.py` exporting your processor
4. Register in the unified ingestion system

## Dependencies

- `trafilatura` — content extraction
- `httpx` — LLM API calls
