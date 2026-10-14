"""Supervisor output schema DTO for client and API consumption."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class SupervisorResponse(BaseModel):
    """Standardized response object returned by SupervisorOrchestrator to API / Frontend."""

    session_id: str = Field(..., description="고유 세션 식별자")
    current_step: str = Field(..., description="FSM 현재 상태 ('TRIAGE' | 'MATCHING' | 'LOGISTICS' | 'EMERGENCY_ESCALATION' | 'COMPLETED')")
    turn_count: int = Field(..., description="현재 세션 대화 턴 수 (최대 3턴)")
    is_emergency: bool = Field(default=False, description="0ms Red Flag 긴급 감지 여부")
    message: str = Field(..., description="보호자 전달 텍스트 (공감 멘트, 보충 질문 또는 종합 진료 안내)")
    emergency_guide: Optional[str] = Field(default=None, description="119 직행 및 구급차 대기 시 기도확보 응급처치 가이드")
    hospitals: list[dict[str, Any]] = Field(default_factory=list, description="소아 가용 응급실 또는 달빛어린이병원 (TOP 3)")
    pharmacies: list[dict[str, Any]] = Field(default_factory=list, description="30분 안전 조제 마진 확보 심야 약국 목록")
    call_script: Optional[str] = Field(default=None, description="내원 전 30초 유선 확인 통화 스크립트")
    checklist: list[str] = Field(default_factory=list, description="2024년 5월 개정 본인확인 의무화 필수 지참 서류 목록")
    disclaimer: str = Field(
        default="※ 본 서비스는 의료법 제27조를 준수하며 의학적 진단을 제공하지 않습니다. 대면 진료를 권장합니다.",
        description="의료법 제27조 준수 법적 면책 고지문",
    )
