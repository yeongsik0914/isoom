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

# Cached compact KTAS Grounding Text
_ktas_grounding_cache: Optional[str] = None


def _get_ktas_grounding_context() -> str:
    """Loads and caches the 168 pediatric symptoms full grounding context (~8,500 tokens)."""
    global _ktas_grounding_cache
    if _ktas_grounding_cache is not None:
        return _ktas_grounding_cache

    dataset_path = settings.project_root / "data" / "ktas_pediatric_dataset.json"
    if dataset_path.exists():
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                db = json.load(f)
            symptoms = db.get("symptoms", [])
            lines = []
            for s in symptoms:
                cons_str = " | ".join(
                    [f"L{c['level']}:{c['criteria']}" for c in s.get("secondary_considerations", [])]
                )
                lines.append(f"[{s['nacrs_code']}] {s['symptom_name']} ({s['category']}) ➔ {cons_str}")
            _ktas_grounding_cache = "\n".join(lines)
            return _ktas_grounding_cache
        except Exception as e:
            logger.warning(f"[TriageAgent] Failed to load KTAS dataset for grounding: {e}")

    _ktas_grounding_cache = ""
    return _ktas_grounding_cache


# Pydantic schema for structured triage output
class TriageExtractionResult(BaseModel):
    """Structured output schema for Triage Agent (v2 Enhanced with KTAS classification)."""

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

    # KTAS v2 Classification & Clinical Reasoning Fields
    ktas_level: Optional[int] = Field(default=None, description="공식 KTAS 분류 등급 (1, 2, 3, 4, 5)")
    ktas_level_name: Optional[str] = Field(default=None, description="KTAS 등급 명칭 (소생/긴급/응급/준응급/비응급)")
    is_red_flag: bool = Field(default=False, description="즉각 생명위협/골든타임 Red Flag 여부 (KTAS 1~2단계)")
    matched_nacrs_code: Optional[str] = Field(default=None, description="매핑된 KTAS 주증상 NACRS 코드")
    matched_symptom_name: Optional[str] = Field(default=None, description="매핑된 KTAS 주증상명")
    clinical_rationale: Optional[str] = Field(default=None, description="비정형 문맥 완독 및 임상 감별 핵심 근거")
    time_trajectory_assessment: Optional[str] = Field(default=None, description="시간 경과 평가 (급성 진행형, 시간차 호전, 지연성 악화 등)")
    recommended_action: Optional[str] = Field(default=None, description="즉각 조치 권고요령 (119 구급차 호출, 달빛어린이병원 방문, 가정 케어 등)")


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

[공식 소아 KTAS 1~5단계 분류 및 비정형 문맥 완독 지침]
4. 주입된 [공식 2021 소아 KTAS 168개 주증상 지식 베이스]를 1:1로 직접 대조하여 환아에게 부합하는 KTAS 분류 등급(1~5단계)과 NACRS 코드, 임상 감별 근거를 도출하십시오.
   - 문맥 완독 원칙: 보호자의 초반 안도성 표현("정신은 차렸다", "열은 떨어졌다")에 현혹되지 말고 문장 후반부의 전신 상태(Ill-appearing)와 시간 경과를 끝까지 완독하십시오.
   - 소아 1차 고려사항 최우선: 심정지, 무의식(GCS 3~8), 지속 경련(발작 진행 중), 심각한 호흡부전(흉벽 함몰+청색증), 중증 아나필락시스는 KTAS 1단계(소생, is_red_flag=True)로 판정하십시오.
   - Red Flag 긴급 판정: 생후 100일 미만 38.0℃ 발열, 수지 절단, 안면/수부 2도 화상, 두부 외상 후 반복 구토, 소아 장중첩증(주기적 복통+딸기잼 혈변), 크룹(흡기 쇳소리+침흘림), 실신 후 지속 발열/Ill-appearing은 KTAS 2단계(긴급, is_red_flag=True)로 판정하십시오.
   - 시간차 호전(가역성) 감별: 고열 병력이 있더라도 해열제 투약 후 땀을 흘리며 식사와 활동성이 완전히 정상 회복(Well-appearing)된 18개월 이상 소아는 KTAS 4단계(준응급, is_red_flag=False)로 판정하십시오.

