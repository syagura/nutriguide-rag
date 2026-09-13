from pydantic import BaseModel

class SourceItem(BaseModel):
    label: str
    url: str | None = None

class ChatRespose(BaseModel):
    """Schema for chat endpoint response"""
    query: str
    answer: str
    sources: list[SourceItem]
    has_sources: bool
    session_id: str

class HealthResponse(BaseModel):
    """Schema for health check endpoint response"""
    status: str
    version: str