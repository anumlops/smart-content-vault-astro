from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    og_title: str = ""
    og_description: str = ""
    og_image: str = ""


class ExtractedDocument(BaseModel):
    source_type: str = "website"
    url: str
    canonical_url: str = ""
    domain: str
    title: str = ""
    description: str = ""
    author: str = ""
    published_date: str = ""
    language: str = ""
    content: str
    word_count: int = 0
    extracted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    metadata: Metadata = Field(default_factory=Metadata)
