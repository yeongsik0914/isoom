"""Unit & Integration Tests for TECH_UPGRADE_PLAN.md (Phases 1~4)."""

from __future__ import annotations

import os
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from httpx import ASGITransport, AsyncClient

from app.agents.conformal_triage import evaluate_triage_uncertainty
from app.agents.guardrail_agent import (
    check_safety_violations,
    verify_and_sanitize_clinical_response,
)
from app.evaluation.pediatric_benchmark import run_pediatric_benchmark
from app.orchestrator.supervisor import SupervisorOrchestrator
from app.schemas.state import PatientSessionState
from app.services.ktas_retriever import KtasHybridRetriever
from app.services.llm_gateway import LLMGateway
from app.services.ranking_service import (
    FacilityBandit,
    apply_mmr_diversity_reranking,
    compute_facility_multi_objective_score,
)
from app.services.semantic_cache import SafetyAwareSemanticCache
from app.services.telemetry import telemetry
from main import app


class TestTechUpgrade(unittest.IsolatedAsyncioTestCase):
    """Verifies Hybrid RAG, CRAG, Self-RAG, Conformal Triage, LangGraph FSM, Bandit, Cache, & Ops."""

    def test_01_hybrid_ktas_retriever_crag_and_self_rag(self) -> None:
        retriever = KtasHybridRetriever()
        res = retriever.retrieve_with_crag(
            query="아기가 열이 펄펄 나고 숨을 쌕쌕거려요",
            symptoms=["발열", "쌕쌕거림/천명"],
            temperature=39.1,
            age_months=18,
            top_k=5,
        )
        self.assertEqual(len(res.documents), 5)
        self.assertGreater(res.top_score, 0.0)
        self.assertLess(res.compressed_chars, 5000)

        # CRAG triggers on colloquial short query without matching clinical keywords directly
        weak_res = retriever.retrieve_with_crag(query="애가 아파보여", top_k=5, crag_threshold=0.05)
        self.assertTrue(weak_res.crag_triggered)

        # Self-RAG repairs non-existent NACRS code to top retrieved code
        verified = retriever.verify_clinical_grounding(
            ktas_level=5,
            matched_nacrs_code="INVALID-999",
            retrieved=res,
        )
        self.assertFalse(verified["grounded"])
        self.assertEqual(verified["nacrs_code"], res.documents[0][0].nacrs_code)

    def test_02_conformal_triage_boundary_escalation(self) -> None:
        state = PatientSessionState(
            session_id="conf-test",
            age_days=105,
            temperature=38.3,
            duration_hours=3,
            symptoms=["발열"],
        )
        assessment = evaluate_triage_uncertainty(state, proposed_ktas=3, retrieval_top_score=0.03, retrieval_margin=0.001)
        self.assertTrue(assessment.escalated)
        self.assertEqual(assessment.escalated_ktas, 2)
        self.assertEqual(assessment.prediction_set, [2, 3])
        self.assertGreater(assessment.uncertainty_score, 0.3)

    def test_03_semantic_guardrail_and_constitutional_post_guard(self) -> None:
        dosage_evasion = check_safety_violations("아기 해열제 반 알 쪼개서 먹여도 괜찮을까요?")
        self.assertIsNotNone(dosage_evasion)
        self.assertEqual(dosage_evasion["violation_type"], "SEMANTIC_DOSAGE_EVASION")

        diag_evasion = check_safety_violations("열이랑 발진 있는데 돌발진 맞죠?")
        self.assertIsNotNone(diag_evasion)
        self.assertEqual(diag_evasion["violation_type"], "SEMANTIC_DIAGNOSIS_EVASION")

        raw = "별일 아닙니다. 장염입니다. 타이레놀 10ml 먹이세요."
        cleaned, modified = verify_and_sanitize_clinical_response(raw, is_red_flag=True)
        self.assertTrue(modified)
        self.assertNotIn("별일 아닙니다", cleaned)
        self.assertNotIn("10ml", cleaned)
        self.assertIn("119", cleaned)
        self.assertIn("의료법 제27조 준수 고지", cleaned)

    def test_04_safety_aware_semantic_cache(self) -> None:
        cache = SafetyAwareSemanticCache()
        # Clinical queries MUST bypass
        cache.store("24개월 아이 열이 38.5도 나요", "응급실 가세요")
        self.assertIsNone(cache.lookup("24개월 아이 열이 38.5도 나요"))
        self.assertIsNone(cache.lookup("근처 달빛어린이병원 알려줘"))

        # Static informational query is safe to cache
        stored = cache.store("아이숨 서비스는 어떤 기능을 제공하나요", "소아 야간 응급 및 달빛어린이병원 안내 서비스입니다.")
        self.assertTrue(stored)
        hit = cache.lookup("아이숨 서비스는 어떤 기능을 제공하나요")
        self.assertIsNotNone(hit)
        self.assertIn("달빛어린이병원", hit)

    def test_05_multi_objective_mmr_and_safety_constrained_bandit(self) -> None:
        bandit = FacilityBandit(seed=7)
        for _ in range(10):
            bandit.record_feedback("H-GOOD", positive=True)

        # Red Flag / KTAS <= 2 MUST disable bandit exploration completely
        self.assertEqual(bandit.sample_bonus("H-GOOD", ktas_level=1, is_red_flag=False), 0.0)
        self.assertEqual(bandit.sample_bonus("H-GOOD", ktas_level=3, is_red_flag=True), 0.0)

        hospitals = [
            {"기관명": "A달빛의원", "유형": "달빛어린이병원", "거리_km": 2.0, "소아병상수": 0, "일반병상수": 0},
            {"기관명": "B달빛의원", "유형": "달빛어린이병원", "거리_km": 2.1, "소아병상수": 0, "일반병상수": 0},
            {"기관명": "C대학병원", "유형": "응급실 백업", "거리_km": 3.5, "소아병상수": 3, "일반병상수": 10},
        ]
        reranked = apply_mmr_diversity_reranking(hospitals, ktas_level=4, is_red_flag=False)
        self.assertEqual(len(reranked), 3)
        self.assertIn("종합점수", reranked[0])
        self.assertIn("점수세부", reranked[0])

        score_obj = compute_facility_multi_objective_score(
            hospitals[0], ktas_level=4, is_red_flag=False, paired_pharmacy={"안전마진_분": 45}
        )
        self.assertGreater(score_obj["score"], 50.0)

    def test_06_llm_gateway_model_fallback_and_telemetry(self) -> None:
        gw = LLMGateway(agent_label="TestGW")
        mock_client = MagicMock()
        mock_resp = SimpleNamespace(
            text='{"ok": true}',
            usage_metadata=SimpleNamespace(prompt_token_count=40, candidates_token_count=10),
        )
        # Primary model fails, secondary succeeds
        mock_client.models.generate_content.side_effect = [
            RuntimeError("503 overloaded"),
            mock_resp,
        ]
        txt, used_model = gw.generate_structured(
            prompt="hello",
            response_schema=dict,
            primary_model="gemini-3.8-flash",
            client_override=mock_client,
        )
        self.assertEqual(txt, '{"ok": true}')
        self.assertEqual(used_model, "gemini-2.5-flash")
        self.assertIn("gemini-2.5-flash", telemetry.get_summary()["model_usage"])

    async def test_07_state_graph_supervisor_and_golden_benchmark_and_ops_api(self) -> None:
        supervisor = SupervisorOrchestrator()
        resp = await supervisor.process_turn(
            user_message="36개월 아이 어제부터 38.4도 열과 콧물이 나요",
            force_matching=True,
        )
        self.assertEqual(resp.current_step, "COMPLETED")
        self.assertGreater(len(resp.pipeline_trace), 0)
        self.assertIn("guardrail", resp.pipeline_trace)
        self.assertIn("output_verifier", resp.pipeline_trace)

        bench = await run_pediatric_benchmark()
        self.assertEqual(bench["under_triage_rate_pct"], 0.0)
        self.assertEqual(bench["safety_defense_rate_pct"], 100.0)
        self.assertGreaterEqual(bench["pass_rate_pct"], 90.0)
        self.assertGreater(bench["rag_token_savings_pct"], 70.0)

        transport = ASGITransport(app=app)
        with patch.dict(os.environ, {"ADMIN_API_TOKEN": "ops-secret-token"}, clear=False):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                r_metrics = await client.get("/metrics")
                self.assertEqual(r_metrics.status_code, 200)
                self.assertIn("isoom_uptime_seconds", r_metrics.text)

                r_unauth = await client.get("/api/v1/ops/summary")
                self.assertEqual(r_unauth.status_code, 401)

                r_summary = await client.get(
                    "/api/v1/ops/summary",
                    headers={"Authorization": "Bearer ops-secret-token"},
                )
                self.assertEqual(r_summary.status_code, 200)
                self.assertIn("stage_latencies_ms", r_summary.json())

                r_fb = await client.post(
                    "/api/v1/ops/feedback",
                    json={"facility_key": "A1100010", "positive": True},
                )
                self.assertEqual(r_fb.status_code, 200)
                self.assertEqual(r_fb.json()["posterior"]["alpha"], 2.0)


if __name__ == "__main__":
    unittest.main()
