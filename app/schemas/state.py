"""Shared patient session state DTO (PatientSessionState) for MoonlightCare multi-agent layer.

Acts as the single source of truth across all deterministic tools and AI agents,
tracking conversation turns, triage variables, location, and FSM lifecycle steps.
"""

from __future__ import annotations

import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field

KST = datetime.timezone(datetime.timedelta(hours=9))


class MessageRecord(BaseModel):
    """Single chat dialogue turn."""

    role: str = Field(..., description="메시지 발화 주체 ('user' | 'assistant' | 'system')")
    content: str = Field(..., description="대화 메시지 내용")
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(KST).isoformat(),
        description="발화 시각 (KST ISO)",
    )


class PatientSessionState(BaseModel):
    """Shared state object passed through Guardrail, Triage, Matching, and Logistics agents."""

    # 1. Session Identification & FSM Lifecycle
    session_id: str = Field(..., description="고유 세션 식별자 (UUID 등)")
    current_step: str = Field(
        default="INIT",
        description="현재 FSM 상태 ('INIT' | 'TRIAGE' | 'MATCHING' | 'LOGISTICS' | 'EMERGENCY_ESCALATION' | 'COMPLETED')",
    )
    turn_count: int = Field(default=0, description="현재까지 진행된 대화 턴 수 (최대 3턴 제한)")

    # 2. Patient Demographics & Clinical Triage Variables (4대 필수 변수)
    age_months: Optional[int] = Field(default=None, description="환아 월령 (개월 수, e.g. 14)")
    age_days: Optional[int] = Field(default=None, description="환아 일령 (생후 N일, e.g. 55)")
    temperature: Optional[float] = Field(default=None, description="현재 측정 체온 (℃, e.g. 38.5)")
    duration_hours: Optional[int] = Field(default=None, description="증상 지속 시간 (시간 단위, e.g. 3)")
    symptoms: list[str] = Field(default_factory=list, description="환아 주증상 목록 (e.g. ['발열', '구토'])")

    # 3. User Geolocation (GPS)
    user_lat: float = Field(default=37.5133, description="보호자 현재 GPS 위도 (기본: 서울 송파구 잠실역)")
    user_lon: float = Field(default=127.1001, description="보호자 현재 GPS 경도 (기본: 서울 송파구 잠실역)")
    user_address: Optional[str] = Field(default=None, description="보호자 입력 또는 역지오코딩 주소")

    # 4. Emergency Red Flag Protocol (2-Tier Guardrail: 0ms Rule + Gemini Thinking)
    is_red_flag: bool = Field(default=False, description="KTAS 생명 위급 응급 징후 감지 여부")
    red_flag_reason: Optional[str] = Field(default=None, description="Red Flag 감지 사유 (e.g. '생후 100일 미만 고열')")
    emergency_action_guide: Optional[str] = Field(
        default=None, description="구급차 도착 전 1차 응급 처치 가이드 (기도 확보, 혀 물림 방지 등)"
    )
    ktas_level: Optional[int] = Field(default=None, description="공식 KTAS 분류 등급 (1~5)")
    ktas_level_name: Optional[str] = Field(default=None, description="KTAS 등급 명칭 (소생/긴급/응급/준응급/비응급)")
    matched_nacrs_code: Optional[str] = Field(default=None, description="매핑된 주증상 NACRS 코드 (e.g. 553, 008, 852)")
    matched_symptom_name: Optional[str] = Field(default=None, description="매핑된 KTAS 공식 주증상명")
    clinical_rationale: Optional[str] = Field(default=None, description="비정형 문맥 완독 및 임상 감별 근거")
    time_trajectory_assessment: Optional[str] = Field(default=None, description="시간 경과 및 가역성 평가")

    # 5. Matching & Logistics Results
    matched_hospitals: list[dict[str, Any]] = Field(
        default_factory=list, description="추천 응급실 또는 야간 소아과 목록 (TOP 3)"
    )
    matched_pharmacies: list[dict[str, Any]] = Field(
        default_factory=list, description="30분 안전 마진 확보된 인근 야간 조제 약국 목록"
    )
    call_script: Optional[str] = Field(default=None, description="30초 병원 유선 확인 스크립트")
    document_checklist: list[str] = Field(
        default_factory=list, description="2024년 5월 본인확인 의무화 지참 서류 체크리스트"
    )

    # 6. Dialogue History & Timestamps
    conversation_history: list[MessageRecord] = Field(
        default_factory=list, description="대화 기록 전체 히스토리"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.datetime.now(KST).isoformat(),
        description="세션 생성 시각 (KST)",
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.datetime.now(KST).isoformat(),
        description="최종 상태 갱신 시각 (KST)",
    )

    def add_message(self, role: str, content: str) -> None:
        """Appends a message to conversation history and increments turn count for user messages."""
        self.conversation_history.append(MessageRecord(role=role, content=content))
        if role == "user":
            self.turn_count += 1
        self.updated_at = datetime.datetime.now(KST).isoformat()

    def escalate_to_emergency(self, reason: str, guide: str) -> None:
        """Immediately halts normal triage flow and escalates state to EMERGENCY_ESCALATION."""
        self.is_red_flag = True
        self.red_flag_reason = reason
        self.emergency_action_guide = guide
        self.current_step = "EMERGENCY_ESCALATION"
        self.updated_at = datetime.datetime.now(KST).isoformat()

    def is_triage_complete(self) -> bool:
        """Checks whether the 4 essential triage variables have been gathered."""
        return (
            (self.age_months is not None or self.age_days is not None)
            and self.temperature is not None
            and bool(self.symptoms)
        )
