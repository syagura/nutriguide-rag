from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Schema for incoming chat requests."""

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="User's question about pediatric nutrition"
    )

    session_id: str | None = Field(
        default=None,
        description="Session ID for conversational continuity. Omit to start a new session."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"query": "What are the iron requirements for a 6-month-old baby?"}
            ]
        }
    }