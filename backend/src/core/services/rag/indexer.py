import logging
from pathlib import Path

from core.services.processing.pdf_loader import load_all_pdfs
from core.services.processing.preprocessor import preprocess_pages
from core.services.processing.chunker import chunk_pages
from core.services.rag.embedder import load_embedding_model, embed_chunks
from core.services.rag.vector_store import build_vector_store, save_vector_store
from core.services.rag.bm25_retriever import build_bm25, save_bm25

logger = logging.getLogger(__name__)

# default Path to storage folder - relative from root project
DEFAULT_RAW_DIR = "storage/raw"
DEFAULT_VECTOR_DIR = "storage/vectordb"
DEFAULT_BM25_DIR = "storage/vectordb"

def build_index(
        raw_dir: str = DEFAULT_RAW_DIR,
        vector_dir: str = DEFAULT_VECTOR_DIR,
        bm25_dir: str = DEFAULT_BM25_DIR,
        chunk_size: int = 512,
        chunk_overlap: int = 128,
        embeddinng_model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    ) -> dict:
    """
    Run the full indexing pipeline: Load PDFs, preprocess, chunk, embed, and save indexes.

    Args:
        raw_dir: Path to folder containing raw PDF files
        vector_dir: Path to save FAISS index and chunks
        bm25_dir: path to save BM25 index
        chunk_size: Maximum characters per chunk (default: 512)
        chunk_overlap: Overlapping characters betweem chunks (default: 128)
        embedding_model_name: HuggingFace model name for embeddings

    Returns:
        Dict containing pipeline summary: n_pages, n_chunks, vector_dir, bm25_dir

    Raises:
        ValueError: If not pages were extracted or no chunks were generated
    """
    logger.info("=" * 50)
    logger.info("Start indexing pipeline")
    logger.info("=" * 50)

    # Step 1 - Load all PDFs from raw folder
    logger.info(f"[1/5] Loading PDFs from {raw_dir}")
    pages = load_all_pdfs(raw_dir)
    if not pages:
        raise ValueError(f"No pages were successfully loaded from {raw_dir}. Make sure the raw folder contains PDF files.")
    
    # Preprocess 
    logger.info(f"[2/5] Preprocessing {len(pages)} pages")
    cleaned_pages = preprocess_pages(pages)
    if not cleaned_pages:
        raise ValueError("no pages passed preprocessing. Check PDF quality")
    
    # Chunking 
    logger.info(f"[3/5] Chunking {len(cleaned_pages)} pages")
    chunks = chunk_pages(cleaned_pages, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    if not chunks:
        raise ValueError("No chunks were generated. Check the chunk_size and chunk_overlap parameters.")
    
    # Embedding
    logger.info(f"[4/5] Embedding {len(chunks)} chunks")
    embedding_model = load_embedding_model(embeddinng_model_name)
    chunks, embeddings = embed_chunks(chunks, embedding_model)

    # Build and save index 
    logger.info(f"[5/5] Building and saving indezes")

    # FAISS Index for semantic search
    faiss_index = build_vector_store(embeddings)
    save_vector_store(faiss_index, chunks, vector_dir)

    # BM25 index for keyword search 
    bm25 = build_bm25(chunks)
    save_bm25(bm25, bm25_dir)

    summary = {
        "n_pages": len(cleaned_pages),
        "n_chunks": len(chunks),
        "vector_dir": vector_dir,
        "bm25_dir": bm25_dir
    }

    logger.info("=" * 50)
    logger.info(f"Indexing completed: {len(chunks)} chunks from {len(cleaned_pages)} pages")
    logger.info("=" * 50)

    return summary