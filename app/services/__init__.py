"""Pure Zero-LLM domain services package for MoonlightCare.

Contains:
- holiday_service: KASI public holiday and emergency surge risk analysis
- emergency_sync_service: NMC E-Gen real-time bed ingestion, notice NLP, and Hash Diffing Firestore sync
- spatial_service: Haversine spherical distance calculation and proximity ranking
"""

from app.services.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitBreakerOpenException,
    CircuitState,
    default_egen_circuit_breaker,
)
from app.services.emergency_sync_service import (
    PEDIATRIC_BLOCK_PATTERN,
    BedStateHashCache,
    default_hash_cache,
    fetch_emergency_beds,
    get_cached_emergency_beds,
    get_stale_in_memory_beds,
    resolve_fallback_hierarchy,
    sync_to_firestore,
)
from app.services.holiday_service import HolidayService, get_kasi_holiday_info
from app.services.pairing_service import (
    find_nearby_pairings,
    load_nationwide_pairings,
)
from app.services.spatial_service import (
    haversine_distance,
    rank_emergency_hospitals,
)

__all__ = [
    "HolidayService",
    "get_kasi_holiday_info",
    "haversine_distance",
    "rank_emergency_hospitals",
    "find_nearby_pairings",
    "load_nationwide_pairings",
    "PEDIATRIC_BLOCK_PATTERN",
    "BedStateHashCache",
    "default_hash_cache",
    "fetch_emergency_beds",
    "get_cached_emergency_beds",
    "get_stale_in_memory_beds",
    "resolve_fallback_hierarchy",
    "sync_to_firestore",
    "AsyncCircuitBreaker",
    "CircuitBreakerOpenException",
    "CircuitState",
    "default_egen_circuit_breaker",
]

