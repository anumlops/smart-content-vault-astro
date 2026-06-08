# Instagram Intelligence Service

Extract Open Graph metadata from Instagram Reels and Posts.

## Architecture

```
Client → POST /api/v1/extract {url}
         → api/routes.py (validate + route)
           → extractor/parser.py (validate Instagram URL)
             → extractor/fetcher.py (fetch HTML)
               → extractor/metadata.py (extract OG metadata)
                 → extractor/service.py (normalize data)
         ← {success, data: {platform, url, title, description, thumbnail}}
```

## Project Structure

```
instagram-intelligence-service/
├── app/
│   ├── extractor/
│   │   ├── parser.py      # Instagram URL validation
│   │   ├── fetcher.py     # HTTP fetch with browser headers
│   │   ├── metadata.py    # Open Graph metadata extraction
│   │   └── service.py     # Orchestration layer
│   ├── api/
│   │   └── routes.py      # FastAPI endpoints
│   ├── schemas/
│   │   └── instagram.py   # Pydantic request/response models
│   └── main.py            # FastAPI app entry
├── tests/
│   ├── test_parser.py
│   ├── test_fetcher.py
│   ├── test_metadata.py
│   ├── test_service.py
│   └── test_api.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API

### POST /api/v1/extract

Extract Open Graph metadata from an Instagram URL.

**Request:**
```json
{
  "url": "https://www.instagram.com/reel/DW8PkC0AZvb/"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "platform": "instagram",
    "url": "https://www.instagram.com/reel/DW8PkC0AZvb/",
    "canonical_url": "https://www.instagram.com/reel/DW8PkC0AZvb/",
    "title": "OG Title Here",
    "description": "OG Description Here",
    "thumbnail": "https://scontent.cdninstagram.com/og-image.jpg",
    "extracted_at": "2026-06-08T23:30:00Z"
  }
}
```

**Error Response (422):**
```json
{
  "detail": {
    "success": false,
    "error": "Not an Instagram URL: https://youtube.com/watch?v=12345"
  }
}
```

### GET /health

Health check endpoint.

## Testing

```bash
pytest tests/ -v
```

## Supported URLs

- Instagram Reels: `https://www.instagram.com/reel/{id}/`
- Instagram Posts: `https://www.instagram.com/p/{id}/`

## Future Roadmap

### Phase 1 (Current)
Open Graph Metadata Extraction

### Phase 2
```
Instagram URL → Video Download → Audio Extraction → Whisper Transcription
```

### Phase 3
```
Instagram URL → Video Download → OCR Extraction → Multimodal Analysis
```

### Phase 4
```
Caption + Transcript + OCR Text → LLM → Summary → Tags → Knowledge Base Integration
```
