from pydantic import BaseModel, HttpUrl


class ProcessURLRequest(BaseModel):
    url: HttpUrl


class ProcessURLResponse(BaseModel):
    job_id: str
    status: str


class JobResponse(BaseModel):
    job_id: str
    url: str
    status: str
    data: dict | None = None
    error: str | None = None
    created_at: str
    updated_at: str
