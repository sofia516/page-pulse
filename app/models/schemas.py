from pydantic import BaseModel, HttpUrl
from typing import Optional


class AuditRequest(BaseModel):
    url: HttpUrl


class AuditResponse(BaseModel):
    url: str
    status_code: int
    response_time_ms: float
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    title: Optional[str] = None
    cached: bool = False