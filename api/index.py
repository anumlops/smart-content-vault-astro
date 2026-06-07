from fastapi import FastAPI
from pydantic import BaseModel
from ai.service import AIService

app = FastAPI(title="AI Analysis")

ai_service = AIService()


class AnalyzeRequest(BaseModel):
    title: str | None = None
    content: str


class AnalyzeResponse(BaseModel):
    summary: str
    tags: list[str]


@app.post("/analyze-llm")
def analyze_llm(request: AnalyzeRequest):
    result = ai_service.analyze(content=request.content, title=request.title)
    return AnalyzeResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok"}
