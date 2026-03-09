import logging
import sys
from pathlib import Path

# Path to logs folder - relative path from backend root
LOG_DIR = Path(__file__).resolve().parent.parent.parent.parent / "logs"

def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure application-wide logging with console and file handlers.

    Args:
        level: Logging level to use (default: logging.INFO)
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger 
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console Handler
            logging.StreamHandler(sys.stdout),
            # File Handler
            logging.FileHandler(LOG_DIR / "nutriguide.log", encoding="utf-8")
        ]
    )