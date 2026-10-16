"""Location and Geocoding API Router using Kakao Local REST API with 3-Tier Fallback."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Query
import httpx

logger = logging.getLogger("moonlightcare.location")

router = APIRouter(tags=["Location & Geocoding"])

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")

# 3-Tier L3 Fallback: 주요 랜드마크 및 전국 주요 행정동 중심 좌표 캐시
FALLBACK_POI_LOCATIONS = [
    # 주요 랜드마크 / 키워드
    {"name": "롯데월드타워", "category": "관광명소", "road_address": "서울특별시 송파구 올림픽로 300", "jibun_address": "서울특별시 송파구 신천동 29", "dong": "신천동", "gu": "송파구", "city": "서울특별시", "lat": 37.5126, "lon": 127.1025},
    {"name": "롯데월드", "category": "테마파크", "road_address": "서울특별시 송파구 올림픽로 240", "jibun_address": "서울특별시 송파구 잠실동 40-1", "dong": "잠실동", "gu": "송파구", "city": "서울특별시", "lat": 37.5111, "lon": 127.0982},
    {"name": "코엑스", "category": "전시관", "road_address": "서울특별시 강남구 영동대로 513", "jibun_address": "서울특별시 강남구 삼성동 159", "dong": "삼성동", "gu": "강남구", "city": "서울특별시", "lat": 37.5118, "lon": 127.0592},
    {"name": "강남역", "category": "지하철역", "road_address": "서울특별시 강남구 강남대로 396", "jibun_address": "서울특별시 강남구 역삼동 858", "dong": "역삼동", "gu": "강남구", "city": "서울특별시", "lat": 37.4979, "lon": 127.0276},
    {"name": "판교현대백화점", "category": "백화점", "road_address": "경기도 성남시 분당구 판교역로146번길 20", "jibun_address": "경기도 성남시 분당구 백현동 541", "dong": "백현동", "gu": "분당구", "city": "성남시", "lat": 37.3927, "lon": 127.1121},
    {"name": "해운대해수욕장", "category": "해수욕장", "road_address": "부산광역시 해운대구 해운대해변로 264", "jibun_address": "부산광역시 해운대구 중동 1015", "dong": "중동", "gu": "해운대구", "city": "부산광역시", "lat": 35.1587, "lon": 129.1604},
    {"name": "서울아산병원", "category": "종합병원", "road_address": "서울특별시 송파구 올림픽로43길 88", "jibun_address": "서울특별시 송파구 풍납동 388-1", "dong": "풍납동", "gu": "송파구", "city": "서울특별시", "lat": 37.5268, "lon": 127.1086},
    {"name": "삼성서울병원", "category": "종합병원", "road_address": "서울특별시 강남구 일원로 81", "jibun_address": "서울특별시 강남구 일원동 50", "dong": "일원동", "gu": "강남구", "city": "서울특별시", "lat": 37.4883, "lon": 127.0856},
    {"name": "서울대학교어린이병원", "category": "어린이병원", "road_address": "서울특별시 종로구 대학로 101", "jibun_address": "서울특별시 종로구 연건동 28", "dong": "연건동", "gu": "종로구", "city": "서울특별시", "lat": 37.5796, "lon": 127.0003},
    {"name": "가든파이브", "category": "쇼핑몰", "road_address": "서울특별시 송파구 충민로 66", "jibun_address": "서울특별시 송파구 문정동 634", "dong": "문정동", "gu": "송파구", "city": "서울특별시", "lat": 37.4777, "lon": 127.1250},
    {"name": "문정법조타운", "category": "업무지구", "road_address": "서울특별시 송파구 법원로 101", "jibun_address": "서울특별시 송파구 문정동 651", "dong": "문정동", "gu": "송파구", "city": "서울특별시", "lat": 37.4848, "lon": 127.1218},
    # 주요 행정동 / 지역명
    {"name": "문정동", "category": "지역", "road_address": "서울특별시 송파구 송파대로", "jibun_address": "서울특별시 송파구 문정동", "dong": "문정동", "gu": "송파구", "city": "서울특별시", "lat": 37.4858, "lon": 127.1225},
    {"name": "잠실동", "category": "지역", "road_address": "서울특별시 송파구 올림픽로", "jibun_address": "서울특별시 송파구 잠실동", "dong": "잠실동", "gu": "송파구", "city": "서울특별시", "lat": 37.5133, "lon": 127.1001},
    {"name": "가락동", "category": "지역", "road_address": "서울특별시 송파구 송파대로", "jibun_address": "서울특별시 송파구 가락동", "dong": "가락동", "gu": "송파구", "city": "서울특별시", "lat": 37.4950, "lon": 127.1200},
    {"name": "역삼동", "category": "지역", "road_address": "서울특별시 강남구 테헤란로", "jibun_address": "서울특별시 강남구 역삼동", "dong": "역삼동", "gu": "강남구", "city": "서울특별시", "lat": 37.5006, "lon": 127.0365},
    {"name": "삼성동", "category": "지역", "road_address": "서울특별시 강남구 영동대로", "jibun_address": "서울특별시 강남구 삼성동", "dong": "삼성동", "gu": "강남구", "city": "서울특별시", "lat": 37.5140, "lon": 127.0628},
    {"name": "서초동", "category": "지역", "road_address": "서울특별시 서초구 서초대로", "jibun_address": "서울특별시 서초구 서초동", "dong": "서초동", "gu": "서초구", "city": "서울특별시", "lat": 37.4919, "lon": 127.0076},
    {"name": "방배동", "category": "지역", "road_address": "서울특별시 서초구 방배로", "jibun_address": "서울특별시 서초구 방배동", "dong": "방배동", "gu": "서초구", "city": "서울특별시", "lat": 37.4816, "lon": 126.9976},
    {"name": "천호동", "category": "지역", "road_address": "서울특별시 강동구 천호대로", "jibun_address": "서울특별시 강동구 천호동", "dong": "천호동", "gu": "강동구", "city": "서울특별시", "lat": 37.5450, "lon": 127.1350},
    {"name": "목동", "category": "지역", "road_address": "서울특별시 양천구 목동동로", "jibun_address": "서울특별시 양천구 목동", "dong": "목동", "gu": "양천구", "city": "서울특별시", "lat": 37.5300, "lon": 126.8700},
    {"name": "화곡동", "category": "지역", "road_address": "서울특별시 강서구 강서로", "jibun_address": "서울특별시 강서구 화곡동", "dong": "화곡동", "gu": "강서구", "city": "서울특별시", "lat": 37.5350, "lon": 126.8500},
    {"name": "구로동", "category": "지역", "road_address": "서울특별시 구로구 구로동로", "jibun_address": "서울특별시 구로구 구로동", "dong": "구로동", "gu": "구로구", "city": "서울특별시", "lat": 37.4950, "lon": 126.8850},
    {"name": "여의도동", "category": "지역", "road_address": "서울특별시 영등포구 여의대로", "jibun_address": "서울특별시 영등포구 여의도동", "dong": "여의도동", "gu": "영등포구", "city": "서울특별시", "lat": 37.5215, "lon": 126.9242},
    {"name": "분당동", "category": "지역", "road_address": "경기도 성남시 분당구 불정로", "jibun_address": "경기도 성남시 분당구 분당동", "dong": "분당동", "gu": "분당구", "city": "성남시", "lat": 37.3700, "lon": 127.1400},
    {"name": "일산동", "category": "지역", "road_address": "경기도 고양시 일산서구 일산로", "jibun_address": "경기도 고양시 일산서구 일산동", "dong": "일산동", "gu": "일산서구", "city": "고양시", "lat": 37.6850, "lon": 126.7700},
    {"name": "해운대구", "category": "지역", "road_address": "부산광역시 해운대구 중동2로", "jibun_address": "부산광역시 해운대구 중동", "dong": "중동", "gu": "해운대구", "city": "부산광역시", "lat": 35.1631, "lon": 129.1636},
    {"name": "수성구", "category": "지역", "road_address": "대구광역시 수성구 달구벌대로", "jibun_address": "대구광역시 수성구 범어동", "dong": "범어동", "gu": "수성구", "city": "대구광역시", "lat": 35.8580, "lon": 128.6210},
]


def _search_fallback_locations(query: str, search_type: str = "all") -> List[Dict[str, Any]]:
    """Local In-Memory Fallback Location Search."""
    q_norm = query.strip().replace(" ", "").lower()
    matches = []

    for loc in FALLBACK_POI_LOCATIONS:
        name_norm = loc["name"].replace(" ", "").lower()
        road_norm = loc["road_address"].replace(" ", "").lower()
        jibun_norm = loc["jibun_address"].replace(" ", "").lower()
        dong_norm = loc["dong"].replace(" ", "").lower()

        is_match = (
            q_norm in name_norm
            or q_norm in road_norm
            or q_norm in jibun_norm
            or q_norm in dong_norm
        )

        if is_match:
            item_type = "keyword" if loc["category"] not in ["지역"] else "address"
            if search_type != "all" and search_type != item_type:
                continue

            matches.append({
                "type": item_type,
                "title": loc["name"],
                "category": loc["category"],
                "road_address": loc["road_address"],
                "jibun_address": loc["jibun_address"],
                "dong": loc["dong"],
                "gu": loc["gu"],
                "city": loc["city"],
                "lat": loc["lat"],
                "lon": loc["lon"],
                "source": "fallback_local_db"
            })

    return matches[:10]


@router.get("/search")
async def search_location(
    q: str = Query(..., min_length=1, description="검색어 (지번, 도로명, 건물명, 장소명)"),
    search_type: Literal["all", "address", "keyword"] = Query("all", description="검색 모드 (all, address, keyword)"),
    limit: int = Query(10, ge=1, le=15, description="반환 개수")
) -> Dict[str, Any]:
    """
    주소 검색(지번/도로명) 및 키워드 검색(건물명/장소명) 통합 위치 변환 API
    - 카카오 로컬 REST API를 우선 활용하여 WGS84 위경도 좌표 실시간 반환
    - API 키 부재 또는 장애 발생 시 3-Tier 로컬 Fallback DB로 0ms 안전 격리
    """
    api_key = os.getenv("KAKAO_REST_API_KEY", "") or KAKAO_REST_API_KEY
    clean_q = q.strip()

    # 1. 카카오 API 키가 설정되어 있는 경우 실시간 원격 호출
    if api_key:
        headers = {"Authorization": f"KakaoAK {api_key}"}
        results: List[Dict[str, Any]] = []

        async with httpx.AsyncClient(timeout=3.5) as client:
            tasks = []

            # (1) 주소 검색 (지번 / 도로명)
            if search_type in ["all", "address"]:
                addr_url = "https://dapi.kakao.com/v2/local/search/address.json"
                tasks.append(client.get(addr_url, params={"query": clean_q, "size": limit}, headers=headers))

            # (2) 키워드 검색 (건물명, 장소명, 랜드마크)
            if search_type in ["all", "keyword"]:
                key_url = "https://dapi.kakao.com/v2/local/search/keyword.json"
                tasks.append(client.get(key_url, params={"query": clean_q, "size": limit}, headers=headers))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for res in responses:
                if isinstance(res, httpx.Response) and res.status_code == 200:
                    data = res.json()
                    docs = data.get("documents", [])

                    for doc in docs:
                        # 주소 검색 결과인 경우
                        if "address_type" in doc or "address_name" in doc and "place_name" not in doc:
                            road = doc.get("road_address") or {}
                            jibun = doc.get("address") or {}
                            dong_name = jibun.get("region_3depth_name") or road.get("region_3depth_name") or ""
                            gu_name = jibun.get("region_2depth_name") or road.get("region_2depth_name") or ""
                            city_name = jibun.get("region_1depth_name") or road.get("region_1depth_name") or ""

                            results.append({
                                "type": "address",
                                "title": doc.get("address_name"),
                                "category": "주소",
                                "road_address": road.get("address_name") or doc.get("address_name"),
                                "jibun_address": jibun.get("address_name") or doc.get("address_name"),
                                "dong": dong_name,
                                "gu": gu_name,
                                "city": city_name,
                                "lat": float(doc.get("y")),
                                "lon": float(doc.get("x")),
                                "source": "kakao_address_api"
                            })
                        # 키워드/장소 검색 결과인 경우
                        elif "place_name" in doc:
                            addr_full = doc.get("address_name", "")
                            parts = addr_full.split()
                            dong_name = parts[2] if len(parts) >= 3 else (parts[1] if len(parts) >= 2 else "")
                            gu_name = parts[1] if len(parts) >= 2 else ""
                            city_name = parts[0] if len(parts) >= 1 else ""

                            results.append({
                                "type": "keyword",
                                "title": doc.get("place_name"),
                                "category": doc.get("category_group_name") or "장소",
                                "road_address": doc.get("road_address_name") or addr_full,
                                "jibun_address": addr_full,
                                "dong": dong_name,
                                "gu": gu_name,
                                "city": city_name,
                                "lat": float(doc.get("y")),
                                "lon": float(doc.get("x")),
                                "source": "kakao_keyword_api"
                            })

            if results:
                return {
                    "status": "success",
                    "query": clean_q,
                    "search_type": search_type,
                    "source": "kakao_local_api",
                    "total_count": len(results),
                    "results": results[:limit]
                }

    # 2. API 키 미설정 또는 0건 결과 시 L3 로컬 Fallback 검색 가동
    fallback_results = _search_fallback_locations(clean_q, search_type=search_type)
    return {
        "status": "success" if fallback_results else "empty",
        "query": clean_q,
        "search_type": search_type,
        "source": "fallback_local_db",
        "total_count": len(fallback_results),
        "results": fallback_results[:limit]
    }


@router.get("/coord2address")
async def coord_to_address(
    lat: float = Query(..., ge=33.0, le=43.0, description="WGS84 위도"),
    lon: float = Query(..., ge=124.0, le=132.0, description="WGS84 경도")
) -> Dict[str, Any]:
    """
    GPS 위경도 좌표 ➔ 행정동/법정동 도로명 주소 역변환 API (Reverse Geocoding)
    """
    api_key = os.getenv("KAKAO_REST_API_KEY", "") or KAKAO_REST_API_KEY
    if api_key:
        url = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
        headers = {"Authorization": f"KakaoAK {api_key}"}
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(url, params={"x": lon, "y": lat}, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    docs = data.get("documents", [])
                    if docs:
                        road = docs[0].get("road_address") or {}
                        jibun = docs[0].get("address") or {}
                        dong = jibun.get("region_3depth_name") or road.get("region_3depth_name") or "현재 위치"
                        full_addr = road.get("address_name") or jibun.get("address_name") or "현재 위치"
                        return {
                            "status": "success",
                            "dong": dong,
                            "full_address": full_addr,
                            "lat": lat,
                            "lon": lon,
                            "source": "kakao_reverse_geocoding"
                        }
        except Exception as e:
            logger.warning(f"Kakao coord2address exception: {e}")

    # Fallback 기본 반환: 좌표와 가장 가까운 POI 위치를 찾아 실제 행정동과 주소 반환
    closest_dong = "문정동"
    closest_addr = "서울특별시 송파구 문정동"
    min_dist = float("inf")
    for loc in FALLBACK_POI_LOCATIONS:
        d = (loc["lat"] - lat) ** 2 + (loc["lon"] - lon) ** 2
        if d < min_dist:
            min_dist = d
            closest_dong = loc["dong"]
            closest_addr = loc.get("road_address") or loc.get("jibun_address") or f"서울특별시 송파구 {closest_dong}"

    return {
        "status": "fallback",
        "dong": closest_dong,
        "full_address": closest_addr,
        "lat": lat,
        "lon": lon,
        "source": "fallback_gps"
    }
