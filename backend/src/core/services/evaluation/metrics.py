from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
import logging

logger = logging.getLogger(__name__)

def run_ragas_evaluation(evaluation_data: list[dict]) -> dict:
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

    dataset = Dataset.from_list(evaluation_data)
    results = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision
        ]
    )

    scores = {
        "faithfulness": round(float(results["faithfulness"]), 4),
        "answer_relevancy": round(float(results["answer_relevancy"]), 4),
        "context_precision": round(float(results["context_precision"]), 4),
        "n_samples": len(evaluation_data)
    }

    logger.info(f"RAGAS evaluation complete - scores: {scores}")
    return scores