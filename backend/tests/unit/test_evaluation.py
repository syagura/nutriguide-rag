import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.core.services.evaluation.report_generator import generate_report, _interpret_scores, generate_comparative_report
from src.core.services.evaluation.ragas_pipeline import prepare_evaluation_sample, run_comparative_evaluation

def test_generate_report_creates_file(tmp_path):
    scores = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.78,
        "context_precision": 0.72,
        "n_samples": 5
    }
    report_path = generate_report(scores, output_dir=str(tmp_path))

    assert Path(report_path).exists()
    assert report_path.endswith(".json")

def test_generate_report_content(tmp_path):
    scores = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.78,
        "context_precision": 0.72,
        "n_samples": 5
    }
    report_path = generate_report(scores, output_dir=str(tmp_path))

    with open(report_path) as f:
        report = json.load(f)

    assert "scores" in report
    assert "interpretation" in report
    assert "timestamp" in report

def test_interpret_scores_above_threshold():
    scores = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.80,
        "context_precision": 0.75
    }
    interpretation = _interpret_scores(scores)

    for metric, text in interpretation.items():
        assert "✅" in text

def test_interpret_scores_below_threshold():
    scores = {
        "faithfulness": 0.50,
        "answer_relevancy": 0.45,
        "context_precision": 0.60
    }
    interpretation = _interpret_scores(scores)

    for metric, text in interpretation.items():
        assert "⚠️" in text

def test_interpret_scores_mixed():
    scores = {
        "faithfulness": 0.85,
        "answer_relevancy": 0.50
    }
    interpretation = _interpret_scores(scores)

    assert "✅" in interpretation["faithfulness"]
    assert "⚠️" in interpretation["answer_relevancy"]

def test_generate_comparative_report_creates_file(tmp_path):
    all_scores = {
        "pdf_only": {"faithfulness": 0.8, "answer_relevancy": 0.75, "context_precision": 0.7, "n_samples": 3},
        "web_only": {"faithfulness": 0.6, "answer_relevancy": 0.65, "context_precision": 0.5, "n_samples": 3},
        "hybird": {"faithfulness": 0.85, "answer_relevancy": 0.8, "context_precision": 0.78, "n_samples": 3},
        "memory_retrieval": None
    }
    report_path = generate_comparative_report(all_scores, output_dir=str(tmp_path))
    assert Path(report_path).exists()

def test_generate_comparative_report_ranks_modes_per_metric(tmp_path):
    all_scores = {
            "pdf_only": {"faithfulness": 0.8, "answer_relevancy": 0.75, "context_precision": 0.7, "n_samples": 3},
            "web_only": {"faithfulness": 0.6, "answer_relevancy": 0.65, "context_precision": 0.5, "n_samples": 3}
        }
    report_path = generate_comparative_report(all_scores, output_dir=str(tmp_path))

    with open(report_path) as f:
        report = json.load(f)

    faithfulness_ranking = report["comparison_summary"]["faithfulness"]
    assert faithfulness_ranking[0]["mode"] == "pdf_only"
    assert faithfulness_ranking[1]["mode"] == "web_only"

def test_generate_comparative_report_skips_one_scores(tmp_path):
    all_scores = {"pdf_only": {"faithfulness": 0.8, "answer_relevancy": 0.75, "context_precision": 0.7, "n_samples": 3}, "memory_retrieval": None}
    report_path = generate_comparative_report(all_scores, output_dir=str(tmp_path))

    with open(report_path) as f:
        report = json.load(f)

    assert report["modes"]["memory_retrieval"]["scores"] is None
    assert report["modes"]["memory_retrieval"]["interpretation"] is None

@patch("src.core.services.evaluation.ragas_pipeline.run_rag_chain")
@patch("src.core.services.evaluation.ragas_pipeline.retrieve_web_context")
@patch("src.core.services.evaluation.ragas_pipeline.retrieve_pdf_chunks")
def test_prepare_evaluation_sample_pdf_only_skips_web(mock_pdf, mock_web, mock_chain):
    mock_pdf.return_value = ([{"text": "pdf content", "metadata": {}}], "id")
    mock_chain.return_value = {"answer": "answer", "sources": []}

    sample = prepare_evaluation_sample(
        query="q", ground_truth="gt", mode="pdf_only", chunks=[], faiss_index=None,
        bm25=None, embedding_model=None, reranker=None, llm=MagicMock()
    )

    mock_pdf.assert_called_once()
    mock_web.assert_no_called()
    assert sample["contexts"] == ["pdf content"]

