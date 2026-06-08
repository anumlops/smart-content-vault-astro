from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    url: str


class InstagramData(BaseModel):
    platform: str = "instagram"
    url: str
    canonical_url: str = ""
    title: str = ""
    description: str = ""
    thumbnail: str = ""
    extracted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )


class ExtractResponse(BaseModel):
    success: bool
    data: InstagramData | None = None
    error: str | None = None
