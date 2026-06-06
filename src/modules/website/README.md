# Website Intelligence Module

Extracts and analyzes content from any website URL.

## Architecture

```
URL → WebsiteCrawler (Readability) → WebsiteAnalyzer (keyword/LLM) → ProcessingResult
```

## How It Works

1. **Crawler** fetches the URL and extracts clean article content using Mozilla's Readability library
2. **Analyzer** attempts LLM analysis (if `LLM_API_KEY` is set), otherwise falls back to keyword-based analysis
3. **Service** orchestrates the full pipeline

## Zero API Key Required

The module works **without any API key**. If `LLM_API_KEY` is not set, it uses built-in keyword analysis:
- Category detection via keyword matching across title, domain, and content
- Tag generation from significant words
- Summary from first sentences
- Key takeaways from significant sentences

## Adding YouTube / Instagram

1. Create folder `src/modules/<source>/`
2. Implement `ContentProcessor` from `src/modules/shared/types.ts`
3. Follow the same `crawler → analyzer → service` pattern
