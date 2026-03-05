import fitz
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def load_pdf(file_path: str) -> list[dict]:
    """
    Load one PDF file and extract text per page.

    Args:
        file_path: Path to the PDF file to be loaded

    Returns:
        List of dict, each containing 'text' and 'metadata' (source, page)

    Raises:
        FileNotFoundError: if the file is not found
        ValueError: if the file is not a PDF
    """
    path = Path(file_path)

    if not path.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File not found: {path}")
    
    if path.suffix.lower() != ".pdf":
        logger.error(f"Not a PDF file: {path}")
        raise ValueError(f"Not a PDF file: {path}")
    
    pages = []

    with fitz.open(str(path)) as doc:
        logger.info(f"Open PDF: {path.name} ({len(doc)} page)")

        for page_num, page in enumerate(doc):
            text = page.get_text()

            if len(text.strip()) < 50:
                logger.warning(
                    f"Page {page_num + 1} skipped - "
                    f"content is too short ({len(text.strip())} character)"
                )
                continue

            pages.append({
                "text": text,
                "metadata": {
                    "source": path.name,
                    "page": page_num + 1
                }
            })
    
    logger.info(f"Finish load {path.name}: {len(pages)} page successfully extracted")
    return pages

def load_all_pdfs(data_dir: str) -> list[dict]:
    """
    Load all PDF files from a folder recursively

    Args:
        data_dir: Path to the folder containing the PDF files

    Returns:
        List of combained dictionaries from all PDFs, same format as load_pdf()
    """
    dir_path = Path(data_dir)

    pdf_files = list(dir_path.glob("**/*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files found in: {data_dir}")
        return []
    
    logger.info(f"Founded {len(pdf_files)} PDF file in {data_dir}")

    all_pages = []
    for pdf_file in pdf_files:
        try:
            pages = load_pdf(str(pdf_file))
            all_pages.extend(pages)
        except Exception as e:
            logger.error(f"Failed load {pdf_file.name}: {e}")
            continue

    logger.info(f"Total pages successfully loaded from all PDFs: {len(all_pages)}")
    return all_pages