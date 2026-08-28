import time
import uuid
import logging
from threading import Lock

logger =  logging.getLogger(__name__)

class SessionStore:
    """
    In-memory ephemeral session store for conversational context.

    Not persisted to disk and not shared across multiple backend workers/instances.
    Session expire via lazy TTL cleanup (checked on access) - no background
    thread/scheduler needed for the MVP
    """

    def __init__(self, ttl_seconds: int = 1800, max_messages: int = 10):
        self._sessions: dict[str, dict] = {}
        self._lock = Lock()
        self.ttl_seconds = ttl_seconds
        self.max_messages = max_messages

    def _is_expired(self, session: dict) -> bool:
        return (time.time() - session["last_seen"]) > self.ttl_seconds

    def _cleanup_expired(self) -> None:
        expired_ids = [sid for sid, s in self._sessions.items() if self._is_expired(s)]
        for sid in expired_ids:
            del self._sessions[sid]
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired session(s)")

    def get_or_create(self, session_id:str | None) -> str:
        """Return an existing valid session_id, or create a new one"""
        with self._lock:
            self._cleanup_expired()

            if session_id and session_id in self._sessions:
                return session_id

            new_id = session_id if session_id else str(uuid.uuid4())
            self._sessions[new_id] = {
                "messages": [],
                "created_at": time.time(),
                "last_seen": time.time()
            }
            logger.info(f"Created new session: {new_id}")
            return new_id

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Append a message and trim history to max_messages (most recent kept)."""
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return
            session["messages"].append({"role": role, "content": content})
            session["messages"] = session["messages"][-self.max_messages:]
            session["last_seen"] = time.time()

    def get_recent_messages(self, session_id: str) -> list[dict]:
        with self._lock:
            session = self._sessions.get(session_id)
            return list(session["messages"]) if session else []

session_store = SessionStore()