from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    title: str | None = None
    content: str


class AnalyzeResponse(BaseModel):
    title: str
    summary: str
    category: str
    tags: list[str]
    key_takeaways: list[str]
