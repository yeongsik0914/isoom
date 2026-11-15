"""Safety-Aware 2-Tier Semantic Cache for i-Soom.

Never caches clinical Red-Flag scenarios, numeric vitals (temperatures/ages),
or live hospital/bed queries. Only serves high-similarity static educational/app
guidance queries to achieve ultra-low latency without clinical staleness.
"""

from __future__ import annotations

import re
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

from app.services.llm_gateway import compute_local_embedding, cosine_similarity
from app.services.telemetry import telemetry

# Clinical & dynamic markers that MUST bypass semantic caching for patient safety
SAFETY_BYPASS_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?\s*(?:도|℃|개월|일|살|세|시간|분|ml|cc|mg))"
    r"|(열|고열|구토|설사|기침|경련|경기|발작|호흡|청색증|피똥|혈변|화상|절단|실신|병원|응급실|약국|주변|어디)"
)


@dataclass
class SemanticCacheEntry:
    query: str
    embedding: list[float]
    response_text: str
    created_at: float


class SafetyAwareSemanticCache:
    """Thread-safe LRU semantic cache strictly gated by clinical safety rules."""

    def __init__(
        self,
        max_entries: int = 256,
        ttl_sec: float = 3600.0,
        similarity_threshold: float = 0.94,
    ) -> None:
        self._lock = threading.Lock()
        self._entries: OrderedDict[str, SemanticCacheEntry] = OrderedDict()
        self.max_entries = max_entries
        self.ttl_sec = ttl_sec
        self.similarity_threshold = similarity_threshold

    def is_cacheable_query(
        self,
        query: str,
        session_id: Optional[str] = None,
        force_matching: bool = False,
    ) -> tuple[bool, str]:
        """Determines whether a query is purely static/non-clinical and safe to cache."""
        if force_matching:
            return False, "force_matching_live_routing"
        if session_id:
            return False, "active_patient_session"
        clean = (query or "").strip()
        if len(clean) < 4:
            return False, "too_short"
        if SAFETY_BYPASS_PATTERN.search(clean):
            return False, "clinical_or_dynamic_signal"
        return True, "safe_static"

    def lookup(
        self,
        query: str,
        session_id: Optional[str] = None,
        force_matching: bool = False,
    ) -> Optional[str]:
        cacheable, reason = self.is_cacheable_query(
            query=query, session_id=session_id, force_matching=force_matching
        )
        if not cacheable:
            telemetry.inc("semantic_cache_safety_bypass")
            return None

        q_vec = compute_local_embedding(query)
        now = time.time()
        best_key: Optional[str] = None
        best_sim = 0.0

        with self._lock:
            expired = [k for k, v in self._entries.items() if (now - v.created_at) > self.ttl_sec]
            for k in expired:
                del self._entries[k]

            for k, entry in self._entries.items():
                sim = cosine_similarity(q_vec, entry.embedding)
                if sim >= self.similarity_threshold and sim > best_sim:
                    best_sim = sim
                    best_key = k

            if best_key is not None:
                self._entries.move_to_end(best_key)
                telemetry.inc("semantic_cache_hit")
                return self._entries[best_key].response_text

        telemetry.inc("semantic_cache_miss")
        return None

    def store(
        self,
        query: str,
        response_text: str,
        session_id: Optional[str] = None,
        force_matching: bool = False,
    ) -> bool:
        cacheable, _ = self.is_cacheable_query(
            query=query, session_id=session_id, force_matching=force_matching
        )
        if not cacheable or not response_text.strip():
            return False

        clean = " ".join(query.strip().lower().split())
        entry = SemanticCacheEntry(
            query=clean,
            embedding=compute_local_embedding(clean),
            response_text=response_text,
            created_at=time.time(),
        )
        with self._lock:
            self._entries[clean] = entry
            self._entries.move_to_end(clean)
            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
        return True

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()


semantic_cache = SafetyAwareSemanticCache()
