import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv
from core.logging import setup_logging
from core.services.rag.reranker import load_reranker
from core.services.web.web_retriever import retrieve_web_context

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

if __name__ ==  "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "penelitian terbaru tentang creatine untuk anak"

    logger.info(f"Testing web retieval for query: '{query}'")
    reranker = load_reranker()

    chunks = retrieve_web_context(query, reranker)

    if not chunks:
        logger.warning("No web context retrieved.")
    else:
        for i, chunk in enumerate(chunks, start=1):
            print(f"\n--- Web Chunk {i} ---")
            print(f"Source: {chunk['metadata']['source']}")
            print(f"Title: {chunk['metadata']['title']}")
            print(f"Score: {chunk['metadata'].get('reranker_score')}")
            print(chunk["text"][:300], "...")