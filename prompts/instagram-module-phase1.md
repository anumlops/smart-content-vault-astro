# Instagram Module — Phase 1: OG Metadata Extraction

Build a complete Instagram extraction module following the same architecture as the existing `website-intelligence-service` and `WebsiteProcessor`. Phase 1 handles Open Graph metadata extraction (title, description, thumbnail), categorization, and tag generation — the "save-time" pipeline.

---

## Project Context

This is **Smart Content Vault** — an Astro v6 SSR app on Vercel that saves and organizes content from any URL.

### Stack
- **Astro v6 SSR** (`output: 'server'`) deployed on Vercel with `@astrojs/vercel`
- **Tailwind CSS v4** via `@tailwindcss/vite` (no PostCSS config)
- **Prisma v5 + PostgreSQL (Neon)** for persistence
- **Session auth**: httpOnly cookies, SHA-256 hashing, custom (no `better-auth`)
- Node >=22.12.0 (`.nvmrc` says 20, `package.json` engines wins)

### Two-Pass Content Pipeline
1. **Save-time** (`lib/processing.ts`): fetch HTML → regex-extract OG metadata → keyword categorize (20 cats) + generate tags → write to DB
2. **Post-save enrichment** (`lib/enrich.ts` → `modules/website/`): linkedom + Readability crawler → OpenRouter LLM (GPT-4o-mini → DeepSeek → Kimi → keyword fallback) → store `aiSummary`, `aiTags`, `aiCategory`, `keyTakeaways`

### Two Category Systems
| System | File | Count | Used where? | DB field |
|---|---|---|---|---|
| Save-time | `lib/categorizer.ts` | 20 cats | Initial save | `category` (string) |
| LLM enrichment | `modules/shared/constants.ts` | 10 cats | Post-save enrichment | `aiCategory` (string) |

**20 categories** (save-time): DevOps, MLOps, Cloud, Data Science, Machine Learning, AI, Programming, Finance, Business, Productivity, Career, Health, Fitness, Relationships, Education, Entertainment, Gaming, Travel, News, Other

**10 categories** (enrichment): Technology, Business, Finance, Productivity, Education, Career, Marketing, Health, Entertainment, Lifestyle

### Content Processor Architecture
`src/modules/` implements the `ContentProcessor` interface:

```typescript
interface ContentProcessor {
  sourceType: string
  canHandle(url: string): boolean
  extract(url: string): Promise<ContentSource>
  analyze(source: ContentSource): Promise<ProcessingResult>
}
```

Modules exist as subdirectories under `src/modules/`:
- `website/` — **fully implemented** (WebsiteProcessor + WebsiteCrawler + WebsiteAnalyzer)
- `instagram/` — **placeholder only** (throws "not yet implemented")
- `youtube/` — **placeholder only**

### Microservices (independent, not connected to main app)
The project has microservices under `microservices/` as standalone services:
- `crawl4ai/` — Python (Chromium crawler via Docker)
- `content-extractor/` — Python
- `website-intelligence-service/` — Python FastAPI (deployed on Vercel as Python serverless)

Each follows this pattern: Python/FastAPI with `requirements.txt`, `app/main.py`, `app/api/routes.py`, schemas, extractor/service layers, and tests.

The main Astro app does NOT call these microservices — they are standalone. Instead, the Astro app has its own extraction logic inline. The Instagram module's microservice follows this same independent pattern.

---

## Instagram-Specific Challenges

1. **Bot detection**: Instagram's CDN strips OG metadata from non-browser HTTP clients. You MUST send these headers:
   ```
   Sec-Fetch-Dest: document
   Sec-Fetch-Mode: navigate
   Sec-Fetch-Site: none
   Sec-Fetch-User: ?1
   Upgrade-Insecure-Requests: 1
   Referer: https://www.instagram.com/
   ```
   Without them, Instagram returns ~780KB stripped HTML with no OG tags. With them, it returns ~1.46MB full HTML.

2. **Timeout**: Instagram is slow (1-3s warm, up to 10s cold). Use a **15s timeout** everywhere (server fetch and client fetch).

3. **HTML size**: The returned HTML is ~1.4MB. Avoid regex with global flags and backtracking — use `indexOf`/`substring` or `innerHTML`-safe HTML parsing (BeautifulSoup `html.parser` in Python, `linkedom` or regex substring in JS).

