from typing import Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ContentCategory(str, Enum):
    TECHNOLOGY = "Technology"
    BUSINESS = "Business"
    FINANCE = "Finance"
    PRODUCTIVITY = "Productivity"
    EDUCATION = "Education"
    CAREER = "Career"
    MARKETING = "Marketing"
    HEALTH = "Health"
    ENTERTAINMENT = "Entertainment"
    LIFESTYLE = "Lifestyle"


class EnrichmentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingResult:
    url: str
    domain: str
    title: str | None
    summary: str | None
    category: ContentCategory | None
    tags: list[str]
    key_takeaways: list[str]
    extracted_text: str | None
    raw_content: str | None
    error: str | None = None
    status: EnrichmentStatus = EnrichmentStatus.PENDING
    processed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ContentSource:
    url: str
    content_type: str
    raw_html: str | None = None
    extracted_text: str | None = None
    metadata: dict = field(default_factory=dict)


@runtime_checkable
class ContentProcessor(Protocol):
    """Interface that all content source processors must implement."""

    source_type: str

    def can_handle(self, url: str) -> bool:
        """Check if this processor can handle the given URL."""
        ...

    async def extract(self, url: str) -> ContentSource:
        """Extract raw content from the source."""
        ...

    async def analyze(self, content: ContentSource) -> ProcessingResult:
        """Analyze extracted content and produce results."""
        ...
