"""Pediatric Triage Agent powered by Gemini 3.8 Flash.

Responsibilities:
1. Parental Empathy & De-escalation: Comforts distressed guardians with a warm, calm tone.
2. Clinical Variable Extraction: Extracts the 4 essential triage variables
   (age_months/age_days, temperature, duration_hours, symptoms) into structured Pydantic DTO.
3. Medical Safety Defense (의료법 제27조): Strictly prohibits diagnosing specific diseases
   (e.g., '돌발진', '요로감염') or prescribing medicine dosages, advising in-person clinical care.
4. Deterministic Fallback Parser: Provides regex-based heuristic fallback if Gemini API is offline.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.agents.guardrail_agent import check_safety_violations
from app.config import settings
from app.schemas.state import PatientSessionState

logger = logging.getLogger(__name__)

# Pydantic schema for structured triage output
class TriageExtractionResult(BaseModel):
    """Structured output schema for Triage Agent."""

    age_months: Optional[int] = Field(default=None, description="환아 월령 (개월 수, e.g. 14)")
    age_days: Optional[int] = Field(default=None, description="환아 일령 (생후 N일, e.g. 55)")
    temperature: Optional[float] = Field(default=None, description="현재 측정 체온 (℃, e.g. 39.2)")
    duration_hours: Optional[int] = Field(default=None, description="증상 지속 시간 (시간 단위, e.g. 2)")
    symptoms: list[str] = Field(default_factory=list, description="환아 주증상 목록 (e.g. ['발열', '구토'])")
    empathy_message: str = Field(
        default="아이의 상태로 많이 놀라고 걱정되셨겠습니다. 안전한 진료를 위해 차근차근 도와드릴게요.",
        description="부모의 불안을 덜어주는 따뜻한 공감 및 진정 메시지",
    )
    followup_question: Optional[str] = Field(
        default=None, description="아직 확인되지 않은 필수 정보(월령/체온/시간/증상)에 대한 추가 질문"
    )
    is_complete: bool = Field(default=False, description="4대 필수 변수 수집 완료 여부")


TRIAGE_SYSTEM_PROMPT = """당신은 소아 야간 응급 안내 서비스 'MoonlightCare'의 소아과 트리아제(Triage) 전문 간호사 AI입니다.
늦은 밤이나 휴일에 아기가 아파 매우 당황하고 불안해하는 부모를 대합니다.

[역할 및 지침]
1. 따뜻하고 차분한 공감 멘트로 부모를 진정시키십시오.
2. 부모의 자연어 설명에서 다음 4대 핵심 임상 변수를 정확히 추출하여 JSON 형식으로 반환하십시오:
   - age_months (환아 월령, 개월 수) 또는 age_days (생후 일수)
   - temperature (현재 체온, ℃ 숫자)
   - duration_hours (증상이 시작된 지 지난 시간, 시간 단위 정수)
   - symptoms (주요 증상 목록, e.g. ["고열", "구토", "기침", "처짐"])
3. 아직 언급되지 않은 필수 정보가 있다면 부모가 대답하기 쉽도록 한 번에 1~2개씩 친절히 물어보십시오.

