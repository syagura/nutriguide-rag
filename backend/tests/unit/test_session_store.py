import time
from src.core.services.memory.session_store import SessionStore

def test_get_or_create_generates_new_session_id():
    store = SessionStore()
    session_id = store.get_or_create(None)
    assert isinstance(session_id, str)
    assert len(session_id) > 0

def test_get_or_create_reuses_existing_session_id():
    store = SessionStore()
    first_id = store.get_or_create(None)
    second_id = store.get_or_create(first_id)
    assert first_id == second_id

def test_get_or_create_unknown_id_creates_new_session():
    store = SessionStore()
    session_id = store.get_or_create("an-ID-that-has-never-existed")
    assert session_id == 'an-ID-that-has-never-existed'
    assert store.get_recent_messages(session_id) == []

def test_add_message_and_get_recent_messages():
    store = SessionStore()
    session_id = store.get_or_create(None)

    store.add_message(session_id, "user", "When should I start MPASI")
    store.add_message(session_id, "assistant", "MPASI are introduced at 6 months of age.")

    messages = store.get_recent_messages(session_id)
    assert len(messages) == 2
    assert messages[0] == {"role": "user", "content": "When should I start MPASI"}
    assert messages[1]["role"] == "assistant"

def test_add_message_trims_to_max_messages():
    store = SessionStore(max_messages=2)
    session_id = store.get_or_create(None)

    store.add_message(session_id, "user", "message 1")
    store.add_message(session_id, "assistant", "message 2")
    store.add_message(session_id, "user", "message 3")

    messages = store.get_recent_messages(session_id)
    assert len(messages) == 2
    assert messages[0]["content"] == "message 2"
    assert messages[1]["content"] == "message 3"

def test_get_recent_messages_on_unknown_session_returns_empty():
    store = SessionStore()
    assert store.get_recent_messages("nonexistent-session") == []

def test_session_expires_after_ttl():
    store = SessionStore(eel_seconds=0.05)
    session_id = store.get_or_create(None)
    store.add_message(session_id, "user", "hallo")

    time.sleep(0.1)

    new_id = store.get_or_create(session_id)
    assert store.get_recent_messages(new_id) == []

def test_add_message_on_unknown_session_does_nothing():
    store = SessionStore()
    store.add_message("nonexistent-session", "user", "test")
    assert store.get_recent_messages("nonexistent-session") == []