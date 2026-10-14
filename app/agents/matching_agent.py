"""Zero-LLM Deterministic Matching Agent.

Responsibilities:
1. Orchestrates deterministic domain tools without LLM hallucinations:
   - KASI Holiday & Surge Risk Service
   - NMC E-Gen Real-time Bed Ingestion Service (Dynamic nationwide stage1 resolution)
   - Haversine Proximity Ranking Service
   - Moonlight Hospital & Night Pharmacy Pairing Service (30-min margin)
2. Clinical Route Optimization:
   - High acuity (infant < 3 months, temp >= 39.0℃, or multiple acute symptoms, or late night 23:00~07:00):
     Prioritizes 24-hour pediatric emergency departments.
   - Mild/moderate acuity (temp < 39.0℃ during evening/night hours before 23:00):
     Prioritizes Moonlight Children's Clinics paired with 30-min margin pharmacies.
   - Operating hours awareness: tags clinics near closing (< 40 mins) with "[조기 접수 마감 주의]".
3. Medical Ethics & Neutrality (의료법 제27조 제3항):
   - Prohibits single-facility steering (환자 유인·알선 배제); always presents top 2~3 neutral options.
4. Updates PatientSessionState with matched hospitals and pharmacies, advancing FSM to LOGISTICS.
"""

from __future__ import annotations

import datetime
import re
from typing import Any, Optional

from app.schemas.state import PatientSessionState
from app.services.emergency_sync_service import fetch_emergency_beds
from app.services.holiday_service import HolidayService
from app.services.pairing_service import find_nearby_pairings
from app.services.spatial_service import rank_emergency_hospitals

KST = datetime.timezone(datetime.timedelta(hours=9))


def resolve_stage1_from_coords_or_address(
    lat: float,
    lon: float,
    address: Optional[str] = None,
) -> str:
    """Dynamically resolves Korea 17 metropolitan/provincial stage1 region name."""
    clean_addr = (address or "").strip()

    # 1. Primary Priority: Exact Metropolitan & Provincial Keywords
    if clean_addr:
        primary_mappings = [
            (r"(서울|서울특별시)", "서울특별시"),
            (r"(부산|부산광역시)", "부산광역시"),
            (r"(대구|대구광역시)", "대구광역시"),
            (r"(인천|인천광역시)", "인천광역시"),
            (r"(광주광역시|광주직할시)", "광주광역시"),
            (r"(대전|대전광역시)", "대전광역시"),
            (r"(울산|울산광역시)", "울산광역시"),
            (r"(세종|세종특별자치시)", "세종특별자치시"),
            (r"(경기|경기도)", "경기도"),
            (r"(강원|강원도|강원특별자치도)", "강원특별자치도"),
            (r"(충북|충청북도)", "충청북도"),
            (r"(충남|충청남도)", "충청남도"),
            (r"(전북|전라북도|전북특별자치도)", "전북특별자치도"),
            (r"(전남|전라남도)", "전라남도"),
            (r"(경북|경상북도)", "경상북도"),
            (r"(경남|경상남도)", "경상남도"),
            (r"(제주|제주도|제주특별자치도)", "제주특별자치도"),
        ]
        for pattern, stage1 in primary_mappings:
            if re.search(pattern, clean_addr):
                return stage1

        # 2. Secondary Priority: Distinctive Cities and Counties
        secondary_mappings = [
            (r"(수원|성남|용인|고양|안양|부천|남양주|화성|평택|의정부|파주|시흥|김포|광명|군포|이천|오산|하남|양주|구리|안성|포천|의왕|여주|양평|동두천|과천|가평|연천)", "경기도"),
            (r"(해운대|사하|수영|동래|금정|부산진|기장)", "부산광역시"),
            (r"(수성구|달서구|달성군)", "대구광역시"),
            (r"(연수구|부평구|남동구|계양구|미추홀구|강화군|영종도)", "인천광역시"),
            (r"(광산구|광주시\s*북구)", "광주광역시"),
            (r"(유성구|대덕구)", "대전광역시"),
            (r"(울주군)", "울산광역시"),
            (r"(춘천|원주|강릉|평창|속초|동해|삼척|태백|홍천|철원|횡성|영월|정선|화천|양구|인제|고성|양양)", "강원특별자치도"),
            (r"(청주|충주|제천|음성|진천|옥천|영동|괴산|보은|단양)", "충청북도"),
            (r"(천안|아산|서산|당진|공주|보령|논산|홍성|예산|부여|서천|태안|금산|청양)", "충청남도"),
            (r"(전주|익산|군산|정읍|남원|김제|완주|고창|부안|순창|임실|무주|진안|장수)", "전북특별자치도"),
            (r"(목포|여수|순천|나주|광양|담양|곡성|구례|고흥|보성|화순|장흥|강진|해남|영암|무안|함평|영광|장성|완도|진도|신안)", "전라남도"),
            (r"(포항|구미|경주|김천|안동|영주|상주|문경|경산|군위|의성|청송|영양|영덕|청도|고령|성주|칠곡|예천|봉화|울진|울릉)", "경상북도"),
            (r"(창원|김해|진주|양산|거제|통영|사천|밀양|함안|거창|창녕|고성군|하동|합천|남해군|산청|함양|의령)", "경상남도"),
            (r"(서귀포)", "제주특별자치도"),
            (r"(강남|송파|서초|강동|마포|영등포|용산|종로|중구|성동|광진|동대문|중랑|성북|강북|도봉|노원|은평|서대문|양천|강서|구로|금천|동작|관악)", "서울특별시"),
        ]
        for pattern, stage1 in secondary_mappings:
            if re.search(pattern, clean_addr):
                return stage1

    # 2. Coordinate Bounding Box Fallback
    if lat < 34.0:
        return "제주특별자치도"
    if lat < 35.6 and lon > 128.5:
        return "부산광역시"
    if 35.7 <= lat <= 36.1 and 128.3 <= lon <= 128.8:
        return "대구광역시"
    if lat < 35.4 and lon < 127.3:
        return "광주광역시"
    if 36.1 <= lat <= 36.6 and 127.1 <= lon <= 127.6:
        return "대전광역시"
    if 37.3 <= lat <= 37.7 and lon < 126.8:
        return "인천광역시"
    if lat >= 37.0 and lon > 127.9:
        return "강원특별자치도"
    if 36.9 <= lat <= 38.3 and (lat < 37.42 or lat > 37.7 or lon < 126.75 or lon > 127.2):
        return "경기도"

    return "서울특별시"


