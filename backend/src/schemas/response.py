from pydantic import BaseModel

class ChatRespose(BaseModel):
    """Schema for chat endpoint response"""
    query: str
    answer: str
    sources: list[str]
    has_sources: bool

class HealthResponse(BaseModel):
    """Schema for health check endpoint response"""
    status: str
    version: str