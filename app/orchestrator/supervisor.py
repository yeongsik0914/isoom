"""Main Orchestrator (Supervisor FSM) for MoonlightCare Multi-Agent Layer.

Coordinates Guardrail, Triage, Matching, and Logistics agents via
a deterministic 6-state FSM with a 3-turn deadlock guard, instant Red Flag escalation,
and a single-exit Medical Service Act Art. 27 sanitization gateway.
"""

from __future__ import annotations

import logging
import re
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

    async def _handle_emergency_escalation(
        self,
        state: PatientSessionState,
        user_message: str,
    ) -> SupervisorResponse:
        """Handles immediate 119 emergency escalation for Tier 1 or Tier 2 Red Flags."""
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
            age_months=state.age_months,
            temperature=state.temperature,
            ktas_level=state.ktas_level or 1,
            ktas_level_name=state.ktas_level_name or "소생/긴급 (Red Flag)",
            symptoms=state.symptoms or ["응급 위험 징후"],
            hospitals=state.matched_hospitals,
            pharmacies=[],
            call_script=None,
            checklist=["주민등록등본 또는 모바일 건강보험증", "보호자 신분증"],
        )

    async def process_turn(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        user_lat: float = 37.5133,
        user_lon: float = 127.1001,
        user_address: Optional[str] = None,
        force_matching: bool = False,
    ) -> SupervisorResponse:
        """Executes a single conversational turn through the FSM pipeline.

        1. Retrieves or creates PatientSessionState.
        2. Performs instant (0ms) Red Flag guardrail check.
           -> If triggered: aborts all agents immediately, escalates to EMERGENCY_ESCALATION.
        3. Executes Triage Agent to extract demographics and clinical variables.
           -> If variables incomplete and turn_count < 3 and not force_matching: stays in TRIAGE and returns follow-up inquiry.
           -> If complete OR turn_count >= 3 (Deadlock Guard) OR force_matching (Phase 1 1-shot): transitions to MATCHING.
        4. Executes Matching Agent (Zero-LLM 2-Track Clinical Router).
           -> Transitions to LOGISTICS.
        5. Executes Logistics Agent (30-sec Call Script & May 2024 Document Checklist).
           -> Transitions to COMPLETED.
        6. Passes output through the Medical Service Act Art. 27 single-exit sanitization gateway.
        7. Saves updated state and returns structured SupervisorResponse with clinical vital chips.
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

        # Step 2: 0ms Red Flag Pre-Interceptor (Checked Every Turn - Tier 1)
        is_red = check_red_flag_instant(user_message, state)
        if is_red or state.is_red_flag:
            return await self._handle_emergency_escalation(state, user_message)

        # Step 3: Triage & Deadlock Guard (Tier 2 KTAS Grounding)
        empathy_msg = "아이가 열이 나서 보호자님께서도 많이 걱정되시겠습니다."
        if state.current_step in ("INIT", "TRIAGE"):
            try:
                triage_res = await self.triage_agent.triage_message(user_message, state)
                empathy_msg = triage_res.empathy_message or empathy_msg
            except Exception as e:
                logger.error(f"[Supervisor] TriageAgent error (using fallback): {e}")
                empathy_msg = "아이가 많이 힘들어해서 많이 놀라셨겠습니다. 안전한 진료 시설을 신속히 확인해 드리겠습니다."

            # Check if Tier 2 (Triage Agent KTAS Grounding) triggered Red Flag
            if state.is_red_flag:
                return await self._handle_emergency_escalation(state, user_message)

            # Check if user explicitly indicated unknown age or temperature
            is_explicit_unknown_age = any(k in user_message for k in ["나이는 미입력", "나이 모름", "나이 미입력", "나이: 미입력"])
            is_explicit_unknown_temp = any(k in user_message for k in ["체온은 미측정", "체온 모름", "체온 미측정", "체온: 미측정"])
            if is_explicit_unknown_age:
                state.age_months = None
                state.age_days = None
            if is_explicit_unknown_temp:
                state.temperature = None

            # Check Triage Completion or 3-Turn Upper Bound (Deadlock Guard) or force_matching (Phase 1 1-shot)
            is_complete = state.is_triage_complete()
            turn_limit_reached = state.turn_count >= 3

            if is_complete or turn_limit_reached or force_matching:
                # If forced transition due to turn limit or force_matching, validate clinical intent
                if not is_complete and (turn_limit_reached or force_matching):
                    # Extract the pure symptom text portion if sent via structured front format
                    symptom_target_text = user_message
                    if "주요 증상:" in user_message:
                        part = user_message.split("주요 증상:", 1)[1]
                        if ", 투약/동반:" in part:
                            part = part.split(", 투약/동반:", 1)[0]
                        symptom_target_text = part.strip()

                    clinical_patterns = [
                        r"(?<!해)열(?!제)|발열|고열|미열|초고열|불덩|뜨거|뜨겁",
                        r"기침|콜록|컹컹|콧물|코막|가래|쌕쌕|쌕색|천명|숨소리|호흡|헐떡|숨차",
                        r"구토|토했|토하|게우|분수토|올렸어|설사|피똥|혈변|배가\s*아|배아파|배아프|복통|배통증",
                        r"처짐|축\s*처|늘어져|기면|보챔|칭얼|울음|자지러|안자|경련|경기|발작|떨림|의식",
                        r"발진|열꽃|두드러기|가려|수포|물집|화상|피가|출혈|다침|상처|골절",
                        r"귀가\s*아|이통|눈곱|눈꼽|탈수|기저귀.*안|소변.*안|안먹|수유\s*거부|침흘림",
                    ]
                    has_symptoms = bool(state.symptoms) or any(re.search(pat, symptom_target_text) for pat in clinical_patterns)

                    # If user entered non-symptom gibberish or chatter (e.g. "안녕", "배고파", "ㅋㅋㅋ", "asdf"):
                    if not has_symptoms and not turn_limit_reached:
                        state.current_step = "TRIAGE"
                        inquiry = "소아 야간 의료기관 안내를 위해 아이의 구체적인 증상(예: 열, 기침, 구토, 콧물, 복통, 처짐 등)을 알려주세요."
                        sanitized_inquiry = sanitize_output(inquiry)
                        state.add_message(role="assistant", content=sanitized_inquiry)
                        await self.session_manager.save_session(state)
                        return SupervisorResponse(
                            session_id=state.session_id,
                            current_step=state.current_step,
                            turn_count=state.turn_count,
                            is_emergency=False,
                            message=sanitized_inquiry,
                            age_months=state.age_months,
                            temperature=state.temperature,
                            ktas_level=None,
                            ktas_level_name=None,
                            symptoms=[],
                            hospitals=[],
                            pharmacies=[],
                            call_script=None,
                            checklist=[],
                        )

                    # Do NOT overwrite age or temperature if user chose unknown!
                    if is_explicit_unknown_age:
                        state.age_months = None
                        state.age_days = None
                    elif state.age_months is None:
                        state.age_months = 24

                    if is_explicit_unknown_temp:
                        state.temperature = None
                    elif state.temperature is None:
                        state.temperature = 38.0

                    if not state.symptoms:
                        state.symptoms = ["소아 불편감"]

                    if not state.ktas_level:
                        temp = state.temperature
                        syms = " ".join(state.symptoms) if state.symptoms else ""
                        if (temp is not None and temp >= 39.0) or any(k in syms for k in ["구토", "처짐", "복통", "호흡", "탈수", "설사"]):
                            state.ktas_level = 3
                            state.ktas_level_name = "응급 (달빛어린이병원 우선 권고)"
                        elif (temp is not None and temp >= 38.0) or any(k in syms for k in ["발열", "기침", "콧물", "열", "보챔", "칭얼"]):
                            state.ktas_level = 4
                            state.ktas_level_name = "준응급 (달빛어린이병원 권고)"
                        else:
                            state.ktas_level = 4 if any(k in syms for k in ["보챔", "칭얼", "통증", "아파"]) else 5
                            state.ktas_level_name = "준응급 (달빛어린이병원 권고)" if state.ktas_level == 4 else "비응급 (외래 진료 또는 가정 케어)"
                    elif not state.ktas_level_name:
                        level_names = {1: "소생", 2: "긴급", 3: "응급", 4: "준응급", 5: "비응급"}
                        state.ktas_level_name = level_names.get(state.ktas_level, "준응급")

                    if turn_limit_reached:
                        empathy_msg += "\n\n※ 증상 입력이 불충분하여 더 이상 지체하지 않고 보호자님 현재 위치 기준 가장 안전한 야간 의료기관으로 우선 안내합니다."

                state.current_step = "MATCHING"
            else:
                # Still incomplete and turn_count < 3 and not force_matching: Stay in TRIAGE and ask for missing variables
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
                    age_months=state.age_months,
                    temperature=state.temperature,
                    ktas_level=state.ktas_level,
                    ktas_level_name=state.ktas_level_name,
                    symptoms=state.symptoms,
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
            age_months=state.age_months,
            temperature=state.temperature,
            ktas_level=state.ktas_level or 4,
            ktas_level_name=state.ktas_level_name or "준응급",
            symptoms=state.symptoms,
            hospitals=state.matched_hospitals,
            pharmacies=state.matched_pharmacies,
            call_script=state.call_script,
            checklist=state.document_checklist,
        )

