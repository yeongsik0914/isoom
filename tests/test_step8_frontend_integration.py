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

    def test_04_result_html_ktas_dual_track_contract(self):
        """TC-804: Validates result.html contains KTAS 1-3 ER status and KTAS 4-5 Moonlight matching elements."""
        from pathlib import Path
        result_html_path = Path(__file__).resolve().parent.parent / "frontend" / "templates" / "result.html"
        self.assertTrue(result_html_path.exists(), "result.html template must exist.")

        html_content = result_html_path.read_text(encoding="utf-8")

        # 1. Essential DOM containers and tabs
        self.assertIn('id="pane-emergency"', html_content)
        self.assertIn('id="pane-moonlight"', html_content)
        self.assertIn('id="tab-btn-emergency"', html_content)
        self.assertIn('id="tab-btn-moonlight"', html_content)
        self.assertIn('id="emergency-scroll-list"', html_content)
        self.assertIn('id="moonlight-scroll-list"', html_content)

        # 2. KTAS 1, 2, 3 emergency escalation and call banner
        self.assertIn('id="ktas-emergency-call-banner"', html_content)
        self.assertIn('id="ktas-emergency-call-msg"', html_content)

        # 3. Dynamic JavaScript logic contracts
        self.assertIn("switchTrackTab('emergency')", html_content)
        self.assertIn("switchTrackTab('moonlight')", html_content)
        self.assertIn("renderEmergencyBedCards", html_content)
        self.assertIn("renderMoonlightPairingCards", html_content)
        self.assertIn("updateCallScript", html_content)
        self.assertIn("refreshLiveEmergencyBeds", html_content)

        # 4. Strict KTAS 4, 5 emergency room deterrence: #tab-btn-emergency hidden
        self.assertIn("btnEmergency.style.display = 'none'", html_content)
        self.assertIn("window.currentKtasLevel >= 4", html_content)

    async def test_05_ktas_api_routing_matrix(self):
        """TC-805: Validates backend chat API outputs KTAS 1~3 for severe vitals and KTAS 4~5 for mild cases."""
        # 1. Severe case (KTAS 1 or 2)
        res_severe = self.client.post("/api/v1/chat", json={
            "user_message": "생후 45일 신생아가 38.9도 고열에 경련을 일으키며 축 늘어져요",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "force_matching": True,
        })
        self.assertEqual(res_severe.status_code, 200)
        data_severe = res_severe.json()
        self.assertTrue(data_severe["is_emergency"] or (data_severe["ktas_level"] and data_severe["ktas_level"] <= 2))

        # 2. Mild case (KTAS 4 or 5)
        res_mild = self.client.post("/api/v1/chat", json={
            "user_message": "36개월 아기가 미열 37.8도에 콧물이 조금 나요",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "force_matching": True,
        })
        self.assertEqual(res_mild.status_code, 200)
        data_mild = res_mild.json()
        self.assertFalse(data_mild["is_emergency"])
        self.assertGreaterEqual(data_mild["ktas_level"], 4)


if __name__ == "__main__":
    unittest.main()
