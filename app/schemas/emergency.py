"""Pydantic schemas for emergency beds, holidays, and spatial rankings."""

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class EmergencyBedInfo(BaseModel):
    """Raw parsed emergency hospital bed information from NMC E-Gen."""

    hpid: str = Field(..., description="기관 고유 코드 (예: A1100010)")
    hospital_name: str = Field(..., description="병원명 (dutyName)")
    pediatric_beds: int = Field(default=0, description="소아 가용병상 수 (hv28)")
    general_beds: int = Field(default=0, description="응급실 일반병상 수 (hvec)")
    pediatric_iso_beds: int = Field(default=0, description="소아 음압/일반 격리병상 수 (hv29)")
    lat: float = Field(default=37.5, description="위도 (wgs84Lat)")
    lon: float = Field(default=127.0, description="경도 (wgs84Lon)")
    notice_raw: str = Field(default="", description="실시간 공지 원문 (hpmg)")
    is_pediatric_blocked: bool = Field(
        default=False, description="공지사항 NLP 정규식에 의한 소아 진료 제한/거부 감지 여부"
    )
    pediatric_acceptable: bool = Field(
        default=False, description="실제 소아 응급 진료 즉시 가능 여부 (병상>0 and not 차단)"
    )
    input_date: Optional[str] = Field(default=None, description="원천 데이터 입력 일시 (hvidate)")


class HolidayInfo(BaseModel):
    """KASI (한국천문연구원) 특일 정보 및 과밀화 리스크 메타데이터."""

    date: str = Field(..., description="기준 일자 (YYYYMMDD)")
    is_holiday: bool = Field(default=False, description="공휴일 또는 주말 여부")
    holiday_name: str = Field(default="평일", description="특일 명칭 (토요일, 일요일, 법정공휴일 등)")
    is_rest_day_special: bool = Field(
        default=False, description="KASI 공휴일 API에 등록된 법정공휴일/대체공휴일 여부"
    )
    surge_risk_level: str = Field(
        default="NORMAL", description="응급실 과밀화 리스크 등급 (NORMAL | HIGH | CRITICAL)"
    )


class EmergencyBedSyncRecord(EmergencyBedInfo):
    """Firestore 'emergency_beds' 컬렉션에 적재되는 최종 문서 스키마."""

    is_holiday: bool = Field(default=False, description="동기화 시점 공휴일 여부")
    holiday_name: str = Field(default="평일", description="동기화 시점 공휴일 명칭")
    surge_risk_level: str = Field(default="NORMAL", description="응급실 과밀화 리스크 등급")
    synced_at: Optional[Any] = Field(default=None, description="동기화 타임스탬프")


class RankedEmergencyHospital(BaseModel):
    """GPS 사용자 좌표 기준 Haversine 구면거리로 정렬된 추천 응급실."""

    hpid: str = Field(..., description="기관 코드")
    hospital_name: str = Field(..., description="병원명")
    distance_km: float = Field(..., description="사용자 위치로부터의 직선 거리 (km)")
    pediatric_beds: int = Field(default=0, description="소아 가용병상 수")
    general_beds: int = Field(default=0, description="응급실 일반병상 수")
    pediatric_acceptable: bool = Field(default=False, description="즉시 수용 가능 여부")
    is_pediatric_blocked: bool = Field(default=False, description="소아 제한 공지 여부")
    notice_raw: str = Field(default="", description="병원 공지 원문")
    lat: float = Field(..., description="위도")
    lon: float = Field(..., description="경도")


class EmergencySummary(BaseModel):
    """Firestore 'emergency_summary/realtime' 대시보드 뷰용 단일 집계 문서."""

    total_count: int = Field(default=0, description="수집된 전체 응급의료기관 수")
    acceptable_count: int = Field(default=0, description="소아 수용 가능 기관 수")
    surge_risk_level: str = Field(default="NORMAL", description="과밀화 위험 등급")
    holiday_name: str = Field(default="평일", description="공휴일 구분 명칭")
    is_holiday: bool = Field(default=False, description="공휴일 여부")
    top_available_hospitals: list[dict[str, Any]] = Field(
        default_factory=list, description="가용 소아병상 상위 병원 요약 리스트"
    )
    updated_at: Optional[Any] = Field(default=None, description="최종 갱신 시각")


class DataFreshnessMeta(BaseModel):
    """실시간 공공 API 연동 및 서킷 브레이커 폴백 신선도 메타데이터."""

    is_realtime: bool = Field(default=True, description="실시간 공공 API 정상 통신 여부")
    source_tier: str = Field(
        default="PUBLIC_API_LIVE",
        description="데이터 소스 계층 (PUBLIC_API_LIVE | TIER_1_MEMORY_STALE | TIER_2_FIRESTORE_SNAPSHOT | TIER_3_IMMUTABLE_DISK_BASELINE)",
    )
    last_synced_at: Optional[str] = Field(default=None, description="데이터 최종 수집 일시 (ISO-8601)")
    elapsed_minutes: int = Field(default=0, description="데이터 수집 경과 시간 (분)")
    circuit_status: str = Field(default="CLOSED", description="서킷 브레이커 상태 (CLOSED | OPEN | HALF_OPEN)")
    warning_message: Optional[str] = Field(default=None, description="사용자 안내 및 안심 대체/전화 확인 권고 경고 배지")