[음성 인식(STT) 노이즈 복원 및 임상 문맥 정규화 지침]
- 보호자의 메시지는 다급한 소아 응급 상황에서 모바일 음성 인식(STT)을 통해 구어체나 오탈자, 발음 왜곡("삼십팔도오부", "열이 삼팔도", "쌕색거려", "해열재", "분수토햇어", "축쳐져", "경기")으로 전달될 수 있습니다.
- 이러한 음성 전사 노이즈나 부정확한 맞춤법에 구애받지 말고, 전체 임상 맥락을 복원하여 의학적 표준 증상(발열, 천명음, 구토, 보챔, 기면/처짐, 경련 등)으로 정규화하여 추출하십시오.
- 보호자가 숫자가 아닌 한글 음성으로 체온을 말한 경우("삼십팔도 오부" -> 38.5, "삼십구도" -> 39.0) 정확히 수치화하여 temperature 필드에 반영하십시오.
- 보호자가 구체적 체온 수치를 언급하지 않고 단순히 "열나요", "열이 있어요", "미열이 있어요" 등 증상 명칭만 표현한 경우, temperature 필드는 null로 두고 증상 목록(symptoms)에 반영하여 다음 턴에서 구체적인 현재 체온을 확인하십시오. (단, "초고열", "불덩이 같아요" 등 즉각적 위급 표현이면서 체온 측정이 불가능한 극단적 상황일 때만 추정치 39.5℃ 이상을 보수적으로 고려하십시오.)
- 보호자가 나이나 체온을 "모름" 또는 "미입력"으로 전달하더라도 에러를 발생시키지 말고, 소아 안전 기준(Safe Default)으로 위험도를 보수적으로 평가하며 신속한 병원 탐색을 지원하십시오.

