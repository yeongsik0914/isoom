"""Logistics Agent powered by Gemini 3.5 Flash-Lite.

Responsibilities:
1. 30-Second Telephone Confirmation Script Generation:
   Creates a word-for-word, 30-second telephone script for panicked parents to read
   directly to hospital triage/intake desks before departing home.
2. Mandatory Identity Verification Document Checklist:
   Enforces the May 2024 National Health Insurance Act revision (요양기관 본인확인 의무화 제도)
   requiring parent ID and child family relation verification documents.
3. Rapid Execution: Optimized for sub-second serving latency with deterministic fallback.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.config import settings
from app.schemas.state import PatientSessionState

logger = logging.getLogger(__name__)


class LogisticsCardResult(BaseModel):
    """Structured output schema for Logistics Agent."""

    call_script: str = Field(..., description="병원 출발 전 30초 유선 확인 통화 스크립트")
    document_checklist: list[str] = Field(..., description="본인확인 의무화 서류 및 지참물 체크리스트")


LOGISTICS_SYSTEM_PROMPT = """당신은 소아 야간 응급 안내 서비스 'MoonlightCare'의 병원 방문 출동 코디네이터 AI입니다.
보호자가 추천된 병원에 출발하기 직전 가장 빠르고 안전하게 준비할 수 있도록 지원합니다.

[역할 및 지침]
1. '30초 유선 확인 통화 스크립트'를 생성하십시오:
   - 당황한 보호자가 병원 안내데스크나 응급실에 전화하여 그대로 읽을 수 있는 30초 분량의 문장이어야 합니다.
   - 아기의 월령, 현재 체온, 증상 지속 시간, 주요 증상을 명확히 포함하고 소아 진료 가능 여부를 확인하십시오.
2. '2024년 5월 요양기관 본인확인 의무화 지참 서류 및 준비물 체크리스트'를 생성하십시오:
   - 보호자 신분증 (주민등록증, 모바일 신분증 등)
   - 19세 미만 환아 가족관계 확인용 주민등록등본 또는 가족관계증명서
   - 건강보험증 또는 환아 주민등록번호
   - 복용한 해열제 메모 및 체온계
"""


class LogisticsAgent:
    """Logistics Agent for pre-departure phone scripts and document checklists."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        enable_gemini: bool = True,
    ) -> None:
        self.api_key = (api_key or settings.gemini_api_key) if enable_gemini else None
        self.model_name = model_name or settings.gemini_logistics_model
        self._client: Optional[Any] = None

        if self.api_key:
            try:
                import google.genai as genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"[LogisticsAgent] Failed to initialize Google GenAI Client: {e}")
                self._client = None

    async def generate_logistics(
        self,
        state: PatientSessionState,
    ) -> LogisticsCardResult:
        """Generates pre-departure calling script and legal document checklist."""
        result: Optional[LogisticsCardResult] = None

        if self._client:
            result = await self._call_gemini_logistics(state)

        if result is None:
            result = self._fallback_generate_logistics(state)

        # Update state
        state.call_script = result.call_script
        state.document_checklist = result.document_checklist
        state.current_step = "COMPLETED"

        return result

    async def _call_gemini_logistics(
        self,
        state: PatientSessionState,
    ) -> Optional[LogisticsCardResult]:
        """Calls Gemini Flash-Lite with structured output schema."""
        try:
            from google.genai import types

            hosp_name = (
                state.matched_hospitals[0].get("기관명", "응급의료기관")
                if state.matched_hospitals
                else "소아 응급실"
            )

            prompt = (
                f"{LOGISTICS_SYSTEM_PROMPT}\n\n"
                f"[환아 정보]\n"
                f"- 월령: {state.age_months or state.age_days or '미상'}\n"
                f"- 체온: {state.temperature or '고열'}℃\n"
                f"- 증상 지속 시간: {state.duration_hours or 1}시간 경과\n"
                f"- 주증상: {', '.join(state.symptoms) if state.symptoms else '발열'}\n"
                f"- 방문 예정 병원: {hosp_name}\n\n"
                "위 정보를 반영하여 LogisticsCardResult JSON으로 반환하십시오."
            )

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LogisticsCardResult,
                    temperature=0.2,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )

            if response and response.text:
                data = json.loads(response.text)
                return LogisticsCardResult(**data)
        except Exception as e:
            logger.warning(f"[LogisticsAgent] Gemini API failed: {e}. Falling back to default checklist.")

        return None

    def _fallback_generate_logistics(
        self,
        state: PatientSessionState,
    ) -> LogisticsCardResult:
        """Deterministic fallback script and legal document checklist."""
        hosp_name = (
            state.matched_hospitals[0].get("기관명", "응급실")
            if state.matched_hospitals
            else "병원 접수처"
        )

        age_text = (
            f"생후 {state.age_months}개월"
            if state.age_months is not None
            else (f"생후 {state.age_days}일" if state.age_days is not None else "소아")
        )
        temp_text = f"{state.temperature}도" if state.temperature is not None else "고열"
        dur_text = f"{state.duration_hours}시간째" if state.duration_hours is not None else ""
        symptoms_text = ", ".join(state.symptoms) if state.symptoms else "발열 증상"

        call_script = (
            f"\"안녕하세요, {hosp_name} 접수처 맞으신가요? "
            f"지금 {age_text} 아이가 체온 {temp_text}로 {dur_text} {symptoms_text}이 있어 출발하려고 합니다. "
            "현재 소아과 전문의 선생님 진료 및 가용 병상 접수가 가능한 상태인지 확인 부탁드립니다.\""
        )

        document_checklist = [
            "보호자(부모) 신분증 (주민등록증 / 운전면허증 / 모바일 신분증)",
            "환아 가족관계 확인 서류 (주민등록등본 또는 가족관계증명서 - 정부24 전자문서 가능)",
            "환아 건강보험증 또는 주민등록번호 13자리 메모",
            "최근 복용한 해열제 종류 및 마지막 투약 시간 메모",
            "외출용 보온 담요, 여벌 옷, 기저귀, 미온수 텀블러",
        ]

        return LogisticsCardResult(
            call_script=call_script,
            document_checklist=document_checklist,
        )
