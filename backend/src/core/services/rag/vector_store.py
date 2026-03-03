import faiss
import numpy as np
import pickle
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def build_vector_store(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Build a FAISS index from a numpy array of embeddings.

    Args:
        embeddings: 2D numpy array of shape (n_chunks, embedding_dim)

    Returns:
        FAISS IndexFlapIP index ready for similarity search
    """
    if embeddings.ndim != 2 or len(embeddings) == 0:
        raise ValueError(f"Embeddings must be 2D arrays and cannot be empty, shaped: {embeddings.shape}")
    
    # Initialized index using FAISS (IndexFlatIP) for consine similarity
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)

    # Normalize for inner product 
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    logger.info(f"FAISS index built: {index.ntotal} vectors, dim={dim}")
    return index

def search_vector_store(
        index: faiss.IndexFlatIP,
        query_embedding: np.ndarray,
        top_k: int = 5
    ) -> tuple[np.ndarray, np.ndarray]:
    """
    Search FAISS index for the most similar vectors to a query embedding.

    Args:
        indx: Built FAISS index
        query_embedding: 1D numpy array of the query embedding
        top_k: Number of top results to return (default: 5)
    
    Returns:
        Tuple of (scores, indices) - both are 1D numpy arrays of length top_k
    """
    # reshape from (dim, ) to (1, dim)
    query = query_embedding.reshape(1, -1).astype(np.float32)
    faiss.normalize_L2(query)
    scores, indices = index.search(query, top_k)

    # Flatten from (1, top_k) to (top_k,)
    return scores[0], indices[0]


def save_vector_store(index: faiss.IndexFlatIP, chunks: list[dict], save_dir: str) -> None:
    """
    Save FAISS index and chunks metadata to disk.

    Args:
        index: Built FAISS index to save
        chunks: List of chunk dicts (text + metadata) to save alongside the index
        save_dir: Directory path where files will be saved
    """
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # Save FAISS index to .faiss file 
    faiss.write_index(index, str(save_path / "index.faiss"))

    # Save chunks to .pkl file 
    with open(save_path / "chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    logger.info(f"Vector store saved to {save_path}")

def load_vector_store(save_dir: str) -> tuple[faiss.IndexFlatIP, list[dict]]:
    """
    Load a previously saved FAISS index and chunks from disk.

    Args:
        save_dir: Directory path where index.faiss and chunks.pkl are stored

    Returns:
        Tuple of (faiss_index, chunks)

    Raises:
        FileNotFoundError: If index or chunks file is not found
    """
    save_path = Path(save_dir)
    
    index_path = save_path / "index.faiss"
    chunks_path = save_path / "chunks.pkl"

    if not index_path.exists():
        raise FileNotFoundError(f"FAISS index not found: {index_path}")
    if not chunks_path.exists():
        raise FileNotFoundError(f"Chunks file not found: {chunks_path}")
    
    index = faiss.read_index(str(index_path))

    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)

    logger.info(f"Vector store loaded: {index.ntotal} vectors, {len(chunks)} chunks")
    return index, chunks