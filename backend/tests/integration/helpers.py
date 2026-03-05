import fitz

def create_dummy_pdf(output_path: str, n_pages: int = 3) -> None:
    """
    Create a dummy PDF file with meaningful text content for testing.

    Args:
        output_path: Path where the PDF will be saved
        n_pages: Number of pages to generate (default: 3)
    """
    doc = fitz.open()

    for i in range(n_pages):
        page = doc.new_page()
        text = (
            f"Halaman {i + 1}: Panduan gizi anak menurut WHO dan Kemenkes RI. "
            f"Anak usia enam bulan membutuhkan asupan zat besi yang cukup dari MPASI. "
            f"Stunting dapat dicegah dengan pemberian nutrisi yang tepat sejak dini. "
            f"Pemantauan berat badan secara rutin sangat dianjurkan oleh tenaga kesehatan. "
        )
        page.insert_text((50, 50), text)

    doc.save(output_path)
    doc.close()