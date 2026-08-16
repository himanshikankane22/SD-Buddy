"""In-memory session store (single-demo scale).

In production this would be a Redis/DB-backed store; here it lives in RAM.
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field


@dataclass
class Session:
    id: str
    role: str = "end_user"
    channel: str = "chat"
    history: list[dict] = field(default_factory=list)  # [{"role","content"}]
    active_flow: str | None = None
    flow_state: dict | None = None
    flow_started_at: str | None = None
    ticket: dict | None = None
    context: dict = field(default_factory=dict)

    @property
    def flow_label(self) -> str | None:
        from .flows.router import flow_meta

        if self.active_flow:
            meta = flow_meta(self.active_flow)
            if meta:
                return meta["label"]
        return None


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = threading.Lock()

    def create(self, role: str = "end_user", channel: str = "chat") -> Session:
        with self._lock:
            session = Session(id=uuid.uuid4().hex[:12], role=role, channel=channel)
            self._sessions[session.id] = session
            return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            return self._sessions.get(session_id)

    def get_or_create(self, session_id: str, role: str = "end_user", channel: str = "chat") -> Session:
        session = self.get(session_id)
        if session is None:
            return self.create(role, channel)
        return session

    def list(self) -> list[Session]:
        with self._lock:
            return list(self._sessions.values())


_store = SessionStore()


def get_store() -> SessionStore:
    return _store
