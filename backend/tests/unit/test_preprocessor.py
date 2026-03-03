from src.core.services.processing.preprocessor import clean_text, is_meaningful, preprocess_pages

def test_clean_text_delete_whitespace():
    # Tab dan spasi ganda harus jadi spasi tunggal 
    text = "ini teks\tdengan spasi\tberlebih"
    result = clean_text(text)
    assert "\t" not in result
    assert "  " not in result

def test_clean_text_normalize_new_line():
    # 3 baris kosong berturut-turut harus harus jadi 2
    text = "paragraf satu\n\n\n\nparagraf dua"
    result = clean_text(text)
    assert "\n\n\n" not in result

def test_is_meaningful_just_world():
    # 10 kata atau lebih dianggap meaningful 
    text = "anak usia enam bulan membutuhkan asupan zat besi yang cukup setiap harinya"
    assert is_meaningful(text) is True

def test_is_meaningful_no_enough_kata():
    # Kurang dari 10 kata dianggap tidak meaningful 
    text = "halaman kosong"
    assert is_meaningful(text) is False

def test_preprocess_pages_skip_tidak_bermakna():
    # Halaman yang gak bermakna harus di-skip, yang bermakna harus lolos
    pages = [
        {"text": "teks pendek", "metadata": {"source": "test.pdf", "page": 1}},
        {"text": "anak usia enam bulan membutuhkan asupan zat besi yang cukup setiap harinya",
         "metadata": {"source": "test.pdf", "page": 2}},
    ]
    result = preprocess_pages(pages)

    # Hanya 1 halaman yang lolos (halaman 2)
    assert len(result) == 1
    assert result[0]["metadata"]["page"] == 2

def test_preprocess_pages_metadata_tetap():
    # Metadata harus ikut terbawa, jangan hilang setelah preprocessing
    pages = [
        {"text": "anak usia enam bulan membutuhkan asupan zat besi yang cukup setiap harinya",
         "metadata": {"source": "who_guidelines.pdf", "page": 5}},
    ]
    result = preprocess_pages(pages)
    assert result[0]["metadata"]["source"] == "who_guidelines.pdf"
    assert result[0]["metadata"]["page"] == 5