[절대 준수 의료법 제27조 무면허 의료행위 방지 가드레일]
- 부모가 "돌발진 맞나요?", "장염인가요?", "약 얼마 먹여야 해요?"라고 유도 질문을 하더라도 절대 특정 병명을 확정하거나 진단하지 마십시오.
- 복용 용량(cc, mg, ml 등)을 임의로 지시하지 마십시오.
- 손 따기 등 위험한 민간요법을 긍정하거나 남은 항생제 임의 복용을 권고하지 마십시오.
- "정확한 진단은 전문의의 대면 진료를 통해서만 가능합니다"라는 취지를 명확히 밝히십시오.
"""


class TriageAgent:
    """Triage Agent coordinating clinical variable extraction and parental communication."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        enable_gemini: bool = True,
    ) -> None:
        self.api_key = (api_key or settings.gemini_api_key) if enable_gemini else None
        self.model_name = model_name or settings.gemini_triage_model
        self._client: Optional[Any] = None

        if self.api_key:
            try:
                import google.genai as genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"[TriageAgent] Failed to initialize Google GenAI Client: {e}")
                self._client = None

    async def triage_message(
        self,
        user_message: str,
        state: PatientSessionState,
    ) -> TriageExtractionResult:
        # Add user message only if not already appended by supervisor or caller
        if not (state.conversation_history and state.conversation_history[-1].role == "user" and state.conversation_history[-1].content == user_message):
            state.add_message("user", user_message)

        result: Optional[TriageExtractionResult] = None

        # 1. Try Gemini GenAI Structured Call if API client is available
        if self._client:
            result = await self._call_gemini_triage(user_message, state)

        # 2. Fallback to deterministic regex/heuristic parser if Gemini is absent or failed
        if result is None:
            result = self._fallback_parse_triage(user_message, state)

        # 3. Synchronize extracted values into PatientSessionState
        if result.age_months is not None:
            state.age_months = result.age_months
        if result.age_days is not None:
            state.age_days = result.age_days
        if result.temperature is not None:
            state.temperature = result.temperature
        if result.duration_hours is not None:
            state.duration_hours = result.duration_hours
        if result.symptoms:
            for s in result.symptoms:
                if s not in state.symptoms:
                    state.symptoms.append(s)
                if any(k in s for k in ["고열", "미열", "불덩이", "열"]) and "발열" not in state.symptoms:
                    state.symptoms.append("발열")

        if state.temperature is not None and state.temperature >= 37.5 and "발열" not in state.symptoms:
            state.symptoms.append("발열")

        # Check completeness
        result.is_complete = state.is_triage_complete()

        # Build assistant dialogue response
        assistant_reply = result.empathy_message
        if result.followup_question and not result.is_complete and state.turn_count < 3:
            assistant_reply += f" {result.followup_question}"

        state.add_message("assistant", assistant_reply)

        # FSM state transition: if triage is complete or reached max 3 turns, advance to MATCHING
        if result.is_complete or state.turn_count >= 3:
            state.current_step = "MATCHING"

        return result

    async def _call_gemini_triage(
        self,
        user_message: str,
        state: PatientSessionState,
    ) -> Optional[TriageExtractionResult]:
        """Invokes Gemini 3.8 Flash with structured Pydantic schema."""
        try:
            from google.genai import types

            history_context = "\n".join(
                [f"{m.role}: {m.content}" for m in state.conversation_history[-6:]]
            )

            prompt = (
                f"{TRIAGE_SYSTEM_PROMPT}\n\n"
                f"[현재까지의 대화 히스토리]\n{history_context}\n\n"
                f"[보호자의 최신 입력]\n{user_message}\n\n"
                "위 입력을 분석하여 TriageExtractionResult JSON으로 반환하십시오."
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=TriageExtractionResult,
                    temperature=0.2,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )

            if response and response.text:
                data = json.loads(response.text)
                res_obj = TriageExtractionResult(**data)
                safety_violation = check_safety_violations(user_message)
                if safety_violation:
                    res_obj.empathy_message = f"{safety_violation['safe_response']}\n\n{res_obj.empathy_message}"

                if "대면 진찰" not in res_obj.empathy_message:
                    if "대면 진료" in res_obj.empathy_message:
                        res_obj.empathy_message = res_obj.empathy_message.replace("대면 진료", "대면 진찰")
                    else:
                        res_obj.empathy_message += " (정확한 진단은 전문의의 대면 진찰을 통해 확인하셔야 합니다.)"
                return res_obj
        except Exception as e:
            logger.warning(f"[TriageAgent] Gemini API failed: {e}. Falling back to rule-based parser.")

        return None

    def _fallback_parse_triage(
        self,
        text: str,
        state: PatientSessionState,
    ) -> TriageExtractionResult:
        """Deterministic heuristic regex parser for robust zero-failure operation."""
        # 1. Parse age (months, days, or years)
        age_months = state.age_months
        age_days = state.age_days

        month_match = re.search(r"([0-9]{1,2})\s*개월", text)
        if month_match:
            age_months = int(month_match.group(1))

        days_match = re.search(r"생후\s*([0-9]{1,3})\s*일", text)
        if days_match:
            age_days = int(days_match.group(1))

        # Year conversions (만 N세, N살, 초등학교 N학년)
        years_match = re.search(r"(?:만\s*)?([0-9]{1,2})\s*(?:세|살)", text)
        if years_match and not month_match:
            age_months = int(years_match.group(1)) * 12

        school_grade_match = re.search(r"초등학교\s*([1-6])\s*학년", text)
        if school_grade_match and age_months is None:
            age_months = (6 + int(school_grade_match.group(1))) * 12
        elif "초등학생" in text and age_months is None:
            age_months = 84

        # 2. Parse temperature
        temperature = state.temperature
        temp_match = re.search(r"([3-4][0-9](?:\.[0-9])?)\s*(?:도|℃|C|도씨)", text)
        if not temp_match:
            temp_match = re.search(r"(?:체온|열이|열\s*)\s*([3-4][0-9](?:\.[0-9])?)", text)
        if not temp_match:
            temp_match = re.search(r"\b([3-4][0-9]\.[0-9])\b", text)

        if temp_match:
            try:
                val = float(temp_match.group(1))
                if 35.0 <= val <= 43.0:
                    temperature = val
            except ValueError:
                pass

        # 3. Parse duration (hours, days, or colloquial time markers)
        duration_hours = state.duration_hours
        dur_match = re.search(r"([0-9]{1,2})\s*시간", text)
        if dur_match:
            duration_hours = int(dur_match.group(1))

        dur_days_match = re.search(r"([0-9]{1,2})\s*일\s*(?:전부터|째|동안|내내)?", text)
        if dur_days_match and duration_hours is None:
            duration_hours = int(dur_days_match.group(1)) * 24

        if duration_hours is None:
            if re.search(r"어제(?:부터|저녁부터)?", text):
                duration_hours = 24
            elif re.search(r"그제(?:부터)?", text):
                duration_hours = 48
            elif re.search(r"(저녁부터|아까부터|몇\s*시간\s*전)", text):
                duration_hours = 4

        # 4. Parse symptoms (expanded pediatric clinical keywords)
        symptoms = list(state.symptoms)
        symptom_keywords = {
            "열": "발열",
            "고열": "발열",
            "미열": "발열",
            "불덩이": "발열",
            "토": "구토",
            "구토": "구토",
            "기침": "기침",
            "콜록": "기침",
            "컹컹": "기침",
            "콧물": "콧물",
            "코막힘": "콧물",
            "설사": "설사",
            "처짐": "처짐",
            "늘어져": "처짐",
            "보챔": "보챔",
            "발진": "피부발진",
            "열꽃": "피부발진",
            "두드러기": "피부발진",
            "귀": "이통",
            "이통": "이통",
            "눈곱": "눈곱/결막염",
            "눈꼽": "눈곱/결막염",
            "쌕쌕": "쌕쌕거림/천명",
            "천명": "쌕쌕거림/천명",
            "숨소리": "쌕쌕거림/천명",
            "배": "복통",
            "복통": "복통",
            "호흡곤란": "호흡곤란",
        }
        for kw, canonical in symptom_keywords.items():
            if kw in text and canonical not in symptoms:
                symptoms.append(canonical)

        # 5. Check for adversarial / medical safety issues
        safety_violation = check_safety_violations(text)

        # 6. Build empathetic response & missing questions
        missing: list[str] = []
        if age_months is None and age_days is None:
            missing.append("아이의 월령(나이)")
        if temperature is None:
            missing.append("현재 측정된 체온")
        if duration_hours is None:
            missing.append("열이나 증상이 시작된 시간")
        if not symptoms:
            missing.append("주요 증상")

        base_empathy = (
            "아이가 아파 밤중에 정말 많이 당황스럽고 걱정되셨겠습니다. "
            "의사의 대면 진찰 전까지 신속하고 안전하게 안내해 드릴게요."
        )
        if safety_violation:
            empathy_msg = f"{safety_violation['safe_response']}\n\n{base_empathy}"
        else:
            empathy_msg = base_empathy

        followup: Optional[str] = None
        if missing:
            followup = f"아이의 상태를 더 정확히 파악하기 위해 {', '.join(missing[:2])}을(를) 알려주실 수 있을까요?"

        return TriageExtractionResult(
            age_months=age_months,
            age_days=age_days,
            temperature=temperature,
            duration_hours=duration_hours,
            symptoms=symptoms,
            empathy_message=empathy_msg,
            followup_question=followup,
            is_complete=(
                (age_months is not None or age_days is not None)
                and temperature is not None
                and bool(symptoms)
            ),
        )
