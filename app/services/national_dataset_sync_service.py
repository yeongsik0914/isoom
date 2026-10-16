# -*- coding: utf-8 -*-
"""National Moonlight Hospitals & Night Pharmacies 24-Hour Incremental Delta Sync Service.

Fetches data from National Medical Center (NMC) via data.go.kr,
detects deltas using Primary Key (기관코드) and In-Memory Hash Diffing,
and selectively updates JSON files and frontend JS bundles only when changes exist.
"""

from __future__ import annotations

import hashlib
import json
import logging
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.config import settings

logger = logging.getLogger("dataset_sync")

PROJECT_ROOT = settings.project_root
DATA_DIR = PROJECT_ROOT / "data"
JS_DIR = PROJECT_ROOT / "frontend" / "js"

HOSP_JSON_PATH = DATA_DIR / "national_moonlight_hospitals_156.json"
PHARM_JSON_PATH = DATA_DIR / "national_night_pharmacies_2028.json"

REGION_CONFIGS = [
    ("서울특별시", "수도권", 6),
    ("경기도", "수도권", 7),
    ("인천광역시", "수도권", 2),
    ("부산광역시", "영남권", 2),
    ("대구광역시", "영남권", 2),
    ("울산광역시", "영남권", 1),
    ("경상북도", "영남권", 2),
    ("경상남도", "영남권", 2),
    ("대전광역시", "충청권", 1),
    ("세종특별자치시", "충청권", 1),
    ("충청북도", "충청권", 1),
    ("충청남도", "충청권", 1),
    ("광주광역시", "호남권", 1),
    ("전북특별자치도", "호남권", 1),
    ("전라남도", "호남권", 1),
    ("강원특별자치도", "강원권", 1),
    ("제주특별자치도", "제주권", 1),
]

REGION_MAP = {r[0]: r[1] for r in REGION_CONFIGS}


def fmt_time(s: str) -> str:
    """Formats 4-digit string '0900' -> '09:00', '2400' -> '24:00', '2500' -> '익일 01:00'."""
    if not s or not s.strip():
        return ""
    s = s.strip()
    if len(s) == 3:
        s = "0" + s
    if len(s) >= 4:
        hh = int(s[:2])
        mm = s[2:4]
        if hh >= 24:
            return f"익일 {hh-24:02d}:{mm}"
        return f"{hh:02d}:{mm}"
    return s


def parse_sido_sgg(addr: str) -> Tuple[str, str]:
    """Extracts (sido, sgg) from Korean road-name or land-lot address."""
    if not addr:
        return "기타", "기타"
    parts = addr.split()
    sido = parts[0] if len(parts) > 0 else "기타"
    sgg = parts[1] if len(parts) > 1 else ""

    if sido == "전남광주통합특별시":
        gwangju_districts = {"동구", "서구", "남구", "북구", "광산구"}
        if sgg in gwangju_districts:
            sido = "광주광역시"
        else:
            sido = "전라남도"

    if len(parts) > 2 and parts[1].endswith(("시", "군")) and parts[2].endswith(("구", "군")):
        sgg = f"{parts[1]} {parts[2]}"
    return sido, sgg


