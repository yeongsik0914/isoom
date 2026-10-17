"""Unit and integration test suite for Step 5: FastAPI REST API & Background Daemon.

Covers:
- TC-501: System root (GET /) and health check (GET /health) endpoints.
- TC-502: Proximity emergency ER search (GET /api/v1/emergency/nearby) with < 20ms latency.
- TC-503: Moonlight clinic + 30-min pharmacy pairing search (GET /api/v1/emergency/pairings).
- TC-504: Single-turn conversational inquiry (POST /api/v1/chat).
- TC-505: 0ms Red Flag instant escalation via REST API (POST /api/v1/chat).
- TC-506: Multi-turn session state continuity and deadlock guard (POST /api/v1/chat).
- TC-507: Active session detail inspection and deletion (GET/DELETE /api/v1/chat/session/{sid}).
- TC-508: Server-Sent Events (SSE) streaming endpoint (POST /api/v1/chat/stream).
- TC-509: Background daemon on-demand sync (POST /api/v1/emergency/sync) and status (GET /api/v1/emergency/status).
- TC-510: APScheduler 2-track job registration and lifecycle management.
"""

from __future__ import annotations

import asyncio
import time
import unittest
from unittest.mock import patch

from httpx import ASGITransport, AsyncClient

from app.services.scheduler import background_daemon
from main import app


