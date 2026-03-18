import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from core.logging import setup_logging
from api.routes.chat import router as chat_router
from api.routes.health import router as health_router
from api.middleware.cors import setup_cors
from api.dependencies import get_pipeline_components

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifespan context manager
    logger.info("NutriGuide API is starting up...")
    get_pipeline_components()
    logger.info("Pipeline preloaded and ready!")
    yield
    logger.info("NutriGuide API has shut down")

app = FastAPI(
    title="NutriGuide AI",
    description="RAG-based pediatric nutrition assistant",
    version="0.1.0",
    lifespan=lifespan
)

# Setup CORS 
setup_cors(app)

app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")