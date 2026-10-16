"""Unit & Integration Tests for Kakao Location & Geocoding REST API Router."""

import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app
from app.api.v1.location import _search_fallback_locations, FALLBACK_POI_LOCATIONS


class TestLocationApi(unittest.TestCase):
    """카카오 로컬 REST API 및 3-Tier 하이브리드 Fallback 검증 테스트"""

    def setUp(self):
        self.client = TestClient(app)

    def test_search_fallback_locations_function(self):
        """인메모리 로컬 Fallback 검색 로직 단위 테스트"""
        # 1. 키워드 검색 (코엑스)
        coex_matches = _search_fallback_locations("코엑스", search_type="keyword")
        self.assertGreater(len(coex_matches), 0)
        self.assertEqual(coex_matches[0]["title"], "코엑스")
        self.assertEqual(coex_matches[0]["type"], "keyword")
        self.assertAlmostEqual(coex_matches[0]["lat"], 37.5118, places=3)
        self.assertAlmostEqual(coex_matches[0]["lon"], 127.0592, places=3)

        # 2. 주소 검색 (문정동)
        munjeong_matches = _search_fallback_locations("문정동", search_type="address")
        self.assertGreater(len(munjeong_matches), 0)
        self.assertTrue(any(m["dong"] == "문정동" for m in munjeong_matches))

        # 3. 전체 검색 (롯데)
        lotte_matches = _search_fallback_locations("롯데", search_type="all")
        self.assertGreaterEqual(len(lotte_matches), 2)

        # 4. 없는 검색어
        none_matches = _search_fallback_locations("존재하지않는외계지역xyz")
        self.assertEqual(len(none_matches), 0)

    def test_location_search_api_fallback(self):
        """API 키가 없을 때 로컬 Fallback으로 안전하게 200 반환하는지 테스트"""
        with patch.dict("os.environ", {"KAKAO_REST_API_KEY": ""}):
            with patch("app.api.v1.location.KAKAO_REST_API_KEY", ""):
                response = self.client.get("/api/v1/location/search?q=강남역&search_type=keyword")
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertIn(data["status"], ["success", "empty"])
                self.assertIn("results", data)
                if data["status"] == "success":
                    self.assertGreater(len(data["results"]), 0)
                    self.assertEqual(data["results"][0]["title"], "강남역")
                    self.assertEqual(data["results"][0]["source"], "fallback_local_db")

    def test_location_search_api_address_type(self):
        """주소 모드로 검색 시 동작 확인"""
        response = self.client.get("/api/v1/location/search?q=잠실동&search_type=address")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["search_type"], "address")

    def test_location_search_validation(self):
        """유효하지 않은 파라미터 요청 시 422 Unprocessable Entity 검증"""
        # 1. q 파라미터 누락
        response = self.client.get("/api/v1/location/search")
        self.assertEqual(response.status_code, 422)

        # 2. search_type 잘못된 enum
        response = self.client.get("/api/v1/location/search?q=서울&search_type=invalid_type")
        self.assertEqual(response.status_code, 422)

    def test_coord2address_api_fallback(self):
        """좌표 역변환 API의 Fallback 응답 검증"""
        response = self.client.get("/api/v1/location/coord2address?lat=37.5126&lon=127.1025")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data["status"], ["success", "fallback"])
        self.assertIn("dong", data)
        self.assertIn("lat", data)
        self.assertIn("lon", data)

    @patch("app.api.v1.location.httpx.AsyncClient")
    def test_kakao_remote_api_mocked(self, mock_client_cls):
        """카카오 원격 REST API 응답 Mocking 정상 파싱 검증"""
        import os
        import httpx
        from unittest.mock import AsyncMock
        with patch.dict(os.environ, {"KAKAO_REST_API_KEY": "fake_test_key_1234"}):
            # Mock client and real httpx.Response
            mock_client = MagicMock()
            mock_client_cls.return_value.__aenter__.return_value = mock_client

            fake_payload = {
                "documents": [
                    {
                        "place_name": "카카오 판교아지트",
                        "category_group_name": "기업",
                        "road_address_name": "경기 성남시 분당구 판교역로 166",
                        "address_name": "경기 성남시 분당구 백현동 532",
                        "x": "127.1105",
                        "y": "37.3957"
                    }
                ]
            }
            mock_resp = httpx.Response(
                200,
                json=fake_payload,
                request=httpx.Request("GET", "https://dapi.kakao.com/v2/local/search/keyword.json")
            )
            mock_client.get = AsyncMock(return_value=mock_resp)

            response = self.client.get("/api/v1/location/search?q=카카오판교&search_type=keyword")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["source"], "kakao_local_api")
            self.assertEqual(len(data["results"]), 1)
            self.assertEqual(data["results"][0]["title"], "카카오 판교아지트")
            self.assertAlmostEqual(data["results"][0]["lat"], 37.3957)
            self.assertAlmostEqual(data["results"][0]["lon"], 127.1105)


if __name__ == "__main__":
    unittest.main()
