import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def generate_report(scores: dict, output_dir: str = 'storage/evaluation') -> str:
    """
    Generate and save a JSON evaluation report from RAGAS scores.

    Args:
        scores: Dict containing RAGAS metric scores from run_ragas_evaluation()
        output_dir: Directory to save the report (default: storage/evaluation)

    Returns:
        Path to the saved report file as a string
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_path / f"evaluation_report_{timestamp}.json"

    report = {
        "timestamp": timestamp,
        "scores": scores,
        "interpretation": _interpret_scores(scores)
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Evaluation report saved to {report_file}")
    return str(report_file)

def _interpret_scores(scores: dict) -> dict:
    """
    Provide human-readable interpretation of RAGAS scores.

    Args:
        scores: Dict containing RAGAS metric scores

    Returns:
        Dict with interpretation string for each metric
    """
    thresholds = {
        "faithfulness": (0.7, "Good - LLM answer are well-grounded in the documents"),
        "answer_relevancy": (0.7, "Good - answer are relevenat to user questions"),
        "context_precision": (0.7, "Goog - retrieved chunks are precise and relevant")
    }

    interpretation = {}
    for metric, (threshold, good_msg) in thresholds.items():
        if metric not in scores:
            continue

        score = scores[metric]
        if score >= threshold:
            interpretation[metric] = f" {good_msg} (score: {score})"
        else:
            interpretation[metric] = f" Needs inprovement (score: {score})"

    return interpretation

def generate_comparative_report(all_scores: dict, output_dir: str = "storage/evaluation") -> str:
    """
    Generate and save a JSON report comparing RAGAS scores across 4 retrieval modes
    (PDF-only/Web-only/Hybrid/Memory + Retrieval)

    Args:
        all_scores: Dict{mode:scores_dict_or_None} from run_comparative_evaluation()
        output_dir: Directoru where the report will be saved
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_path / f"comparative_evaluation_{timestamp}.json"

    report = {
        "timestamp": timestamp,
        "modes": {
            mode: {
                "scores": scores,
                "interpretation": _interpret_scores(scores) if scores else None
            }
            for mode, scores in all_scores.items()
        },
        "comparison_summary": _build_comparison_summary(all_scores)
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Comparative evaluation report saved to {report_file}")
    return str(report_file)

def _build_comparison_summary(all_scores: dict) -> dict:
    """
    Rankings by metric across modes, so it's easy to see which mode perfoms
    best on which metric without having to dig into the raw data one by one.
    """
    metrics = ["faithfulness", "answer_relevancy", "context_precision"]
    summary = {}
    for metric in metrics:
        ranked = sorted(
            ((mode, scores[metric]) for mode, scores in all_scores.items() if scores),
            key=lambda x: x[1],
            reverse=True
        )
        summary[metric] = [{"mode": mode, "score": score} for mode, score in ranked]
    return summary