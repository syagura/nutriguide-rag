import logging
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
    from langchain_ollama import ChatOllama

    ollama_llm = ChatOllama(
        model="qwen2.5:0.5b",
        temperature=0
    )

    return LangchainLLMWrapper(ollama_llm)

def run_full_evaluation(
        test_cases: list[dict],
        chunks: list[dict],
        faiss_index,
        bm25,
        embedding_model,
        reranker,
        llm
    ) -> dict:

    logger.info(f"Starting full RAGAS evaluation - {len(test_cases)} test cases")

    # Jalanin inference dulu — kumpulin semua evaluation_data
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
            logger.error(f"Failed to process test case {i + 1}: {e}")
            continue

    if not evaluation_data:
        raise RuntimeError("All test cases failed - no evaluation data to process")

    # Inference selesai — bebasin RAM sebelum RAGAS jalan
    logger.info("Inference complete — freeing RAM before RAGAS evaluation...")
    import gc
    del embedding_model
    del reranker
    gc.collect()
    logger.info("RAM freed!")

    ragas_llm = setup_ragas_llm()
    scores = run_ragas_evaluation(evaluation_data, ragas_llm=ragas_llm)
    return scores