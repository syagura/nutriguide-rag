import logging
from fastapi import APIRouter
from schemas.response import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the API is running.

    Returns:
        HealthResponse with status and version info
    """
    logger.info("Health check requested")
    return HealthResponse(status="ok", version="0.1.0")