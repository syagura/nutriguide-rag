import logging
import pickle
from pathlib import Path
from functools import lru_cache

import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder

from core.services.llm.model_factory import get_llm
from config.settings import (
    VECTOR_DIR, BM25_DIR,
    EMBEDDING_MODEL, RERANKER_MODEL
)

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def get_pipeline_components() -> dict:
    """
    load and cache all pipeline components needed for inference.

    Uses lru_cache so components are loaded once and reused across requests -
    loading models and indexes on evert request would be extremely slow.

    Returns:
        Dict containing faiss_index, chunks, bm25, embedding_model, reranker, llm

    Raises:
        RuntimeError: If required index files are not found
    """
    logger.info("Loading pipeline components...")

    # Load FAISS index 
    index_path = Path(VECTOR_DIR) / "index.faiss"
    chunks_path = Path(VECTOR_DIR) / "chunks.pkl"
    bm25_path = Path(BM25_DIR) / "bm25.pkl"

    if not index_path.exists():
        raise RuntimeError(f"FAISS index not found at {index_path} - run build_index.py first")
    if not chunks_path.exists():
        raise RuntimeError(f"Chunks file not found at {chunks_path} - run build_index.py first")
    if not bm25_path.exists():
        raise RuntimeError(f"BM25 index not found at {bm25_path} - run buil_index.py first")
    
    faiss_index = faiss.read_index(str(index_path))

    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    with open(bm25_path, "rb") as f:
        bm25 = pickle.load(f)

    # Load Embedding model and reranker 
    embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    reranker = CrossEncoder(RERANKER_MODEL)

    llm = get_llm()

    logger.info("All pipeline components loaded successfully")

    return {
        "faiss_index": faiss_index,
        "chunks": chunks,
        "bm25": bm25,
        "embedding_model": embedding_model,
        "reranker": reranker,
        "llm": llm
    }