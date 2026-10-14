"""Unit and integration test suite for Step 2: Session State DTO & 0ms Safety Guardrail.

Covers:
- PatientSessionState initialization and FSM transition.
- KTAS Pediatric Red Flag instant 0ms interception across 8 clinical categories (TC-16 ~ TC-23).
- Non-emergency normal symptoms passing through safely without false positives.
- Medical Service Act Article 27 sanitization (scrubbing diagnoses & drug dosages).
- Zero-latency (< 0.1ms) performance benchmark.
"""

from __future__ import annotations

import time
import unittest

from app.agents.guardrail_agent import (
    MedicalGuardrailAgent,
    check_red_flag_instant,
    sanitize_output,
)
from app.schemas.state import PatientSessionState


class TestStep2Guardrail(unittest.TestCase):
    """Step 2 test suite."""

    def setUp(self) -> None:
        self.state = PatientSessionState(session_id="test-session-001")

    def test_01_state_dto_lifecycle(self) -> None:
        """Verifies PatientSessionState fields, message appending, and escalation methods."""
        self.assertEqual(self.state.current_step, "INIT")
        self.assertEqual(self.state.turn_count, 0)
        self.assertFalse(self.state.is_red_flag)

        self.state.add_message("user", "아기가 열이 나요")
        self.assertEqual(self.state.turn_count, 1)
        self.assertEqual(len(self.state.conversation_history), 1)

        self.state.escalate_to_emergency("테스트 사유", "테스트 가이드")
        self.assertTrue(self.state.is_red_flag)
        self.assertEqual(self.state.current_step, "EMERGENCY_ESCALATION")
        self.assertEqual(self.state.red_flag_reason, "테스트 사유")

    def test_02_red_flag_infant_fever_tc16(self) -> None:
        """TC-16: Infant < 100 days with high fever must trigger instant emergency escalation."""
        text = "생후 55일 된 아기인데 방금 체온 재보니 38.3도예요. 어떡하죠?"
        is_red = check_red_flag_instant(text, self.state)
        self.assertTrue(is_red)
        self.assertTrue(self.state.is_red_flag)
        self.assertEqual(self.state.current_step, "EMERGENCY_ESCALATION")
        self.assertIn("100일 미만", self.state.red_flag_reason or "")

    def test_03_red_flag_seizure_tc17(self) -> None:
        """TC-17: Pediatric febrile seizure / convulsion must trigger emergency escalation."""
        text = "24개월 아이가 열나면서 눈이 돌아가고 온몸을 덜덜 떨어요! 3분째 이러고 있어요 살려주세요!"
        is_red = check_red_flag_instant(text, self.state)
        self.assertTrue(is_red)
        self.assertEqual(self.state.current_step, "EMERGENCY_ESCALATION")
        self.assertIn("경련", self.state.red_flag_reason or "")
        self.assertIn("기도를 확보", self.state.emergency_action_guide or "")

    def test_04_red_flag_unresponsiveness_tc18(self) -> None:
        """TC-18: Severe lethargy and unresponsiveness must trigger emergency escalation."""
        text = "아이가 눈을 못 뜨고 축 늘어져서 이름을 불러도 반응이 없어요."
        is_red = check_red_flag_instant(text, self.state)
        self.assertTrue(is_red)
        self.assertEqual(self.state.current_step, "EMERGENCY_ESCALATION")
        self.assertIn("의식 저하", self.state.red_flag_reason or "")

    def test_05_red_flag_respiratory_and_cyanosis_tc19_tc20(self) -> None:
        """TC-19 & TC-20: Chest retraction, stridor, and cyanosis must trigger emergency escalation."""
        text_19 = "숨 쉴 때마다 갈비뼈 아래가 쑥쑥 들어가고 코를 벌렁거리면서 쌕쌕거려요. 숨쉬기 힘들어 보여요."
        state_19 = PatientSessionState(session_id="test-19")
        self.assertTrue(check_red_flag_instant(text_19, state_19))
        self.assertEqual(state_19.current_step, "EMERGENCY_ESCALATION")

        text_20 = "아기 입술이랑 손톱이 파랗게 질렸어요. 울음소리도 제대로 못 내요."
        state_20 = PatientSessionState(session_id="test-20")
        self.assertTrue(check_red_flag_instant(text_20, state_20))
        self.assertEqual(state_20.current_step, "EMERGENCY_ESCALATION")
        self.assertIn("청색증", state_20.red_flag_reason or "")

    def test_06_red_flag_severe_dehydration_tc21(self) -> None:
        """TC-21: Severe dehydration (no urine for 8+ hours) must trigger emergency escalation."""
        text = "아이가 오늘 아침부터 8시간 넘게 소변을 한 번도 안 보고 울어도 눈물이 안 나와요. 입술도 바짝 말랐어요."
        is_red = check_red_flag_instant(text, self.state)
        self.assertTrue(is_red)
        self.assertEqual(self.state.current_step, "EMERGENCY_ESCALATION")
        self.assertIn("탈수", self.state.red_flag_reason or "")

    def test_07_red_flag_bilious_vomiting_tc22(self) -> None:
        """TC-22: Green bilious vomiting must trigger emergency escalation."""
        text = "아기가 토를 하는데 초록색 진한 담즙 같은 액체를 계속 뿜어내요. 배가 빵빵해요."
        is_red = check_red_flag_instant(text, self.state)
        self.assertTrue(is_red)
        self.assertEqual(self.state.current_step, "EMERGENCY_ESCALATION")
        self.assertIn("담즙", self.state.red_flag_reason or "")

    def test_08_red_flag_head_trauma_tc23(self) -> None:
        """TC-23: Head trauma followed by vomiting and drowsiness must trigger emergency escalation."""
        text = "침대에서 떨어져 머리를 쿵 찧었는데, 그 뒤로 분수처럼 3번 토하고 계속 눈이 감기면서 잠만 자려고 해요."
        is_red = check_red_flag_instant(text, self.state)
        self.assertTrue(is_red)
        self.assertEqual(self.state.current_step, "EMERGENCY_ESCALATION")
        self.assertIn("두부 외상", self.state.red_flag_reason or "")

    def test_09_state_based_numeric_infant_fever(self) -> None:
        """Verifies Red Flag trigger when age <= 100 days and temp >= 38.0 are stored in state."""
        state = PatientSessionState(
            session_id="test-numeric",
            age_days=50,
            temperature=38.4,
        )
        is_red = check_red_flag_instant("아이가 열이 나면서 칭얼거려요", state)
        self.assertTrue(is_red)
        self.assertEqual(state.current_step, "EMERGENCY_ESCALATION")

    def test_10_normal_symptoms_not_blocked(self) -> None:
        """Verifies that non-emergency normal pediatric symptoms pass through without false alarm."""
        normal_cases = [
            "만 4세 아이가 3일 전부터 콧물 나고 기침해요. 지금 37.8도 미열인데 오늘 밤에 병원 가야 할까요?",
            "18개월 아기 열이 38.2도예요. 미열인데 지켜봐도 될까요?",
            "초등학교 1학년인데 밤에 귀가 아프다고 울어요. 열은 38.1도예요.",
            "낮잠 자고 일어났는데 목이 따갑고 밥을 잘 안 먹으려고 해요.",
        ]

        for text in normal_cases:
            s = PatientSessionState(session_id="test-normal")
            is_red = check_red_flag_instant(text, s)
            self.assertFalse(is_red, f"Should NOT trigger Red Flag for text: '{text}'")
            self.assertNotEqual(s.current_step, "EMERGENCY_ESCALATION")

    def test_11_medical_law_sanitization(self) -> None:
        """Verifies Medical Service Act Article 27 post-filtering of diagnosis and dosage."""
        raw_llm_1 = "아이의 증상을 종합해보니 전형적인 급성 중이염입니다."
        sanitized_1 = sanitize_output(raw_llm_1)
        self.assertNotIn("중이염입니다", sanitized_1)
        self.assertIn("의료법 제27조 준수 고지", sanitized_1)

        raw_llm_2 = "열을 내리기 위해 아세트아미노펜 시럽 5ml를 먹이세요."
        sanitized_2 = sanitize_output(raw_llm_2)
        self.assertNotIn("5ml를 먹이세요", sanitized_2)
        self.assertIn("복약지도를 따르십시오", sanitized_2)
        self.assertIn("의료법 제27조 준수 고지", sanitized_2)

    def test_12_zero_latency_performance_benchmark(self) -> None:
        """Verifies 0ms (< 0.1ms per call) execution speed over 1,000 iterations."""
        text = "아이가 열이 38.5도이고 기침을 해요"
        state = PatientSessionState(session_id="bench-session")

        start = time.perf_counter()
        for _ in range(1000):
            check_red_flag_instant(text, state)
        elapsed_total = (time.perf_counter() - start) * 1000  # ms
        avg_call_ms = elapsed_total / 1000

        # Must execute within < 0.05ms (50 microseconds) per call
        self.assertLess(avg_call_ms, 0.05)
        print(f"\n[BENCHMARK] 1,000회 Red Flag 검사: 총 {elapsed_total:.2f}ms (회당 평균 {avg_call_ms*1000:.2f} us)")


if __name__ == "__main__":
    unittest.main()
