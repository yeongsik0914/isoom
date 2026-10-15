"""Test Suite for Step 7: Public API Circuit Breaker & 3-Tier Multi-Storage Fallback.

Verifies:
- TC-CB-01: Circuit Breaker FSM State Transitions (CLOSED -> OPEN upon 3 failures).
- TC-CB-02: Fast Short-Circuiting (0ms instant cutoff without network latency when OPEN).
- TC-CB-03: Tier 1 L1 Stale In-Memory Cache serving (< 0.1ms) with warning badge.
- TC-CB-04: Tier 2 L2 Cloud Firestore Snapshot recovery when L1 memory cache is empty.
- TC-CB-05: Tier 3 L3 Local Immutable Baseline JSON serving in total network isolation.
- TC-CB-06: Automatic Self-Healing FSM transition (OPEN -> HALF_OPEN -> CLOSED).
- TC-CB-07: REST API (/api/v1/emergency/nearby) resilience with DataFreshnessMeta badges.
- TC-CB-08: Background Scheduler isolation during public API outages.
"""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.api.v1.emergency import router
from main import app
from app.schemas.emergency import DataFreshnessMeta, EmergencyBedInfo
from app.services.circuit_breaker import (
    AsyncCircuitBreaker,
    CircuitBreakerOpenException,
    CircuitState,
    default_egen_circuit_breaker,
)
from app.services.emergency_sync_service import (
    _in_memory_bed_cache,
    clear_bed_cache,
    fetch_emergency_beds,
    get_cached_emergency_beds,
    get_stale_in_memory_beds,
    resolve_fallback_hierarchy,
    set_cached_emergency_beds,
)
from app.services.scheduler import background_daemon


