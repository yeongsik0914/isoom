"""Pydantic schemas for Chat and Session REST endpoints."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.schemas.state import MessageRecord


class ChatRequest(BaseModel):
    """Payload for POST /api/v1/chat endpoint."""

    user_message: str = Field(..., min_length=1, description="보호자 입력 메시지 (증상, 문의사항 등)")
    session_id: Optional[str] = Field(default=None, description="기존 세션 ID (미지정 시 신규 세션 자동 발급)")
    user_lat: float = Field(default=37.5133, description="사용자 GPS 위도 (기본값: 서울 잠실역 37.5133)")
    user_lon: float = Field(default=127.1001, description="사용자 GPS 경도 (기본값: 서울 잠실역 127.1001)")
    user_address: Optional[str] = Field(default=None, description="사용자 거주지 또는 현재 지번/도로명 주소")
    stream: bool = Field(default=False, description="Server-Sent Events (SSE) 실시간 스트리밍 여부")
    force_matching: bool = Field(
        default=False,
        description="1턴 즉시 매칭 강제 플래그 (Phase 1 단발성 증상 입력 화면 input.html 전용: 결측치 안전 기본값 채움)",
    )
    patient_vitals: Optional[dict[str, Any]] = Field(default=None, description="단발성 문진 화면 전달 바이탈 정보")
    age_months: Optional[int] = Field(default=None, description="환아 월령 (미입력/모름 시 None)")
    temperature: Optional[float] = Field(default=None, description="환아 체온 (미입력/모름 시 None)")



class SessionDetailResponse(BaseModel):
    """Detailed view of an active patient session state."""

    session_id: str = Field(..., description="고유 세션 식별자")
    current_step: str = Field(..., description="현재 FSM 단계")
    turn_count: int = Field(..., description="대화 턴 수")
    is_red_flag: bool = Field(..., description="Red Flag 긴급 감지 여부")
    red_flag_reason: Optional[str] = Field(default=None, description="Red Flag 사유")
    age_months: Optional[int] = Field(default=None, description="환아 월령")
    temperature: Optional[float] = Field(default=None, description="환아 체온 (℃)")
    duration_hours: Optional[int] = Field(default=None, description="증상 지속 시간")
    symptoms: list[str] = Field(default_factory=list, description="확인된 증상 목록")
    created_at: str = Field(..., description="세션 생성 일시")
    updated_at: str = Field(..., description="최근 갱신 일시")
    messages: list[MessageRecord] = Field(default_factory=list, description="대화 이력 히스토리")
