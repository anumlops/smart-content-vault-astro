# Instagram Module — Placeholder

**Status:** Not yet implemented.

## Future Implementation

This module will process Instagram posts and reels:

1. Extract post metadata (caption, author, media type)
2. Download image/video for analysis
3. Analyze caption with LLM for summary, category, tags
4. Store alongside existing content

## Required Dependencies (future)

- `instagrapi` — Instagram API client
- `Pillow` — image analysis if needed

## Interface

Implements `ContentProcessor` protocol from `src/modules/shared/types.py`:

```python
class InstagramProcessor(ContentProcessor):
    source_type = "instagram"
    def can_handle(self, url) -> bool
    async def extract(self, url) -> ContentSource
    async def analyze(self, content) -> ProcessingResult
```

## Registration

Once implemented, register in the unified ingestion system alongside WebsiteProcessor.
