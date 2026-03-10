import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path
from src.core.services.evaluation.report_generator import generate_report, _interpret_scores

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