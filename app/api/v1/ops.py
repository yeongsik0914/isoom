"""LLMOps Observability, Bandit Feedback & Clinical Evaluation Endpoints (v1)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.evaluation.pediatric_benchmark import run_pediatric_benchmark
from app.services.auth import require_admin_token
from app.services.ranking_service import facility_bandit
from app.services.telemetry import telemetry

router = APIRouter()


class FacilityFeedbackRequest(BaseModel):
    facility_key: str = Field(..., min_length=1, description="병원 HPID 또는 기관명")
    positive: bool = Field(default=True, description="긍정(전화/길찾기 선택) 여부")


@router.get(
    "/summary",
    dependencies=[Depends(require_admin_token)],
    summary="LLMOps 실시간 텔레메트리 요약",
)
async def get_ops_summary():
    """Returns real-time stage latencies, token costs, RAG stats, and recent traces."""
    return telemetry.get_summary()


@router.post(
    "/feedback",
    summary="의료기관 추천 사용자 피드백 기록 (Bandit Reward)",
)
async def record_facility_feedback(req: FacilityFeedbackRequest):
    """Records positive or negative interaction reward for Safety-Constrained Thompson Sampling."""
    stats = facility_bandit.record_feedback(req.facility_key, positive=req.positive)
    return {"status": "ok", "facility_key": req.facility_key, "posterior": stats}


@router.post(
    "/benchmark",
    dependencies=[Depends(require_admin_token)],
    summary="소아 KTAS 골든 벤치마크 및 안전 평가 실행",
)
async def execute_benchmark():
    """Executes the Golden Pediatric Triage & Safety benchmark suite."""
    return await run_pediatric_benchmark()