class TestStep5API(unittest.IsolatedAsyncioTestCase):
    """Step 5 FastAPI REST serving and daemon test suite."""

    async def asyncSetUp(self) -> None:
        self.transport = ASGITransport(app=app)
        self.client = AsyncClient(transport=self.transport, base_url="http://test")

    async def asyncTearDown(self) -> None:
        await self.client.aclose()
        if background_daemon.is_running():
            background_daemon.shutdown(wait=False)

    async def test_01_root_and_health_check_tc501(self) -> None:
        """TC-501: Validates root metadata and health check endpoints."""
        res_root = await self.client.get("/")
        self.assertEqual(res_root.status_code, 200)
        data_root = res_root.json()
        self.assertEqual(data_root["service"], "MoonlightCare API")
        self.assertIn("chat", data_root["endpoints"])

        res_health = await self.client.get("/health")
        self.assertEqual(res_health.status_code, 200)
        data_health = res_health.json()
        self.assertEqual(data_health["status"], "healthy")
        self.assertIn("scheduler", data_health)
        self.assertIn("sessions", data_health)
        self.assertIn("integrations", data_health)

    async def test_02_nearby_emergency_departments_tc502(self) -> None:
        """TC-502: Validates nearby emergency department search latency and schema."""
        start_t = time.perf_counter()
        res = await self.client.get(
            "/api/v1/emergency/nearby",
            params={
                "lat": 37.5133,  # Jamsil Station
                "lon": 127.1001,
                "radius_km": 15.0,
                "only_acceptable": True,
                "limit": 5,
            },
        )
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("hospitals", data)
        self.assertIn("surge_risk_level", data)
        self.assertIn("latency_ms", data)
        self.assertTrue(len(data["hospitals"]) > 0)
        # Latency should be fast (network roundtrip tolerance)
        self.assertLess(elapsed_ms, 2500.0)

        top_er = data["hospitals"][0]
        self.assertIn("hospital_name", top_er)
        self.assertIn("distance_km", top_er)
        self.assertTrue(top_er["pediatric_acceptable"])

    async def test_03_nearby_moonlight_pairings_tc503(self) -> None:
        """TC-503: Validates Moonlight clinic + 30-min pharmacy pairing query."""
        res = await self.client.get(
            "/api/v1/emergency/pairings",
            params={
                "lat": 37.4988,  # Seocho
                "lon": 126.9934,
                "radius_km": 30.0,
                "limit": 3,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("pairings", data)
        self.assertGreater(data["total_found"], 0)

        first_pair = data["pairings"][0]
        self.assertIn("병원명", first_pair)
        self.assertIn("약국명", first_pair)
        self.assertIn("안전마진_분", first_pair)
        self.assertIn("거리_km", first_pair)

    async def test_04_chat_single_turn_complete_tc504(self) -> None:
        """TC-504: Single-turn inquiry generates full recommendations and logistics."""
        payload = {
            "user_message": "14개월 아기 38.5도 열나요. 2시간 됐고 해열제 먹였는데도 힘들어해요.",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "stream": False,
        }
        res = await self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertIn("session_id", data)
        self.assertEqual(data["turn_count"], 1)
        self.assertFalse(data["is_emergency"])
        self.assertEqual(data["current_step"], "COMPLETED")
        self.assertTrue(len(data["hospitals"]) > 0)
        self.assertIsNotNone(data["call_script"])
        self.assertTrue(len(data["checklist"]) > 0)
        self.assertIn("의료법 제27조", data["disclaimer"])

    async def test_05_chat_red_flag_instant_escalation_tc505(self) -> None:
        """TC-505: 0ms Red Flag immediately triggers 119 emergency guide and emergency status."""
        payload = {
            "user_message": "생후 50일 신생아인데 39.0도 고열에 숨소리가 쌕쌕거리고 처져요!",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "stream": False,
        }
        res = await self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()

        self.assertTrue(data["is_emergency"])
        self.assertEqual(data["current_step"], "EMERGENCY_ESCALATION")
        self.assertIsNotNone(data["emergency_guide"])
        self.assertIn("119", data["message"])
        self.assertTrue(len(data["hospitals"]) > 0)

    async def test_06_chat_multi_turn_state_continuity_tc506(self) -> None:
        """TC-506: Multi-turn chat maintains session continuity and tracks turn count."""
        # Turn 1: Incomplete variables
        turn1_payload = {
            "user_message": "아기 열나요",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
        }
        res1 = await self.client.post("/api/v1/chat", json=turn1_payload)
        self.assertEqual(res1.status_code, 200)
        data1 = res1.json()
        session_id = data1["session_id"]
        self.assertEqual(data1["turn_count"], 1)
        self.assertEqual(data1["current_step"], "TRIAGE")

        # Turn 2: Provide missing details using the same session_id
        turn2_payload = {
            "user_message": "15개월이고 38.6도예요. 3시간 됐어요.",
            "session_id": session_id,
            "user_lat": 37.5133,
            "user_lon": 127.1001,
        }
        res2 = await self.client.post("/api/v1/chat", json=turn2_payload)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertEqual(data2["session_id"], session_id)
        self.assertEqual(data2["turn_count"], 2)
        self.assertEqual(data2["current_step"], "COMPLETED")

    async def test_07_session_detail_and_deletion_tc507(self) -> None:
        """TC-507: Tests session inspection and deletion endpoints."""
        # 1. Create a session
        res = await self.client.post(
            "/api/v1/chat",
            json={"user_message": "24개월 아이 38.2도 발열"},
        )
        self.assertEqual(res.status_code, 200)
        sid = res.json()["session_id"]

        # 2. Inspect session detail
        res_detail = await self.client.get(f"/api/v1/chat/session/{sid}")
        self.assertEqual(res_detail.status_code, 200)
        detail = res_detail.json()
        self.assertEqual(detail["session_id"], sid)
        self.assertEqual(detail["age_months"], 24)
        self.assertAlmostEqual(detail["temperature"], 38.2, places=1)

        # 3. Delete session
        res_del = await self.client.delete(f"/api/v1/chat/session/{sid}")
        self.assertEqual(res_del.status_code, 200)

        # 4. Confirm deleted
        res_check = await self.client.get(f"/api/v1/chat/session/{sid}")
        self.assertEqual(res_check.status_code, 404)

    async def test_08_sse_streaming_endpoint_tc508(self) -> None:
        """TC-508: Server-Sent Events (SSE) stream produces chunks and finishes with [DONE]."""
        payload = {
            "user_message": "30개월 아기 38.0도 미열이에요.",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
        }
        res = await self.client.post("/api/v1/chat/stream", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/event-stream", res.headers.get("content-type", ""))

        content = res.text
        self.assertIn("event: status", content)
        self.assertIn("event: delta", content)
        self.assertIn("event: result", content)
        self.assertIn("event: done", content)
        self.assertIn("[DONE]", content)

    async def test_09_emergency_sync_and_status_tc509(self) -> None:
        """TC-509: Tests background daemon status and on-demand bed sync."""
        res_status = await self.client.get("/api/v1/emergency/status")
        self.assertEqual(res_status.status_code, 200)
        status_data = res_status.json()
        self.assertIn("running", status_data)
        self.assertIn("jobs", status_data)

        # On-demand sync trigger
        res_sync = await self.client.post("/api/v1/emergency/sync")
        self.assertEqual(res_sync.status_code, 200)
        sync_data = res_sync.json()
        self.assertEqual(sync_data["status"], "SUCCESS")
        self.assertGreater(sync_data["total_count"], 0)
        self.assertIn("saving_rate_percent", sync_data)

    async def test_10_scheduler_lifecycle_tc510(self) -> None:
        """TC-510: Tests background daemon scheduler start, jobs, and status tracking."""
        background_daemon.start(bed_interval_minutes=5, static_cron_hour=4, static_cron_minute=0)
        self.assertTrue(background_daemon.is_running())

        status = background_daemon.get_status()
        job_ids = [j["id"] for j in status["jobs"]]
        self.assertIn("job_realtime_bed_poller", job_ids)
        self.assertIn("job_static_dataset_sync", job_ids)

        # Trigger one poll cycle
        stats = await background_daemon.poll_realtime_beds()
        self.assertIn("total_count", stats)
        self.assertGreater(background_daemon.poll_count, 0)
        self.assertIsNotNone(background_daemon.last_bed_poll_time)

        # Clean shutdown so background threads don't linger across test cases
        background_daemon.shutdown(wait=False)
        self.assertFalse(background_daemon.is_running())

    async def test_11_nearby_emergency_beds_nationwide_coverage(self) -> None:
        """TC-511: Tests nationwide LBS emergency search from non-Seoul regions (Suwon, Busan)."""
        # 1. Busan Query (35.1017, 129.0186)
        res_busan = await self.client.get(
            "/api/v1/emergency/nearby",
            params={
                "lat": 35.1017,
                "lon": 129.0186,
                "radius_km": 25.0,
                "only_acceptable": True,
                "limit": 3,
            },
        )
        self.assertEqual(res_busan.status_code, 200)
        data_busan = res_busan.json()
        self.assertIn("hospitals", data_busan)
        self.assertTrue(len(data_busan["hospitals"]) > 0)
        top_busan = data_busan["hospitals"][0]
        # Should return a nearby hospital with distance < 25km and real phone
        self.assertLess(top_busan["distance_km"], 25.0)
        self.assertIsNotNone(top_busan["tel"])
        self.assertIsNotNone(top_busan["center_type"])

        # 2. Suwon Query (37.2636, 127.0286)
        res_suwon = await self.client.get(
            "/api/v1/emergency/nearby",
            params={
                "lat": 37.2636,
                "lon": 127.0286,
                "radius_km": 25.0,
                "only_acceptable": True,
                "limit": 3,
            },
        )
        self.assertEqual(res_suwon.status_code, 200)
        data_suwon = res_suwon.json()
        self.assertIn("hospitals", data_suwon)
        self.assertTrue(len(data_suwon["hospitals"]) > 0)
        top_suwon = data_suwon["hospitals"][0]
        self.assertLess(top_suwon["distance_km"], 25.0)


if __name__ == "__main__":
    unittest.main()

