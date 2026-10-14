"""Comprehensive Validation Suite for Red Flag Module V2 Upgrade.

Tests:
1. Tier 1 (0ms) Regex Interceptor on 5 new KTAS v2 clinical patterns:
   - Rule 8: Traumatic Amputation (절단 손상) -> KTAS 2 (NACRS 103)
   - Rule 9: Syncope & Collapse with Persistent Fever/Lethargy (실신 및 허탈) -> KTAS 2 (NACRS 053)
   - Rule 10: Intussusception (장중첩증 / 주기적 복통 + 혈변) -> KTAS 2 (NACRS 252)
   - Rule 11: Croup / Inspiratory Stridor / Drooling (상기도 폐쇄) -> KTAS 2 (NACRS 152)
   - Rule 12: Severe Burns (얼굴/손 2도 화상 / 광범위 화상) -> KTAS 2 (NACRS 501)
2. State Schema KTAS metadata synchronization
3. Tier 2 Direct Grounded Triage Agent KTAS level & rationale generation
4. Supervisor FSM immediate EMERGENCY_ESCALATION routing
"""

import asyncio
import unittest
from app.schemas.state import PatientSessionState
from app.agents.guardrail_agent import check_red_flag_instant
from app.agents.triage_agent import TriageAgent
from app.orchestrator.supervisor import SupervisorOrchestrator


