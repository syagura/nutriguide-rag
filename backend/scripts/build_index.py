import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv
from src.core.logging import setup_logging
from src.core.services.rag.indexer import build_index

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

RAW_DIR = str(Path(__file__).resolve().parent.parent / "storage" / "raw")
VECTOR_DIR = str(Path(__file__).resolve().parent.parent / "storage" / "vectordb")

if __name__ == "__main__":
    logger.info("Starting index build process...")
    logger.info(f"Reading PDFs from: {RAW_DIR}")
    logger.info(f"Saving indexes to: {VECTOR_DIR}")

    try:
        summary = build_index(
            raw_dir=RAW_DIR,
            vector_dir=VECTOR_DIR,
            bm25_dir=VECTOR_DIR
        )
        logger.info("=" * 50)
        logger.info("Index build completed successfully!")
        logger.info(f"Pages processed: {summary['n_pages']}")
        logger.info(f"Chunks generated: {summary['n_chunks']}")
        logger.info(f"Indexes saved to: {summary['vector_dir']}")
        logger.info("=" * 50)
        logger.info("You can now start the API with: uvicorn main:app --reload")

    except Exception as e:
        logger.error(f"Index build failed: {e}")
        sys.exit(1)