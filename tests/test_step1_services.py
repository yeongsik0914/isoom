"""Unit and integration test suite for Step 1: Zero-LLM domain services and storage.

Covers:
- Configuration and API key/Firebase credential resolution.
- KASI holiday surge risk assessment.
- Medical notice NLP regex 10 Golden Test Cases (100% accuracy).
- Haversine spherical distance calculation and 10km hospital ranking.
- In-memory Hash Diffing (FinOps: free tier quota defense).
- E-Gen emergency bed live/mock data ingestion.
- Firestore write batch synchronization and realtime summary upsert.
"""

from __future__ import annotations

import datetime
import unittest

from app.config import get_firestore_client, settings
from app.schemas.emergency import EmergencyBedInfo, HolidayInfo
from app.services.emergency_sync_service import (
    PEDIATRIC_BLOCK_PATTERN,
    BedStateHashCache,
    fetch_emergency_beds,
    sync_to_firestore,
)
from app.services.holiday_service import HolidayService, get_kasi_holiday_info
from app.services.spatial_service import (
    haversine_distance,
    rank_emergency_hospitals,
)


class TestStep1Services(unittest.TestCase):
    """Step 1 domain services test suite."""

    def test_01_config_and_credentials_resolution(self) -> None:
        """Verifies that project configuration resolves API keys and Firebase credentials."""
        self.assertTrue(settings.project_root.exists())
        self.assertIsNotNone(settings.firebase_key_path, "FIREBASE_KEY_PATH must be resolved.")
        self.assertTrue(settings.has_firebase_key(), "Firebase serviceAccountKey.json must exist.")
        if not settings.data_go_api_key:
            self.skipTest("DATA_GO_API_KEY not configured in .env (mock mode active).")
        self.assertTrue(len(settings.data_go_api_key or "") > 5)


    def test_02_holiday_service_and_surge_risk(self) -> None:
        """Verifies weekend and public holiday surge risk level determination."""
        # Test known Saturday
        saturday = datetime.date(2026, 10, 10)
        sat_info = HolidayService.get_holiday_info(target_date=saturday)
        self.assertTrue(sat_info.is_holiday)
        self.assertEqual(sat_info.holiday_name, "토요일")
        self.assertIn(sat_info.surge_risk_level, ["HIGH", "CRITICAL"])

        # Test known Sunday
        sunday = datetime.date(2026, 10, 11)
        sun_info = HolidayService.get_holiday_info(target_date=sunday)
        self.assertTrue(sun_info.is_holiday)
        self.assertEqual(sun_info.holiday_name, "일요일")
        self.assertIn(sun_info.surge_risk_level, ["HIGH", "CRITICAL"])

        # Test today's evaluation
        today_info = get_kasi_holiday_info()
        self.assertIsInstance(today_info, HolidayInfo)
        self.assertIn(today_info.surge_risk_level, ["NORMAL", "HIGH", "CRITICAL"])

    def test_03_pediatric_notice_nlp_golden_cases(self) -> None:
        """Evaluates clinical notice NLP regex against all 10 Golden Test Cases (Target: 100% accuracy)."""
        golden_cases = [
            {"text": "소아 전용 응급실 정상 진료 가능", "expected_blocked": False, "desc": "정상 가동"},
            {"text": "야간 소아 당직의 부재로 소아 발열 진료 불가", "expected_blocked": True, "desc": "의사 부재"},
            {"text": "신생아 및 12개월 미만 영유아 진료 제한", "expected_blocked": True, "desc": "영아 거부"},
            {"text": "성인 응급실만 운영 중이며 소아 환자 접수 불가", "expected_blocked": True, "desc": "성인 전용"},
            {"text": "소아 단순 열감기는 가능하나 소아 봉합/외상 불가", "expected_blocked": True, "desc": "부분 제한"},
            {"text": "소아청소년과 전문의 병가로 소아 수술 중단", "expected_blocked": True, "desc": "수술 중단"},
            {"text": "소아 야간 진료 21시 조기 마감됨", "expected_blocked": True, "desc": "조기 마감"},
            {"text": "소아 병상 만실로 대기 시간 3시간 이상", "expected_blocked": False, "desc": "지연 진료 (병상 유효)"},
            {"text": "소아 음압 격리병상 가동 중", "expected_blocked": False, "desc": "격리 가동"},
            {"text": "소아 진료 일체 안됨 (119 구급대 이송 불가)", "expected_blocked": True, "desc": "원천 차단"},
        ]

        passed = 0
        for tc in golden_cases:
            is_blocked = bool(PEDIATRIC_BLOCK_PATTERN.search(tc["text"]))
            self.assertEqual(
                is_blocked,
                tc["expected_blocked"],
                f"Failed on case '{tc['desc']}': '{tc['text']}'",
            )
            passed += 1

        self.assertEqual(passed, len(golden_cases), "All 10 Golden Test Cases must pass 100%.")

    def test_04_spatial_haversine_and_ranking(self) -> None:
        """Verifies Haversine spherical distance calculation and hospital ranking."""
        # Distance between Jamsil Station (37.5133, 127.1001) and Gangnam Station (37.4979, 127.0276)
        dist = haversine_distance(37.5133, 127.1001, 37.4979, 127.0276)
        self.assertAlmostEqual(dist, 6.64, delta=0.5)

        # Distance to identical point must be 0
        self.assertEqual(haversine_distance(37.5, 127.0, 37.5, 127.0), 0.0)

        # Test sample ranking around Jamsil Station (37.5133, 127.1001)
        test_hospitals = [
            EmergencyBedInfo(
                hpid="H1",
                hospital_name="서울아산병원 (풍납동)",
                pediatric_beds=4,
                general_beds=10,
                lat=37.5266,
                lon=127.1086,
                notice_raw="정상",
                is_pediatric_blocked=False,
                pediatric_acceptable=True,
            ),
            EmergencyBedInfo(
                hpid="H2",
                hospital_name="삼성서울병원 (일원동)",
                pediatric_beds=2,
                general_beds=8,
                lat=37.4882,
                lon=127.0856,
                notice_raw="정상",
                is_pediatric_blocked=False,
                pediatric_acceptable=True,
            ),
            EmergencyBedInfo(
                hpid="H3",
                hospital_name="신촌세브란스 (서대문구)",
                pediatric_beds=1,
                general_beds=5,
                lat=37.5623,
                lon=126.9408,
                notice_raw="원거리",
                is_pediatric_blocked=False,
                pediatric_acceptable=True,
            ),
        ]

        ranked = rank_emergency_hospitals(
            test_hospitals,
            user_lat=37.5133,
            user_lon=127.1001,
            max_radius_km=10.0,
            only_acceptable=True,
        )

        # H1 (Asan ~1.7km) and H2 (Samsung ~3.1km) are within 10km, H3 (~15km) is excluded
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0].hpid, "H1")
        self.assertEqual(ranked[1].hpid, "H2")
        self.assertLess(ranked[0].distance_km, ranked[1].distance_km)

    def test_05_hash_diffing_finops_quota_defense(self) -> None:
        """Verifies In-memory Hash Diffing logic preventing redundant Firestore writes."""
        cache = BedStateHashCache()

        sample_dataset = [
            EmergencyBedInfo(
                hpid=f"HP_{i}",
                hospital_name=f"Hospital {i}",
                pediatric_beds=2,
                general_beds=5,
                notice_raw="정상 진료",
                pediatric_acceptable=True,
            )
            for i in range(20)
        ]

        # 1st run: All items must be marked as changed (100% write)
        changed_1, skipped_1 = cache.diff_and_filter(sample_dataset)
        self.assertEqual(len(changed_1), 20)
        self.assertEqual(skipped_1, 0)

        # 2nd run with exact same data: 0 writes, 20 skipped (100% cost saving)
        changed_2, skipped_2 = cache.diff_and_filter(sample_dataset)
        self.assertEqual(len(changed_2), 0)
        self.assertEqual(skipped_2, 20)

        # 3rd run with 1 item modified: only 1 written, 19 skipped (95% cost saving)
        modified_dataset = [h.model_copy() for h in sample_dataset]
        modified_dataset[0].pediatric_beds = 0
        modified_dataset[0].pediatric_acceptable = False

        changed_3, skipped_3 = cache.diff_and_filter(modified_dataset)
        self.assertEqual(len(changed_3), 1)
        self.assertEqual(changed_3[0].hpid, "HP_0")
        self.assertEqual(skipped_3, 19)

    def test_06_fetch_emergency_beds(self) -> None:
        """Verifies live or mock ingestion of emergency beds."""
        beds = fetch_emergency_beds(stage1="서울특별시")
        self.assertGreater(len(beds), 0, "Emergency beds must be fetched.")
        sample = beds[0]
        self.assertIsInstance(sample, EmergencyBedInfo)
        self.assertTrue(len(sample.hpid) > 0)
        self.assertTrue(len(sample.hospital_name) > 0)
        self.assertIsInstance(sample.pediatric_acceptable, bool)

    def test_07_firestore_sync_integration(self) -> None:
        """Verifies end-to-end integration: Firestore batch sync and realtime summary doc."""
        db = get_firestore_client()
        self.assertIsNotNone(db, "Firestore client must be connected.")

        beds = fetch_emergency_beds(stage1="서울특별시")
        holiday_meta = get_kasi_holiday_info()

        isolated_cache = BedStateHashCache()
        # 1st sync: Write batch to Firestore
        result = sync_to_firestore(
            hospitals=beds,
            holiday_meta=holiday_meta,
            db=db,
            use_diffing=True,
            hash_cache=isolated_cache,
        )

        self.assertGreater(result["total_count"], 0)
        self.assertEqual(result["synced_count"], result["total_count"])
        self.assertEqual(result["skipped_count"], 0)

        # Verify summary document in Firestore
        summary_doc = db.collection("emergency_summary").document("realtime").get()
        self.assertTrue(summary_doc.exists, "Summary doc emergency_summary/realtime must exist.")
        summary_data = summary_doc.to_dict()
        self.assertEqual(summary_data["total_count"], result["total_count"])
        self.assertEqual(summary_data["acceptable_count"], result["acceptable_count"])

        # 2nd sync: Zero write cost verification
        result_2 = sync_to_firestore(
            hospitals=beds,
            holiday_meta=holiday_meta,
            db=db,
            use_diffing=True,
            hash_cache=isolated_cache,
        )
        self.assertEqual(result_2["synced_count"], 0)
        self.assertEqual(result_2["skipped_count"], result_2["total_count"])
        self.assertEqual(result_2["saving_rate_percent"], 100.0)


if __name__ == "__main__":
    unittest.main()