class MatchingAgent:
    """Deterministic spatial & clinical matching agent."""

    def __init__(self) -> None:
        self.holiday_service = HolidayService()

    async def match_destinations(
        self,
        state: PatientSessionState,
        max_radius_km: float = 15.0,
        target_time: Optional[datetime.datetime] = None,
    ) -> dict[str, Any]:
        """Matches top hospitals and 30-min safe margin pharmacies for the patient."""
        now_kst = target_time or datetime.datetime.now(KST)
        date_str = now_kst.strftime("%Y%m%d")
        current_hour = now_kst.hour
        current_minute = now_kst.minute
        now_time_val = current_hour * 60 + current_minute

        # 1. Check holiday and emergency room surge risk level
        holiday_info = self.holiday_service.get_holiday_info(date_str)
        surge_risk = holiday_info.surge_risk_level

        # 2. Dynamic stage1 resolution from user address or coordinates
        stage1 = resolve_stage1_from_coords_or_address(
            lat=state.user_lat,
            lon=state.user_lon,
            address=state.user_address,
        )

        # 3. Fetch real-time emergency beds for resolved stage1
        all_beds = fetch_emergency_beds(stage1=stage1)

        # 4. Rank emergency hospitals by proximity (10~15km radius)
        ranked_ers = rank_emergency_hospitals(
            hospitals=all_beds,
            user_lat=state.user_lat,
            user_lon=state.user_lon,
            max_radius_km=max_radius_km,
            only_acceptable=True,
            limit=3,
        )

        # If ranked ERs are empty within tight radius, relax radius to find at least top 3
        if not ranked_ers and all_beds:
            ranked_ers = rank_emergency_hospitals(
                hospitals=all_beds,
                user_lat=state.user_lat,
                user_lon=state.user_lon,
                max_radius_km=50.0,
                only_acceptable=False,
                limit=3,
            )

        # 5. Fetch nearest Moonlight clinic + 30-min pharmacy pairings
        nearby_pairings = find_nearby_pairings(
            user_lat=state.user_lat,
            user_lon=state.user_lon,
            max_radius_km=max_radius_km + 5.0,
            limit=3,
        )

        # 6. Operating hour awareness (Late night check: 23:00 ~ 07:00 is late night ER only)
        is_late_night = (current_hour >= 23) or (current_hour < 7)

        # 7. Clinical routing priority judgment
        is_high_acuity = (
            (state.temperature is not None and state.temperature >= 39.0)
            or (state.age_months is not None and state.age_months < 3)
            or (state.age_days is not None and state.age_days < 100)
            or "호흡곤란" in state.symptoms
            or "처짐" in state.symptoms
            or "경련" in state.symptoms
            or is_late_night
        )

        matched_hospitals: list[dict[str, Any]] = []
        matched_pharmacies: list[dict[str, Any]] = []

        if is_high_acuity or not nearby_pairings:
            # Route to Emergency Departments (Multiple options for neutrality)
            for er in ranked_ers:
                matched_hospitals.append({
                    "기관명": er.hospital_name,
                    "유형": "24시간 소아 응급실" if is_late_night else "소아 가용 응급실",
                    "거리_km": er.distance_km,
                    "소아병상수": er.pediatric_beds,
                    "일반병상수": er.general_beds,
                    "공지사항": er.notice_raw,
                    "lat": er.lat,
                    "lon": er.lon,
                    "hpid": er.hpid,
                })
        else:
            # Filter and tag Moonlight clinics by closing time
            valid_pairings = []
            for p in nearby_pairings:
                closing_str = p.get("병원_평일마감", "23:00")
                closing_time_val = 23 * 60  # Default 23:00
                m_close = re.search(r"(\d{1,2}):(\d{2})", closing_str)
                if m_close:
                    closing_time_val = int(m_close.group(1)) * 60 + int(m_close.group(2))

                # Check if already closed
                if now_time_val > closing_time_val:
                    continue

                # Check if near closing (within 40 mins)
                time_left = closing_time_val - now_time_val
                status_tag = ""
                if 0 <= time_left <= 40:
                    status_tag = f" [⚠️ 조기 접수 마감 주의: {time_left}분 남음]"

                p_copy = dict(p)
                p_copy["status_tag"] = status_tag
                valid_pairings.append(p_copy)

            if not valid_pairings:
                # All Moonlight clinics closed -> route to ERs
                for er in ranked_ers:
                    matched_hospitals.append({
                        "기관명": er.hospital_name,
                        "유형": "소아 가용 응급실 (달빛병원 야간 진료 마감)",
                        "거리_km": er.distance_km,
                        "소아병상수": er.pediatric_beds,
                        "일반병상수": er.general_beds,
                        "lat": er.lat,
                        "lon": er.lon,
                        "hpid": er.hpid,
                    })
            else:
                for p in valid_pairings[:2]:
                    hosp_name = p.get("병원명", "") + p.get("status_tag", "")
                    matched_hospitals.append({
                        "기관명": hosp_name,
                        "유형": p.get("병원유형", "달빛어린이병원"),
                        "거리_km": p.get("거리_km", 0.0),
                        "주소": p.get("병원주소", ""),
                        "전화번호": p.get("병원전화", ""),
                        "진료시간": p.get("병원_평일진료", ""),
                        "마감시간": p.get("병원_평일마감", ""),
                        "lat": p.get("병원위도", 0.0),
                        "lon": p.get("병원경도", 0.0),
                    })
                    matched_pharmacies.append({
                        "약국명": p.get("약국명", ""),
                        "약국구분": p.get("약국구분", "공식 협약약국"),
                        "주소": p.get("약국주소", ""),
                        "전화번호": p.get("약국전화", ""),
                        "운영시간": p.get("약국_평일운영", ""),
                        "마감시간": p.get("약국_평일마감", ""),
                        "안전마진_분": p.get("안전마진_분", 30),
                        "조제안전등급": p.get("조제안전등급", "🟢 완벽 매칭 (+30분 이상)"),
                        "이동안내": p.get("이동안내", "동일 건물 도보 이동"),
                    })

                # Always add closest ER as emergency backup to guarantee multiple options
                if ranked_ers:
                    closest_er = ranked_ers[0]
                    matched_hospitals.append({
                        "기관명": f"{closest_er.hospital_name} (비상 응급 대기)",
                        "유형": "응급실 백업",
                        "거리_km": closest_er.distance_km,
                        "소아병상수": closest_er.pediatric_beds,
                        "일반병상수": closest_er.general_beds,
                        "lat": closest_er.lat,
                        "lon": closest_er.lon,
                    })

        # Fallback guarantee: if still empty, populate top hospitals from all_beds
        if not matched_hospitals and all_beds:
            for b in all_beds[:3]:
                matched_hospitals.append({
                    "기관명": b.hospital_name,
                    "유형": "광역 소아 응급실",
                    "거리_km": 0.0,
                    "소아병상수": b.pediatric_beds,
                    "일반병상수": b.general_beds,
                    "lat": b.lat,
                    "lon": b.lon,
                })

        # Save to state
        state.matched_hospitals = matched_hospitals
        state.matched_pharmacies = matched_pharmacies
        state.current_step = "LOGISTICS"

        return {
            "surge_risk_level": surge_risk,
            "is_holiday": holiday_info.is_holiday,
            "holiday_name": holiday_info.holiday_name,
            "stage1": stage1,
            "matched_hospitals": matched_hospitals,
            "matched_pharmacies": matched_pharmacies,
        }
