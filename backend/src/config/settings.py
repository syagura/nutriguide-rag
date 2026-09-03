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

# Web retrieval config
WEB_SEARCH_MAX_RESULTS = int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5"))
WEB_RERANK_TOP_K = int(os.getenv("WEB_RERANK_TOP_K", "3"))
WEB_FETCH_TIMEOUT = int(os.getenv("WEB_FETCH_TIMEOUT", "8"))

# Allowlist of trusted health sources by trust tier.
# Tier 1: Official government and international health institutions
# Tier 2: Academic and research institutions
# Tier 3: Trusted health organizations (platforms reviewed by doctors)
TRUSTED_HEALTH_DOMAINS = {
    # Tier 1
    "kemenkes.go.id": 1,
    "idai.or.id": 1,
    "who.int": 1,
    "cdc.gov": 1,
    "nih.gov": 1,
    "medlineplus.gov": 1,
    "unicef.org": 1,
    # Tier 2
    "mayoclinic.org": 2,
    "healthychildren.org": 2,
    # Tier 3
    "alodokter.com": 3,
    "halodoc.com": 3,
}