4. **`<title>` tag**: Always just "Instagram" — never use it as the display title. Use `og:title` instead.

5. **`og:title` content**: Contains the full Instagram caption with HTML entities (`&quot;`, `&#x2019;`) and line breaks — decode entities before displaying.

---

## Implementation Plan

You need to build THREE things:

### 1. Microservice: `microservices/instagram-intelligence-service/`
A standalone Python/FastAPI service following `website-intelligence-service` architecture. Does OG metadata extraction only (no LLM, no categorization — that's the Astro app's job).

**File structure:**
```
microservices/instagram-intelligence-service/
├── api/
│   └── index.py              # Vercel serverless entry
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app with CORS, /health, router
│   ├── api/
│   │   ├── __init__.py        # Exports router
│   │   └── routes.py          # POST /api/v1/extract
│   ├── extractor/
│   │   ├── __init__.py        # Exports InstagramExtractor
│   │   ├── fetcher.py         # HTTP fetch with browser headers + 15s timeout
│   │   ├── metadata.py        # BeautifulSoup OG extraction
│   │   ├── parser.py          # URL validation /reel/ /p/ + content_id extraction
│   │   └── service.py         # Orchestration: validate → fetch → parse → InstagramData
│   └── schemas/
│       ├── __init__.py
│       └── instagram.py       # Pydantic models: ExtractRequest, InstagramData, ExtractResponse
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_fetcher.py
│   ├── test_metadata.py
│   ├── test_parser.py
│   └── test_service.py
├── .env.example
├── .gitignore
├── Dockerfile                 # python:3.12-slim, uvicorn on 8000
├── README.md
├── requirements.txt
└── vercel.json
```

**Key implementation details:**
- `parser.py`: regex `/(reel|p)/[A-Za-z0-9_-]+` — validate URL has scheme, host is `instagram.com`, path is `/reel/XXX` or `/p/XXX`; `get_content_id()` extracts shortcode
- `fetcher.py`: `requests.get(url, headers={...all 7 browser headers...}, timeout=15)` — return `FetchResult(html, url, status_code, headers_dict)`
- `metadata.py`: BeautifulSoup `html.parser` — extract `meta[property="og:title"]`, `og:description`, `og:image`, `og:url`, `link[rel="canonical"]`, `meta[name="description"]`; decode HTML entities; handle missing gracefully (empty string)
- `service.py`: `InstagramExtractor.extract(url)` → validate → fetch → extract_all → return `InstagramData`
- `schemas/instagram.py`:
  ```python
  class ExtractRequest(BaseModel): url: str
  class InstagramData(BaseModel): platform="instagram", url, canonical_url="", title="", description="", thumbnail="", extracted_at (ISO datetime)
  class ExtractResponse(BaseModel): success: bool, data: InstagramData | None, error: str | None
  ```
- `routes.py`: `POST /api/v1/extract` — parse body → call extractor → return JSON; handle errors with 400/500
- `main.py`: FastAPI + CORS `allow_origins=["*"]` + include router with `/api/v1` prefix + `/health` endpoint
- `api/index.py`: sys.path insert parent → `from app.main import app` (same pattern as website-intelligence-service)
- `vercel.json`: same structure as website-intelligence-service (`@vercel/python` build)
- `Dockerfile`: `FROM python:3.12-slim`, pip install, `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`
- Tests: pytest, mock `requests.get`, test valid reel/post URLs, invalid URLs, empty URLs, timeout, connection error, edge cases in metadata parsing (missing tags, empty HTML, malformed HTML)

### 2. Astro ContentProcessor: `src/modules/instagram/`

Replace the placeholder at `src/modules/instagram/placeholder.ts` with a full implementation.

**Files to create:**
```
src/modules/instagram/
├── schemas.ts        # InstagramContent, InstagramAnalysis interfaces
├── crawler.ts        # InstagramCrawler — fetch HTML + extract OG metadata
├── analyzer.ts       # InstagramAnalyzer — keyword categorize + tag generate
└── service.ts        # InstagramProcessor — implements ContentProcessor
```

