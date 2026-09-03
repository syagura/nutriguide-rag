import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dotenv import load_dotenv
from core.logging import setup_logging
from core.services.llm.model_factory import get_llm
from core.services.router.query_router import route_query

load_dotenv()
setup_logging()

logger = logging.getLogger(__name__)

TEST_QUERIES = [
    ("What foods are high in protein?", []),
    ("What did we just discuss?", [{"role": "user", "content": "What foods are high in protein?"}]),
    ("What about affordable ones?", [{"role": "user", "content": "Fish, eggs, and tempe kaya protein"}]),
    ("What’s the latest research on creatine for children?", []),
    ("Compare this PDF with the latest WHO information on stunting", []),
]

if __name__ == "__main__":
    llm = get_llm()

    for query, history in TEST_QUERIES:
        decision = route_query(query, history, llm)
        print(f"\nQuery: {query}")
        print(f"History: {'available' if history else 'not available'}")
        print(f"Decision: {decision}")