import os
from pathlib import Path

# Root directory backend 
BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent

# Path to folder storage 
STORAGE_DIR = BACKEND_ROOT / "storage"
VECTOR_DIR = str(STORAGE_DIR / "vectordb")
BM25_DIR = str(STORAGE_DIR / "vectordb")
RAW_DIR = str(STORAGE_DIR / "raw")

# Groq config
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Retrieval config 
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "10"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "3"))

# Embedding config
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")

# Session memory config
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "1800"))
SESSION_MAX_MESSAGES = int(os.getenv("SESSION_MAX_MESSAGES", "10"))