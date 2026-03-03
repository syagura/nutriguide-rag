from rank_bm25 import BM25Okapi
import pickle
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def build_bm25(chunks: list[dict]) -> BM25Okapi:
    """
    Build a BM25 index from a list of chunks

    Args:
        chunks: List of chunk dicts, each containing 'text' and 'metadata'

    Retruns:
        Fitted BM250kapi instance ready for keyword search

    Raises:
        ValueError: if chunks list is empty
    """
    if not chunks:
        raise ValueError("Chunks must not be empty to build the BM25 index")
    
    tokenized = [chunk["text"].lower().split() for chunk in chunks]

    logger.info(f"Building BM25 index from {len(chunks)} chunks")
    return BM25Okapi(tokenized)

def search_bm25(
        bm25: BM25Okapi,
        query: str,
        chunks: list[dict],
        top_k: int = 5
    ) -> list[tuple[int, float]]:
    """
    Search BM25 index for chunks most relevant to the query.

    Args:
        bm25: Fitted BM25kapi instance
        query: Raw query string from the user
        chunks: Original list of chunks used to build the BM25 index
        top_k: Number of top results to return (default: 5)

    Returns:
        List of (chunk_index, score) tuples sorted by descending score
    """
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)

    scored = [(idx, float(score)) for idx, score in enumerate(scores)]
    scored.sort(key=lambda x: x[1], reverse=True)

    return scored[:top_k]

def save_bm25(bm25: BM25Okapi, save_dir: str) -> None:
    """
    Save BM25 index to disk using pickle

    Args:
        bm25: Fitted BM25kapi instance to save
        save_dir: Directory path where the file will be saved
    """
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    with open(save_path / "bm25.pkl", "wb") as f:
        pickle.dump(bm25, f)

    logger.info(f"BM25 index saved to {save_path}")

def load_bm25(save_dir: str) -> BM25Okapi:
    """
    Load a previously saved BM25 index from disk

    Args:
        save_dir: Directory path where bm25.pkl is sorted

    Returns:
        FileNotFoundError: If bm25.pkl is not found in the given directory
    """
    bm25_path = Path(save_dir) / "bm25.pkl"

    if not bm25_path.exists():
        raise FileNotFoundError(f"BM25 index not found: {bm25_path}")
    
    with open(bm25_path, "rb") as f:
        bm25 = pickle.load(f)

    logger.info(f"B<25 index loaded from {bm25_path}")
    return bm25