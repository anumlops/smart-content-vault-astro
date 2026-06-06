# YouTube Module — Placeholder

**Status:** Not yet implemented.

## Future Implementation

This module will process YouTube videos:

1. Extract video metadata (title, description, channel, duration)
2. Download captions/transcripts via yt-dlp
3. Analyze transcript with LLM for summary, category, tags
4. Store alongside existing content

## Required Dependencies (future)

- `yt-dlp` — video metadata and transcript extraction
- `yt-transcript-api` — YouTube transcript retrieval

## Interface

Implements `ContentProcessor` protocol from `src/modules/shared/types.py`:

```python
class YouTubeProcessor(ContentProcessor):
    source_type = "youtube"
    def can_handle(self, url) -> bool
    async def extract(self, url) -> ContentSource
    async def analyze(self, content) -> ProcessingResult
```

## Registration

Once implemented, register in the unified ingestion system alongside WebsiteProcessor.
