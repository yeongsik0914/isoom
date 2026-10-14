"""Main Orchestrator (Supervisor FSM) for MoonlightCare Multi-Agent Layer.

Coordinates Guardrail, Triage, Matching, and Logistics agents via
a deterministic 6-state FSM with a 3-turn deadlock guard, instant Red Flag escalation,
and a single-exit Medical Service Act Art. 27 sanitization gateway.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.agents.guardrail_agent import (
    check_red_flag_instant,
    check_safety_violations,
    sanitize_output,
)
from app.agents.logistics_agent import LogisticsAgent
from app.agents.matching_agent import MatchingAgent
from app.agents.triage_agent import TriageAgent
from app.orchestrator.session_manager import SessionManager
from app.schemas.state import PatientSessionState
from app.schemas.supervisor import SupervisorResponse

logger = logging.getLogger(__name__)


class SupervisorOrchestrator:
    """Master FSM Orchestrator coordinating all MoonlightCare agents and services."""

    def __init__(
        self,
        triage_agent: Optional[TriageAgent] = None,
        matching_agent: Optional[MatchingAgent] = None,
        logistics_agent: Optional[LogisticsAgent] = None,
        session_manager: Optional[SessionManager] = None,
    ) -> None:
        self.triage_agent = triage_agent or TriageAgent()
        self.matching_agent = matching_agent or MatchingAgent()
        self.logistics_agent = logistics_agent or LogisticsAgent()
        self.session_manager = session_manager or SessionManager()

    async def process_turn(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        user_lat: float = 37.5133,
        user_lon: float = 127.1001,
        user_address: Optional[str] = None,
    ) -> SupervisorResponse:
        """Executes a single conversational turn through the FSM pipeline.

        1. Retrieves or creates PatientSessionState.
        2. Performs instant (0ms) Red Flag guardrail check.
           -> If triggered: aborts all agents immediately, escalates to EMERGENCY_ESCALATION.
        3. Executes Triage Agent to extract demographics and clinical variables.
           -> If variables incomplete and turn_count < 3: stays in TRIAGE and returns follow-up inquiry.
           -> If complete OR turn_count >= 3 (Deadlock Guard): transitions to MATCHING.
        4. Executes Matching Agent (Zero-LLM 2-Track Clinical Router).
           -> Transitions to LOGISTICS.
        5. Executes Logistics Agent (30-sec Call Script & May 2024 Document Checklist).
           -> Transitions to COMPLETED.
        6. Passes output through the Medical Service Act Art. 27 single-exit sanitization gateway.
        7. Saves updated state and returns structured SupervisorResponse.
        """
        # Step 1: Session Management
        state = await self.session_manager.get_or_create_session(
            session_id=session_id,
            user_lat=user_lat,
            user_lon=user_lon,
            user_address=user_address,
        )
        state.add_message(role="user", content=user_message)

        # If previous state was COMPLETED, reset to TRIAGE for new consultation round
        if state.current_step == "COMPLETED":
            state.current_step = "TRIAGE"

        # Step 2: 0ms Red Flag Pre-Interceptor (Checked Every Turn)
        is_red = check_red_flag_instant(user_message, state)
        if is_red or state.is_red_flag:
            logger.warning(
                f"[Supervisor] Red Flag detected on turn {state.turn_count}: {state.red_flag_reason}"
            )
            # Fast clinical matching for nearest emergency centers
            try:
                await self.matching_agent.match_destinations(state)
            except Exception as e:
                logger.error(f"[Supervisor] Emergency facility matching error: {e}")

            escalation_msg = (
                f"🚨 [긴급 119 즉시 이송 권고]\n"
                f"환아에게 생명 위급 응급 징후({state.red_flag_reason or '중증 응급 증상'})가 감지되었습니다. "
                f"지체 없이 119에 즉각 신고하시고 아래 응급처치 요령에 따라 구급차를 대기해 주세요."
            )
            safety_viol = check_safety_violations(user_message)
            if safety_viol:
                escalation_msg = f"{safety_viol['safe_response']}\n\n{escalation_msg}"

            sanitized_escalation = sanitize_output(escalation_msg)
            state.add_message(role="assistant", content=sanitized_escalation)
            await self.session_manager.save_session(state)

            return SupervisorResponse(
                session_id=state.session_id,
                current_step="EMERGENCY_ESCALATION",
                turn_count=state.turn_count,
                is_emergency=True,
                message=sanitized_escalation,
                emergency_guide=state.emergency_action_guide,
                hospitals=state.matched_hospitals,
                pharmacies=[],
                call_script=None,
                checklist=["주민등록등본 또는 모바일 건강보험증", "보호자 신분증"],
            )

        # Step 3: Triage & Deadlock Guard
        empathy_msg = "아이가 열이 나서 보호자님께서도 많이 걱정되시겠습니다."
        if state.current_step in ("INIT", "TRIAGE"):
            try:
                triage_res = await self.triage_agent.triage_message(user_message, state)
                empathy_msg = triage_res.empathy_message or empathy_msg
            except Exception as e:
                logger.error(f"[Supervisor] TriageAgent error (using fallback): {e}")
                empathy_msg = "아이가 많이 힘들어해서 많이 놀라셨겠습니다. 안전한 진료 시설을 신속히 확인해 드리겠습니다."

            # Check Triage Completion or 3-Turn Upper Bound (Deadlock Guard)
            is_complete = state.is_triage_complete()
            turn_limit_reached = state.turn_count >= 3

            if is_complete or turn_limit_reached:
                # If forced transition due to turn limit, populate safe defaults
                if not is_complete and turn_limit_reached:
                    if state.temperature is None:
                        state.temperature = 38.0
                    if not state.symptoms:
                        state.symptoms = ["발열", "컨디션 저하"]
                    empathy_msg += "\n\n※ 증상 입력이 불충분하여 더 이상 지체하지 않고 보호자님 현재 위치 기준 가장 안전한 야간 의료기관으로 우선 안내합니다."

                state.current_step = "MATCHING"
            else:
                # Still incomplete and turn_count < 3: Stay in TRIAGE and ask for missing variables
                state.current_step = "TRIAGE"
                sanitized_inquiry = sanitize_output(empathy_msg)
                if state.conversation_history and state.conversation_history[-1].role == "assistant":
                    state.conversation_history[-1].content = sanitized_inquiry
                else:
                    state.add_message(role="assistant", content=sanitized_inquiry)
                await self.session_manager.save_session(state)

                return SupervisorResponse(
                    session_id=state.session_id,
                    current_step=state.current_step,
                    turn_count=state.turn_count,
                    is_emergency=False,
                    message=sanitized_inquiry,
                    emergency_guide=None,
                    hospitals=[],
                    pharmacies=[],
                    call_script=None,
                    checklist=[],
                )

        # Step 4: Matching Agent (Zero-LLM 2-Track Clinical Router)
        if state.current_step == "MATCHING":
            try:
                await self.matching_agent.match_destinations(state)
            except Exception as e:
                logger.error(f"[Supervisor] MatchingAgent error: {e}")
            state.current_step = "LOGISTICS"

        # Step 5: Logistics Agent (Call Script & May 2024 Checklist)
        if state.current_step == "LOGISTICS":
            try:
                await self.logistics_agent.generate_logistics(state)
            except Exception as e:
                logger.error(f"[Supervisor] LogisticsAgent error: {e}")
                if not state.document_checklist:
                    state.document_checklist = [
                        "주민등록등본 (정부24 모바일 앱 발급 가능)",
                        "건강보험증 (모바일 건강보험증 앱)",
                        "보호자(부모) 신분증 (주민등록증 또는 운전면허증)",
                        "아기가 최근 복용한 해열제 종류 및 시간 기록",
                    ]
            state.current_step = "COMPLETED"

        # Step 6: Single-Exit Medical Service Act Art. 27 Sanitization Gateway
        hosp_details = ""
        if state.matched_hospitals:
            top_hosp = state.matched_hospitals[0]
            h_name = top_hosp.get("기관명", "")
            h_type = top_hosp.get("유형", "병원")
            h_dist = top_hosp.get("거리_km", 0.0)
            hosp_details = f"🏥 추천 내원 기관: [{h_type}] {h_name} (약 {h_dist}km)"

            if state.matched_pharmacies:
                top_pharm = state.matched_pharmacies[0]
                p_name = top_pharm.get("약국명", "")
                p_margin = top_pharm.get("안전마진_분", 30)
                hosp_details += f"\n💊 30분 안심 조제 약국: {p_name} (+{p_margin}분 조제 마진 확보)"

        final_response_text = (
            f"{empathy_msg}\n\n{hosp_details}\n\n"
            f"출발 전 아래 '30초 유선 확인 통화 스크립트'로 확인 후 내원하시기 바랍니다."
        )
        sanitized_final_text = sanitize_output(final_response_text)
        if state.conversation_history and state.conversation_history[-1].role == "assistant":
            state.conversation_history[-1].content = sanitized_final_text
        else:
            state.add_message(role="assistant", content=sanitized_final_text)
        await self.session_manager.save_session(state)

        return SupervisorResponse(
            session_id=state.session_id,
            current_step=state.current_step,
            turn_count=state.turn_count,
            is_emergency=False,
            message=sanitized_final_text,
            emergency_guide=None,
            hospitals=state.matched_hospitals,
            pharmacies=state.matched_pharmacies,
            call_script=state.call_script,
            checklist=state.document_checklist,
        )
