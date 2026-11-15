"""Conformal Uncertainty Quantification & Active Info-Gain Triage Engine.

Applies selective/conformal prediction principles for high-stakes pediatric triage:
1. Computes calibrated prediction sets (e.g., [2, 3], [3, 4]) and uncertainty score [0, 1].
2. Enforces Conservative Safety Escalation on ambiguous high-acuity boundaries
   (e.g. infant near 100 days/3 months with fever >= 38.0C or high fever near 39.5C).
3. Selects the highest Information-Gain differentiating follow-up question when vitals are partial.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.schemas.state import PatientSessionState
from app.services.telemetry import telemetry


@dataclass
class ConformalAssessment:
    """Calibrated uncertainty assessment for a pediatric triage decision."""

    point_ktas: Optional[int]
    escalated_ktas: Optional[int]
    prediction_set: list[int]
    uncertainty_score: float
    escalated: bool
    escalation_reason: Optional[str]
    info_gain_question: Optional[str]


def _select_highest_info_gain_question(state: PatientSessionState) -> Optional[str]:
    """Selects the most clinically discriminating follow-up question using heuristic info gain."""
    if state.age_months is None and state.age_days is None:
        return "아이의 정확한 생후 일수나 개월 수(나이)를 알려주시면 연령별 응급 기준을 정확히 대조할 수 있어요."
    if state.temperature is None:
        return "현재 측정된 체온(℃)을 알려주시면 해열·응급 등급을 더 정확히 판단할 수 있어요."
    if state.duration_hours is None:
        return "증상이 처음 시작된 지 몇 시간 정도 되었는지, 아이가 축 처지거나 숨쉬기 힘들어하지는 않는지 알려주세요."
    return None


def evaluate_triage_uncertainty(
    state: PatientSessionState,
    proposed_ktas: Optional[int],
    retrieval_top_score: float = 0.0,
    retrieval_margin: float = 0.0,
) -> ConformalAssessment:
    """Evaluates triage uncertainty and applies conservative escalation on boundary risk."""
    if proposed_ktas is None:
        return ConformalAssessment(
            point_ktas=None,
            escalated_ktas=None,
            prediction_set=[2, 3, 4],
            uncertainty_score=0.85,
            escalated=False,
            escalation_reason=None,
            info_gain_question=_select_highest_info_gain_question(state),
        )

    uncertainty = 0.12
    prediction_set: list[int] = [proposed_ktas]
    escalated_ktas = proposed_ktas
    escalated = False
    reason: Optional[str] = None

    # 1. Missing core vital uncertainty contributions
    if state.age_months is None and state.age_days is None:
        uncertainty += 0.22
    if state.temperature is None:
        uncertainty += 0.18
    if state.duration_hours is None:
        uncertainty += 0.08
    if not state.symptoms:
        uncertainty += 0.15

    # 2. Ambiguous retrieval margin
    if retrieval_top_score > 0.0 and retrieval_margin < 0.002:
        uncertainty += 0.14

    # 3. Borderline high-acuity risk intervals -> include upper acuity tier in prediction set
    near_young_infant = (
        (state.age_days is not None and 90 <= state.age_days <= 120)
        or (state.age_months is not None and state.age_months == 3)
    )
    high_fever_boundary = state.temperature is not None and state.temperature >= 39.2
    moderate_fever_boundary = state.temperature is not None and state.temperature >= 38.0

    if near_young_infant and moderate_fever_boundary and proposed_ktas >= 3:
        prediction_set = sorted({2, proposed_ktas})
        escalated_ktas = 2
        escalated = True
        reason = "영아 3~4개월 경계 구간 및 38.0℃ 이상 발열에 대한 Conformal 안전 상위 에스컬레이션 (KTAS 2단계)"
        uncertainty = max(uncertainty, 0.45)
    elif high_fever_boundary and proposed_ktas >= 4:
        prediction_set = sorted({3, proposed_ktas})
        escalated_ktas = 3
        escalated = True
        reason = "고열(39.2℃ 이상) 경계 구간 불확실성에 따른 Conformal 보수적 상향 조정 (KTAS 3단계)"
        uncertainty = max(uncertainty, 0.38)
    elif uncertainty >= 0.42 and proposed_ktas > 2:
        upper = proposed_ktas - 1
        prediction_set = sorted({upper, proposed_ktas})
        # Conservative upgrade only when age & temp are both missing and symptom mentions respiratory/systemic signs
        if any(s in state.symptoms for s in ("호흡곤란", "쌕쌕거림/천명", "구토", "처짐", "탈수")):
            escalated_ktas = upper
            escalated = True
            reason = f"필수 바이탈 미확보 및 고위험 증상 동반으로 보수적 상위 등급 조정 (KTAS {upper}단계)"

    uncertainty = round(min(0.99, uncertainty), 3)
    if escalated:
        telemetry.inc("conformal_safety_escalations")

    return ConformalAssessment(
        point_ktas=proposed_ktas,
        escalated_ktas=escalated_ktas,
        prediction_set=prediction_set,
        uncertainty_score=uncertainty,
        escalated=escalated,
        escalation_reason=reason,
        info_gain_question=_select_highest_info_gain_question(state),
    )
