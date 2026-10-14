"""Moonlight hospital & night pharmacy pairing service.

Provides spatial search and retrieval for Moonlight children's hospitals paired
with designated night/late-hour pharmacies ensuring a +30-minute safe dispensing margin.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from app.config import settings
from app.services.spatial_service import haversine_distance

PAIRINGS_FILE = settings.project_root / "data" / "nationwide_pairings.json"

_cached_pairings: list[dict[str, Any]] = []


def load_nationwide_pairings() -> list[dict[str, Any]]:
    """Loads nationwide hospital-pharmacy pairings from disk cache."""
    global _cached_pairings
    if _cached_pairings:
        return _cached_pairings

    if PAIRINGS_FILE.exists():
        try:
            with open(PAIRINGS_FILE, "r", encoding="utf-8") as f:
                _cached_pairings = json.load(f)
                return _cached_pairings
        except Exception:
            pass

    return []


def find_nearby_pairings(
    user_lat: float,
    user_lon: float,
    max_radius_km: float = 25.0,
    limit: int = 3,
) -> list[dict[str, Any]]:
    """Finds nearest Moonlight children's hospitals and their 30-min margin paired pharmacies.

    Args:
        user_lat: User GPS latitude.
        user_lon: User GPS longitude.
        max_radius_km: Maximum search radius in km.
        limit: Maximum number of results to return.

    Returns:
        List of paired hospital-pharmacy dicts sorted by proximity to the user.
    """
    pairings = load_nationwide_pairings()
    results: list[dict[str, Any]] = []

    for item in pairings:
        h_lat = float(item.get("병원위도", 0.0))
        h_lon = float(item.get("병원경도", 0.0))
        if not h_lat or not h_lon:
            continue

        dist_km = haversine_distance(user_lat, user_lon, h_lat, h_lon)
        if dist_km <= max_radius_km:
            entry = dict(item)
            entry["거리_km"] = dist_km
            results.append(entry)

    results.sort(key=lambda x: x["거리_km"])
    return results[:limit]
