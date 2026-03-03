from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

def create_chunker(chunk_size: int = 512, chunk_overlap: int = 128) -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter instance with the given configuration.

    Args:
        chunk_size: Maximum number of characters per chunk (default: 512)
        chunk_overlap: Number of overlapping characters between chunks (default=128)

    Returns:
        Configured RecursiveCharacterTextSplitter instance
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

def chunk_pages(pages: list[dict], chunk_size: int = 512, chunk_overlap: int = 128) -> list[dict]:
    """
    Split preprocessed pages into smaller chunks for embedding and retrieval.

    Args:
        pages: List of cleaned pages from preprocessor, each containing 'text' and 'metadata'
        chunk_size: Maximum number of characters per chunks (default: 512)
        chunk_overlap: Number of overlapping characters between chunks (default: 128)

    Returns:
        List of chunks, each containing 'text', 'metadata', and 'chunk_index'
    """
    logger.info(f"Start chunking {len(pages)} pafes (chunk_size={chunk_size}, overlap={chunk_overlap})")

    chunker = create_chunker(chunk_size, chunk_overlap)

    all_chunks = []

    for page in pages:
        # split text 
        raw_chunks = chunker.split_text(page["text"])

        for idx, chunk_text in enumerate(raw_chunks):
            if len(chunk_text.strip()) < 30:
                logger.warning(f"Chunk skipped - too short ({len(chunk_text.strip())} character)")
                continue

            all_chunks.append({
                "text": chunk_text.strip(),
                "metadata": {
                    **page["metadata"],
                    "chunk_index": idx
                }
            })

    logger.info(f"Chunking completed: {len(all_chunks)} chunk generated from {len(pages)} pages")

    # Return the final list of chunk 
    return all_chunks