"""Thread-safe and asyncio-compliant session manager for PatientSessionState.

Supports pluggable storage backends:
- InMemorySessionStore (default for local dev & unit tests)
- FirestoreSessionStore (for multi-instance Cloud Run horizontal scaling, via SESSION_STORE_BACKEND=firestore)
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import os
import uuid
from typing import Optional, Protocol

from app.schemas.state import KST, PatientSessionState

logger = logging.getLogger(__name__)


class SessionStore(Protocol):
    """Storage backend interface for PatientSessionState persistence."""

    async def get(self, session_id: str) -> Optional[PatientSessionState]: ...
    async def save(self, state: PatientSessionState) -> None: ...
    async def delete(self, session_id: str) -> bool: ...
    async def evict_expired(self, max_idle_seconds: int) -> int: ...
    def count(self) -> int: ...


class InMemorySessionStore:
    """Process-local in-memory session repository with TTL eviction."""

    def __init__(self) -> None:
        self._sessions: dict[str, PatientSessionState] = {}

    async def get(self, session_id: str) -> Optional[PatientSessionState]:
        return self._sessions.get(session_id)

    async def save(self, state: PatientSessionState) -> None:
        self._sessions[state.session_id] = state

    async def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    async def evict_expired(self, max_idle_seconds: int) -> int:
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
        return len(self._sessions)


class FirestoreSessionStore:
    """Firestore-backed session repository enabling multi-instance Cloud Run scaling."""

    def __init__(self, collection_name: str = "patient_sessions") -> None:
        self.collection_name = collection_name
        self._fallback = InMemorySessionStore()

    def _get_collection(self):
        from app.config import get_firestore_client

        client = get_firestore_client()
        return client.collection(self.collection_name)

    async def get(self, session_id: str) -> Optional[PatientSessionState]:
        try:
            def _fetch():
                doc = self._get_collection().document(session_id).get()
                return doc.to_dict() if doc.exists else None

            data = await asyncio.to_thread(_fetch)
            if data:
                return PatientSessionState.model_validate(data)
            return None
        except Exception as e:
            logger.warning(f"[SessionStore] Firestore get fallback to memory: {e}")
            return await self._fallback.get(session_id)

    async def save(self, state: PatientSessionState) -> None:
        payload = state.model_dump()
        try:
            def _write():
                self._get_collection().document(state.session_id).set(payload)

            await asyncio.to_thread(_write)
        except Exception as e:
            logger.warning(f"[SessionStore] Firestore save fallback to memory: {e}")
            await self._fallback.save(state)

    async def delete(self, session_id: str) -> bool:
        try:
            def _remove() -> bool:
                doc_ref = self._get_collection().document(session_id)
                snap = doc_ref.get()
                if not snap.exists:
                    return False
                doc_ref.delete()
                return True

            return await asyncio.to_thread(_remove)
        except Exception as e:
            logger.warning(f"[SessionStore] Firestore delete fallback to memory: {e}")
            return await self._fallback.delete(session_id)

    async def evict_expired(self, max_idle_seconds: int) -> int:
        cutoff = (datetime.datetime.now(KST) - datetime.timedelta(seconds=max_idle_seconds)).isoformat()
        try:
            def _evict() -> int:
                docs = self._get_collection().where("updated_at", "<", cutoff).stream()
                deleted = 0
                for doc in docs:
                    doc.reference.delete()
                    deleted += 1
                return deleted

            return await asyncio.to_thread(_evict)
        except Exception as e:
            logger.warning(f"[SessionStore] Firestore eviction fallback to memory: {e}")
            return await self._fallback.evict_expired(max_idle_seconds)

    def count(self) -> int:
        return self._fallback.count()


def _create_default_store() -> SessionStore:
    backend = os.getenv("SESSION_STORE_BACKEND", "memory").strip().lower()
    if backend == "firestore":
        return FirestoreSessionStore()
    return InMemorySessionStore()


class SessionManager:
    """Manages active patient session states with concurrency locking and TTL eviction."""

    def __init__(self, store: Optional[SessionStore] = None) -> None:
        self._store: SessionStore = store or _create_default_store()
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
            existing_state = await self._store.get(session_id) if session_id else None
            if existing_state is None:
                sid = session_id or f"sess-{uuid.uuid4().hex[:12]}"
                new_state = PatientSessionState(
                    session_id=sid,
                    user_lat=user_lat,
                    user_lon=user_lon,
                    user_address=user_address,
                )
                await self._store.save(new_state)
                return new_state

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
            return await self._store.get(session_id)

    async def save_session(self, state: PatientSessionState) -> None:
        """Saves or updates the session state in the repository."""
        async with self._lock:
            state.updated_at = datetime.datetime.now(KST).isoformat()
            await self._store.save(state)

    async def delete_session(self, session_id: str) -> bool:
        """Deletes a session from the store. Returns True if found and deleted."""
        async with self._lock:
            return await self._store.delete(session_id)

    async def evict_expired_sessions(self, max_idle_seconds: int = 1800) -> int:
        """Purges sessions inactive for longer than max_idle_seconds (default: 30 minutes)."""
        async with self._lock:
            return await self._store.evict_expired(max_idle_seconds)

    def count(self) -> int:
        """Returns current count of tracked active sessions."""
        return self._store.count()
