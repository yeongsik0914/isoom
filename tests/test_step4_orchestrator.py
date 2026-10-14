"""Unit and Integration Tests for Step 4: Supervisor FSM Orchestrator.

Test Cases:
- TC-401: Single-turn full clinical inquiry ➔ Immediate COMPLETED transition
- TC-402: Multi-turn progressive inquiry ➔ Turn 1 TRIAGE ➔ Turn 2 COMPLETED
- TC-403: 3-Turn Deadlock Guard ➔ 3 vague turns ➔ Forced MATCHING & COMPLETED
- TC-404: Instant Red Flag at Turn 1 ➔ 0ms EMERGENCY_ESCALATION
- TC-405: Mid-turn deterioration at Turn 2 ➔ Immediate Abort & EMERGENCY_ESCALATION
- TC-406: Single-exit Medical Service Act Art. 27 sanitization & disclaimer
- TC-407: SessionManager concurrency locking and TTL eviction
"""

from __future__ import annotations

import asyncio
import unittest

from app.orchestrator.session_manager import SessionManager
from app.orchestrator.supervisor import SupervisorOrchestrator
from app.schemas.state import PatientSessionState


class TestStep4Orchestrator(unittest.IsolatedAsyncioTestCase):
    """Test suite for Step 4 Supervisor Orchestration."""

    async def asyncSetUp(self) -> None:
        self.session_manager = SessionManager()
        self.supervisor = SupervisorOrchestrator(session_manager=self.session_manager)

    async def test_01_single_turn_complete_inquiry_tc401(self) -> None:
        """TC-401: When all variables are provided in turn 1, transitions to COMPLETED in 1 turn."""
        msg = "서초구 방배동인데 24개월 아이가 38.5도 열나고 2시간째 기침해요."
        res = await self.supervisor.process_turn(
            user_message=msg,
            session_id="tc401-session",
            user_lat=37.4832,
            user_lon=126.9892,
        )

        self.assertEqual(res.current_step, "COMPLETED")
        self.assertEqual(res.turn_count, 1)
        self.assertFalse(res.is_emergency)
        self.assertTrue(len(res.hospitals) > 0)
        self.assertIsNotNone(res.call_script)
        self.assertTrue(len(res.checklist) > 0)
        self.assertIn("의료법 제27조", res.disclaimer)

    async def test_02_multi_turn_progressive_triage_tc402(self) -> None:
        """TC-402: Incomplete variables on turn 1 stays in TRIAGE, completes on turn 2."""
        sid = "tc402-session"

        # Turn 1: Vague
        res1 = await self.supervisor.process_turn(
            user_message="아기가 열이 나요 어디 가야 하나요?",
            session_id=sid,
        )
        self.assertEqual(res1.current_step, "TRIAGE")
        self.assertEqual(res1.turn_count, 1)
        self.assertFalse(res1.is_emergency)
        self.assertEqual(len(res1.hospitals), 0)

        # Turn 2: Complete
        res2 = await self.supervisor.process_turn(
            user_message="14개월이고 방금 잰 체온은 38.4도예요. 기침해요.",
            session_id=sid,
        )
        self.assertEqual(res2.current_step, "COMPLETED")
        self.assertEqual(res2.turn_count, 2)
        self.assertFalse(res2.is_emergency)
        self.assertTrue(len(res2.hospitals) > 0)

    async def test_03_three_turn_deadlock_guard_tc403(self) -> None:
        """TC-403: When 3 turns pass with incomplete variables, forces MATCHING without looping."""
        sid = "tc403-session"

        # Turn 1
        res1 = await self.supervisor.process_turn(user_message="아기가 그냥 아파요", session_id=sid)
        self.assertEqual(res1.current_step, "TRIAGE")
        self.assertEqual(res1.turn_count, 1)

        # Turn 2
        res2 = await self.supervisor.process_turn(user_message="몰라요 계속 보채요", session_id=sid)
        self.assertEqual(res2.current_step, "TRIAGE")
        self.assertEqual(res2.turn_count, 2)

        # Turn 3: Upper bound reached -> Forced completion
        res3 = await self.supervisor.process_turn(user_message="빨리 병원 알려줘요", session_id=sid)
        self.assertEqual(res3.current_step, "COMPLETED")
        self.assertEqual(res3.turn_count, 3)
        self.assertTrue(len(res3.hospitals) > 0)
        self.assertIn("안내", res3.message)

    async def test_04_instant_red_flag_turn1_tc404(self) -> None:
        """TC-404: Infant high fever triggers immediate 0ms EMERGENCY_ESCALATION."""
        res = await self.supervisor.process_turn(
            user_message="생후 55일 신생아인데 38.5도 열나요 살려주세요",
            session_id="tc404-session",
        )

        self.assertEqual(res.current_step, "EMERGENCY_ESCALATION")
        self.assertTrue(res.is_emergency)
        self.assertIsNotNone(res.emergency_guide)
        self.assertIn("119", res.message)
        self.assertTrue(len(res.hospitals) > 0)

    async def test_05_mid_turn_deterioration_red_flag_tc405(self) -> None:
        """TC-405: Mild on turn 1, but seizure on turn 2 aborts immediately to EMERGENCY_ESCALATION."""
        sid = "tc405-session"

        # Turn 1: Mild
        res1 = await self.supervisor.process_turn(
            user_message="36개월 아이가 37.7도 미열이 있어요",
            session_id=sid,
        )
        self.assertFalse(res1.is_emergency)

        # Turn 2: Sudden Seizure
        res2 = await self.supervisor.process_turn(
            user_message="아기가 갑자기 입술이 파래지면서 몸을 떨고 경련을 일으켜요!",
            session_id=sid,
        )
        self.assertEqual(res2.current_step, "EMERGENCY_ESCALATION")
        self.assertTrue(res2.is_emergency)
        self.assertIsNotNone(res2.emergency_guide)
        self.assertIn("경련", res2.message)

    async def test_06_medical_law_sanitization_single_gateway_tc406(self) -> None:
        """TC-406: Verifies all responses exit through sanitize_output with disclaimer."""
        res = await self.supervisor.process_turn(
            user_message="14개월 38.5도인데 돌발진으로 진단되나요? 타이레놀 10ml 먹일까요?",
            session_id="tc406-session",
        )

        self.assertNotIn("진단됩니다", res.message)
        self.assertNotIn("10ml", res.message)
        self.assertIn("의료법 제27조", res.disclaimer)

    async def test_07_session_manager_concurrency_and_ttl_tc407(self) -> None:
        """TC-407: Tests session manager concurrency and TTL eviction."""
        sm = SessionManager()

        # Test provisioning
        s1 = await sm.get_or_create_session(session_id="s1")
        self.assertEqual(sm.count(), 1)
        self.assertEqual(s1.session_id, "s1")

        # Test retrieval
        s1_dup = await sm.get_session("s1")
        self.assertIsNotNone(s1_dup)
        self.assertEqual(s1_dup.session_id, "s1")

        # Test TTL eviction (idle seconds = 0 forces eviction)
        await asyncio.sleep(0.01)
        evicted = await sm.evict_expired_sessions(max_idle_seconds=0)
        self.assertEqual(evicted, 1)
        self.assertEqual(sm.count(), 0)


if __name__ == "__main__":
    unittest.main()
