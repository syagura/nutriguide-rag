import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", ""),
]

def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware to allow frontend requests.

    Args:
        app: FastAPI application instance
    """
    origins = [o for o in ALLOWED_ORIGINS if o]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )