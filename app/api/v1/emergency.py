"""Emergency, Spatial Ranking, and Sync API Endpoints (v1).

Serves:
- GET  /api/v1/emergency/nearby: GPS-based ultra-fast (< 10ms) pediatric emergency department search.
- GET  /api/v1/emergency/pairings: Moonlight hospital + 30-minute margin night pharmacy set search.
- POST /api/v1/emergency/sync: On-demand real-time bed synchronization & Hash Diffing trigger.
- GET  /api/v1/emergency/status: Background scheduler operational status and sync metrics.
"""

from __future__ import annotations

import datetime
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.emergency import RankedEmergencyHospital
from app.schemas.emergency_api import (
    NearbyEmergencyResponse,
    PairingSearchResponse,
    SchedulerStatusResponse,
    SyncTriggerResponse,
)
from app.services.emergency_sync_service import fetch_emergency_beds
from app.services.holiday_service import HolidayService
from app.services.pairing_service import find_nearby_pairings
from app.services.scheduler import background_daemon
from app.services.spatial_service import rank_emergency_hospitals

router = APIRouter()
holiday_service = HolidayService()
KST = datetime.timezone(datetime.timedelta(hours=9))


@router.get(
    "/nearby",
    response_model=NearbyEmergencyResponse,
    summary="주변 소아 가용 응급실 초고속 공간 검색",
    description="사용자 GPS 좌표 기준 10km 이내 소아 가용 응급실을 Haversine 구면거리로 5ms 내외로 정렬 반환합니다.",
)
async def get_nearby_emergency_departments(
    lat: float = Query(default=37.5133, description="사용자 위도 (기본값: 잠실역 37.5133)"),
    lon: float = Query(default=127.1001, description="사용자 경도 (기본값: 잠실역 127.1001)"),
    radius_km: float = Query(default=10.0, ge=1.0, le=50.0, description="검색 반경 (km)"),
    only_acceptable: bool = Query(
        default=True, description="소아 응급 진료 즉시 가능 기관만 필터링 (병상>0 and 제한공지 없음)"
    ),
    limit: int = Query(default=10, ge=1, le=50, description="최대 반환 개수"),
):
    """Calculates spherical distance and returns nearest pediatric emergency hospitals."""
    start_time = time.perf_counter()

    # 1. Holiday metadata & surge risk
    today_str = datetime.datetime.now(KST).strftime("%Y%m%d")
    holiday_info = holiday_service.get_holiday_info(today_str)

    # 2. Fetch real-time beds (with memory/disk cache and circuit breaker)
    all_beds, freshness_meta = fetch_emergency_beds(stage1="서울특별시", return_meta=True)

    # 3. Spatial Haversine ranking
    ranked = rank_emergency_hospitals(
        hospitals=all_beds,
        user_lat=lat,
        user_lon=lon,
        max_radius_km=radius_km,
        only_acceptable=only_acceptable,
        limit=limit,
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    acceptable_count = sum(1 for b in all_beds if b.pediatric_acceptable)

    return NearbyEmergencyResponse(
        user_lat=lat,
        user_lon=lon,
        radius_km=radius_km,
        is_holiday=holiday_info.is_holiday,
        holiday_name=holiday_info.holiday_name,
        surge_risk_level=holiday_info.surge_risk_level,
        hospitals=ranked,
        total_found=len(ranked),
        acceptable_count=acceptable_count,
        latency_ms=elapsed_ms,
        data_freshness=freshness_meta,
    )


@router.get(
    "/pairings",
    response_model=PairingSearchResponse,
    summary="달빛어린이병원 + 30분 마진 심야약국 페어링 세트 검색",
    description="사용자 좌표 기준 반경 내 달빛어린이병원과 야간 30분 안전 마진 약국 세트를 거리순 정렬하여 제공합니다.",
)
async def get_nearby_moonlight_pairings(
    lat: float = Query(default=37.5133, description="사용자 위도 (기본값: 잠실역)"),
    lon: float = Query(default=127.1001, description="사용자 경도 (기본값: 잠실역)"),
    radius_km: float = Query(default=15.0, ge=1.0, le=100.0, description="검색 반경 (km)"),
    limit: int = Query(default=5, ge=1, le=20, description="최대 반환 개수"),
):
    """Retrieves nearest Moonlight hospital and 30-min pharmacy pairings."""
    start_time = time.perf_counter()
    pairings = find_nearby_pairings(
        user_lat=lat,
        user_lon=lon,
        max_radius_km=radius_km,
        limit=limit,
    )
    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return PairingSearchResponse(
        user_lat=lat,
        user_lon=lon,
        radius_km=radius_km,
        pairings=pairings,
        total_found=len(pairings),
        latency_ms=elapsed_ms,
    )


@router.post(
    "/sync",
    response_model=SyncTriggerResponse,
    summary="실시간 병상 즉시 수집 및 Firestore Hash Diffing 동기화",
    description="E-Gen 실시간 병상을 수집하고 In-Memory Hash Diffing을 거쳐 변경분만 Firestore에 반영합니다.",
)
async def trigger_emergency_bed_sync():
    """Triggers an on-demand synchronization cycle."""
    now_iso = datetime.datetime.now(KST).isoformat()
    stats = await background_daemon.poll_realtime_beds()

    if "error" in stats:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"동기화 중 오류 발생: {stats.get('error')}",
        )

    return SyncTriggerResponse(
        status="SUCCESS",
        total_count=stats.get("total_count", 0),
        synced_count=stats.get("synced_count", 0),
        skipped_count=stats.get("skipped_count", 0),
        acceptable_count=stats.get("acceptable_count", 0),
        surge_risk_level=stats.get("surge_risk_level", "NORMAL"),
        saving_rate_percent=stats.get("saving_rate_percent", 0.0),
        triggered_at=now_iso,
    )


@router.post(
    "/sync-static",
    summary="전국 달빛병원 & 야간약국 24시간 증분 동기화 즉시 실행",
    description="공공데이터포털 NMC API를 호출하고 In-Memory Hash Diffing을 통해 변경된 병원/약국만 선택적으로 갱신합니다.",
)
async def trigger_static_dataset_sync(
    force: bool = Query(default=False, description="변경분이 없어도 강제로 갱신 및 JS 번들 재생성 여부"),
):
    """Triggers on-demand 24-hour static dataset & incremental delta sync."""
    stats = await background_daemon.sync_static_datasets(force=force)

    if stats.get("status") == "FAILED":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"정적 데이터 델타 동기화 중 오류 발생: {stats.get('error')}",
        )

    return {
        "status": "SUCCESS",
        "result": stats,
    }


@router.get(
    "/status",
    response_model=SchedulerStatusResponse,
    summary="백그라운드 스케줄러 가동 상태 및 동기화 지표",
    description="5분 주기 실시간 병상 폴러 및 24시간 정적 데이터 갱신 워커의 실행 상태를 조회합니다.",
)
async def get_scheduler_status():
    """Returns background daemon metrics and registered tasks."""
    raw_status = background_daemon.get_status()
    return SchedulerStatusResponse(
        running=raw_status["running"],
        jobs=raw_status["jobs"],
        last_bed_poll_time=raw_status["last_bed_poll_time"],
        last_bed_poll_stats=raw_status["last_bed_poll_stats"],
        last_static_sync_time=raw_status["last_static_sync_time"],
        poll_count=raw_status["poll_count"],
    )