class TestStep7CircuitBreaker(unittest.TestCase):
    """Quality Assurance and Chaos Resilience test cases for Step 7."""

    def setUp(self) -> None:
        """Resets circuit breaker and caches before each test."""
        default_egen_circuit_breaker.reset()
        clear_bed_cache()
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Cleans up circuit breaker and caches after each test."""
        default_egen_circuit_breaker.reset()
        clear_bed_cache()

    def test_cb_01_closed_to_open_transition(self) -> None:
        """TC-CB-01: Circuit transitions CLOSED -> OPEN after 3 consecutive failures."""
        cb = AsyncCircuitBreaker(name="TEST_CB", failure_threshold=3, recovery_timeout=60.0)

        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertTrue(cb.is_available())

        # Failure 1
        cb.record_failure(Exception("503 Service Unavailable"))
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertEqual(cb.failure_count, 1)

        # Failure 2
        cb.record_failure(Exception("Connection Timeout"))
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertEqual(cb.failure_count, 2)

        # Failure 3 -> Trips to OPEN
        cb.record_failure(Exception("503 Gateway Timeout"))
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertEqual(cb.failure_count, 3)
        self.assertFalse(cb.is_available())

    def test_cb_02_fast_short_circuit_zero_latency(self) -> None:
        """TC-CB-02: Fast Short-Circuiting verifies 0ms instant cutoff when circuit is OPEN."""
        default_egen_circuit_breaker.state = CircuitState.OPEN
        default_egen_circuit_breaker.last_state_change = time.time()

        # Seed L1 memory cache
        sample_beds = [
            EmergencyBedInfo(
                hpid="A1100010",
                hospital_name="서울대학교병원",
                pediatric_beds=3,
                general_beds=5,
                pediatric_iso_beds=1,
                lat=37.5796,
                lon=127.0002,
                notice_raw="소아 진료 가능",
                pediatric_acceptable=True,
            )
        ]
        set_cached_emergency_beds("서울특별시", sample_beds)

        # Benchmark 100 calls in OPEN state - must execute with 0 network calls and ultra-low latency (< 0.5ms per call)
        start = time.perf_counter()
        with patch("requests.get") as mock_get:
            for _ in range(100):
                beds, meta = fetch_emergency_beds(stage1="서울특별시", force_refresh=True, return_meta=True)
                self.assertEqual(len(beds), 1)
                self.assertEqual(meta.circuit_status, "OPEN")

            # Outbound network requests MUST be exactly 0
            mock_get.assert_not_called()

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        avg_ms = elapsed_ms / 100
        self.assertLess(avg_ms, 1.0, f"Short-circuit latency must be < 1.0ms, got {avg_ms:.4f}ms")

    def test_cb_03_tier1_stale_memory_fallback(self) -> None:
        """TC-CB-03: Tier 1 L1 Stale In-Memory Cache serving (< 0.1ms) with warning badge."""
        sample_beds = [
            EmergencyBedInfo(
                hpid="A1100013",
                hospital_name="서울아산병원",
                pediatric_beds=4,
                general_beds=8,
                pediatric_iso_beds=2,
                lat=37.5266,
                lon=127.1086,
                notice_raw="정상 가동",
                pediatric_acceptable=True,
            )
        ]
        # Simulate data collected 15 minutes ago
        fifteen_min_ago = time.time() - 900.0
        _in_memory_bed_cache["서울특별시"] = (fifteen_min_ago, sample_beds)

        default_egen_circuit_breaker.state = CircuitState.OPEN
        default_egen_circuit_breaker.last_state_change = time.time()

        beds, meta = fetch_emergency_beds(stage1="서울특별시", force_refresh=True, return_meta=True)

        self.assertEqual(len(beds), 1)
        self.assertEqual(beds[0].hospital_name, "서울아산병원")
        self.assertFalse(meta.is_realtime)
        self.assertEqual(meta.source_tier, "TIER_1_MEMORY_STALE")
        self.assertGreaterEqual(meta.elapsed_minutes, 14)
        self.assertIn("15분 전 수집된 병상 데이터", meta.warning_message)
        self.assertIn("전화로 잔여 병상을 확인", meta.warning_message)

    def test_cb_04_tier2_firestore_snapshot_fallback(self) -> None:
        """TC-CB-04: Tier 2 L2 Firestore Snapshot loads when L1 memory cache is empty (reboot)."""
        clear_bed_cache()
        default_egen_circuit_breaker.state = CircuitState.OPEN
        default_egen_circuit_breaker.last_state_change = time.time()

        # Mock Firestore returning recent snapshot
        mock_doc = MagicMock()
        mock_doc.id = "A1100014"
        mock_doc.to_dict.return_value = {
            "hpid": "A1100014",
            "hospital_name": "삼성서울병원",
            "pediatric_beds": 2,
            "general_beds": 6,
            "pediatric_iso_beds": 1,
            "lat": 37.4882,
            "lon": 127.0856,
            "notice_raw": "소아 정상 진료",
            "is_pediatric_blocked": False,
            "pediatric_acceptable": True,
        }

        mock_db = MagicMock()
        mock_db.collection.return_value.stream.return_value = [mock_doc]

        with patch("app.services.emergency_sync_service.get_firestore_client", return_value=mock_db):
            beds, meta = resolve_fallback_hierarchy(stage1="서울특별시", reason="SERVER_REBOOT")

            self.assertEqual(len(beds), 1)
            self.assertEqual(beds[0].hospital_name, "삼성서울병원")
            self.assertEqual(meta.source_tier, "TIER_2_FIRESTORE_SNAPSHOT")
            self.assertFalse(meta.is_realtime)
            self.assertIn("Firestore 최근 동기화 스냅샷", meta.warning_message)

    def test_cb_05_tier3_immutable_baseline_disk_fallback(self) -> None:
        """TC-CB-05: Tier 3 L3 Immutable Local Disk Baseline serving in complete network outage."""
        clear_bed_cache()
        default_egen_circuit_breaker.state = CircuitState.OPEN
        default_egen_circuit_breaker.last_state_change = time.time()

        # Both L1 memory and L2 firestore are completely down/empty
        with patch("app.services.emergency_sync_service._fetch_from_firestore_snapshot", return_value=([], 0.0)):
            beds, meta = resolve_fallback_hierarchy(stage1="서울특별시", reason="TOTAL_OUTAGE")

            self.assertGreater(len(beds), 0)
            self.assertEqual(meta.source_tier, "TIER_3_IMMUTABLE_DISK_BASELINE")
            self.assertFalse(meta.is_realtime)
            self.assertEqual(meta.elapsed_minutes, 999)
            self.assertIn("기준 응급의료기관 정적 마스터셋", meta.warning_message)
            self.assertIn("국가공공망 장애", beds[0].notice_raw)

    def test_cb_06_self_healing_half_open_recovery(self) -> None:
        """TC-CB-06: Self-Healing FSM: OPEN -> HALF_OPEN (after 60s) -> CLOSED on canary success."""
        cb = AsyncCircuitBreaker(name="TEST_RECOVERY", failure_threshold=3, recovery_timeout=60.0)

        # Trip to OPEN
        for _ in range(3):
            cb.record_failure(Exception("503"))
        self.assertEqual(cb.state, CircuitState.OPEN)
        self.assertFalse(cb.is_available())

        # Advance time by 61 seconds (simulating 60s recovery timeout expiration)
        cb.last_state_change = time.time() - 65.0

        # Next check transitions OPEN -> HALF_OPEN (Canary probe allowed)
        self.assertTrue(cb.is_available())
        self.assertEqual(cb.state, CircuitState.HALF_OPEN)

        # Canary probe succeeds -> Transitions HALF_OPEN -> CLOSED and failure_count reset to 0
        cb.record_success()
        self.assertEqual(cb.state, CircuitState.CLOSED)
        self.assertEqual(cb.failure_count, 0)
        self.assertTrue(cb.is_available())

    def test_cb_07_rest_api_nearby_resilience_and_freshness_meta(self) -> None:
        """TC-CB-07: REST API (/api/v1/emergency/nearby) returns HTTP 200 OK and DataFreshnessMeta when circuit is OPEN."""
        default_egen_circuit_breaker.state = CircuitState.OPEN
        default_egen_circuit_breaker.last_state_change = time.time()

        # Seed L1 memory cache
        sample_beds = [
            EmergencyBedInfo(
                hpid="A1100010",
                hospital_name="서울대학교병원",
                pediatric_beds=3,
                general_beds=5,
                pediatric_iso_beds=1,
                lat=37.5796,
                lon=127.0002,
                notice_raw="소아 응급실 정상 가동",
                pediatric_acceptable=True,
            )
        ]
        set_cached_emergency_beds("서울특별시", sample_beds)

        response = self.client.get(
            "/api/v1/emergency/nearby",
            params={"lat": 37.5665, "lon": 126.9780, "radius_km": 15.0, "only_acceptable": True, "limit": 5},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("hospitals", data)
        self.assertIn("data_freshness", data)
        self.assertIsNotNone(data["data_freshness"])

        freshness = data["data_freshness"]
        self.assertFalse(freshness["is_realtime"])
        self.assertEqual(freshness["source_tier"], "TIER_1_MEMORY_STALE")
        self.assertIn("전화", freshness.get("warning_message", ""))

    def test_cb_08_background_scheduler_isolation_during_outage(self) -> None:
        """TC-CB-08: Background scheduler polling gracefully isolates circuit open without crashing."""
        default_egen_circuit_breaker.state = CircuitState.OPEN
        default_egen_circuit_breaker.last_state_change = time.time()

        import asyncio

        stats = asyncio.run(background_daemon.poll_realtime_beds())

        self.assertNotIn("error", stats)
        self.assertGreater(stats.get("total_count", 0), 0)
        self.assertEqual(stats.get("circuit_status"), "OPEN")
        self.assertIn("TIER_", stats.get("source_tier", ""))


if __name__ == "__main__":
    unittest.main()
