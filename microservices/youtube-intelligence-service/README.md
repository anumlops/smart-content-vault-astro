# YouTube Intelligence Service

Extract metadata and transcripts from YouTube videos.

## Architecture

```
Client → POST /api/v1/extract {url}
         → api/routes.py (validate + route)
           → extractor/parser.py (validate YouTube URL, extract video ID)
             → extractor/metadata.py (oEmbed API + page scrape for metadata)
               → extractor/transcript.py (youtube-transcript-api)
                 → extractor/service.py (orchestrate + normalize)
         ← {success, data: {platform, url, title, description, thumbnail, channel, video_id, transcript}}
```

## Project Structure

```
youtube-intelligence-service/
├── app/
│   ├── extractor/
│   │   ├── parser.py      # YouTube URL validation + video ID
│   │   ├── fetcher.py     # HTTP fetch
│   │   ├── metadata.py    # oEmbed + OG metadata extraction
│   │   ├── transcript.py  # YouTube transcript extraction
│   │   └── service.py     # Orchestration layer
│   ├── api/
│   │   └── routes.py      # FastAPI endpoints
│   ├── schemas/
│   │   └── youtube.py     # Pydantic request/response models
│   └── main.py            # FastAPI app entry
├── tests/
│   ├── test_parser.py
│   ├── test_fetcher.py
│   ├── test_metadata.py
│   ├── test_transcript.py
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

Extract metadata and transcript from a YouTube URL.

**Request:**
```json
{
  "url": "https://www.youtube.com/watch?v=Pdp3p23P-TI"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "platform": "youtube",
    "url": "https://www.youtube.com/watch?v=Pdp3p23P-TI",
    "canonical_url": "https://www.youtube.com/watch?v=Pdp3p23P-TI",
    "title": "Video Title",
    "description": "Video description text...",
    "thumbnail": "https://i.ytimg.com/vi/Pdp3p23P-TI/maxresdefault.jpg",
    "channel_name": "Channel Name",
    "channel_url": "https://www.youtube.com/channel/UC...",
    "video_id": "Pdp3p23P-TI",
    "transcript": [
      {"text": "Hello world", "start": 0.0, "duration": 1.5}
    ],
    "extracted_at": "2026-06-10T20:00:00Z"
  }
}
```

**Error Response (422):**
```json
{
  "detail": {
    "success": false,
    "error": "Not a YouTube URL: https://vimeo.com/12345"
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

- Standard: `https://www.youtube.com/watch?v={id}`
- Short: `https://youtu.be/{id}`
- Embed: `https://www.youtube.com/embed/{id}`
- Shorts: `https://www.youtube.com/shorts/{id}`
- With timestamps, playlists, params: any of the above with `?t=...`, `&list=...`

## Future Roadmap

### Phase 1 (Current)
Metadata + Transcript Extraction

### Phase 2
```
YouTube URL → Transcript → LLM → Summary → Tags → Knowledge Base
```

### Phase 3
```
YouTube URL → Video Download → Audio Processing → Advanced Analysis
```
