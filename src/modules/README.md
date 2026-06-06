# Content Processing Modules

Modular content processing architecture for Smart Content Vault.
Each content source has its own module following the same interface pattern.

## Architecture

```
src/modules/
├── shared/          # Shared types, constants, utilities
│   ├── types.py     # ContentProcessor protocol, ProcessingResult, dataclasses
│   ├── constants.py # Category taxonomy, limits
│   └── utils.py     # URL validation, domain extraction, text cleaning
├── website/         # ✅ Implemented — Trafilatura + LLM analysis
├── youtube/         # 📋 Placeholder — ready for implementation
└── instagram/       # 📋 Placeholder — ready for implementation
```

## Adding a New Content Source

### 1. Create module folder

```
src/modules/<source>/
├── __init__.py
├── crawler.py       # Extract raw content
├── analyzer.py      # LLM analysis
├── prompts.py       # LLM prompts
├── schemas.py       # Data classes
├── service.py       # Main processor (implements ContentProcessor)
└── README.md
```

### 2. Implement the ContentProcessor protocol

```python
from src.modules.shared.types import ContentProcessor

class MyProcessor(ContentProcessor):
    source_type = "mysource"

    def can_handle(self, url: str) -> bool:
        return "mysource.com" in url

    async def extract(self, url: str) -> ContentSource:
        # Download and extract content
        pass

    async def analyze(self, content: ContentSource) -> ProcessingResult:
        # Analyze with LLM or rules
        pass
```

### 3. Register in the ingestion pipeline

Add to the unified processor registry so the system auto-detects which
processor to use based on the URL.

## Processor Interface

All processors implement `ContentProcessor` from `src/modules/shared/types.py`:

- `can_handle(url)` → bool — checks if this processor supports the URL
- `extract(url)` → ContentSource — fetches and extracts raw content
- `analyze(content)` → ProcessingResult — analyzes and returns structured data

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_API_KEY` | — | API key for LLM provider |
| `LLM_API_URL` | OpenAI endpoint | LLM API endpoint |
| `LLM_MODEL` | gpt-4o-mini | Model name |
| `LLM_TIMEOUT` | 30 | Request timeout in seconds |

Without an LLM key, the system falls back to keyword-based analysis.
