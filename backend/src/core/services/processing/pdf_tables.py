import logging

logger = logging.getLogger(__name__)

def format_table(table: list[list[str | None]]) -> str:
    rows = []
    for row in table:
        cells = [(c or "").strip() for c in row]
        rows.append(" | ".join(cells))
    return "\n".join(rows)

def extract_page_tables_text(plumber_page) -> str:
    try:
        tables = plumber_page.extract_tables()
    except Exception as e:
        logger.warning(f"Table extraction failed on a page: {e}")
        return ""

    if not tables:
        return ""

    formatted = [format_table(t) for t in tables if t]
    if not formatted:
        return ""

    return "\n\n[TABLE]\n" + "\n\n[TABLE]\n".join(formatted)