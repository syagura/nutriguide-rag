from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)

# A multilingual model was chosen because the knowledge base is a mix of Indonesian and English
# The monolingual Englih all_MiniLM-L6-v2 will drop in quality for Indonesian text.
DEFAULT_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def load_embedding_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """
    Load a SentenceTransformer embedding model.

    Args:
        model_name: HuggingFace model name or local path (default: multilingual MiniLM)

    Returns:
        Loaded SentenceTransformer model instance
    """
    logger.info(f"Loading embedding model: {model_name}")

    # download an load model 
    model = SentenceTransformer(model_name)

    logger.info(f"Embedding model loaded successfully")
    return model

def embed_chunks(chunks: list[dict], model: SentenceTransformer) -> tuple[list[dict], np.ndarray]:
    """
    Generate embeddings for a list of text chunks.

    Args:
        chunks: List of chunk dicts from chunker, each containing 'text' and 'metadata'
        model: Loaded SentenceTransformer model instance

    Returns:
        Tuple of (chunks, embeddings) where embeddings is a numpy array of shape (n_chunks, dim)
    """
    if not chunks:
        logger.warning("Empty chunks list received, returning empty embedding")
        return chunks, np.array([])
    
    logger.info(f"Generaying embedding for {len(chunks)} chunks")

    # Extract text from each chunk to embed 
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True
    )

    logger.info(f"Embeddings generated: shape {embeddings.shape}")
    return chunks, embeddings