@patch("src.core.services.evaluation.ragas_pipeline.run_rag_chain")
@patch("src.core.services.evaluation.ragas_pipeline.retrieve_web_context")
@patch("src.core.services.evaluation.ragas_pipeline.retrieve_pdf_chunks")
def  test_prepare_evaluation_sample_web_only_skips_pdf(mock_pdf, mock_web, mock_chain):
    mock_web.return_value = [{"text": "web content", "metadata": {}}]
    mock_chain.return_value = {"answer": "answer", "sources": []}


    sample = prepare_evaluation_sample(
        query="q", ground_truth="gt", mode="web_only", chunks=[], faiss_index=None,
        bm25=None, embedding_model=None, reranker=None, llm=MagicMock()
    )

    mock_pdf.assert_not_called()
    mock_web.assert_called_once()
    assert sample["contexts"] == ["web content"]

@patch("src.core.services.evaluation.ragas_pipeline.rewrite_query_for_retrieval")
@patch("src.core.services.evaluation.ragas_pipeline.run_rag_chain")
@patch("src.core.services.evaluation.ragas_pipeline.retrieve_web_context")
@patch("src.core.services.evaluation.ragas_pipeline.retrieve_pdf_chunks")
def test_prepare_evaluation_sample_memory_retrieval_rewrites_query(mock_pdf, mock_web, mock_chain, mock_rewrite):
    mock_rewrite.return_value = "the reformulated query"
    mock_pdf.return_value = ([{"text": "pdf content", "metadata": {}}], "id")
    mock_chain.return_value = {"answer": "answer", "sources": []}

    history = [{"role": "user", "content": "..."}]
    prepare_evaluation_sample(
        query="What about the cheaper ones?", ground_truth="gt", mode="memory_retrieval", chunks=[], faiss_index=None,
        bm25=None, embedding_model=None, reranker=None, llm=MagicMock(), conversation_history=history
    )

    mock_rewrite.assert_called_once()
    called_query_arg = mock_pdf.call_args[0][0]
    assert called_query_arg == "the reformulated query"

def test_prepare_evaluation_sample_falls_back_to_corpus_when_no_context():
    with patch("src.core.services.evaluation.ragas_pipeline.retrieve_pdf_chunks", return_value=([], "id")), \
         patch("src.core.services.evaluation.ragas_pipeline.run_rag_chain", return_value={"answer": "answer", "sources": []}):
        chunks = [{"text": f"chunks {i}", "metadata": {}} for i in range(5)]
        sample = prepare_evaluation_sample(
            query="q", ground_truth="gt", mode="pdf_only", chunks=chunks, faiss_index=None,
            bm25=None, embedding_model=None, reranker=None, llm=MagicMock()
        )
        assert sample["contexts"] == [c["text"] for c in chunks[:3]]

@patch("src.core.services.evaluation.ragas_pipeline.run_ragas_evaluation")
@patch("src.core.services.evaluation.ragas_pipeline.setup_ragas_llm")
@patch("src.core.services.evaluation.ragas_pipeline.prepare_evaluation_sample")
def test_run_comparative_evaluation_skips_mempry_mode_without_history(mock_prepare, mock_setup_llm, mock_ragas):
    mock_prepare.return_value = {"question": "q", "answer": "a", "contexts": ["c"], "ground_truth": "gt"}
    mock_ragas.return_value = {"faithfulness": 0.8, "answer_relevancy": 0.7, "context_precision": 0.6, "n_samples": 1}

    test_cases = [{"question": "q", "ground_truth": "gt"}]

    result = run_comparative_evaluation(
        test_cases=test_cases, chunks=[], faiss_index=None, bm25=None,
        embedding_model=MagicMock(), reranker=MagicMock(), llm=MagicMock()
    )

    assert result["memory_retrieval"] is None
    assert mock_prepare.call_count == 3