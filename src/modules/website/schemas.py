from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class WebsiteContent:
    url: str
    domain: str
    title: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class WebsiteAnalysis:
    title: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    key_takeaways: list[str] = field(default_factory=list)
    error: Optional[str] = None
    processed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class WebsiteResult:
    url: str
    domain: str
    title: Optional[str]
    summary: Optional[str]
    category: Optional[str]
    tags: list[str]
    key_takeaways: list[str]
    extracted_text: Optional[str]
    error: Optional[str]
    status: str
    processed_at: str
