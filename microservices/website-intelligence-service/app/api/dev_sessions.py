import logging
import threading
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DevSessionManager:
    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._lock = threading.Lock()

    def create(self, url: str, title: str, summary: str, tags: list[str], content: str) -> str:
        session_id = uuid.uuid4().hex[:12]
        session = {
            "session_id": session_id,
            "url": url,
            "title": title,
            "summary": summary,
            "tags": tags,
            "content": content,
            "published": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with self._lock:
            self._sessions[session_id] = session
        logger.info("Dev session %s created for %s", session_id, url)
        return session_id

    def get(self, session_id: str) -> dict | None:
        with self._lock:
            return self._sessions.get(session_id)

    def list_sessions(self) -> list[dict]:
        with self._lock:
            return [
                {
                    "session_id": s["session_id"],
                    "url": s["url"],
                    "title": s["title"],
                    "published": s["published"],
                    "created_at": s["created_at"],
                }
                for s in reversed(list(self._sessions.values()))
            ]

    def publish(self, session_id: str) -> bool:
        with self._lock:
            session = self._sessions.get(session_id)
            if session and not session["published"]:
                session["published"] = True
                logger.info("Dev session %s published", session_id)
                return True
            return False


dev_sessions = DevSessionManager()
