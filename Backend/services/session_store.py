from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import RLock
from uuid import uuid4

import pandas as pd

from core.settings import settings
from services.memory_manager import MemoryManager


@dataclass
class SessionState:
    session_id: str
    df: pd.DataFrame | None = None
    stats: dict | None = None
    report: dict | None = None
    quality: dict | None = None
    insights: dict | None = None
    upload_name: str | None = None
    memory: MemoryManager = field(default_factory=MemoryManager)
    model_cache: dict = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
        + timedelta(minutes=settings.SESSION_TTL_MINUTES)
    )

    def touch(self):
        self.expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.SESSION_TTL_MINUTES
        )


class SessionStore:
    def __init__(self):
        self._sessions: dict[str, SessionState] = {}
        self._lock = RLock()

    def _prune_expired(self):
        now = datetime.now(timezone.utc)
        expired = [
            session_id
            for session_id, state in self._sessions.items()
            if state.expires_at <= now
        ]
        for session_id in expired:
            self._sessions.pop(session_id, None)

    def create_or_replace(
        self,
        *,
        df: pd.DataFrame,
        stats: dict,
        report: dict,
        quality: dict,
        insights: dict,
        upload_name: str | None = None,
    ) -> SessionState:
        with self._lock:
            self._prune_expired()
            state = SessionState(
                session_id=str(uuid4()),
                df=df,
                stats=stats,
                report=report,
                quality=quality,
                insights=insights,
                upload_name=upload_name,
            )
            self._sessions[state.session_id] = state
            return state

    def get(self, session_id: str | None) -> SessionState | None:
        if not session_id:
            return None

        with self._lock:
            self._prune_expired()
            state = self._sessions.get(session_id)
            if state is not None:
                state.touch()
            return state


session_store = SessionStore()