[절대 준수 의료법 제27조 무면허 의료행위 방지 가드레일]
- 부모가 "돌발진 맞나요?", "장염인가요?", "약 얼마 먹여야 해요?"라고 유도 질문을 하더라도 절대 특정 병명을 확정하거나 진단하지 마십시오.
- 복용 용량(cc, mg, ml 등)을 임의로 지시하지 마십시오.
- 손 따기 등 위험한 민간요법을 긍정하거나 남은 항생제 임의 복용을 권고하지 마십시오.
- "정확한 진단은 전문의의 대면 진찰을 통해서만 가능합니다"라는 취지를 명확히 밝히십시오.
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

        # Synchronize KTAS v2 Classification metadata onto state
        if result.ktas_level is not None:
            state.ktas_level = result.ktas_level
            state.ktas_level_name = result.ktas_level_name or (
                "1단계(소생)" if result.ktas_level == 1 else ("2단계(긴급)" if result.ktas_level == 2 else f"KTAS {result.ktas_level}단계")
            )
        if result.matched_nacrs_code:
            state.matched_nacrs_code = result.matched_nacrs_code
        if result.matched_symptom_name:
            state.matched_symptom_name = result.matched_symptom_name
        if result.clinical_rationale:
            state.clinical_rationale = result.clinical_rationale
        if result.time_trajectory_assessment:
            state.time_trajectory_assessment = result.time_trajectory_assessment

        # Immediate escalation if Tier 2 Gemini Thinking detects a Red Flag (KTAS 1 or 2)
        if result.is_red_flag or (result.ktas_level is not None and result.ktas_level in (1, 2)):
            state.is_red_flag = True
            state.escalate_to_emergency(
                reason=result.clinical_rationale or state.red_flag_reason or "KTAS 1~2단계 위급 응급 징후 감지",
                guide=result.recommended_action
                or state.emergency_action_guide
                or "즉시 119 구급차를 호출하거나 가장 가까운 소아전문응급의료센터로 직행하십시오.",
            )

        # Check completeness
        result.is_complete = state.is_triage_complete()

        # Build assistant dialogue response
        assistant_reply = result.empathy_message
        if result.followup_question and not result.is_complete and state.turn_count < 3 and not state.is_red_flag:
            assistant_reply += f" {result.followup_question}"

        state.add_message("assistant", assistant_reply)

        # FSM state transition: if triage is complete or reached max 3 turns, advance to MATCHING
        if not state.is_red_flag and (result.is_complete or state.turn_count >= 3):
            state.current_step = "MATCHING"

        return result

    async def _call_gemini_triage(
        self,
        user_message: str,
        state: PatientSessionState,
    ) -> Optional[TriageExtractionResult]:
        """Invokes Gemini 3.8 Flash Thinking with Direct Grounded pediatric KTAS knowledge."""
        try:
            from google.genai import types

            history_context = "\n".join(
                [f"{m.role}: {m.content}" for m in state.conversation_history[-6:]]
            )

            grounding_text = _get_ktas_grounding_context()

            prompt = (
                f"{TRIAGE_SYSTEM_PROMPT}\n\n"
                f"[공식 2021 소아 KTAS 168개 주증상 및 세부 지식 베이스]\n{grounding_text}\n\n"
                f"[현재까지의 대화 히스토리]\n{history_context}\n\n"
                f"[보호자의 최신 입력]\n{user_message}\n\n"
                "위 입력을 분석하여 TriageExtractionResult JSON으로 반환하십시오."
            )

            config_args = {
                "response_mime_type": "application/json",
                "response_schema": TriageExtractionResult,
                "temperature": 0.1,
                "thinking_config": types.ThinkingConfig(thinking_budget=1024),
                "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
            }

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(**config_args),
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

        # 2. Parse temperature (including Korean verbal representations)
        temperature = state.temperature
        temp_match = re.search(r"([3-4][0-9](?:\.[0-9])?)\s*(?:도|℃|C|도씨)", text)
        if not temp_match:
            temp_match = re.search(r"(?:체온|열이|열\s*)\s*([3-4][0-9](?:\.[0-9])?)", text)
        if not temp_match:
            temp_match = re.search(r"\b([3-4][0-9]\.[0-9])\b", text)

        # Korean verbal temp fallback (e.g. 삼십팔도, 삼팔도 오부)
        if not temp_match:
            korean_temp_map = {
                "삼십팔도": 38.0, "삼팔도": 38.0, "삼십구도": 39.0, "삼구도": 39.0, "사십도": 40.0,
                "삼십칠도": 37.0, "삼칠도": 37.0
            }
            for kt, kv in korean_temp_map.items():
                if kt in text:
                    temperature = kv + (0.5 if any(b in text for b in ["오부", "5부", "반", "점오", "쩜오"]) else 0.0)
                    break

        if temp_match and temperature is None:
            try:
                val = float(temp_match.group(1))
                if 35.0 <= val <= 43.0:
                    temperature = val
            except ValueError:
                pass

        # 2-1. Colloquial symptom-based temperature fallback (Extreme urgent markers only)
        # Generic symptoms like "열나요", "미열" remain in symptoms for multi-turn triage clarification.
        if temperature is None:
            if re.search(r"초고열|불덩이\s*같|열이\s*펄펄", text):
                temperature = 40.0


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

        # 4. Parse symptoms (expanded pediatric clinical & voice STT keywords)
        symptoms = list(state.symptoms)
        symptom_keywords = {
            "열": "발열",
            "고열": "발열",
            "미열": "발열",
            "불덩이": "발열",
            "해열재": "발열",
            "해열제": "발열",
            "토": "구토",
            "구토": "구토",
            "분수토": "구토",
            "기침": "기침",
            "콜록": "기침",
            "컹컹": "기침",
            "콧물": "콧물",
            "코막힘": "콧물",
            "설사": "설사",
            "처짐": "처짐",
            "축쳐": "처짐",
            "늘어져": "처짐",
            "보챔": "보챔",
            "칭얼": "보챔",
            "발진": "피부발진",
            "열꽃": "피부발진",
            "두드러기": "피부발진",
            "귀": "이통",
            "이통": "이통",
            "눈곱": "눈곱/결막염",
            "눈꼽": "눈곱/결막염",
            "쌕쌕": "쌕쌕거림/천명",
            "쌕색": "쌕쌕거림/천명",
            "쌕섹": "쌕쌕거림/천명",
            "천명": "쌕쌕거림/천명",
            "숨소리": "쌕쌕거림/천명",
            "호흡곤란": "호흡곤란",
            "숨차": "호흡곤란",
            "배": "복통",
            "복통": "복통",
            "경련": "경련",
            "경기": "경련",
            "경끼": "경련",
            "발작": "경련",
            "탈수": "탈수",
            "소변": "탈수",
        }
        for kw, canonical in symptom_keywords.items():
            if kw in text and canonical not in symptoms:
                symptoms.append(canonical)

        # 5. Check for adversarial / medical safety issues
        safety_violation = check_safety_violations(text)

        # 6. Preserve or populate KTAS v2 metadata in fallback mode
        ktas_level = state.ktas_level
        ktas_level_name = state.ktas_level_name
        is_red_flag = state.is_red_flag
        matched_nacrs_code = state.matched_nacrs_code
        matched_symptom_name = state.matched_symptom_name
        clinical_rationale = state.clinical_rationale
        time_trajectory_assessment = state.time_trajectory_assessment
        recommended_action = state.emergency_action_guide

        # Safety check: Infant high fever (<= 100 days or <= 3 months + temp >= 38.0)
        if not is_red_flag:
            if (age_days is not None and age_days <= 100 and temperature is not None and temperature >= 38.0) or (
                age_months is not None and age_months <= 3 and temperature is not None and temperature >= 38.0
            ):
                is_red_flag = True
                ktas_level = 2
                ktas_level_name = "2단계(긴급)"
                matched_nacrs_code = "003"
                matched_symptom_name = "발열"
                clinical_rationale = "생후 100일(3개월) 이하 영아의 38℃ 이상 발열은 균혈증 및 패혈증 위험으로 KTAS 2단계(긴급) 즉시 분류"
                recommended_action = "지체 없이 가장 가까운 대학병원 소아전문응급의료센터로 즉시 이동하십시오."

        # 7. Build empathetic response & missing questions
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
            ktas_level=ktas_level,
            ktas_level_name=ktas_level_name,
            is_red_flag=is_red_flag,
            matched_nacrs_code=matched_nacrs_code,
            matched_symptom_name=matched_symptom_name,
            clinical_rationale=clinical_rationale,
            time_trajectory_assessment=time_trajectory_assessment,
            recommended_action=recommended_action,
        )
