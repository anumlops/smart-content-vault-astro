from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    url: str


class TranscriptSegment(BaseModel):
    text: str
    start: float
    duration: float


class YouTubeData(BaseModel):
    platform: str = "youtube"
    url: str
    canonical_url: str = ""
    title: str = ""
    description: str = ""
    thumbnail: str = ""
    channel_name: str = ""
    channel_url: str = ""
    video_id: str = ""
    transcript: list[TranscriptSegment] | None = None
    extracted_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )


class ExtractResponse(BaseModel):
    success: bool
    data: YouTubeData | None = None
    error: str | None = None
