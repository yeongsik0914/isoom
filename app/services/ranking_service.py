"""Multi-Objective Pareto Ranking, MMR Diversity & Safety-Constrained Bandit.

Enhances deterministic clinical facility matching with:
1. Multi-Objective Composite Score balancing Distance/ETA, Pediatric Bed Availability,
   Clinical Acuity Fit, and 30-min Safe Pharmacy Margin.
2. Maximal Marginal Relevance (MMR) penalty preventing homogeneous facility clustering.
3. Safety-Constrained Beta-Bernoulli Thompson Sampling: strictly DISABLED (0.0 weight)
   for Red Flag / KTAS 1~2 emergencies; bounded feedback adjustment for KTAS 3~5.
"""

from __future__ import annotations

import math
import random
import threading
from typing import Any, Optional

from app.services.telemetry import telemetry


class FacilityBandit:
    """Beta-Bernoulli Thompson Sampling tracker for non-critical hospital feedback."""

    def __init__(self, seed: int = 42) -> None:
        self._lock = threading.Lock()
        self._rng = random.Random(seed)
        # facility_key -> [alpha, beta]
        self._stats: dict[str, list[float]] = {}

    def record_feedback(self, facility_key: str, positive: bool) -> dict[str, float]:
        if not facility_key:
            return {"alpha": 1.0, "beta": 1.0}
        with self._lock:
            ab = self._stats.setdefault(facility_key, [1.0, 1.0])
            if positive:
                ab[0] += 1.0
            else:
                ab[1] += 1.0
            telemetry.inc("bandit_feedback_positive" if positive else "bandit_feedback_negative")
            return {"alpha": ab[0], "beta": ab[1]}

    def sample_bonus(self, facility_key: str, ktas_level: Optional[int], is_red_flag: bool) -> float:
        """Returns bounded exploration bonus; strictly 0.0 for KTAS 1~2 or Red Flag."""
        if is_red_flag or (ktas_level is not None and ktas_level <= 2):
            return 0.0
        with self._lock:
            alpha, beta = self._stats.get(facility_key, (1.0, 1.0))
            if alpha == 1.0 and beta == 1.0:
                return 0.0
            sampled = self._rng.betavariate(alpha, beta)
        # Centered around 0.0 within [-0.04, +0.06] so clinical distance & safety dominate
        return round((sampled - 0.5) * 0.10, 4)


facility_bandit = FacilityBandit()


def compute_facility_multi_objective_score(
    hospital: dict[str, Any],
    ktas_level: Optional[int],
    is_red_flag: bool,
    paired_pharmacy: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Computes transparent multi-objective score [0..100] and clinical rationale tags."""
    dist_km = float(hospital.get("거리_km", 0.0) or 0.0)
    ped_beds = int(hospital.get("소아병상수", 0) or 0)
    gen_beds = int(hospital.get("일반병상수", 0) or 0)
    utype = str(hospital.get("유형", ""))

    # 1. Distance / ETA proximity decay (0..45 pts)
    dist_score = 45.0 * math.exp(-dist_km / 10.0)

    # 2. Bed / capacity readiness (0..25 pts)
    if "달빛" in utype:
        bed_score = 18.0
    else:
        bed_score = min(25.0, ped_beds * 4.5 + min(gen_beds, 10) * 0.8)

    # 3. Clinical acuity fit (0..20 pts)
    is_er = "응급" in utype
    if is_red_flag or (ktas_level is not None and ktas_level <= 2):
        fit_score = 20.0 if is_er else 4.0
    else:
        fit_score = 20.0 if ("달빛" in utype or is_er) else 12.0

    # 4. 30-min pharmacy margin alignment (0..10 pts)
    margin_min = float((paired_pharmacy or {}).get("안전마진_분", 0) or 0)
    if margin_min >= 30:
        margin_score = 10.0
    elif margin_min > 0:
        margin_score = min(8.0, margin_min / 4.0)
    else:
        margin_score = 5.0 if is_er else 2.0

    # 5. Safety-constrained Thompson Sampling adjustment
    key = str(hospital.get("hpid") or hospital.get("기관명") or "")
    bandit_bonus = facility_bandit.sample_bonus(key, ktas_level=ktas_level, is_red_flag=is_red_flag) * 100.0

    total = round(min(100.0, max(0.0, dist_score + bed_score + fit_score + margin_score + bandit_bonus)), 2)
    return {
        "score": total,
        "breakdown": {
            "proximity": round(dist_score, 2),
            "capacity": round(bed_score, 2),
            "acuity_fit": round(fit_score, 2),
            "pharmacy_margin": round(margin_score, 2),
            "bandit_adj": round(bandit_bonus, 2),
        },
    }


def apply_mmr_diversity_reranking(
    hospitals: list[dict[str, Any]],
    ktas_level: Optional[int],
    is_red_flag: bool,
    pharmacies: Optional[list[dict[str, Any]]] = None,
    lambda_div: float = 0.82,
) -> list[dict[str, Any]]:
    """Enriches matched hospitals with multi-objective scores & MMR diversity ordering.

    For KTAS 1~2 emergencies, preserves strict distance-first safety guarantees while
    still attaching explainable multi-objective telemetry fields.
    """
    if not hospitals:
        return hospitals

    scored: list[dict[str, Any]] = []
    for idx, h in enumerate(hospitals):
        paired = pharmacies[idx] if pharmacies and idx < len(pharmacies) else None
        mo = compute_facility_multi_objective_score(
            h, ktas_level=ktas_level, is_red_flag=is_red_flag, paired_pharmacy=paired
        )
        enriched = dict(h)
        enriched["종합점수"] = mo["score"]
        enriched["점수세부"] = mo["breakdown"]
        scored.append(enriched)

    # Preserve strict ER proximity ordering for critical KTAS 1~2 emergencies
    if is_red_flag or (ktas_level is not None and ktas_level <= 2):
        return scored

    # Greedy MMR selection balancing composite utility and facility type diversity
    selected: list[dict[str, Any]] = []
    remaining = list(scored)
    while remaining:
        best_item = None
        best_mmr = -1e9
        for cand in remaining:
            rel = float(cand["종합점수"]) / 100.0
            redundancy = 0.0
            if selected:
                c_type = str(cand.get("유형", ""))
                redundancy = max(
                    1.0 if str(s.get("유형", "")) == c_type else 0.25 for s in selected
                )
            mmr = lambda_div * rel - (1.0 - lambda_div) * redundancy
            if mmr > best_mmr:
                best_mmr = mmr
                best_item = cand
        assert best_item is not None
        selected.append(best_item)
        remaining.remove(best_item)

    return selected