- `schemas.ts`:
  ```typescript
  export interface InstagramContent {
    url: string
    domain: string
    title: string | null
    html: string | null
    text: string | null
    description: string | null
    thumbnail: string | null
    metadata: Record<string, any>
    error?: string | null
  }

  export interface InstagramAnalysis {
    title: string | null
    description?: string | null
    thumbnail?: string | null
    summary: string | null
    category: string | null
    tags: string[]
    keyTakeaways: string[]
    error?: string | null
    processedAt: string
  }
  ```

- `crawler.ts`: Mirror `WebsiteCrawler` but for Instagram
  - `canHandle(url)` — check `instagram.com` + `/reel/` or `/p/` path
  - `extract(url)` — fetch with browser headers (all 7 sec-fetch-* headers + Referer), 15s AbortController timeout; parse HTML with `indexOf`/`substring` to extract `og:title`, `og:description`, `og:image`, `og:url`, `canonical url`; decode HTML entities (`&quot;` → `"`, `&#x2019;` → `'`, etc.); return `InstagramContent`
  - Return error gracefully (not throw) for failed fetches, timeouts, empty HTML

- `analyzer.ts`: Keyword-based analysis (Phase 1, no LLM)
  - `detectCategory(content)` — use the 20-category `lib/categorizer.ts` system OR the 10-category `modules/shared/constants.ts` matching `WebsiteAnalyzer.detectCategory()`
  - `generateTags(title, text, domain)` — extract significant words, multiphrase patterns; return max 5-10 tags
  - Phase 1 uses keyword-only; Phase 4 will add LLM enrichment

- `service.ts`: Follow `WebsiteProcessor` pattern exactly
  ```typescript
  export class InstagramProcessor implements ContentProcessor {
    sourceType = 'instagram'
    private crawler = new InstagramCrawler()
    private analyzer = new InstagramAnalyzer()

    canHandle(url: string): boolean { ... }
    async extract(url: string): Promise<ContentSource> { ... }
    async analyze(source: ContentSource): Promise<ProcessingResult> { ... }
    async processUrl(url: string): Promise<ProcessingResult> { ... }
  }
  ```

### 3. Astro Integration Points

**a. API endpoint: `src/pages/api/extract/instagram.ts`** (use the existing one already written here)
- `POST` handler, accepts `{ url }` JSON body
- Validates the URL is Instagram
- Calls `fetch()` with the 7 browser headers + Referer + 15s timeout
- Extracts OG metadata using `indexOf`/`substring` (not regex)
- Calls `categorize()` from `lib/categorizer.ts` (20-category system)
- Calls `generateTags()` from `lib/tag-generator.ts`
- Returns JSON: `{ success, data: { platform, url, canonical_url, title, description, thumbnail, extracted_at, category, tags } }`
- Returns 400 for missing URL or non-Instagram URL, 500 for extraction failures

**b. Dev test page: `src/pages/dev/instagram.astro`** (use the existing one already written here)
- Form with URL input and "Extract" button
- On submit: POST to `/api/extract/instagram`
- Show results: metadata card (thumbnail, title, description), category badge, tags list, collapsible raw JSON response
- Loading state, error handling

**c. Add link from `/dev` to `/dev/instagram`** (already done)
- Add a tab/button at top of `/dev.astro` pointing to `/dev/instagram`
- Add a similar "back to dev" link on `/dev/instagram`

**d. Preview card on save form: `src/components/content/ContentForm.astro`** (already done)
- On URL paste, detect `instagram.com`, debounce 800ms, POST to `/api/extract/instagram`
- Show compact preview card with: thumbnail (left), title + description (middle), category badge + first 3 tags (bottom)
- Handle loading state ("Fetching preview..."), missing data, errors (hide preview)

**e. Wire `InstagramProcessor` into the enrichment pipeline**
- In `src/lib/enrich.ts`, import `InstagramProcessor` and use it when URL matches Instagram (alongside `WebsiteProcessor` for non-Instagram URLs)
- In `src/pages/api/enrich.ts`, same pattern — detect content type and dispatch to the right processor
- Use `canHandle()` to decide which processor to use:
  ```typescript
  const processors = [new InstagramProcessor(), new WebsiteProcessor()]
  const processor = processors.find(p => p.canHandle(url))
  if (!processor) throw new Error('No processor found for URL')
  ```

---

## Key Gotchas to Remember

