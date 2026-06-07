from pydantic import BaseModel, HttpUrl


class ExtractRequest(BaseModel):
    url: HttpUrl


class ExtractResponse(BaseModel):
    success: bool
    url: str
    domain: str
    title: str | None = None
    content: str | None = None
    error: str | None = None
