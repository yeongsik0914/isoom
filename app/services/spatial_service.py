"""Spatial distance and ranking service using Haversine spherical formula.

Calculates spherical distance between user coordinates and emergency departments
within microseconds, filtering and ranking by proximity and pediatric availability.
"""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path
from typing import Any, Optional, Sequence, Union

from app.config import settings
from app.schemas.emergency import EmergencyBedInfo, RankedEmergencyHospital

logger = logging.getLogger(__name__)

EARTH_RADIUS_KM = 6371.0
NATIONAL_METADATA_FILE = settings.project_root / "data" / "national_emergency_metadata.json"

# In-memory cached nationwide metadata
_national_er_metadata: Optional[dict[str, dict[str, Any]]] = None


def get_national_er_metadata() -> dict[str, dict[str, Any]]:
    """Loads and caches national emergency hospital metadata (530 institutions)."""
    global _national_er_metadata
    if _national_er_metadata is not None:
        return _national_er_metadata

    _national_er_metadata = {}
    if NATIONAL_METADATA_FILE.exists():
        try:
            with open(NATIONAL_METADATA_FILE, "r", encoding="utf-8") as f:
                _national_er_metadata = json.load(f)
        except Exception as e:
            logger.warning(f"[SpatialService] Failed to load national_emergency_metadata.json: {e}")

    return _national_er_metadata


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates spherical distance (km) between two coordinates using Haversine formula.

    Execution time is typically < 5 microseconds per call.
    """
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return round(EARTH_RADIUS_KM * c, 2)


# Well-known pediatric specialized centers designated by Ministry of Health and Welfare
PEDIATRIC_SPECIALIZED_CENTERS: dict[str, str] = {
    "A1100010": "삼성서울병원",
    "A1100013": "서울아산병원",
    "A1100009": "재단법인아산사회복지재단 서울아산병원",
    "A1100012": "연세대학교 신촌세브란스병원",
    "A1100014": "서울대학교병원",
    "A2100005": "차의과학대학교 분당차병원",
    "A2100002": "아주대학교병원",
    "A1400001": "가천대길병원",
    "A1300010": "칠곡경북대학교병원",
    "A2800011": "양산부산대학교병원",
    "A1800441": "세종충남대학교병원",
    "A1500002": "전남대학교병원",
    "A2300002": "순천향대학교부속천안병원",
}

EMERGENCY_HOSPITAL_METADATA_MAP: dict[str, dict[str, str]] = {
    "A1100010": {"tel": "02-3410-2060", "center_type": "권역 소아전문응급센터", "alias": "삼성서울병원"},
    "A1100013": {"tel": "02-3010-3333", "center_type": "권역 소아전문응급센터", "alias": "서울아산병원"},
    "A1100009": {"tel": "02-3010-3333", "center_type": "권역 소아전문응급센터", "alias": "서울아산병원"},
    "A1100011": {"tel": "02-2258-2003", "center_type": "권역응급의료센터", "alias": "가톨릭대학교 서울성모병원"},
    "A1100012": {"tel": "02-2227-7777", "center_type": "권역 소아전문응급센터", "alias": "연세대학교 신촌세브란스병원"},
    "A1100014": {"tel": "02-2072-3400", "center_type": "권역 소아전문응급센터", "alias": "서울대학교병원"},
    "A1100015": {"tel": "02-2019-1400", "center_type": "지역응급의료센터", "alias": "강남세브란스병원"},
    "A1100002": {"tel": "02-2030-5555", "center_type": "지역응급의료센터", "alias": "건국대학교병원"},
    "A1100043": {"tel": "02-440-7000", "center_type": "지역응급의료센터", "alias": "강동경희대학교병원"},
    "A1100027": {"tel": "02-2224-2114", "center_type": "지역응급의료센터", "alias": "강동성심병원"},
    "A1100019": {"tel": "02-6299-1119", "center_type": "지역응급의료센터", "alias": "중앙대학교병원"},
    "A1100001": {"tel": "02-958-8114", "center_type": "지역응급의료센터", "alias": "경희대학교병원"},
    "A1100003": {"tel": "02-920-5370", "center_type": "권역응급의료센터", "alias": "고려대학교안암병원"},
    "A1100005": {"tel": "02-2626-1114", "center_type": "권역응급의료센터", "alias": "고려대학교구로병원"},
    "A1100006": {"tel": "02-2290-8282", "center_type": "권역응급의료센터", "alias": "한양대학교병원"},
    "A1100007": {"tel": "02-2650-5119", "center_type": "권역응급의료센터", "alias": "이대목동병원"},
    "A1100008": {"tel": "02-2260-7114", "center_type": "중앙응급의료센터", "alias": "국립중앙의료원"},
    "A1100025": {"tel": "02-870-2114", "center_type": "지역응급의료센터", "alias": "보라매병원"},
    "A1100030": {"tel": "02-3400-1114", "center_type": "지역응급의료기관", "alias": "경찰병원"},
}


def resolve_hospital_metadata(hpid: str, name: str) -> tuple[str, str]:
    """Resolves phone number and center classification type for any emergency department nationwide."""
    # 1. Specialized pediatric center designation
    if hpid in PEDIATRIC_SPECIALIZED_CENTERS or "소아전문" in name:
        ctype = "권역 소아전문응급센터"
    else:
        ctype = None

    # 2. Check national metadata cache
    nat_meta = get_national_er_metadata()
    if hpid in nat_meta:
        m = nat_meta[hpid]
        tel = m.get("tel") or "119"
        center_type = ctype or m.get("center_type") or "지역응급의료센터"
        return tel, center_type

    # 3. Check legacy static map
    if hpid in EMERGENCY_HOSPITAL_METADATA_MAP:
        meta = EMERGENCY_HOSPITAL_METADATA_MAP[hpid]
        return meta.get("tel", "119"), ctype or meta.get("center_type", "지역응급의료센터")

    # 4. Name-based fallback lookup
    for meta in EMERGENCY_HOSPITAL_METADATA_MAP.values():
        alias = meta.get("alias", "")
        if alias and (alias in name or name in alias):
            return meta.get("tel", "119"), ctype or meta.get("center_type", "지역응급의료센터")

    # 5. Generic heuristics
    if not ctype:
        if "대학" in name or "의료원" in name:
            ctype = "권역응급의료센터"
        else:
            ctype = "지역응급의료센터"

    return "119", ctype


def rank_emergency_hospitals(
    hospitals: Sequence[Union[dict[str, Any], EmergencyBedInfo]],
    user_lat: float,
    user_lon: float,
    max_radius_km: float = 25.0,
    only_acceptable: bool = False,
    limit: int = 10,
) -> list[RankedEmergencyHospital]:
    """Filters and sorts emergency hospitals within max_radius_km by distance.

    Calculates Haversine distance from user GPS coordinates. If no hospital is
    within initial max_radius_km (e.g. in rural/provincial areas), adaptively
    expands the search up to 60km to guarantee nearest emergency care routing.
    """
    candidates: list[tuple[float, Any]] = []

    for hosp in hospitals:
        if isinstance(hosp, dict):
            h_lat = float(hosp.get("lat", 37.5))
            h_lon = float(hosp.get("lon", 127.0))
            p_acceptable = bool(hosp.get("pediatric_acceptable", False))
        else:
            h_lat = hosp.lat
            h_lon = hosp.lon
            p_acceptable = hosp.pediatric_acceptable

        dist = haversine_distance(user_lat, user_lon, h_lat, h_lon)

        # Check pediatric acceptability if required
        if only_acceptable and not p_acceptable:
            continue

        candidates.append((dist, hosp))

    # Sort all candidates by distance ascending
    candidates.sort(key=lambda x: x[0])

    # Filter within max_radius_km
    matched = [c for c in candidates if c[0] <= max_radius_km]

    # Adaptive radius expansion: If no hospital within max_radius_km, expand up to 60km
    if not matched and candidates:
        matched = [c for c in candidates if c[0] <= 60.0]
        if not matched:
            # Absolute fallback: Return top 2 nearest hospitals anywhere
            matched = candidates[:2]

    ranked_list: list[RankedEmergencyHospital] = []
    for dist, hosp in matched[:limit]:
        if isinstance(hosp, dict):
            hpid = str(hosp.get("hpid", ""))
            name = str(hosp.get("hospital_name", ""))
            p_beds = int(hosp.get("pediatric_beds", 0))
            g_beds = int(hosp.get("general_beds", 0))
            p_iso_beds = int(hosp.get("pediatric_iso_beds", 0))
            p_acceptable = bool(hosp.get("pediatric_acceptable", False))
            p_blocked = bool(hosp.get("is_pediatric_blocked", False))
            notice = str(hosp.get("notice_raw", ""))
            synced_at = hosp.get("synced_at")
            h_lat = float(hosp.get("lat", 37.5))
            h_lon = float(hosp.get("lon", 127.0))
        else:
            hpid = hosp.hpid
            name = hosp.hospital_name
            p_beds = hosp.pediatric_beds
            g_beds = hosp.general_beds
            p_iso_beds = hosp.pediatric_iso_beds
            p_acceptable = hosp.pediatric_acceptable
            p_blocked = hosp.is_pediatric_blocked
            notice = hosp.notice_raw
            synced_at = getattr(hosp, "input_date", None)
            h_lat = hosp.lat
            h_lon = hosp.lon

        tel, center_type = resolve_hospital_metadata(hpid, name)
        synced_at_str = str(synced_at) if synced_at else None

        ranked_list.append(
            RankedEmergencyHospital(
                hpid=hpid,
                hospital_name=name,
                distance_km=dist,
                pediatric_beds=p_beds,
                general_beds=g_beds,
                pediatric_iso_beds=p_iso_beds,
                pediatric_acceptable=p_acceptable,
                is_pediatric_blocked=p_blocked,
                notice_raw=notice,
                lat=h_lat,
                lon=h_lon,
                tel=tel,
                center_type=center_type,
                synced_at=synced_at_str,
            )
        )

    return ranked_list

