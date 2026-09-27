from src.core.prompts.templates import build_conversation_block, build_pdf_block, build_web_block, build_rag_prompt

def test_build_conversation_block_empty_when_no_history():
    assert build_conversation_block(None) == ""
    assert build_conversation_block([]) == ""

def test_build_conversation_block_formats_roles():
    history = [{"role": "user", "content": "Halo"}, {"role": "assistant", "content": "Hai!"}]
    block = build_conversation_block(history)
    assert block.startswith("[CONVERSATION CONTEXT]")
    assert "User: Halo" in block
    assert "Assistant: Hai!" in block

def test_build_pdf_block_empty_when_no_chunks():
    assert build_pdf_block([]) == ""

def test_build_pdf_block_includes_source_and_page():
    chunks = [{"text": "Zat besi penting untuk bayi", "metadata": {"source": "Pedoman Gizi.pdf", "page": 12}}]
    block = build_pdf_block(chunks)
    assert block.startswith("[PDF SOURCE]")
    assert "Pedoman Gizi.pdf, page 12" in block

def test_build_web_block_includes_title_and_url():
    chunks = [{"text": "WHO merekomendasikan ASI ekslusif", "metadata": {"source": "https://who.int/asrtikel", "title": "Breastfeeding Guide"}}]
    block = build_web_block(chunks)
    assert block.startswith("[WEB SOURCE]")
    assert "Breastfeeding Guide" in block
    assert "https://who.int/artikel" in block

def test_build_rag_prompt_combines_all_blocks_in_order():
    prompt =  build_rag_prompt(
        query="Apa makanan tinggi zat besi?",
        pdf_chunks=[{"text": "pdf content", "metadata": {"source": "a.pdf", "page": 1}}],
        web_chunks=[{"text": "web content", "metadata": {"source": "https://who.int/x", "title": "Title"}}],
        conversation_history=[{"role": "user", "content": "halo"}]
    )
    assert prompt.index("[CONVERSATION CONTEXT]") < prompt.index("[PDF SOURCE]") < prompt.index("[WEB SOURCE]")
    assert "Apa makanan tinggi zat besi?" in prompt

def test_build_rag_prompt_omits_empty_blocks():
    prompt = build_rag_prompt(query="test", pdf_chunks=[], web_chunks=[], conversation_history=None)
    assert "[CONVERSATION CONTEXT]" not in prompt
    assert "[PDF SOURCE]" not in prompt
    assert "[WEB SOURCE]" not in prompt