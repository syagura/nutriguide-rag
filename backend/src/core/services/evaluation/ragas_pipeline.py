import os
from langchain_groq import ChatGroq
import logging
from ragas.llms import LangchainLLMWrapper

from core.services.inference.inference_engine import run_inference, retrieve_pdf_chunks
from core.services.web.web_retriever import retrieve_web_context
from core.services.router.query_rewriter import rewrite_query_for_retrieval
from core.prompts.chain import run_rag_chain
from core.services.evaluation.metrics import run_ragas_evaluation

logger = logging.getLogger(__name__)

MODES = ["pdf_only", "web_only", "hybrid", "memory_retrieval"]

def prepare_evaluation_sample(
        query: str,
        ground_truth: str,
        mode: str,
        chunks: list[dict],
        faiss_index,
        bm25,
        embedding_model,
        reranker,
        llm,
        conversation_history: list[dict] | None = None
    ) -> dict:
    """
    Run inference for a single query under a specific retrieval mode and format the result for RAGAS evaluation.

    Args:
        query: The evaluation question
        ground_truth: The expected correct answer for this question
        mode:
            "pdf_only" - PDF rewtrieval only
            "web_only" - web retrieval only
            "hybrid" - PDF + web retrievsl combined
            "memory_retrieval" - PDF retrieval + conversation history, query rewritten for retrieval first
                                (needs conversation_history to be meaningful)
        chunks: Full list of indexed chunks
        faiss_index: Built FAISS index
        bm25: Fitted BM25 index
        embedding_model: SentenceTransformer model
        reranker: CrossEncoder model
        llm: Initilaized LLM backend

    Returns:
        Dict formatted for RAGAS evaluation with question, answer, context, ground_truth
    """
    conversation_history = conversation_history or []

    retrieval_query = query
    if mode == "memory_retrieval" and conversation_history:
        retrieval_query = rewrite_query_for_retrieval(query, conversation_history, llm)

    pdf_chunks = []
    web_chunks = []

    if mode in ("pdf_only", "hybrid", "memory_retrieval"):
        pdf_chunks, _ = retrieve_pdf_chunks(retrieval_query, chunks, faiss_index, bm25, embedding_model, reranker)

    if mode in ("web_only", "hybrid"):
        web_chunks = retrieve_web_context(retrieval_query, reranker)
    
    result = run_rag_chain(
        query=query,
        llm=llm,
        pdf_chunks=pdf_chunks,
        web_chunks=web_chunks,
        conversation_history=conversation_history if mode == "memory_retrieval" else []
    )

    contexts = [c["text"] for c in pdf_chunks] + [c["text"] for c in web_chunks]

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
    # from langchain_ollama import ChatOllama

    # ollama_llm = ChatOllama(
    #     model="qwen2.5:0.5b",
    #     temperature=0
    # )

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key: 
        raise RuntimeError("GROQ_API_KEY is not set - required for RAGAS evaluation")

    groq_llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=api_key,
        temperature=0
    )

    return LangchainLLMWrapper(groq_llm)

def run_full_evaluation(
        test_cases: list[dict],
        chunks,
        faiss_index,
        bm25,
        embedding_model,
        reranker,
        llm,
        mode: str = "pdf_only"
    ) -> dict:

    logger.info(f"Starting full RAGAS evaluation - mode={mode} {len(test_cases)} test cases")

    # Jalanin inference dulu — kumpulin semua evaluation_data
    evaluation_data = []
    for i, test_case in enumerate(test_cases):
        logger.info(f"Processing test case {i + 1}/{len(test_cases)}: '{test_case['question']}'")
        try:
            sample = prepare_evaluation_sample(
                query=test_case["question"],
                ground_truth=test_case["ground_truth"],
                mode=mode,
                chunks=chunks,
                faiss_index=faiss_index,
                bm25=bm25,
                embedding_model=embedding_model,
                reranker=reranker,
                llm=llm,
                conversation_history=test_case.get("conversation_history")
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

def run_comparative_evaluation(
        test_cases: list[dict], chunks, faiss_index, bm25, embedding_model,reranker, llm
) -> dict:
    """
    Run RAGAS evaluation in 4 retrieval modes for the same test case to compare PDF-only/Web-only/Hybrid/Memory + Retrieval.

    Test case must include a 'conversation_history' key to be included in the memory_retrieval
    mode-test cases without this key are skipped specifically for this mode.
    """
    logger.info(f"Starting comparative RAGAS evaluation - {len(test_cases)} test cases x {len(MODES)} modes")
    evaluation_data_by_mode = {mode: [] for mode in MODES}

    for i, test_case in enumerate(test_cases):
        for mode in MODES:
            if mode == "memory_retrieval" and not test_case.get("conversation_history"):
                continue

            logger.info(f"[{mode}] Processing test case {i + 1}/{len(test_cases)}: '{test_case['question']}'")
            try:
                sample = prepare_evaluation_sample(
                    query=test_case["question"], ground_truth=test_case["ground_truth"], mode=mode,
                    chunks=chunks, faiss_index=faiss_index, bm25=bm25, embedding_model=embedding_model,
                    reranker=reranker, llm=llm, conversation_history=test_case.get("conversation_history")
                )
                evaluation_data_by_mode[mode].append(sample)
            except Exception as e:
                logger.error(f"[{mode}] Failed to process test case {i + 1}: {e}")
                continue

    logger.info("Inference complete for all modes - freeing RAM before RAGAS evaluation...")
    import gc
    del embedding_model
    del reranker
    gc.collect()
    logger.info("RAM freed!")

    ragas_llm = setup_ragas_llm()

    all_scores = {}
    for mode, evaluation_data in evaluation_data_by_mode.items():
        if not evaluation_data:
            logger.warning(f"[{mode}] No useable test case, skipping")
            all_scores[mode] = None
            continue
        all_scores[mode] = run_ragas_evaluation(evaluation_data, ragas_llm=ragas_llm)

    return all_scores