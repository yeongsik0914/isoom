"""Demo script for Step 1 Zero-LLM domain services and storage pipeline.

Executes:
1. Public holiday surge risk analysis (KASI API)
2. Live emergency bed ingestion from NMC E-Gen API
3. Notice NLP filtering (pediatric denial regex)
4. In-memory Hash Diffing & Firestore Batch Sync
5. Proximity Haversine ranking within 10km of Jamsil Station
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import time
from app.config import get_firestore_client
from app.services.emergency_sync_service import (
    BedStateHashCache,
    fetch_emergency_beds,
    sync_to_firestore,
)
from app.services.holiday_service import get_kasi_holiday_info
from app.services.spatial_service import rank_emergency_hospitals


def run_pipeline_demo() -> None:
    print("=" * 70)
    print("🚀 [MoonlightCare] Step 1: Zero-LLM 도구 및 스토리지 파이프라인 가동")
    print("=" * 70)

    start_total = time.perf_counter()

    # 1. 특일 정보 조회
    t0 = time.perf_counter()
    holiday_info = get_kasi_holiday_info()
    t_holiday = (time.perf_counter() - t0) * 1000
    print(f"\n[1] KASI 특일 판정 ({t_holiday:.1f}ms):")
    print(f"    - 날짜: {holiday_info.date}")
    print(f"    - 구분: {holiday_info.holiday_name} (공휴일 여부: {holiday_info.is_holiday})")
    print(f"    - 응급실 과밀화 리스크: {holiday_info.surge_risk_level}")

    # 2. 실시간 응급실 병상 수집 & 의료 가드레일
    t0 = time.perf_counter()
    beds = fetch_emergency_beds(stage1="서울특별시")
    t_fetch = (time.perf_counter() - t0) * 1000
    acceptable_count = sum(1 for b in beds if b.pediatric_acceptable)
    print(f"\n[2] E-Gen 실시간 병상 수집 ({t_fetch:.1f}ms):")
    print(f"    - 수집 병원 수: {len(beds)}개소")
    print(f"    - 소아 즉시 수용 가능 병원: {acceptable_count}개소")

    # 3. Hash Diffing & Firestore 배치 적재
    db = get_firestore_client()
    cache = BedStateHashCache()

    t0 = time.perf_counter()
    sync_res_1 = sync_to_firestore(beds, holiday_info, db=db, hash_cache=cache)
    t_sync1 = (time.perf_counter() - t0) * 1000
    print(f"\n[3-1] Firestore 1회차 동기화 ({t_sync1:.1f}ms):")
    print(f"    - Firestore Write 문서: {sync_res_1['synced_count']}건")
    print(f"    - 스킵된 문서: {sync_res_1['skipped_count']}건")

    # 2회차 동기화 (FinOps 무료 쿼터 방어 검증)
    t0 = time.perf_counter()
    sync_res_2 = sync_to_firestore(beds, holiday_info, db=db, hash_cache=cache)
    t_sync2 = (time.perf_counter() - t0) * 1000
    print(f"\n[3-2] Firestore 2회차 동기화 [FinOps Hash Diffing] ({t_sync2:.1f}ms):")
    print(f"    - 실제 Write 문서: {sync_res_2['synced_count']}건")
    print(f"    - 스킵된 문서: {sync_res_2['skipped_count']}건")
    print(f"    - 쓰기 비용 절감률: {sync_res_2['saving_rate_percent']}% (일일 2만 회 한도 영구 방어)")

    # 4. 사용자 위치(잠실역) 기준 10km 이내 소아 가용 응급실 Haversine 랭킹
    USER_LAT = 37.5133
    USER_LON = 127.1001
    MAX_RADIUS_KM = 10.0

    t0 = time.perf_counter()
    ranked = rank_emergency_hospitals(
        beds,
        user_lat=USER_LAT,
        user_lon=USER_LON,
        max_radius_km=MAX_RADIUS_KM,
        only_acceptable=True,
        limit=5,
    )
    t_spatial = (time.perf_counter() - t0) * 1000
    print(f"\n[4] 잠실역 기준 10km 소아 가용 응급실 거리 랭킹 ({t_spatial:.2f}ms):")
    for idx, h in enumerate(ranked, 1):
        print(f"    {idx}. 🏥 {h.hospital_name}")
        print(f"       - 거리: {h.distance_km} km | 소아병상: {h.pediatric_beds}석")
        if h.notice_raw:
            print(f"       - 공지: {h.notice_raw[:60]}")

    elapsed_total = (time.perf_counter() - start_total) * 1000
    print("\n" + "=" * 70)
    print(f"✨ [성공] Step 1 Zero-LLM 파이프라인 전체 실행 완료 (총 소요: {elapsed_total:.1f}ms)")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline_demo()
