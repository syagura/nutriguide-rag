import os
import logging
from langchain_groq import ChatGroq
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper

from core.services.inference.inference_engine import run_inference
from core.services.evaluation.metrics import run_ragas_evaluation

logger = logging.getLogger(__name__)

def prepare_evaluation_sample(
        query: str,
        ground_truth: str,
        chunks: list[dict],
        faiss_index,
        bm25,
        embedding_model,
        reranker,
        llm
    ) -> dict:
    """
    Run inference for a single query and format the result for RAGAS evaluation.

    Args:
        query: The evaluation question
        ground_truth: The expected correct answer for this question
        chunks: Full list of indexed chunks
        faiss_index: Built FAISS index
        bm25: Fitted BM25 index
        embedding_model: SentenceTransformer model
        reranker: CrossEncoder model
        llm: Initilaized LLM backend

    Returns:
        Dict formatted for RAGAS evaluation with question, answer, context, ground_truth
    """
    result = run_inference(
        query=query,
        chunks=chunks,
        faiss_index=faiss_index,
        bm25=bm25,
        embedding_model=embedding_model,
        reranker=reranker,
        llm=llm
    )

    contexts = [
        chunk["text"] for chunk in chunks
        if chunk["metadata"].get("source") in result.get("sources", [])
    ]

    if not contexts:
        contexts = [chunk["text"] for chunk in chunks[:3]]

    return {
        "question": query,
        "answer": result["answer"],
        "contexts": contexts,
        "ground_truth": ground_truth
    }


def setup_ragas_llm() -> LangchainLLMWrapper: # type: ignore
    """
    Configure RAGAS to use Groq as its internal evaluation LLM.

    Returns:
        LangchainLLMWrapper warapping a Groq ChatGroq instance

    Raises:
        RuntimeError: If GROQ_API_KEY is not set
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set - required for RAGAS evaluation")
    
    groq_llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=api_key,
        temperature=0
    )

    return LangchainLLMWrapper(groq_llm)

def run_full_evaluation(
        test_cases: list[dict],
        chunks: list[dict],
        faiss_index,
        bm25,
        embedding_model,
        reranker,
        llm
    ) -> dict:
    """
    Run the full RAGAS evaluation pipeline on a list test cases.

    Args:
        test_cases: List of dicts with 'question' and 'ground_truth' keys
        chunks: Full list of indexed chunks
        faiss_index: Built FAISS index
        bm25: Fitted BM25 index
        embedding_model: SentenceTransformer model
        reranker: CrossEncoder model
        llm: Intialized LLm backend

    Returns:
        Dict containing RAGAS scores and evaluation metadata
    """
    logger.info(f"Starting full RAGAS evaluation - {len(test_cases)} test cases")

    ragas_llm = setup_ragas_llm()

    evaluation_data = []
    for i, test_case in enumerate(test_cases):
        logger.info(f"Processing test case {i + 1}/{len(test_cases)}: '{test_case['question']}'")
        try:
            sample = prepare_evaluation_sample(
                query=test_case["question"],
                ground_truth=test_case["ground_truth"],
                chunks=chunks,
                faiss_index=faiss_index,
                bm25=bm25,
                embedding_model=embedding_model,
                reranker=reranker,
                llm=llm
            )
            evaluation_data.append(sample)

        except Exception as e:
            logger.error(f"Failed to process test cases {i + 1}: {e}")
            continue

    if not evaluation_data:
        raise RuntimeError("All test cases failed - no evaluation data to process")
    
    scores = run_ragas_evaluation(evaluation_data)
    return scores