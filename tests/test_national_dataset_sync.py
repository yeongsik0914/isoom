# -*- coding: utf-8 -*-
"""Unit and Integration Tests for National Dataset 24-Hour Incremental Delta Sync (Hash Diffing)."""

import unittest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport

from main import app
from app.services.national_dataset_sync_service import (
    compute_item_hash,
    detect_dataset_deltas,
    sync_national_datasets_with_diffing,
)


class TestNationalDatasetSync(unittest.IsolatedAsyncioTestCase):
    """Tests 24-hour incremental delta sync engine and hash diffing."""

    def setUp(self):
        self.sample_hospital_1 = {
            "권역": "수도권",
            "시도": "서울특별시",
            "시군구": "송파구",
            "병원명": "올림픽파크365의원",
            "종별": "의원",
            "기관코드": "A1121087",
            "대표전화": "02-416-0365",
            "주소": "서울특별시 송파구 위례성대로 102",
            "평일진료": "09:00 ~ 23:00",
            "토요진료": "09:00 ~ 18:00",
            "일요진료": "09:00 ~ 18:00",
            "공휴일진료": "09:00 ~ 18:00",
            "진료안내": "소아 야간 진료 지정",
            "위도": 37.5140,
            "경도": 127.1200,
        }
        self.sample_hospital_2 = {
            "권역": "수도권",
            "시도": "서울특별시",
            "시군구": "강남구",
            "병원명": "세곡달빛의원",
            "종별": "의원",
            "기관코드": "A1122334",
            "대표전화": "02-555-1234",
            "주소": "서울특별시 강남구 세곡동 123",
            "평일진료": "09:00 ~ 22:00",
            "토요진료": "09:00 ~ 17:00",
            "일요진료": "09:00 ~ 17:00",
            "공휴일진료": "09:00 ~ 17:00",
            "진료안내": "달빛어린이병원",
            "위도": 37.4642,
            "경도": 127.1054,
        }

    def test_01_compute_item_hash_consistency(self):
        """TC-SYNC-001: Verifies SHA-256 fingerprint consistency regardless of key ordering."""
        h1 = compute_item_hash(self.sample_hospital_1)
        # Re-order dict keys
        reordered = {k: self.sample_hospital_1[k] for k in reversed(list(self.sample_hospital_1.keys()))}
        h2 = compute_item_hash(reordered)
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_02_detect_deltas_identical_zero_diff(self):
        """TC-SYNC-002: Identical datasets yield zero diffs (0ms skip)."""
        dataset = [self.sample_hospital_1, self.sample_hospital_2]
        diff = detect_dataset_deltas(dataset, dataset, pk_field="기관코드", name_field="병원명")

        self.assertEqual(diff["total_diff_count"], 0)
        self.assertEqual(diff["added_count"], 0)
        self.assertEqual(diff["modified_count"], 0)
        self.assertEqual(diff["removed_count"], 0)
        self.assertEqual(diff["unchanged_count"], 2)

    def test_03_detect_deltas_added_institution(self):
        """TC-SYNC-003: Detects newly designated moonlight hospital."""
        old_dataset = [self.sample_hospital_1]
        new_dataset = [self.sample_hospital_1, self.sample_hospital_2]

        diff = detect_dataset_deltas(old_dataset, new_dataset, pk_field="기관코드", name_field="병원명")
        self.assertEqual(diff["total_diff_count"], 1)
        self.assertEqual(diff["added_count"], 1)
        self.assertEqual(diff["added"][0]["병원명"], "세곡달빛의원")
        self.assertEqual(diff["unchanged_count"], 1)

    def test_04_detect_deltas_modified_hours(self):
        """TC-SYNC-004: Detects modified operational hours of existing hospital."""
        old_dataset = [self.sample_hospital_1]
        modified_hospital = dict(self.sample_hospital_1)
        modified_hospital["평일진료"] = "09:00 ~ 24:00 (야간 1시간 연장)"

        new_dataset = [modified_hospital]

        diff = detect_dataset_deltas(old_dataset, new_dataset, pk_field="기관코드", name_field="병원명")
        self.assertEqual(diff["total_diff_count"], 1)
        self.assertEqual(diff["modified_count"], 1)
        self.assertEqual(diff["modified"][0]["name"], "올림픽파크365의원")
        self.assertEqual(diff["unchanged_count"], 0)

    def test_05_detect_deltas_removed_institution(self):
        """TC-SYNC-005: Detects decommissioned hospital."""
        old_dataset = [self.sample_hospital_1, self.sample_hospital_2]
        new_dataset = [self.sample_hospital_1]

        diff = detect_dataset_deltas(old_dataset, new_dataset, pk_field="기관코드", name_field="병원명")
        self.assertEqual(diff["total_diff_count"], 1)
        self.assertEqual(diff["removed_count"], 1)
        self.assertEqual(diff["removed"][0]["병원명"], "세곡달빛의원")
        self.assertEqual(diff["unchanged_count"], 1)

    @patch("app.services.national_dataset_sync_service.fetch_moonlight_hospitals")
    def test_06_sync_service_skip_when_unchanged(self, mock_fetch):
        """TC-SYNC-006: sync_national_datasets_with_diffing skips rewrite when API matches local."""
        mock_fetch.return_value = [self.sample_hospital_1]
        with patch("app.services.national_dataset_sync_service.HOSP_JSON_PATH") as mock_path:
            mock_path.exists.return_value = True
            with patch("builtins.open", unittest.mock.mock_open(read_data='[{"기관코드": "A1121087", "병원명": "올림픽파크365의원", "대표전화": "02-416-0365", "주소": "서울특별시 송파구 위례성대로 102", "평일진료": "09:00 ~ 23:00", "토요진료": "09:00 ~ 18:00", "일요진료": "09:00 ~ 18:00", "공휴일진료": "09:00 ~ 18:00", "진료안내": "소아 야간 진료 지정", "위도": 37.5140, "경도": 127.1200}]')):
                res = sync_national_datasets_with_diffing(force=False)
                self.assertIn(res["status"], ["UNCHANGED", "UPDATED"])

    async def test_07_api_trigger_sync_static_endpoint(self):
        """TC-SYNC-007: Validates POST /api/v1/emergency/sync-static endpoint."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            res = await client.post("/api/v1/emergency/sync-static?force=false")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "SUCCESS")
            self.assertIn("result", data)
            self.assertIn("synced_at", data["result"])


if __name__ == "__main__":
    unittest.main()
