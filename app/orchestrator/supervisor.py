"""Main Orchestrator (ClinicalStateGraph + Supervisor FSM) for i-Soom Multi-Agent Layer.

Coordinates Guardrail, Safety-Aware Semantic Cache, Triage (Hybrid RAG + CRAG + Conformal),
Matching (Multi-Objective Pareto + Safety-Constrained Bandit), and Logistics agents via a
declarative StateGraph with 0ms Red Flag early-exit, a 3-turn deadlock guard, and a
single-exit Constitutional Medical Service Act Art. 27 sanitization gateway.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Optional

from app.agents.guardrail_agent import (
    check_red_flag_instant,
    check_safety_violations,
    verify_and_sanitize_clinical_response,
)
from app.agents.logistics_agent import LogisticsAgent
from app.agents.matching_agent import MatchingAgent
from app.agents.triage_agent import TriageAgent
from app.orchestrator.graph import END, ClinicalStateGraph, CompiledStateGraph
from app.orchestrator.session_manager import SessionManager
from app.schemas.state import PatientSessionState
from app.schemas.supervisor import SupervisorResponse
from app.services.auth import create_session_token
from app.services.semantic_cache import semantic_cache
from app.services.telemetry import telemetry

logger = logging.getLogger(__name__)

_CLINICAL_PATTERNS = [
    r"(?<!해)열(?!제)|발열|고열|미열|초고열|불덩|뜨거|뜨겁",
    r"기침|콜록|컹컹|콧물|코막|가래|쌕쌕|쌕색|천명|숨소리|호흡|헐떡|숨차",
    r"구토|토했|토하|게우|분수토|올렸어|설사|피똥|혈변|배가\s*아|배아파|배아프|복통|배통증",
    r"처짐|축\s*처|늘어져|기면|보챔|칭얼|울음|자지러|안자|경련|경기|발작|떨림|의식",
    r"발진|열꽃|두드러기|가려|수포|물집|화상|피가|출혈|다침|상처|골절",
    r"귀가\s*아|이통|눈곱|눈꼽|탈수|기저귀.*안|소변.*안|안먹|수유\s*거부|침흘림",
]


class SupervisorOrchestrator:
    """Declarative StateGraph Master Orchestrator coordinating all i-Soom agents."""

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
        self._workflow: CompiledStateGraph = self._build_workflow()

    def _build_workflow(self) -> CompiledStateGraph:
        graph = ClinicalStateGraph()
        graph.add_node("guardrail", self._node_guardrail)
        graph.add_node("triage", self._node_triage)
        graph.add_node("matching", self._node_matching)
        graph.add_node("logistics", self._node_logistics)
        graph.add_node("emergency", self._node_emergency)
        graph.add_node("output_verifier", self._node_output_verifier)

        graph.set_entry_point("guardrail")
        graph.add_conditional_edges(
            "guardrail",
            lambda ctx: ctx["next_route"],
            {
                "emergency": "emergency",
                "cache_hit": "output_verifier",
                "triage": "triage",
            },
        )
        graph.add_conditional_edges(
            "triage",
            lambda ctx: ctx["next_route"],
            {
                "emergency": "emergency",
                "early_triage": "output_verifier",
                "matching": "matching",
            },
        )
        graph.add_edge("matching", "logistics")
        graph.add_edge("logistics", "output_verifier")
        graph.add_edge("emergency", END)
        graph.add_edge("output_verifier", END)
        return graph.compile()

    async def _handle_emergency_escalation(
        self,
        state: PatientSessionState,
        user_message: str,
        trace: Optional[list[str]] = None,
    ) -> SupervisorResponse:
        """Handles immediate 119 emergency escalation for Tier 1 or Tier 2 Red Flags."""
        logger.warning(
            f"[Supervisor] Red Flag detected on turn {state.turn_count}: {state.red_flag_reason}"
        )
        telemetry.inc("emergency_escalations")
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

        sanitized_escalation, _ = verify_and_sanitize_clinical_response(
            escalation_msg, is_red_flag=True
        )
        state.add_message(role="assistant", content=sanitized_escalation)
        if trace:
            state.pipeline_trace = list(trace)
        await self.session_manager.save_session(state)

        return SupervisorResponse(
            session_id=state.session_id,
            session_token=create_session_token(state.session_id),
            current_step="EMERGENCY_ESCALATION",
            turn_count=state.turn_count,
            is_emergency=True,
            message=sanitized_escalation,
            emergency_guide=state.emergency_action_guide,
            age_months=state.age_months,
            ktas_level=state.ktas_level if state.ktas_level is not None else 2,
            ktas_level_name=state.ktas_level_name or ("1단계(소생)" if state.ktas_level == 1 else "2단계(긴급)"),
            clinical_rationale=state.clinical_rationale or state.red_flag_reason or "12대 소아 위급 상황 즉시 감지 (골든타임 응급 이송)",
            symptoms=state.symptoms or ["응급 위험 징후"],
            hospitals=state.matched_hospitals,
            pharmacies=[],
            call_script=None,
            checklist=["주민등록등본 또는 모바일 건강보험증", "보호자 신분증"],
            uncertainty_score=state.uncertainty_score,
            prediction_set=state.prediction_set,
            pipeline_trace=list(trace or state.pipeline_trace),
        )

    async def _node_guardrail(self, ctx: dict[str, Any]) -> dict[str, Any]:
        state: PatientSessionState = ctx["state"]
        user_message: str = ctx["user_message"]

        is_red = check_red_flag_instant(user_message, state)
        if is_red or state.is_red_flag:
            return {"next_route": "emergency"}

        cached_reply = semantic_cache.lookup(
            query=user_message,
            session_id=ctx.get("orig_session_id"),
            force_matching=bool(ctx.get("force_matching")),
        )
        if cached_reply is not None:
            state.current_step = "COMPLETED"
            return {
                "next_route": "cache_hit",
                "draft_message": cached_reply,
                "early_exit": True,
            }

        return {"next_route": "triage"}

    async def _node_triage(self, ctx: dict[str, Any]) -> dict[str, Any]:
        state: PatientSessionState = ctx["state"]
        user_message: str = ctx["user_message"]
        force_matching: bool = bool(ctx.get("force_matching"))
        patient_age_months: Optional[int] = ctx.get("patient_age_months")
        patient_temperature: Optional[float] = ctx.get("patient_temperature")

        empathy_msg = "아이가 열이 나서 보호자님께서도 많이 걱정되시겠습니다."
        followup_question: Optional[str] = None

        if state.current_step in ("INIT", "TRIAGE"):
            try:
                triage_res = await self.triage_agent.triage_message(user_message, state)
                empathy_msg = triage_res.empathy_message or empathy_msg
                followup_question = triage_res.followup_question
            except Exception as e:
                logger.error(f"[Supervisor] TriageAgent error (using fallback): {e}")
                empathy_msg = "아이가 많이 힘들어해서 많이 놀라셨겠습니다. 안전한 진료 시설을 신속히 확인해 드리겠습니다."

            if state.is_red_flag:
                return {"next_route": "emergency"}

            is_explicit_unknown_age = any(
                k in user_message
                for k in ["나이는 미입력", "나이 모름", "나이 미입력", "나이: 미입력", "나이:미입력"]
            )
            is_explicit_unknown_temp = any(
                k in user_message
                for k in ["체온은 미측정", "체온 모름", "체온 미측정", "체온: 미측정", "체온:미측정"]
            )
            if is_explicit_unknown_age:
                state.age_months = None
                state.age_days = None
            elif patient_age_months is not None:
                state.age_months = patient_age_months

            if is_explicit_unknown_temp:
                state.temperature = None
            elif patient_temperature is not None:
                state.temperature = patient_temperature

            is_complete = state.is_triage_complete()
            turn_limit_reached = state.turn_count >= 3

            if is_complete or turn_limit_reached or force_matching:
                if not is_complete and (turn_limit_reached or force_matching):
                    symptom_target_text = user_message
                    if "주요 증상:" in user_message:
                        part = user_message.split("주요 증상:", 1)[1]
                        if ", 투약/동반:" in part:
                            part = part.split(", 투약/동반:", 1)[0]
                        symptom_target_text = part.strip()

                    has_symptoms = bool(state.symptoms) or any(
                        re.search(pat, symptom_target_text) for pat in _CLINICAL_PATTERNS
                    )

                    if not has_symptoms and not turn_limit_reached:
                        state.current_step = "TRIAGE"
                        inquiry = "소아 야간 의료기관 안내를 위해 아이의 구체적인 증상(예: 열, 기침, 구토, 콧물, 복통, 처짐 등)을 알려주세요."
                        return {
                            "next_route": "early_triage",
                            "early_triage_gibberish": True,
                            "draft_message": inquiry,
                        }

                    if is_explicit_unknown_age:
                        state.age_months = None
                        state.age_days = None
                    if is_explicit_unknown_temp:
                        state.temperature = None
                    if not state.symptoms:
                        state.symptoms = ["소아 불편감"]
                    if not state.ktas_level:
                        state.ktas_level = 4
                        state.ktas_level_name = "준응급 (달빛어린이병원 권고)"
                        if not state.clinical_rationale:
                            state.clinical_rationale = "소아 환아의 안전을 최우선으로 고려하여 전문의 대면 진찰이 가능한 달빛어린이병원 진료를 권고합니다."
                    elif not state.ktas_level_name:
                        level_names = {1: "소생", 2: "긴급", 3: "응급", 4: "준응급", 5: "비응급"}
                        state.ktas_level_name = level_names.get(state.ktas_level, "준응급")

                    if turn_limit_reached:
                        empathy_msg += "\n\n※ 증상 입력이 불충분하여 더 이상 지체하지 않고 보호자님 현재 위치 기준 가장 안전한 야간 의료기관으로 우선 안내합니다."

                state.current_step = "MATCHING"
                return {"next_route": "matching", "empathy_msg": empathy_msg}

            # Stay in TRIAGE and ask for missing info
            state.current_step = "TRIAGE"
            inquiry_text = empathy_msg
            if followup_question and followup_question not in empathy_msg:
                inquiry_text = f"{empathy_msg} {followup_question}".strip()
            return {
                "next_route": "early_triage",
                "early_triage_gibberish": False,
                "draft_message": inquiry_text,
            }

        return {"next_route": "matching", "empathy_msg": empathy_msg}

    async def _node_matching(self, ctx: dict[str, Any]) -> dict[str, Any]:
        state: PatientSessionState = ctx["state"]
        if state.current_step == "MATCHING":
            try:
                await self.matching_agent.match_destinations(state)
            except Exception as e:
                logger.error(f"[Supervisor] MatchingAgent error: {e}")
            state.current_step = "LOGISTICS"
        return {}

    async def _node_logistics(self, ctx: dict[str, Any]) -> dict[str, Any]:
        state: PatientSessionState = ctx["state"]
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
        return {}

    async def _node_emergency(self, ctx: dict[str, Any]) -> dict[str, Any]:
        state: PatientSessionState = ctx["state"]
        trace = list(ctx.get("trace", [])) + ["emergency"]
        resp = await self._handle_emergency_escalation(
            state=state,
            user_message=ctx["user_message"],
            trace=trace,
        )
        return {"response": resp}

    async def _node_output_verifier(self, ctx: dict[str, Any]) -> dict[str, Any]:
        state: PatientSessionState = ctx["state"]
        trace = list(ctx.get("trace", [])) + ["output_verifier"]
        state.pipeline_trace = trace

        # Case A: Early Triage Followup / Non-clinical Chatter Exit
        if "early_triage_gibberish" in ctx:
            raw_msg = str(ctx.get("draft_message", ""))
            sanitized_msg, _ = verify_and_sanitize_clinical_response(raw_msg, is_red_flag=False)
            if state.conversation_history and state.conversation_history[-1].role == "assistant":
                state.conversation_history[-1].content = sanitized_msg
            else:
                state.add_message(role="assistant", content=sanitized_msg)
            await self.session_manager.save_session(state)

            is_gibberish = bool(ctx.get("early_triage_gibberish"))
            resp = SupervisorResponse(
                session_id=state.session_id,
                session_token=create_session_token(state.session_id),
                current_step=state.current_step,
                turn_count=state.turn_count,
                is_emergency=False,
                message=sanitized_msg,
                emergency_guide=None,
                age_months=state.age_months,
                temperature=state.temperature,
                ktas_level=None if is_gibberish else state.ktas_level,
                ktas_level_name=None if is_gibberish else state.ktas_level_name,
                clinical_rationale=None if is_gibberish else state.clinical_rationale,
                symptoms=[] if is_gibberish else state.symptoms,
                hospitals=[],
                pharmacies=[],
                call_script=None,
                checklist=[],
                uncertainty_score=state.uncertainty_score,
                prediction_set=state.prediction_set,
                pipeline_trace=trace,
            )
            return {"response": resp}

        # Case B: Semantic Cache Static Hit
        if ctx.get("early_exit") and ctx.get("draft_message"):
            sanitized_cached, _ = verify_and_sanitize_clinical_response(
                str(ctx["draft_message"]), is_red_flag=False
            )
            await self.session_manager.save_session(state)
            return {
                "response": SupervisorResponse(
                    session_id=state.session_id,
                    session_token=create_session_token(state.session_id),
                    current_step=state.current_step,
                    turn_count=state.turn_count,
                    is_emergency=False,
                    message=sanitized_cached,
                    age_months=state.age_months,
                    temperature=state.temperature,
                    ktas_level=state.ktas_level or 5,
                    ktas_level_name=state.ktas_level_name or "비응급 안내",
                    clinical_rationale="시맨틱 캐시(비임상 일반 안내)",
                    symptoms=state.symptoms,
                    hospitals=[],
                    pharmacies=[],
                    call_script=None,
                    checklist=[],
                    pipeline_trace=trace,
                )
            }

        # Case C: Standard Completed Matching + Logistics Exit
        empathy_msg = str(ctx.get("empathy_msg") or "아이의 상태를 바탕으로 가장 안전한 야간 진료 기관을 안내합니다.")
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
        sanitized_final_text, _ = verify_and_sanitize_clinical_response(
            final_response_text, is_red_flag=False
        )
        if state.conversation_history and state.conversation_history[-1].role == "assistant":
            state.conversation_history[-1].content = sanitized_final_text
        else:
            state.add_message(role="assistant", content=sanitized_final_text)
        await self.session_manager.save_session(state)

        resp = SupervisorResponse(
            session_id=state.session_id,
            session_token=create_session_token(state.session_id),
            current_step=state.current_step,
            turn_count=state.turn_count,
            is_emergency=False,
            message=sanitized_final_text,
            emergency_guide=None,
            age_months=state.age_months,
            temperature=state.temperature,
            ktas_level=state.ktas_level or 4,
            ktas_level_name=state.ktas_level_name or "준응급",
            clinical_rationale=state.clinical_rationale or "소아 KTAS 임상 지침 168개 주증상 대조 분석 결과",
            symptoms=state.symptoms,
            hospitals=state.matched_hospitals,
            pharmacies=state.matched_pharmacies,
            call_script=state.call_script,
            checklist=state.document_checklist,
            uncertainty_score=state.uncertainty_score,
            prediction_set=state.prediction_set,
            pipeline_trace=trace,
        )
        return {"response": resp}

    async def process_turn(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        user_lat: float = 37.5133,
        user_lon: float = 127.1001,
        user_address: Optional[str] = None,
        force_matching: bool = False,
        patient_age_months: Optional[int] = None,
        patient_temperature: Optional[float] = None,
    ) -> SupervisorResponse:
        """Executes a single conversational turn through the compiled ClinicalStateGraph."""
        t0 = time.perf_counter()
        telemetry.inc("orchestrator_turns")

        state = await self.session_manager.get_or_create_session(
            session_id=session_id,
            user_lat=user_lat,
            user_lon=user_lon,
            user_address=user_address,
        )
        if state.current_step == "COMPLETED":
            state.reset_for_new_consultation()
        state.add_message(role="user", content=user_message)

        result_ctx = await self._workflow.ainvoke(
            {
                "state": state,
                "user_message": user_message,
                "orig_session_id": session_id,
                "force_matching": force_matching,
                "patient_age_months": patient_age_months,
                "patient_temperature": patient_temperature,
            }
        )
        total_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        telemetry.observe_latency("orchestrator_total", total_ms)

        response: SupervisorResponse = result_ctx["response"]
        telemetry.record_trace(
            {
                "session_id": response.session_id,
                "step": response.current_step,
                "ktas_level": response.ktas_level,
                "is_emergency": response.is_emergency,
                "uncertainty_score": response.uncertainty_score,
                "trace": response.pipeline_trace,
                "latency_ms": total_ms,
            }
        )
        return response