1. **Instagram requires browser fingerprint headers** (`Sec-Fetch-*`, `Referer`, `Upgrade-Insecure-Requests`) — without them OG tags are empty. Test this first before debugging anything else.
2. **15s timeout on ALL fetches** — both server-side and client-side. Instagram is slow.
3. **Never use `<title>`** — it always returns "Instagram"
4. **Decode HTML entities** in `og:title` (captions contain `&quot;`, `&#x2019;`, line breaks)
5. **Use `indexOf`/`substring` not regex** for HTML parsing — Instagram's 1.4MB HTML breaks regex backtracking
6. **The `categorize()` function from `lib/categorizer.ts`** uses 20 categories; **`CATEGORY_KEYWORDS` from `modules/shared/constants.ts`** uses 10 categories. Both are valid — use the right one for the right pipeline stage (save-time vs enrichment).
7. The microservice is **independent** — it does NOT call the Astro app's `categorize()`/`generateTags()`. It only returns raw OG metadata. The Astro app adds categorization/tagging at its endpoints.

---

## Files Already Created (you can reference)

### Microservice
- `microservices/instagram-intelligence-service/app/__init__.py`
- `microservices/instagram-intelligence-service/app/main.py`
- `microservices/instagram-intelligence-service/app/api/__init__.py`
- `microservices/instagram-intelligence-service/app/api/routes.py`
- `microservices/instagram-intelligence-service/app/extractor/__init__.py`
- `microservices/instagram-intelligence-service/app/extractor/fetcher.py`
- `microservices/instagram-intelligence-service/app/extractor/metadata.py`
- `microservices/instagram-intelligence-service/app/extractor/parser.py`
- `microservices/instagram-intelligence-service/app/extractor/service.py`
- `microservices/instagram-intelligence-service/app/schemas/__init__.py`
- `microservices/instagram-intelligence-service/app/schemas/instagram.py`
- `microservices/instagram-intelligence-service/tests/__init__.py`
- `microservices/instagram-intelligence-service/tests/test_api.py`
- `microservices/instagram-intelligence-service/tests/test_fetcher.py`
- `microservices/instagram-intelligence-service/tests/test_metadata.py`
- `microservices/instagram-intelligence-service/tests/test_parser.py`
- `microservices/instagram-intelligence-service/tests/test_service.py`
- `microservices/instagram-intelligence-service/.env.example`
- `microservices/instagram-intelligence-service/.gitignore`
- `microservices/instagram-intelligence-service/Dockerfile`
- `microservices/instagram-intelligence-service/README.md`
- `microservices/instagram-intelligence-service/requirements.txt`
- `microservices/instagram-intelligence-service/api/index.py`
- `microservices/instagram-intelligence-service/vercel.json`

### Astro Module
- `src/modules/instagram/schemas.ts`
- `src/modules/instagram/crawler.ts`
- `src/modules/instagram/analyzer.ts`
- `src/modules/instagram/service.ts`

### Astro Integration
- `src/pages/api/extract/instagram.ts`
- `src/pages/dev/instagram.astro`
- `src/pages/dev.astro` (modified — add link to /dev/instagram)
- `src/components/content/ContentForm.astro` (modified — Instagram preview card)
- `src/lib/enrich.ts` (modified — dispatch to InstagramProcessor)
- `src/pages/api/enrich.ts` (modified — dispatch to InstagramProcessor)

---

## Verification

After building, verify by:
1. Start the microservice: `cd microservices/instagram-intelligence-service && pip install -r requirements.txt && uvicorn app.main:app --port 8000`
2. curl `http://localhost:8000/health` → `{"status":"ok"}`
3. curl `POST http://localhost:8000/api/v1/extract` with `{"url":"https://www.instagram.com/reel/XXXXX/"}` → returns OG metadata
4. Start Astro: `npm run dev`
5. Visit `/dev/instagram` — paste a Reel URL → see metadata, category, tags
6. Visit `/content/new` — paste an Instagram URL → see preview card after 800ms
7. Go to `/dev` — see the Instagram button linking to `/dev/instagram`

---

## Phase Roadmap (for README)

**Phase 1 (current)**: OG metadata extraction + categorization + tagging
**Phase 2**: Download Reel video → extract audio → Whisper transcription → store transcript
**Phase 3**: Download video frames → OCR → multimodal content extraction
**Phase 4**: Caption + transcript + OCR → LLM enrichment (summary, aiTags, aiCategory, keyTakeaways)