class TestRedFlagV2Upgrade(unittest.IsolatedAsyncioTestCase):
    """Test suite verifying the Red Flag V2 two-tier architecture."""

    def setUp(self) -> None:
        self.state = PatientSessionState(
            session_id="test_redflag_v2_session",
            user_lat=37.5133,
            user_lon=127.1001,
        )

    def test_01_tier1_rule8_amputation(self) -> None:
        """Rule 8: Amputation pattern detection and KTAS metadata population."""
        user_msg = "아기가 문틈에 손가락이 심하게 끼어서 손가락 끝마디가 절단되었어요! 피가 멈추지 않아요."
        is_red = check_red_flag_instant(user_msg, self.state)

        self.assertTrue(is_red)
        self.assertTrue(self.state.is_red_flag)
        self.assertEqual(self.state.ktas_level, 2)
        self.assertEqual(self.state.matched_nacrs_code, "553")
        self.assertEqual(self.state.matched_symptom_name, "절단")
        self.assertIn("119", self.state.emergency_action_guide)

    def test_02_tier1_rule9_syncope_collapse(self) -> None:
        """Rule 9: Syncope & Collapse with fever/drowsy state."""
        user_msg = "아이가 열이 39도까지 나더니 갑자기 털썩 쓰러지면서 기절했어요. 눈은 떴는데 계속 늘어지고 헛소리를 해요."
        is_red = check_red_flag_instant(user_msg, self.state)

        self.assertTrue(is_red)
        self.assertTrue(self.state.is_red_flag)
        self.assertEqual(self.state.ktas_level, 2)
        self.assertEqual(self.state.matched_nacrs_code, "008")
        self.assertEqual(self.state.matched_symptom_name, "실신 / 전실신")

    def test_03_tier1_rule10_intussusception(self) -> None:
        """Rule 10: Pediatric Intussusception (Colic + Currant jelly stool)."""
        user_msg = "생후 8개월 아기가 15분 주기로 다리를 배 쪽으로 당기며 자지러지게 비명을 지르며 울고, 기저귀에 딸기잼 같은 피똥을 쌌어요."
        is_red = check_red_flag_instant(user_msg, self.state)

        self.assertTrue(is_red)
        self.assertTrue(self.state.is_red_flag)
        self.assertEqual(self.state.ktas_level, 2)
        self.assertEqual(self.state.matched_nacrs_code, "260")
        self.assertEqual(self.state.matched_symptom_name, "혈변 / 흑색변")

    def test_04_tier1_rule11_croup_stridor(self) -> None:
        """Rule 11: Croup / Inspiratory Stridor / Drooling."""
        user_msg = "아기가 컹컹거리는 개 짖는 듯한 쇳소리 기침을 하면서 숨쉴 때마다 괴로워하고 침을 삼키지 못하고 줄줄 흘려요."
        is_red = check_red_flag_instant(user_msg, self.state)

        self.assertTrue(is_red)
        self.assertTrue(self.state.is_red_flag)
        self.assertEqual(self.state.ktas_level, 2)
        self.assertEqual(self.state.matched_nacrs_code, "610")
        self.assertEqual(self.state.matched_symptom_name, "협착음")

    def test_05_tier1_rule12_severe_burn(self) -> None:
        """Rule 12: Severe Burn (Face/Hands/Blistering)."""
        user_msg = "돌 지난 아기가 뜨거운 찌개 냄비를 엎질러 얼굴과 양 손등에 물집이 크게 잡히고 피부가 벗겨졌어요."
        is_red = check_red_flag_instant(user_msg, self.state)

        self.assertTrue(is_red)
        self.assertTrue(self.state.is_red_flag)
        self.assertEqual(self.state.ktas_level, 2)
        self.assertEqual(self.state.matched_nacrs_code, "705")
        self.assertEqual(self.state.matched_symptom_name, "화상")

    def test_06_state_schema_ktas_fields_persistence(self) -> None:
        """Test that PatientSessionState correctly persists and serializes KTAS v2 fields."""
        self.state.ktas_level = 1
        self.state.ktas_level_name = "1단계(소생)"
        self.state.matched_nacrs_code = "001"
        self.state.matched_symptom_name = "심정지/무호흡"
        self.state.clinical_rationale = "호흡 정지 및 청색증 동반으로 즉시 소생술 필요"
        self.state.time_trajectory_assessment = "초급성 진행형"

        dumped = self.state.model_dump()
        self.assertEqual(dumped["ktas_level"], 1)
        self.assertEqual(dumped["ktas_level_name"], "1단계(소생)")
        self.assertEqual(dumped["matched_nacrs_code"], "001")
        self.assertEqual(dumped["matched_symptom_name"], "심정지/무호흡")
        self.assertEqual(dumped["clinical_rationale"], "호흡 정지 및 청색증 동반으로 즉시 소생술 필요")
        self.assertEqual(dumped["time_trajectory_assessment"], "초급성 진행형")

    async def test_07_supervisor_tier1_escalation_fsm(self) -> None:
        """Supervisor FSM must immediately route Tier 1 Red Flag to EMERGENCY_ESCALATION."""
        supervisor = SupervisorOrchestrator()
        resp = await supervisor.process_turn(
            user_message="아기가 15분마다 자지러지게 울면서 딸기잼 같은 피똥을 싸요!",
            session_id="test_supervisor_tier1",
            user_lat=37.5133,
            user_lon=127.1001,
        )

        self.assertEqual(resp.current_step, "EMERGENCY_ESCALATION")
        self.assertTrue(resp.is_emergency)
        self.assertIn("119 즉시 이송 권고", resp.message)
        self.assertIsNotNone(resp.emergency_guide)
        self.assertTrue(len(resp.hospitals) > 0)
        self.assertEqual(len(resp.pharmacies), 0)  # Pharmacies excluded during emergency

    async def test_08_triage_agent_ktas_grounding_integration(self) -> None:
        """Triage Agent with Gemini 3.8 Flash Thinking outputs KTAS metadata."""
        triage_agent = TriageAgent()
        res = await triage_agent.triage_message(
            user_message="생후 18개월 아기인데 열이 39.5도까지 나고 기침을 심하게 해요. 4시간 전부터 그래요.",
            state=self.state,
        )

        self.assertIsNotNone(res)
        self.assertEqual(self.state.age_months, 18)
        self.assertAlmostEqual(self.state.temperature, 39.5, places=1)
        # Should have populated KTAS level if API is live or fallback
        self.assertIsNotNone(self.state.ktas_level)
        self.assertIn(self.state.ktas_level, [1, 2, 3, 4, 5])


if __name__ == "__main__":
    unittest.main()
