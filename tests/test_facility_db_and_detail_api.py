# -*- coding: utf-8 -*-
"""Unit & Integration Tests for Facility Data Folder JSON Dataset & Detail REST API."""

import json
from pathlib import Path
import unittest
from fastapi.testclient import TestClient

from main import app
from app.services.facility_db_service import init_facility_db, get_facility_detail
from app.services.national_dataset_sync_service import (
    DATA_DIR,
    JS_DIR,
    HOSP_DETAIL_JSON_PATH,
    PHARM_DETAIL_JSON_PATH,
    HOSP_DETAIL_JS_PATH,
    PHARM_DETAIL_JS_PATH,
    build_and_save_detail_datasets,
)


class TestFacilityDbAndDetailApi(unittest.TestCase):
    """Verifies data folder JSON dataset persistence, 24h sync bundle integrity, and REST API serving."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # Ensure datasets and in-memory index are loaded
        cls.seed_result = init_facility_db(force=False)

    def test_01_dataset_loading_integrity(self):
        """Verifies that 156 hospitals and 2,028 pharmacies are loaded from data/ JSON."""
        self.assertGreaterEqual(self.seed_result["hospitals"], 150)
        self.assertGreaterEqual(self.seed_result["pharmacies"], 2000)

    def test_02_hospital_detail_direct_lookup(self):
        """Verifies direct lookup of a moonlight hospital with rich metadata from memory index."""
        hosp = get_facility_detail("hospital", "연세열린의원", user_lat=37.5, user_lon=127.0)
        self.assertIsNotNone(hosp)
        self.assertEqual(hosp["name"], "연세열린의원")
        self.assertIn("specialists", str(hosp))
        self.assertGreaterEqual(hosp["pediatric_specialists"], 1)
        self.assertGreaterEqual(hosp["parking_spaces"], 10)
        self.assertTrue(hosp["is_open_now"])
        self.assertIn("paired_pharmacy_name", hosp)

    def test_03_pharmacy_detail_direct_lookup(self):
        """Verifies direct lookup of a night pharmacy with pharmacist metadata from memory index."""
        pharm = get_facility_detail("pharmacy", "구정열린약국", user_lat=37.5, user_lon=127.0)
        self.assertIsNotNone(pharm)
        self.assertEqual(pharm["name"], "구정열린약국")
        self.assertGreaterEqual(pharm["pharmacist_count"], 1)
        self.assertIn("시럽제", pharm["pharmacist_desc"])
        self.assertEqual(pharm["safety_margin_min"], 30)
        self.assertIn("paired_hospital_name", pharm)

    def test_04_hospital_detail_rest_api(self):
        """Verifies GET /api/v1/emergency/facility-detail endpoint for hospitals."""
        res = self.client.get("/api/v1/emergency/facility-detail?type=hospital&name=연세열린의원&lat=37.5&lon=127.0")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["status"], "success")
        data = payload["data"]
        self.assertEqual(data["name"], "연세열린의원")
        self.assertIn("parking_fee", data)
        self.assertIn("today_hours", data)

    def test_05_pharmacy_detail_rest_api(self):
        """Verifies GET /api/v1/emergency/facility-detail endpoint for pharmacies."""
        res = self.client.get("/api/v1/emergency/facility-detail?type=pharmacy&name=구정열린약국&lat=37.5&lon=127.0")
        self.assertEqual(res.status_code, 200)
        payload = res.json()
        self.assertEqual(payload["status"], "success")
        data = payload["data"]
        self.assertEqual(data["name"], "구정열린약국")
        self.assertIn("pharmacist_count", data)
        self.assertIn("paired_hospital_name", data)

    def test_06_non_existent_facility_404(self):
        """Verifies 404 response when querying an unknown facility."""
        res = self.client.get("/api/v1/emergency/facility-detail?type=hospital&name=존재하지않는가상병원9999")
        self.assertEqual(res.status_code, 404)

    def test_07_detail_json_files_and_js_bundles_integrity(self):
        """Verifies that detail JSON datasets in data/ and JS bundles in frontend/js/ exist and are valid."""
        self.assertTrue(HOSP_DETAIL_JSON_PATH.exists(), f"Missing {HOSP_DETAIL_JSON_PATH}")
        self.assertTrue(PHARM_DETAIL_JSON_PATH.exists(), f"Missing {PHARM_DETAIL_JSON_PATH}")
        self.assertTrue(HOSP_DETAIL_JS_PATH.exists(), f"Missing {HOSP_DETAIL_JS_PATH}")
        self.assertTrue(PHARM_DETAIL_JS_PATH.exists(), f"Missing {PHARM_DETAIL_JS_PATH}")

        # Check JSON content validity
        with open(HOSP_DETAIL_JSON_PATH, "r", encoding="utf-8") as f:
            h_data = json.load(f)
        self.assertGreaterEqual(len(h_data), 150)

        with open(PHARM_DETAIL_JSON_PATH, "r", encoding="utf-8") as f:
            p_data = json.load(f)
        self.assertGreaterEqual(len(p_data), 2000)

        # Check JS Bundle declarations
        with open(HOSP_DETAIL_JS_PATH, "r", encoding="utf-8") as f:
            h_js = f.read()
        self.assertIn("window.HOSPITAL_DETAILS_DATA", h_js)

        with open(PHARM_DETAIL_JS_PATH, "r", encoding="utf-8") as f:
            p_js = f.read()
        self.assertIn("window.PHARMACY_DETAILS_DATA", p_js)

    def test_08_build_and_save_detail_datasets_service(self):
        """Verifies that build_and_save_detail_datasets generates valid datasets without exceptions."""
        h_res, p_res = build_and_save_detail_datasets()
        self.assertGreaterEqual(len(h_res), 150)
        self.assertGreaterEqual(len(p_res), 2000)

    def test_09_smart_back_navigation_integration(self):
        """Verifies 5-Layer Smart Back Navigation markup and script contracts in detail pages."""
        hosp_html_path = Path(__file__).resolve().parent.parent / "frontend" / "templates" / "hospital_detail.html"
        pharm_html_path = Path(__file__).resolve().parent.parent / "frontend" / "templates" / "pharmacy_detail.html"
        main_js_path = Path(__file__).resolve().parent.parent / "frontend" / "js" / "main.js"
        result_html_path = Path(__file__).resolve().parent.parent / "frontend" / "templates" / "result.html"

        # 1. Hospital Detail HTML Checks
        with open(hosp_html_path, "r", encoding="utf-8") as f:
            hosp_html = f.read()
        self.assertIn('id="btn-smart-back"', hosp_html)
        self.assertIn("handleSmartGoBack(event)", hosp_html)
        self.assertIn("window.handleSmartGoBack = function", hosp_html)
        self.assertIn("urlParams.get('from')", hosp_html)
        self.assertIn("window.history.back()", hosp_html)
        self.assertIn("&from=", hosp_html)  # Paired pharmacy detail link has from param

        # 2. Pharmacy Detail HTML Checks
        with open(pharm_html_path, "r", encoding="utf-8") as f:
            pharm_html = f.read()
        self.assertIn('id="btn-smart-back"', pharm_html)
        self.assertIn("handleSmartGoBack(event)", pharm_html)
        self.assertIn("window.handleSmartGoBack = function", pharm_html)
        self.assertIn("urlParams.get('from')", pharm_html)
        self.assertIn("window.history.back()", pharm_html)
        self.assertIn("&from=", pharm_html)  # Paired hospital detail link has from param

        # 3. Main JS and Result HTML navigation parameter checks
        with open(main_js_path, "r", encoding="utf-8") as f:
            main_js = f.read()
        self.assertIn("&from=", main_js)

        with open(result_html_path, "r", encoding="utf-8") as f:
            result_html = f.read()
        self.assertIn("&from=", result_html)


if __name__ == "__main__":
    unittest.main()
