"""
CLI entry point for the Website Intelligence module.
Can be called as a subprocess from the Astro API.

Usage:
    python cli.py analyze <url>
    python cli.py serve

Examples:
    python cli.py analyze https://example.com/article
    python cli.py serve  # starts FastAPI server on port 8001
"""

import json
import sys
import asyncio
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.modules.website import WebsiteProcessor


async def analyze_url(url: str) -> dict:
    processor = WebsiteProcessor()
    result = await processor.process_url(url)
    return {
        "url": result.url,
        "domain": result.domain,
        "title": result.title,
        "summary": result.summary,
        "category": result.category.value if result.category else None,
        "tags": result.tags,
        "key_takeaways": result.key_takeaways,
        "extracted_text": result.extracted_text,
        "error": result.error,
        "status": result.status.value,
        "processed_at": result.processed_at,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: cli.py analyze <url> | serve"}))
        sys.exit(1)

    command = sys.argv[1]

    if command == "analyze":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "URL required"}))
            sys.exit(1)

        url = sys.argv[2]
        result = asyncio.run(analyze_url(url))
        print(json.dumps(result, indent=2))

    elif command == "serve":
        import uvicorn
        port = int(os.getenv("WEBSITE_INTELLIGENCE_PORT", "8001"))
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

    else:
        print(json.dumps({"error": f"Unknown command: {command}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
