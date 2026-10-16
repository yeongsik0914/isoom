"""Step 8 Frontend-Backend Phase 1 Integration Tests.

Validates:
1. TC-801: 1-shot fast routing with force_matching=True completes in 1 turn with hospitals, pharmacies, and safe clinical defaults.
2. TC-802: 0ms Red Flag override safety check (Red Flag takes precedence over force_matching, escalating immediately).
3. TC-803: REST API POST /api/v1/chat schema integrity and complete field payload for frontend result.html binding.
"""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from app.orchestrator.supervisor import SupervisorOrchestrator
from app.schemas.chat import ChatRequest
from main import app


class TestFrontendIntegrationStep1(unittest.IsolatedAsyncioTestCase):
    """Test suite for Phase 1 fullstack backend contract."""

    async def asyncSetUp(self):
        """Initializes isolated orchestrator and test client."""
        self.supervisor = SupervisorOrchestrator()
        self.client = TestClient(app)

    async def test_01_force_matching_single_turn_completion(self):
        """TC-801: Incomplete prompt with force_matching=True reaches COMPLETED in 1 turn."""
        response = await self.supervisor.process_turn(
            user_message="아기가 열이 나고 보채요",
            session_id="test-sess-phase1-001",
            user_lat=37.5133,
            user_lon=127.1001,
            force_matching=True,
        )

        # Must transition directly to COMPLETED
        self.assertEqual(response.current_step, "COMPLETED")
        self.assertFalse(response.is_emergency)
        self.assertEqual(response.turn_count, 1)

        # Per ISSUE-112 & ISSUE-116: Unspecified age/temp are preserved as None to prevent falsification
        self.assertIsNone(response.age_months)
        self.assertIsNone(response.temperature)
        self.assertIsNotNone(response.ktas_level)
        self.assertTrue(len(response.symptoms) >= 1)

        # Must include hospitals, call_script, and checklist
        self.assertTrue(len(response.hospitals) >= 1)
        self.assertIsNotNone(response.call_script)
        self.assertTrue(len(response.checklist) >= 3)

    async def test_02_red_flag_overrides_force_matching(self):
        """TC-802: Emergency Red Flag takes absolute precedence over force_matching."""
        response = await self.supervisor.process_turn(
            user_message="생후 50일 신생아가 38.8도 고열이 나요",
            session_id="test-sess-phase1-002",
            user_lat=37.5133,
            user_lon=127.1001,
            force_matching=True,
        )

        # Must escalate to emergency immediately
        self.assertTrue(response.is_emergency)
        self.assertEqual(response.current_step, "EMERGENCY_ESCALATION")
        self.assertIsNotNone(response.emergency_guide)
        self.assertTrue(len(response.hospitals) >= 1)

    def test_03_rest_api_chat_schema_integrity(self):
        """TC-803: REST API POST /api/v1/chat returns all required frontend fields."""
        payload = {
            "user_message": "14개월 아기가 열이 39.2도까지 오르고 구토를 두 번 했어요",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "force_matching": True,
        }
        res = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        # Essential top-level keys
        self.assertIn("session_id", data)
        self.assertIn("current_step", data)
        self.assertIn("is_emergency", data)
        self.assertIn("message", data)
        self.assertIn("hospitals", data)
        self.assertIn("pharmacies", data)
        self.assertIn("call_script", data)
        self.assertIn("checklist", data)

        # Clinical vital chips keys for result.html
        self.assertIn("age_months", data)
        self.assertIn("temperature", data)
        self.assertIn("ktas_level", data)
        self.assertIn("ktas_level_name", data)
        self.assertIn("symptoms", data)

        # Clinical variable assertion
        self.assertEqual(data["age_months"], 14)
        self.assertAlmostEqual(data["temperature"], 39.2, places=1)


if __name__ == "__main__":
    unittest.main()
