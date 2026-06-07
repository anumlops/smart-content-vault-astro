import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from app.analyzer import ContentAnalyzer
from app.crawler import CrawlerService


def sanitize_filename(domain: str) -> str:
    return domain.replace(".", "_").replace(":", "_").replace("/", "_")


def extract_to_md(url: str, analyze: bool = False):
    service = CrawlerService()
    result = service.extract(url)

    if not result["success"]:
        print(f"Error: {result['error']}")
        sys.exit(1)

    domain = result["domain"]
    title = result["title"] or "Untitled"
    content = result["content"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = f"""# {title}

**Source:** {url}
**Domain:** {domain}
**Extracted:** {timestamp}

---

{content}
"""
    filename = f"{sanitize_filename(domain)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_path = Path(filename)
    out_path.write_text(md, encoding="utf-8")
    print(f"Saved to {out_path}")

    if analyze:
        _run_analysis(content, title, domain)


def _run_analysis(content: str, title: str | None, domain: str):
    analyzer = ContentAnalyzer()
    analysis = analyzer.analyze(content=content, title=title)

    analysis_filename = f"{sanitize_filename(domain)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_analysis.json"
    analysis_path = Path(analysis_filename)
    analysis_path.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    print(f"Analysis saved to {analysis_path}")

    print(f"\nAnalysis:")
    print(f"  Title: {analysis['title']}")
    print(f"  Category: {analysis['category']}")
    print(f"  Tags: {', '.join(analysis['tags'])}")
    print(f"  Summary: {analysis['summary'][:120]}...")
    print(f"  Takeaways: {len(analysis['key_takeaways'])} items")


def main():
    analyze = False
    args = sys.argv[1:]

    if "--analyze" in args or "-a" in args:
        analyze = True
        args = [a for a in args if a not in ("--analyze", "-a")]

    if args:
        url = args[0]
    else:
        url = input("Enter URL: ").strip()

    if not url:
        print("No URL provided")
        sys.exit(1)

    extract_to_md(url, analyze=analyze)


if __name__ == "__main__":
    main()
