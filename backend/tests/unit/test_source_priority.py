from src.core.services.web.source_priority import get_domain_tier, sort_by_source_tier, get_source_label

TIER_MAP = {"who.int": 1, "mayoclinic.org": 2, "alodokter": 3}

def test_get_domain_tier_exact_match():
    assert get_domain_tier("https://who.int/artikel", TIER_MAP) == 1

def test_get_domain_tier_subdomain_match():
    assert get_domain_tier("https://www.who.int/artikel", TIER_MAP) == 1

def test_get_domain_tier_unknown_domain_falls_back_to_default():
    assert get_domain_tier("https://random.com/artikel", TIER_MAP) == 4

def test_sort_by_source_tier_orders_ascending():
    chunks = [
        {"text": "a", "metadata": {"source" : "https://alodokter.com/a"}},
        {"text": "b", "metadata": {"source" : "https://who.int/b"}},
        {"text": "c", "metadata": {"source" : "https://mayoclinic.org/c"}},
    ]
    sorted_chunks = sort_by_source_tier(chunks, TIER_MAP)
    assert [c["metadata"]["source_tier"] for c in sorted_chunks] == [1, 2, 3]
    assert sorted_chunks[0]["text"] == "b"

def test_sort_by_source_tier_preserves_order_within_same_tier():
    chunks = [
        {"text": "first", "metadata": {"source": "https://who.int/a"}},
        {"text": "second", "metadata": {"source": "https://cdc.gov/b"}},
    ]
    tier_map = {"who.int": 1, "cdc.gov": 1}
    sorted_chunks = sort_by_source_tier(chunks, tier_map)
    assert [c["text"] for c in sorted_chunks] == ["first", "second"]

def test_get_source_label_known_domain():
    label = get_source_label("https://who.int/article-about-iron", "Iron Requirements in Infants")
    assert label == "WHO - Iron Requirementd in Infants"

def test_get_source_label_unknown_domain_falls_back_to_netloc():
    label = get_source_label("https://random-blog.com/artikel", "Articel Title")
    assert label == "random-blog.com - Article Title"