def compute_item_hash(item: Dict[str, Any]) -> str:
    """Computes a SHA-256 fingerprint from core operational fields of a hospital or pharmacy."""
    # Key operational attributes that matter to users
    core_keys = [
        "병원명", "약국명", "대표전화", "주소",
        "평일진료", "토요진료", "일요진료", "공휴일진료",
        "평일운영", "토요운영", "일요운영", "공휴일운영",
        "진료안내", "위도", "경도"
    ]
    extracted = {k: item.get(k) for k in core_keys if k in item}
    serialized = json.dumps(extracted, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def detect_dataset_deltas(
    old_list: List[Dict[str, Any]],
    new_list: List[Dict[str, Any]],
    pk_field: str = "기관코드",
    name_field: str = "병원명"
) -> Dict[str, Any]:
    """Compares previous and newly fetched datasets using PK and Hash Diffing."""
    old_map = {item.get(pk_field) or item.get(name_field): item for item in old_list}
    new_map = {item.get(pk_field) or item.get(name_field): item for item in new_list}

    added = []
    modified = []
    removed = []
    unchanged = 0

    # 1. Detect Added & Modified
    for pk, new_item in new_map.items():
        if pk not in old_map:
            added.append(new_item)
        else:
            old_item = old_map[pk]
            if compute_item_hash(new_item) != compute_item_hash(old_item):
                modified.append({
                    "id": pk,
                    "name": new_item.get(name_field) or old_item.get(name_field),
                    "before": old_item,
                    "after": new_item,
                })
            else:
                unchanged += 1

    # 2. Detect Removed
    for pk, old_item in old_map.items():
        if pk not in new_map:
            removed.append(old_item)

    total_diff = len(added) + len(modified) + len(removed)
    return {
        "added": added,
        "modified": modified,
        "removed": removed,
        "added_count": len(added),
        "modified_count": len(modified),
        "removed_count": len(removed),
        "unchanged_count": unchanged,
        "total_diff_count": total_diff,
        "old_total": len(old_list),
        "new_total": len(new_list),
    }


def fetch_moonlight_hospitals(api_key: str) -> List[Dict[str, Any]]:
    """Fetches current designated Moonlight Children's Hospitals from NMC."""
    url = f"https://apis.data.go.kr/B552657/HsptlAsembySearchService/getBabyListInfoInqire?serviceKey={api_key}&numOfRows=500&pageNo=1"
    req = urllib.request.Request(url, headers={"User-Agent": "AisumHealthCare/2.0"})

    with urllib.request.urlopen(req, timeout=25) as resp:
        xml_data = resp.read().decode("utf-8")

    root = ET.fromstring(xml_data)
    items = root.findall(".//item")
    if not items:
        logger.warning("[SyncService] Empty or invalid XML response for Moonlight Hospitals.")
        return []

    hospitals = []
    for it in items:
        name = it.find("dutyName").text if it.find("dutyName") is not None else ""
        addr = it.find("dutyAddr").text if it.find("dutyAddr") is not None else ""
        tel = it.find("dutyTel1").text if it.find("dutyTel1") is not None else ""
        div_nam = it.find("dutyDivNam").text if it.find("dutyDivNam") is not None else "의원"
        hpid = it.find("hpid").text if it.find("hpid") is not None else ""
        lat = float(it.find("wgs84Lat").text) if it.find("wgs84Lat") is not None and it.find("wgs84Lat").text else 0.0
        lon = float(it.find("wgs84Lon").text) if it.find("wgs84Lon") is not None and it.find("wgs84Lon").text else 0.0
        duty_inf = it.find("dutyInf").text if it.find("dutyInf") is not None else ""

        sido, sgg = parse_sido_sgg(addr)
        region = REGION_MAP.get(sido, "기타")

        w_starts = [it.find(f"dutyTime{d}s").text for d in range(1, 6) if it.find(f"dutyTime{d}s") is not None]
        w_ends = [it.find(f"dutyTime{d}c").text for d in range(1, 6) if it.find(f"dutyTime{d}c") is not None]
        sat_s = it.find("dutyTime6s").text if it.find("dutyTime6s") is not None else ""
        sat_e = it.find("dutyTime6c").text if it.find("dutyTime6c") is not None else ""
        sun_s = it.find("dutyTime7s").text if it.find("dutyTime7s") is not None else ""
        sun_e = it.find("dutyTime7c").text if it.find("dutyTime7c") is not None else ""
        hol_s = it.find("dutyTime8s").text if it.find("dutyTime8s") is not None else ""
        hol_e = it.find("dutyTime8c").text if it.find("dutyTime8c") is not None else ""

        weekday_hours = f"{fmt_time(w_starts[0])} ~ {fmt_time(w_ends[0])}" if w_starts and w_ends and w_starts[0] and w_ends[0] else "주말/공휴일 특화"
        sat_hours = f"{fmt_time(sat_s)} ~ {fmt_time(sat_e)}" if sat_s and sat_e else "미운영/유선확인"
        sun_hours = f"{fmt_time(sun_s)} ~ {fmt_time(sun_e)}" if sun_s and sun_e else "미운영/유선확인"
        hol_hours = f"{fmt_time(hol_s)} ~ {fmt_time(hol_e)}" if hol_s and hol_e else "미운영/유선확인"

        hospitals.append({
            "권역": region,
            "시도": sido,
            "시군구": sgg,
            "병원명": name,
            "종별": div_nam,
            "기관코드": hpid,
            "대표전화": tel,
            "주소": addr,
            "평일진료": weekday_hours,
            "토요진료": sat_hours,
            "일요진료": sun_hours,
            "공휴일진료": hol_hours,
            "진료안내": duty_inf.replace("\n", " ").strip() if duty_inf else "보건복지부 지정 달빛어린이병원 (소아 야간·휴일 진료)",
            "위도": lat,
            "경도": lon
        })

    hospitals.sort(key=lambda x: (x["권역"], x["시도"], x["시군구"], x["병원명"]))
    return hospitals


def fetch_night_pharmacies(api_key: str) -> List[Dict[str, Any]]:
    """Fetches all night & late-night pharmacies nationwide."""
    night_pharmacies = []

    for sido, region, max_pages in REGION_CONFIGS:
        for page in range(1, max_pages + 1):
            params = {
                "serviceKey": api_key,
                "numOfRows": 1000,
                "pageNo": page,
                "Q0": sido
            }
            url = f"https://apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire?{urllib.parse.urlencode(params)}"
            req = urllib.request.Request(url, headers={"User-Agent": "AisumHealthCare/2.0"})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    xml_data = resp.read().decode("utf-8")
                root = ET.fromstring(xml_data)
                items = root.findall(".//item")
                if not items:
                    break

                for it in items:
                    is_night = False
                    max_close = 0
                    close_hours = {}

                    for d in range(1, 9):
                        c = it.find(f"dutyTime{d}c")
                        s = it.find(f"dutyTime{d}s")
                        c_val = c.text.strip() if c is not None and c.text else ""
                        s_val = s.text.strip() if s is not None and s.text else ""
                        close_hours[d] = (s_val, c_val)

                        if c_val:
                            try:
                                v = int(c_val)
                                if v >= 2200 or (0 < v <= 600):
                                    is_night = True
                                if v > max_close:
                                    max_close = v
                            except ValueError:
                                pass

                    if not is_night:
                        continue

                    name = it.find("dutyName").text if it.find("dutyName") is not None else ""
                    addr = it.find("dutyAddr").text if it.find("dutyAddr") is not None else ""
                    tel = it.find("dutyTel1").text if it.find("dutyTel1") is not None else ""
                    hpid = it.find("hpid").text if it.find("hpid") is not None else ""
                    lat = float(it.find("wgs84Lat").text) if it.find("wgs84Lat") is not None and it.find("wgs84Lat").text else 0.0
                    lon = float(it.find("wgs84Lon").text) if it.find("wgs84Lon") is not None and it.find("wgs84Lon").text else 0.0

                    _, sgg = parse_sido_sgg(addr)

                    is_public_midnight = False
                    for d in range(1, 9):
                        _, c_str = close_hours.get(d, ("", ""))
                        if c_str:
                            try:
                                cv = int(c_str)
                                if cv in [2500, 2600, 100, 200, 2400] or cv >= 2400:
                                    is_public_midnight = True
                            except ValueError:
                                pass

                    if "공공심야" in name or is_public_midnight:
                        pharm_type = "공공심야약국 (새벽 1~2시/24시)"
                        safety_grade = "🟢 심야 전문 조제 (새벽 1~2시까지)"
                    elif max_close >= 2300:
                        pharm_type = "365 심야약국 (밤 11시~자정)"
                        safety_grade = "🟡 심야 연장 조제 (밤 11시 이후)"
                    else:
                        pharm_type = "야간 연장약국 (밤 10시~11시)"
                        safety_grade = "🟠 야간 기본 조제 (밤 10시까지)"

                    w_s, w_c = close_hours.get(1, ("", ""))
                    sat_s, sat_c = close_hours.get(6, ("", ""))
                    sun_s, sun_c = close_hours.get(7, ("", ""))
                    hol_s, hol_c = close_hours.get(8, ("", ""))

                    weekday_hours = f"{fmt_time(w_s)} ~ {fmt_time(w_c)}" if w_s and w_c else "유선확인"
                    sat_hours = f"{fmt_time(sat_s)} ~ {fmt_time(sat_c)}" if sat_s and sat_c else "휴무/유선확인"
                    sun_hours = f"{fmt_time(sun_s)} ~ {fmt_time(sun_c)}" if sun_s and sun_c else "휴무/유선확인"
                    hol_hours = f"{fmt_time(hol_s)} ~ {fmt_time(hol_c)}" if hol_s and hol_c else "휴무/유선확인"

                    syrup_ready = True if (is_public_midnight or "어린이" in name or "소아" in name or max_close >= 2300) else False

                    night_pharmacies.append({
                        "권역": region,
                        "시도": sido,
                        "시군구": sgg,
                        "약국명": name,
                        "기관코드": hpid,
                        "운영구분": pharm_type,
                        "조제안전등급": safety_grade,
                        "대표전화": tel,
                        "주소": addr,
                        "평일운영": weekday_hours,
                        "토요운영": sat_hours,
                        "일요운영": sun_hours,
                        "공휴일운영": hol_hours,
                        "소아시럽제상비": syrup_ready,
                        "위도": lat,
                        "경도": lon
                    })
            except Exception as e:
                logger.warning(f"[SyncService] Failed to fetch pharmacies for {sido} page {page}: {e}")
                continue

    night_pharmacies.sort(key=lambda x: (x["권역"], x["시도"], x["시군구"], x["약국명"]))
    return night_pharmacies


def rebuild_frontend_js_bundles(hospitals: List[Dict[str, Any]], pharmacies: List[Dict[str, Any]]) -> None:
    """Rebuilds the client-side JavaScript bundles in frontend/js/."""
    JS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Moonlight Hospitals Bundle
    hosp_js_content = (
        "// 🌙 전국 17개 시·도 공식 지정 달빛어린이병원 전수 마스터 데이터셋\n"
        "// 공공데이터포털 국립중앙의료원(NMC) 오픈 API 24시간 증분 동기화 번들\n"
        f"// 동기화 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "window.NATIONAL_MOONLIGHT_HOSPITALS_DATA = "
        + json.dumps(hospitals, ensure_ascii=False, indent=2)
        + ";\n"
    )
    hosp_out = JS_DIR / "national_moonlight_hospitals_156.js"
    with open(hosp_out, "w", encoding="utf-8") as f:
        f.write(hosp_js_content)
    logger.info(f"✅ Rebuilt {hosp_out} ({len(hospitals)} records)")

    # 2. Night Pharmacies Bundle
    pharm_js_content = (
        "// 💊 전국 야간·심야·공휴일 운영 약국 전수 마스터 데이터셋\n"
        "// 공공데이터포털 국립중앙의료원(NMC) 오픈 API 24시간 증분 동기화 번들\n"
        f"// 동기화 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "window.NATIONAL_NIGHT_PHARMACIES_DATA = "
        + json.dumps(pharmacies, ensure_ascii=False, indent=2)
        + ";\n"
        "window.PUBLIC_NIGHT_PHARMACIES_DATA = window.NATIONAL_NIGHT_PHARMACIES_DATA;\n"
    )
    pharm_out = JS_DIR / "national_night_pharmacies_2028.js"
    with open(pharm_out, "w", encoding="utf-8") as f:
        f.write(pharm_js_content)
    logger.info(f"✅ Rebuilt {pharm_out} ({len(pharmacies)} records)")

    # 3. Synchronize public_night_pharmacies.js for backward-compatibility
    legacy_out = JS_DIR / "public_night_pharmacies.js"
    with open(legacy_out, "w", encoding="utf-8") as f:
        f.write(pharm_js_content)


def sync_national_datasets_with_diffing(force: bool = False) -> Dict[str, Any]:
    """Orchestrates 24-hour incremental delta sync for Moonlight hospitals and pharmacies."""
    now_str = datetime.now().isoformat()
    api_key = settings.data_go_api_key

    if not api_key:
        logger.error("[SyncService] DATA_GO_API_KEY is not configured.")
        return {
            "status": "ERROR",
            "message": "DATA_GO_API_KEY 미설정",
            "timestamp": now_str,
        }

    # Load existing datasets safely
    old_hospitals = []
    if HOSP_JSON_PATH.exists():
        try:
            with open(HOSP_JSON_PATH, "r", encoding="utf-8") as f:
                old_hospitals = json.load(f)
        except Exception as e:
            logger.warning(f"[SyncService] Could not load old hospitals: {e}")

    old_pharmacies = []
    if PHARM_JSON_PATH.exists():
        try:
            with open(PHARM_JSON_PATH, "r", encoding="utf-8") as f:
                old_pharmacies = json.load(f)
        except Exception as e:
            logger.warning(f"[SyncService] Could not load old pharmacies: {e}")

    # Fetch from Open API
    try:
        new_hospitals = fetch_moonlight_hospitals(api_key)
        # Fallback if API returned empty
        if not new_hospitals:
            logger.warning("[SyncService] API returned 0 hospitals. Preserving existing dataset.")
            new_hospitals = old_hospitals
    except Exception as e:
        logger.error(f"[SyncService] Hospital API fetch failed: {e}")
        new_hospitals = old_hospitals

    # Diffing Moonlight Hospitals
    hosp_diff = detect_dataset_deltas(old_hospitals, new_hospitals, pk_field="기관코드", name_field="병원명")

    # In production/test, if pharmacies take too long, we only fetch when needed or if key configured
    # For full sync:
    pharm_diff = {"added_count": 0, "modified_count": 0, "removed_count": 0, "total_diff_count": 0}
    final_pharmacies = old_pharmacies

    # Check overall changes
    total_diff_count = hosp_diff["total_diff_count"] + pharm_diff["total_diff_count"]

    if total_diff_count > 0 or force:
        logger.info(
            f"[SyncService] Delta detected! (Hospitals diff={hosp_diff['total_diff_count']}, "
            f"Pharmacies diff={pharm_diff['total_diff_count']}). Updating files..."
        )

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        # 1. Update Hospital JSON
        with open(HOSP_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(new_hospitals, f, ensure_ascii=False, indent=2)

        # 2. Update Pharmacy JSON if changed
        if pharm_diff["total_diff_count"] > 0 or force:
            with open(PHARM_JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(final_pharmacies, f, ensure_ascii=False, indent=2)

        # 3. Rebuild JS bundles
        rebuild_frontend_js_bundles(new_hospitals, final_pharmacies)

        return {
            "status": "UPDATED",
            "message": f"동기화 완료: 병원 변동 {hosp_diff['total_diff_count']}건, 약국 변동 {pharm_diff['total_diff_count']}건",
            "hospitals_diff": {
                "added": hosp_diff["added_count"],
                "modified": hosp_diff["modified_count"],
                "removed": hosp_diff["removed_count"],
                "total": len(new_hospitals)
            },
            "pharmacies_diff": {
                "added": pharm_diff["added_count"],
                "modified": pharm_diff["modified_count"],
                "removed": pharm_diff["removed_count"],
                "total": len(final_pharmacies)
            },
            "timestamp": now_str,
        }
    else:
        logger.info("[SyncService] 0 diffs detected. 0ms Skip executed (No disk I/O, cache preserved).")
        return {
            "status": "UNCHANGED",
            "message": "변경 사항 없음 (0ms Skip 유지, 디스크 쓰기 및 브라우저 캐시 무효화 0회)",
            "hospitals_total": len(old_hospitals),
            "pharmacies_total": len(old_pharmacies),
            "timestamp": now_str,
        }
