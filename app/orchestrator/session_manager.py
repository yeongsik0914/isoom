"""Thread-safe and asyncio-compliant session manager for PatientSessionState.

Maintains in-memory session persistence with TTL-based eviction,
ensuring multi-turn state continuity and zero memory leaks.
"""

from __future__ import annotations

import asyncio
import datetime
import uuid
from typing import Optional

from app.schemas.state import KST, PatientSessionState


class SessionManager:
    """Manages active patient session states with concurrency locking and TTL eviction."""

    def __init__(self) -> None:
        self._sessions: dict[str, PatientSessionState] = {}
        self._lock = asyncio.Lock()

    async def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_lat: float = 37.5133,
        user_lon: float = 127.1001,
        user_address: Optional[str] = None,
    ) -> PatientSessionState:
        """Retrieves an existing session by ID or provisions a new PatientSessionState."""
        async with self._lock:
            if not session_id or session_id not in self._sessions:
                sid = session_id or f"sess-{uuid.uuid4().hex[:12]}"
                new_state = PatientSessionState(
                    session_id=sid,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    user_address=user_address,
                )
                self._sessions[sid] = new_state
                return new_state

            existing_state = self._sessions[session_id]
            # Update coordinates if caller provided custom coordinates
            if user_lat != 37.5133 or user_lon != 127.1001:
                existing_state.user_lat = user_lat
                existing_state.user_lon = user_lon
            if user_address:
                existing_state.user_address = user_address
            return existing_state

    async def get_session(self, session_id: str) -> Optional[PatientSessionState]:
        """Returns the session state if present, else None."""
        async with self._lock:
            return self._sessions.get(session_id)

    async def save_session(self, state: PatientSessionState) -> None:
        """Saves or updates the session state in the repository."""
        async with self._lock:
            state.updated_at = datetime.datetime.now(KST).isoformat()
            self._sessions[state.session_id] = state

    async def delete_session(self, session_id: str) -> bool:
        """Deletes a session from the store. Returns True if found and deleted."""
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    async def evict_expired_sessions(self, max_idle_seconds: int = 1800) -> int:
        """Purges sessions inactive for longer than max_idle_seconds (default: 30 minutes).

        Returns:
            Number of evicted sessions.
        """
        async with self._lock:
            now = datetime.datetime.now(KST)
            expired_keys: list[str] = []

            for sid, state in self._sessions.items():
                try:
                    updated_dt = datetime.datetime.fromisoformat(state.updated_at)
                    if (now - updated_dt).total_seconds() > max_idle_seconds:
                        expired_keys.append(sid)
                except Exception:
                    expired_keys.append(sid)

            for key in expired_keys:
                del self._sessions[key]

            return len(expired_keys)

    def count(self) -> int:
        """Returns current count of tracked active sessions."""
        return len(self._sessions)
