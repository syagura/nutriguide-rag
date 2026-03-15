from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

def _get_ragas_embeddings() -> LangchainEmbeddingsWrapper:    # type: ignore
    """Wrap Groq LLm for RAGAS evaluator"""
    hf_embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    )
    return LangchainEmbeddingsWrapper(hf_embeddings)


def _safe_score(value) -> float:
    """Safely extract float score — handle NaN, list, None from timeout."""
    try:
        if isinstance(value, list):
            valid = [v for v in value if v is not None]
            return round(float(sum(valid) / len(valid)), 4) if valid else 0.0
        if value is None:
            return 0.0
        import math
        f = float(value)
        return 0.0 if math.isnan(f) else round(f, 4)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0
    

def run_ragas_evaluation(evaluation_data: list[dict], ragas_llm) -> dict:
    """
    Run RAGAS evaluation on a list of RAG inference results.

    Args:
        evaluation_data: List of dicts, each containing:
            - 'question': the user query
            - 'answer': the LLM generated answer
            - 'context': list of retrieved chunk texts used to generate the answer
            - 'ground_truth': the expected correct answer (for answer relevancy)

    Returns:
        Dict containing average scores for faithfulness, answer_revancy, context_precision
    """
    if not evaluation_data:
        raise ValueError("Evaluation data canot be empty")
    
    logger.info(f"Running RAGAS evaluation on {len(evaluation_data)} samples...")

    ragas_embeddings = _get_ragas_embeddings()

    run_config = RunConfig(
        timeout=180,
        max_retries=2,
        max_wait=30,
        max_workers=1
    )

    dataset = Dataset.from_list(evaluation_data)
    results = evaluate(
        dataset=dataset,
        llm=ragas_llm,
        embeddings=ragas_embeddings,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision
        ],
        run_config=run_config,
        raise_exceptions=False
    )

    scores = {
        "faithfulness": _safe_score(results["faithfulness"]),
        "answer_relevancy": _safe_score(results["answer_relevancy"]),
        "context_precision": _safe_score(results["context_precision"]),
        "n_samples": len(evaluation_data)
    }

    logger.info(f"RAGAS evaluation complete - scores: {scores}")
    return scores