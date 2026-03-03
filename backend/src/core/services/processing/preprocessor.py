import re
import logging

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean raw text extracted from PDF.

    Args:
        text: Raw text from pdf_loader

    Returns:
        Cleaned and normalized text
    """
    text = re.sub(r"[^\S\n]+", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)

    return text.strip()

def is_meaningful(text: str, min_words: int = 10) -> bool:
    """
    Check whether the text has enough content to be processed further.

    Args:
        text: Cleaned text
        min_words: Minimum number of words to be considered meaningful (default: 10)

    Returns:
        True if text is meaningful, False if not
    """
    word_count = len(text.split())
    return word_count >= min_words

def preprocess_pages(pages: list[dict]) -> list[dict]:
    """
    Cleans and filters extracted PDF pages.

    Args:
        pages:  List of pages from load_pdf(), each containing ‘text’ and ‘metadata’

    Returns:
        List of clean, meaningful pages, ready for the chunker
    """
    logger.info(f"Start preprocessing {len(pages)} pages")

    cleaned_pages = []
    skipped = 0

    for page in pages:
     
        cleaned_text = clean_text(page["text"])

        if not is_meaningful(cleaned_text):
            logger.warning(
                f"Page {page['metadata']['page']} from {page['metadata']['source']} "
                f"skip after cleaning - content is not meaningful enough"
            )
            skipped += 1
            continue

        cleaned_pages.append({
            "text": cleaned_text,
            "metadata": page["metadata"]
        })

    logger.info(
        f"Preprocessing finish: {len(cleaned_pages)} pages preocessed, "
        f"{skipped} pages skipped"
    )

    return cleaned_pages