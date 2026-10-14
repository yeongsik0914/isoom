"""Pydantic schemas for Emergency & Spatial REST endpoints."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field

from app.schemas.emergency import RankedEmergencyHospital


class NearbyEmergencyResponse(BaseModel):
    """Response DTO for GET /api/v1/emergency/nearby endpoint."""

    user_lat: float = Field(..., description="요청 사용자 위도")
    user_lon: float = Field(..., description="요청 사용자 경도")
    radius_km: float = Field(..., description="탐색 반경 (km)")
    is_holiday: bool = Field(..., description="KASI 공휴일/주말 여부")
    holiday_name: str = Field(..., description="특일 구분 명칭")
    surge_risk_level: str = Field(..., description="응급실 과밀화 리스크 (NORMAL | HIGH | CRITICAL)")
    hospitals: list[RankedEmergencyHospital] = Field(
        default_factory=list, description="Haversine 구면거리로 정렬된 소아 응급실 목록"
    )
    total_found: int = Field(..., description="탐색 반경 내 총 검색 병원 수")
    acceptable_count: int = Field(..., description="즉시 소아 수용 가능 병원 수")
    latency_ms: float = Field(..., description="API 내부 연산 소요 시간 (ms)")


class PairingSearchResponse(BaseModel):
    """Response DTO for GET /api/v1/emergency/pairings endpoint."""

    user_lat: float = Field(..., description="요청 사용자 위도")
    user_lon: float = Field(..., description="요청 사용자 경도")
    radius_km: float = Field(..., description="탐색 반경 (km)")
    pairings: list[dict[str, Any]] = Field(
        default_factory=list, description="달빛어린이병원 + 30분 마진 심야약국 1:1 페어링 세트"
    )
    total_found: int = Field(..., description="검색된 페어링 수")
    latency_ms: float = Field(..., description="연산 소요 시간 (ms)")


class SyncTriggerResponse(BaseModel):
    """Response DTO for on-demand synchronization execution."""

    status: str = Field(..., description="동기화 결과 상태 ('SUCCESS' | 'SKIPPED' | 'FAILED')")
    total_count: int = Field(..., description="수집된 전체 응급실 수")
    synced_count: int = Field(..., description="Firestore에 실제 갱신 쓰기된 병원 수")
    skipped_count: int = Field(..., description="Hash Diffing에 의해 쓰기 생략된 병원 수")
    acceptable_count: int = Field(..., description="소아 진료 수용 가능 병원 수")
    surge_risk_level: str = Field(..., description="과밀화 위험 등급")
    saving_rate_percent: float = Field(..., description="비용 절감율 (%)")
    triggered_at: str = Field(..., description="동기화 실행 시각")


class SchedulerStatusResponse(BaseModel):
    """Response DTO for background scheduler status."""

    running: bool = Field(..., description="스케줄러 가동 여부")
    jobs: list[dict[str, Any]] = Field(default_factory=list, description="등록된 백그라운드 작업 목록")
    last_bed_poll_time: Optional[str] = Field(default=None, description="최근 5분 주기 실시간 병상 폴링 시각")
    last_bed_poll_stats: Optional[dict[str, Any]] = Field(default=None, description="최근 병상 폴링 통계")
    last_static_sync_time: Optional[str] = Field(default=None, description="최근 24시간 주기 정적 데이터 갱신 시각")
    last_eviction_time: Optional[str] = Field(default=None, description="최근 세션 만료 정리 시각")
    poll_count: int = Field(default=0, description="누적 폴링 실행 횟수")
    eviction_count: int = Field(default=0, description="누적 세션 만료 정리 횟수")
