"""Spatial distance and ranking service using Haversine spherical formula.

Calculates spherical distance between user coordinates and emergency departments
within microseconds, filtering and ranking by proximity and pediatric availability.
"""

from __future__ import annotations

import math
from typing import Any, Sequence, Union

from app.schemas.emergency import EmergencyBedInfo, RankedEmergencyHospital

EARTH_RADIUS_KM = 6371.0


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


def rank_emergency_hospitals(
    hospitals: Sequence[Union[dict[str, Any], EmergencyBedInfo]],
    user_lat: float,
    user_lon: float,
    max_radius_km: float = 10.0,
    only_acceptable: bool = False,
    limit: int = 10,
) -> list[RankedEmergencyHospital]:
    """Filters and sorts emergency hospitals within max_radius_km by distance.

    Args:
        hospitals: Sequence of hospital dicts or EmergencyBedInfo models.
        user_lat: User GPS latitude (e.g. 37.5133 for Jamsil Station).
        user_lon: User GPS longitude (e.g. 127.1001 for Jamsil Station).
        max_radius_km: Search radius threshold (default: 10.0 km).
        only_acceptable: If True, only include hospitals where pediatric_acceptable is True.
        limit: Maximum number of ranked results to return.

    Returns:
        List of RankedEmergencyHospital sorted by proximity ascending.
    """
    ranked_list: list[RankedEmergencyHospital] = []

    for hosp in hospitals:
        # Extract fields whether dict or Pydantic model
        if isinstance(hosp, dict):
            h_lat = float(hosp.get("lat", 37.5))
            h_lon = float(hosp.get("lon", 127.0))
            hpid = str(hosp.get("hpid", ""))
            name = str(hosp.get("hospital_name", ""))
            p_beds = int(hosp.get("pediatric_beds", 0))
            g_beds = int(hosp.get("general_beds", 0))
            p_acceptable = bool(hosp.get("pediatric_acceptable", False))
            p_blocked = bool(hosp.get("is_pediatric_blocked", False))
            notice = str(hosp.get("notice_raw", ""))
        else:
            h_lat = hosp.lat
            h_lon = hosp.lon
            hpid = hosp.hpid
            name = hosp.hospital_name
            p_beds = hosp.pediatric_beds
            g_beds = hosp.general_beds
            p_acceptable = hosp.pediatric_acceptable
            p_blocked = hosp.is_pediatric_blocked
            notice = hosp.notice_raw

        dist = haversine_distance(user_lat, user_lon, h_lat, h_lon)

        if dist > max_radius_km:
            continue

        if only_acceptable and not p_acceptable:
            continue

        ranked_item = RankedEmergencyHospital(
            hpid=hpid,
            hospital_name=name,
            distance_km=dist,
            pediatric_beds=p_beds,
            general_beds=g_beds,
            pediatric_acceptable=p_acceptable,
            is_pediatric_blocked=p_blocked,
            notice_raw=notice,
            lat=h_lat,
            lon=h_lon,
        )
        ranked_list.append(ranked_item)

    ranked_list.sort(key=lambda x: x.distance_km)
    return ranked_list[:limit]
