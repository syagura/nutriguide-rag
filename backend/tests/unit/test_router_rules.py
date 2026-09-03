from src.core.services.router.rules import rule_based_route

def test_memory_reference_with_history():
    decision = rule_based_route("What did we just discuss?", has_conversation_history=True)
    assert decision == {"need_memory": True, "need_pdf": False, "need_web": False, "query_type": "memory_reference"}

def test_memory_reference_without_history_is_ambiguous():
    decision = rule_based_route("What did we just discuss?", has_conversation_history=False)
    assert decision is None

def test_follow_up_with_history():
    decision = rule_based_route("What about affordable ones?", has_conversation_history=True)
    assert decision == {"need_memory": True, "need_pdf": True, "need_web": False, "query_type": "follow_up"}

def test_follow_up_too_long_is_ambiguous():
    long_query = "If, for example, my child is eight months old and has an egg allergy, what should I do?"
    decision = rule_based_route(long_query, has_conversation_history=True)
    assert decision is None

def test_current_information_query():
    decision = rule_based_route("What is the latest research on creatine?")
    assert decision == {"need_memory": False, "need_pdf": False, "need_web": True, "query_type": "current_information"}
    
def test_current_information_with_history_includes_memory():
    decision = rule_based_route("Are there any recent updates on stunting?", has_conversation_history=True)
    assert decision["need_memory"] is True
    assert decision["need_web"] is True

def test_plain_pdf_question_is_ambiguous():
    decision = rule_based_route("What foods are high in protein?", has_conversation_history=False)
    assert decision is None

def test_current_info_overides_memory_reference_pattern():
    decision = rule_based_route("Has there been any recent research on creatine?", has_conversation_history=True)
    assert decision["need_web"] is True
    assert decision["query_type"] == "current_information"