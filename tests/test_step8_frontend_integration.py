"""Step 8 Frontend-Backend Phase 1 Integration Tests.

Validates:
1. TC-801: 1-shot fast routing with force_matching=True completes in 1 turn with hospitals, pharmacies, and safe clinical defaults.
2. TC-802: 0ms Red Flag override safety check (Red Flag takes precedence over force_matching, escalating immediately).
3. TC-803: REST API POST /api/v1/chat schema integrity and complete field payload for frontend result.html binding.
"""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from app.orchestrator.supervisor import SupervisorOrchestrator
from app.schemas.chat import ChatRequest
from main import app


class TestFrontendIntegrationStep1(unittest.IsolatedAsyncioTestCase):
    """Test suite for Phase 1 fullstack backend contract."""

    async def asyncSetUp(self):
        """Initializes isolated orchestrator and test client."""
        self.supervisor = SupervisorOrchestrator()
        self.client = TestClient(app)

    async def test_01_force_matching_single_turn_completion(self):
        """TC-801: Incomplete prompt with force_matching=True reaches COMPLETED in 1 turn."""
        response = await self.supervisor.process_turn(
            user_message="아기가 열이 나고 보채요",
            session_id="test-sess-phase1-001",
            user_lat=37.5133,
            user_lon=127.1001,
            force_matching=True,
        )

        # Must transition directly to COMPLETED
        self.assertEqual(response.current_step, "COMPLETED")
        self.assertFalse(response.is_emergency)
        self.assertEqual(response.turn_count, 1)

        # Per ISSUE-112 & ISSUE-116: Unspecified age/temp are preserved as None to prevent falsification
        self.assertIsNone(response.age_months)
        self.assertIsNone(response.temperature)
        self.assertIsNotNone(response.ktas_level)
        self.assertTrue(len(response.symptoms) >= 1)

        # Must include hospitals, call_script, and checklist
        self.assertTrue(len(response.hospitals) >= 1)
        self.assertIsNotNone(response.call_script)
        self.assertTrue(len(response.checklist) >= 3)

    async def test_02_red_flag_overrides_force_matching(self):
        """TC-802: Emergency Red Flag takes absolute precedence over force_matching."""
        response = await self.supervisor.process_turn(
            user_message="생후 50일 신생아가 38.8도 고열이 나요",
            session_id="test-sess-phase1-002",
            user_lat=37.5133,
            user_lon=127.1001,
            force_matching=True,
        )

        # Must escalate to emergency immediately
        self.assertTrue(response.is_emergency)
        self.assertEqual(response.current_step, "EMERGENCY_ESCALATION")
        self.assertIsNotNone(response.emergency_guide)
        self.assertTrue(len(response.hospitals) >= 1)

    def test_03_rest_api_chat_schema_integrity(self):
        """TC-803: REST API POST /api/v1/chat returns all required frontend fields."""
        payload = {
            "user_message": "14개월 아기가 열이 39.2도까지 오르고 구토를 두 번 했어요",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "force_matching": True,
        }
        res = self.client.post("/api/v1/chat", json=payload)
        self.assertEqual(res.status_code, 200)

        data = res.json()
        # Essential top-level keys
        self.assertIn("session_id", data)
        self.assertIn("current_step", data)
        self.assertIn("is_emergency", data)
        self.assertIn("message", data)
        self.assertIn("hospitals", data)
        self.assertIn("pharmacies", data)
        self.assertIn("call_script", data)
        self.assertIn("checklist", data)

        # Clinical vital chips keys for result.html
        self.assertIn("age_months", data)
        self.assertIn("temperature", data)
        self.assertIn("ktas_level", data)
        self.assertIn("ktas_level_name", data)
        self.assertIn("symptoms", data)

        # Clinical variable assertion
        self.assertEqual(data["age_months"], 14)
        self.assertAlmostEqual(data["temperature"], 39.2, places=1)

    def test_04_result_html_ktas_dual_track_contract(self):
        """TC-804: Validates result.html contains KTAS 1-3 ER status and KTAS 4-5 Moonlight matching elements."""
        from pathlib import Path
        result_html_path = Path(__file__).resolve().parent.parent / "frontend" / "templates" / "result.html"
        self.assertTrue(result_html_path.exists(), "result.html template must exist.")

        html_content = result_html_path.read_text(encoding="utf-8")

        # 1. Essential DOM containers and tabs
        self.assertIn('id="pane-emergency"', html_content)
        self.assertIn('id="pane-moonlight"', html_content)
        self.assertIn('id="tab-btn-emergency"', html_content)
        self.assertIn('id="tab-btn-moonlight"', html_content)
        self.assertIn('id="emergency-scroll-list"', html_content)
        self.assertIn('id="moonlight-scroll-list"', html_content)

        # 2. KTAS 1, 2, 3 emergency escalation and call banner
        self.assertIn('id="ktas-emergency-call-banner"', html_content)
        self.assertIn('id="ktas-emergency-call-msg"', html_content)

        # 3. Dynamic JavaScript logic contracts
        self.assertIn("switchTrackTab('emergency')", html_content)
        self.assertIn("switchTrackTab('moonlight')", html_content)
        self.assertIn("renderEmergencyBedCards", html_content)
        self.assertIn("renderMoonlightPairingCards", html_content)
        self.assertIn("updateCallScript", html_content)
        self.assertIn("refreshLiveEmergencyBeds", html_content)

        # 4. Strict KTAS 4, 5 emergency room deterrence: #tab-btn-emergency hidden
        self.assertIn("btnEmergency.style.display = 'none'", html_content)
        self.assertIn("window.currentKtasLevel >= 4", html_content)

    async def test_05_ktas_api_routing_matrix(self):
        """TC-805: Validates backend chat API outputs KTAS 1~3 for severe vitals and KTAS 4~5 for mild cases."""
        # 1. Severe case (KTAS 1 or 2)
        res_severe = self.client.post("/api/v1/chat", json={
            "user_message": "생후 45일 신생아가 38.9도 고열에 경련을 일으키며 축 늘어져요",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "force_matching": True,
        })
        self.assertEqual(res_severe.status_code, 200)
        data_severe = res_severe.json()
        self.assertTrue(data_severe["is_emergency"] or (data_severe["ktas_level"] and data_severe["ktas_level"] <= 2))

        # 2. Mild case (KTAS 4 or 5)
        res_mild = self.client.post("/api/v1/chat", json={
            "user_message": "36개월 아기가 미열 37.8도에 콧물이 조금 나요",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "force_matching": True,
        })
        self.assertEqual(res_mild.status_code, 200)
        data_mild = res_mild.json()
        self.assertFalse(data_mild["is_emergency"])
        self.assertGreaterEqual(data_mild["ktas_level"], 4)

    async def test_06_licenses_page_integration(self):
        """TC-806: Validates /licenses and /opensource routes, settings.html link, and open source attribution contracts."""
        # 1. Routes accessibility
        for endpoint in ["/licenses", "/licenses.html", "/opensource", "/opensource.html"]:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 200, f"Endpoint {endpoint} must return 200 OK")
            self.assertIn("text/html", res.headers.get("content-type", ""))
            self.assertIn("오픈소스 라이선스", res.text)

        # 2. settings.html link contract
        res_settings = self.client.get("/settings.html")
        self.assertEqual(res_settings.status_code, 200)
        self.assertIn('href="licenses.html"', res_settings.text)
        self.assertIn("오픈소스 라이선스", res_settings.text)

        # 3. licenses.html content & compliance contracts
        res_lic = self.client.get("/licenses.html")
        html = res_lic.text

        # Core open sources & APIs
        self.assertIn("FastAPI", html)
        self.assertIn("Google GenAI SDK", html)
        self.assertIn("Firebase Admin", html)
        self.assertIn("Uvicorn", html)
        self.assertIn("Pydantic", html)
        self.assertIn("Leaflet.js", html)
        self.assertIn("OpenStreetMap", html)
        self.assertIn("QRCode.js", html)
        self.assertIn("국립중앙의료원", html)
        self.assertIn("보건복지부", html)
        self.assertIn("한국천문연구원", html)

        # License types
        self.assertIn("MIT License", html)
        self.assertIn("Apache 2.0", html)
        self.assertIn("BSD-3-Clause", html)
        self.assertIn("공공누리 제1유형", html)

        # Interactive features
        self.assertIn("filterCategory('all')", html)
        self.assertIn("filterCategory('backend')", html)
        self.assertIn("filterCategory('frontend')", html)
        self.assertIn("filterCategory('data')", html)
        self.assertIn("license-details", html)
        self.assertIn("handleGoBack()", html)

    async def test_07_app_notification_toggle_contract(self):
        """TC-807: Validates app notification on/off toggle in settings.html and its integration with AisumNotificationManager in main.js & index.html."""
        # 1. settings.html contracts
        res_settings = self.client.get("/settings.html")
        self.assertEqual(res_settings.status_code, 200)
        settings_html = res_settings.text
        self.assertIn('id="app-notification-toggle"', settings_html)
        self.assertIn("aisum_app_notification_enabled", settings_html)
        self.assertIn("AisumNotificationManager.setEnabled", settings_html)
        self.assertIn("앱 알림이 켜졌습니다", settings_html)
        self.assertIn("앱 알림이 꺼졌습니다", settings_html)

        # 2. main.js contracts (AisumNotificationManager)
        res_js = self.client.get("/js/main.js")
        self.assertEqual(res_js.status_code, 200)
        js_code = res_js.text
        self.assertIn("SETTINGS_KEY: 'aisum_app_notification_enabled'", js_code)
        self.assertIn("isEnabled: function()", js_code)
        self.assertIn("setEnabled: function(", js_code)
        self.assertIn("!this.isEnabled()", js_code)
        # Verify guard in addNotification, checkBedUpdates, syncAndCheckBeds, and updateBadgeUI
        self.assertIn("앱 알림이 OFF 상태이므로 알림을 등록하지 않습니다", js_code)

        # 3. index.html contracts (notification sheet & storage listener)
        res_index = self.client.get("/index.html")
        self.assertEqual(res_index.status_code, 200)
        index_html = res_index.text
        self.assertIn("aisum_app_notification_enabled", index_html)
        self.assertIn("앱 알림이 꺼져 있습니다", index_html)
        self.assertIn("설정에서 알림 켜기", index_html)
        self.assertIn("window.addEventListener('storage'", index_html)

    async def test_08_guidebook_page_contract(self):
        """TC-808: Validates the comprehensive Aisum Guidebook page (/guidebook) and settings.html linkage."""
        # 1. settings.html linkage contract
        res_settings = self.client.get("/settings.html")
        self.assertEqual(res_settings.status_code, 200)
        self.assertIn('href="guidebook.html"', res_settings.text)
        self.assertIn("아이숨 가이드북", res_settings.text)

        # 2. /guidebook endpoint status and basic header
        res_guide = self.client.get("/guidebook")
        self.assertEqual(res_guide.status_code, 200)
        html = res_guide.text

        # Core title & branding
        self.assertIn("아이숨 가이드북", html)
        self.assertIn("야간 소아 응급실 뺑뺑이 끝", html)

        # 5 Chapters content contract
        self.assertIn("0ms AI 안심 문진", html)
        self.assertIn("2-트랙 맞춤 안내", html)
        self.assertIn("소아 응급실 실시간 병상 변동 알림", html)
        self.assertIn("1초 안심 통화 대본", html)
        self.assertIn("자주 묻는 질문", html)

        # Interactive functions & navigation
        self.assertIn("filterChapter('all')", html)
        self.assertIn("filterChapter('ch1')", html)
        self.assertIn("handleGoBack()", html)
        self.assertIn("우리 아이 증상 문진 시작", html)

        # Check /guidebook.html alias as well
        res_alias = self.client.get("/guidebook.html")
        self.assertEqual(res_alias.status_code, 200)

    async def test_09_pediatric_age_category_selector_contract(self):
        """TC-809: Validates the 5-tier age category buttons (3+2 grid, no select box) and dynamic controls."""
        res = self.client.get("/input.html")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. Select box must be removed per user request
        self.assertNotIn('id="age-category-select"', html)

        # 2. 5-Tier Age Category Buttons in non-truncating 3+2 grid
        self.assertIn('class="age-cat-grid"', html)
        self.assertIn('data-category="newborn"', html)
        self.assertIn('data-category="infant"', html)
        self.assertIn('data-category="toddler"', html)
        self.assertIn('data-category="child"', html)
        self.assertIn('data-category="adolescent"', html)

        # 3. Label & Subtitle Contracts (zero truncation)
        self.assertIn("신생아", html)
        self.assertIn("28일 미만", html)
        self.assertIn("영아", html)
        self.assertIn("~24개월", html)
        self.assertIn("유아", html)
        self.assertIn("만 2~5세", html)
        self.assertIn("어린이(아동)", html)
        self.assertIn("만 6세 ~ 만 12세 미만", html)
        self.assertIn("청소년", html)
        self.assertIn("만 12세 ~ 만 18세", html)

        # 4. Dynamic Controls & Ruler Containers
        self.assertIn('id="age-cat-pill-badge"', html)
        self.assertIn('id="age-ruler-track"', html)
        self.assertIn('id="age-quick-preset-row"', html)
        self.assertIn('id="age-special-notice-box"', html)

        # 5. JavaScript Engine Contracts
        self.assertIn("const AGE_CONFIGS =", html)
        self.assertIn("function setAgeCategory(", html)
        self.assertIn("function updateAgeDisplay(", html)
        self.assertIn("function getFormattedAge(", html)
        self.assertIn("setAgeCategory('infant', 14);", html)

    async def test_10_integrated_measurement_tabs_contract(self):
        """TC-810: Validates the integrated measurement card containing temperature, age, and medication tabs in one container."""
        res = self.client.get("/input.html")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. Integrated Hub Container
        self.assertIn('id="card-measurement-hub"', html)
        self.assertIn('class="triage-section-card integrated-measure-card"', html)

        # 2. 3-Category Tab Bar & Badges
        self.assertIn('class="measure-tab-bar"', html)
        self.assertIn('id="tab-btn-temp"', html)
        self.assertIn('id="tab-btn-age"', html)
        self.assertIn('id="tab-btn-med"', html)
        self.assertIn('id="tab-val-temp"', html)
        self.assertIn('id="tab-val-age"', html)
        self.assertIn('id="tab-val-med"', html)

        # 3. 3 Panels inside Container
        self.assertIn('class="measure-panels-container"', html)
        self.assertIn('id="card-temp"', html)
        self.assertIn('id="card-age"', html)
        self.assertIn('id="card-medication"', html)

        # 4. Tab Switch Engine in JavaScript
        self.assertIn("function switchMeasureTab(", html)
        self.assertIn("window.switchMeasureTab = switchMeasureTab", html)

    async def test_11_notification_sheet_collapse_prevention_contract(self):
        """TC-811: Validates that notification sheet cards prevent flexbox collapse/shrink and apply deduplication."""
        # 1. Validate style.css contracts
        res_css = self.client.get("/css/style.css")
        self.assertEqual(res_css.status_code, 200)
        css = res_css.text

        self.assertIn(".sheet-body {", css)
        self.assertIn("min-height: 0;", css)
        self.assertIn(".notif-card-wrapper {", css)
        self.assertIn("flex-shrink: 0;", css)
        self.assertIn("min-height: 85px;", css)

        # 2. Validate main.js deduplication contract
        res_js = self.client.get("/js/main.js")
        self.assertEqual(res_js.status_code, 200)
        js = res_js.text

        self.assertIn("const seenNames = new Set();", js)
        self.assertIn("isDuplicate", js)

    async def test_12_history_duplicate_and_dummy_prevention_contract(self):
        """TC-812: Validates that dummy ghost history creation is removed and user triage data is preserved."""
        # 1. Validate result.html contract
        res = self.client.get("/result")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # Dummy history creation must NOT exist in renderEmergencyBedCards
        self.assertNotIn("childAge: '아이'", html)
        self.assertNotIn("symptom: '소아 응급 상황'", html)

        # 2. Validate main.js ghost sanitization contract
        res_js = self.client.get("/js/main.js")
        self.assertEqual(res_js.status_code, 200)
        js = res_js.text

        self.assertIn("isDummyGhost", js)
        self.assertIn("isLatestDummy", js)

    async def test_13_emergency_notification_history_sync_and_pediatric_beds_contract(self):
        """TC-813: Validates that AisumNotificationManager syncs with history records and parses pediatric_beds & hospitals properly."""
        # 1. Validate main.js contracts
        res_js = self.client.get("/js/main.js")
        self.assertEqual(res_js.status_code, 200)
        js = res_js.text

        self.assertIn("latestEmergencyHist", js)
        self.assertIn("typeof live.pediatric_beds === 'number'", js)
        self.assertIn("Array.isArray(data.hospitals)", js)

        # 2. Validate result.html registerWatch call contract
        res_res = self.client.get("/result")
        self.assertEqual(res_res.status_code, 200)
        html = res_res.text

        self.assertIn("window.AisumNotificationManager.registerWatch(hospitals, window.currentKtasLevel)", html)

    async def test_14_dedicated_history_page_contract(self):
        """TC-814: Validates dedicated history page (/history, /history.html) and bottom nav links."""
        # 1. /history & /history.html GET endpoint checks
        res_hist = self.client.get("/history")
        self.assertEqual(res_hist.status_code, 200)
        self.assertIn("history-shell", res_hist.text)
        self.assertIn("history-list-container", res_hist.text)
        self.assertIn("AisumHistoryManager", res_hist.text)
        self.assertIn("btn-replay-result", res_hist.text)

        res_hist_html = self.client.get("/history.html")
        self.assertEqual(res_hist_html.status_code, 200)

        # 2. index.html & settings.html bottom nav link verification
        res_idx = self.client.get("/index.html")
        self.assertEqual(res_idx.status_code, 200)
        self.assertIn('href="history.html"', res_idx.text)

        res_settings = self.client.get("/settings.html")
        self.assertEqual(res_settings.status_code, 200)
        self.assertIn('href="history.html"', res_settings.text)

    async def test_15_paramedic_briefing_card_contract(self):
        """TC-815: Validates Paramedic Emergency Briefing Card (/briefing-card) and GNB 4-Tab integration."""
        # 1. /briefing-card, /briefing_card.html, /emergency_guide.html 200 endpoint checks
        res_card = self.client.get("/briefing-card")
        self.assertEqual(res_card.status_code, 200)
        html = res_card.text

        # 2. Key DOM Contracts: 3 core sections & modals
        self.assertIn("cardPatientProfile", html)
        self.assertIn("txtBloodTypeVal", html)
        self.assertIn("btnDirectCallContact", html)
        self.assertIn("cardMedicalRecord", html)
        self.assertIn("btnOpenRecordSelectModal", html)
        self.assertIn("cardSpecialNotes", html)
        self.assertIn("boxTransfusionDirective", html)
        self.assertIn("boxDoctorContact", html)
        self.assertIn("profileInputModal", html)
        self.assertIn("fullscreenParamedicModal", html)

        # 3. Aliased endpoints return same briefing card
        res_alias1 = self.client.get("/briefing_card.html")
        self.assertEqual(res_alias1.status_code, 200)
        self.assertIn("응급 브리핑 카드", res_alias1.text)

        res_alias2 = self.client.get("/emergency_guide.html")
        self.assertEqual(res_alias2.status_code, 200)
        self.assertIn("응급 브리핑 카드", res_alias2.text)

        # 4. GNB Tab 3 verification in index.html, history.html, settings.html
        res_idx = self.client.get("/index.html")
        self.assertEqual(res_idx.status_code, 200)
        self.assertIn('href="briefing_card.html"', res_idx.text)
        self.assertIn("브리핑 카드", res_idx.text)

        res_hist = self.client.get("/history.html")
        self.assertEqual(res_hist.status_code, 200)
        self.assertIn('href="briefing_card.html"', res_hist.text)
        self.assertIn("브리핑 카드", res_hist.text)

        res_sett = self.client.get("/settings.html")
        self.assertEqual(res_sett.status_code, 200)
        self.assertIn('href="briefing_card.html"', res_sett.text)
        self.assertIn("브리핑 카드", res_sett.text)

        # 5. Inline Profile Form Contract (브리핑 페이지에서 직접 입력 & 저장)
        self.assertIn("profileInlineForm", html)
        self.assertIn("inlineInpName", html)
        self.assertIn("inlineInpBirth", html)
        self.assertIn("inlineChipGenderFemale", html)
        self.assertIn("inlineChipRhPlus", html)
        self.assertIn("inlineInpPhone", html)
        self.assertIn("btnInlineSave", html)
        self.assertIn("btnInlineCancel", html)

    async def test_16_patient_profile_autofill_and_symptom_age_status_sync(self):
        """TC-816: Input page auto-detects patient profile from briefing card and syncs age/status from symptom."""
        res = self.client.get("/input.html")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. Briefing Card Patient Profile Auto-Fill Contract
        self.assertIn("patientProfileAutofillBanner", html)
        self.assertIn("txtAutofillPatientName", html)
        self.assertIn("txtAutofillPatientDesc", html)
        self.assertIn("loadSavedProfileAndAutoFillAge", html)
        self.assertIn("aisum_patient_profile", html)

        # 2. Symptom Age & Status Measurement Detection Contract
        self.assertIn("extractAgeFromText", html)
        self.assertIn("extractStatusFromText", html)
        self.assertIn("applyDetectedMedication", html)
        self.assertIn("auto-sync-temp-badge", html)
        self.assertIn("auto-sync-temp-badge warning", html)
        self.assertIn("auto-sync-temp-badge success", html)

        # 3. Comprehensive Age & Clinical Status Detection keywords
        self.assertIn("생후 100일 미만 발열 위험 감지", html)
        self.assertIn("상태 측정에 자동 반영되었습니다", html)

    async def test_17_profile_age_priority_over_symptom_duplicate_age(self):
        """TC-817: When briefing card profile exists, child age is strictly auto-maintained/prioritized even if duplicate/different age is typed in symptom."""
        res = self.client.get("/input.html")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. Profile Priority State Contract
        self.assertIn("hasSavedProfile", html)
        self.assertIn("useProfileAgeFirst", html)
        self.assertIn("savedProfileData", html)

        # 2. Priority Handling & Auto-Maintenance Contract
        self.assertIn("state.hasSavedProfile && state.savedProfileData && state.useProfileAgeFirst", html)
        self.assertIn("브리핑 카드 나이", html)
        self.assertIn("자동 유지", html)

        # 3. Switch & Restore Interactive Control Contract
        self.assertIn("btnSwitchToDetectedAge", html)
        self.assertIn("btnRestoreProfileAge", html)
        self.assertIn("tagAutofillSyncStatus", html)

    async def test_18_briefing_card_age_auto_applied_without_unknown_badge(self):
        """TC-818: Briefing card age is automatically applied to tab-val-age and summary bar without showing '미입력'."""
        res = self.client.get("/input.html")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. Multi-source Briefing Card Detection Contract
        self.assertIn("aisum_patient_profile", html)
        self.assertIn("aisum_active_briefing_record_id", html)
        self.assertIn("aisum_triage_histories_v1", html)

        # 2. State & No '미입력' Contract
        self.assertIn("state.hasSavedProfile = true;", html)
        self.assertIn("state.ageTouched = true;", html)
        self.assertIn("if (state.hasSavedProfile) return false;", html)

        # 3. Direct Tab & Summary Sync Contract
    async def test_19_briefing_card_age_not_overwritten_by_defaults(self):
        """TC-819: Ensure briefing card age is preserved on initial load and not overwritten by default 14 months."""
        res = self.client.get("/input.html")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. Profile AutoFill Priority in Defaults
        self.assertIn("const profileLoaded = loadSavedProfileAndAutoFillAge();", html)
        self.assertIn("if (!profileLoaded && !state.hasSavedProfile)", html)

        # 2. Both app and frontend templates consistency
        self.assertIn("patientProfileAutofillBanner", html)
        self.assertIn("setAgeCategory(foundAge.category, foundAge.val);", html)

    async def test_20_sync_watch_targets_on_history_deletion(self):
        """TC-820: Ensure emergency monitoring watch targets are synced and cleared upon history deletion."""
        # 1. Verify history.html triggers syncWatchTargetsWithHistory
        res_hist = self.client.get("/history.html")
        self.assertEqual(res_hist.status_code, 200)
        hist_html = res_hist.text
        self.assertIn("AisumNotificationManager.syncWatchTargetsWithHistory", hist_html)
        self.assertIn("deleteHistoryRecord", hist_html)
        self.assertIn("clearAllHistoryRecords", hist_html)

        # 2. Verify main.js contains syncWatchTargetsWithHistory logic
        with open("frontend/js/main.js", "r", encoding="utf-8") as f:
            main_js = f.read()
        self.assertIn("syncWatchTargetsWithHistory: function()", main_js)
        self.assertIn("localStorage.removeItem(this.WATCH_KEY)", main_js)
        self.assertIn("isSevereUser: function()", main_js)
        self.assertIn("this.hasEmergencyHistory() && (this.getWatchTargets().length > 0)", main_js)

    async def test_21_briefing_card_record_select_modal_integration(self):
        """TC-821: Ensure briefing card record selection modal loads dynamically and updates active record."""
        res_bc = self.client.get("/briefing-card")
        self.assertEqual(res_bc.status_code, 200)
        bc_html = res_bc.text

        # 1. UI Elements Contract
        self.assertIn("id=\"btnOpenRecordSelectModal\"", bc_html)
        self.assertIn("id=\"recordSelectModal\"", bc_html)
        self.assertIn("id=\"recordSelectListContainer\"", bc_html)
        self.assertIn("기록 변경", bc_html)

        # 2. Logic & Event Handler Contract
        self.assertIn("openRecordSelectModal", bc_html)
        self.assertIn("selectActiveRecord", bc_html)
        self.assertIn("STORAGE_ACTIVE_RECORD_ID_KEY", bc_html)
        self.assertIn("record-select-item", bc_html)
        self.assertIn("저장된 문진 기록이 없습니다", bc_html)

    def test_22_briefing_card_modal_active_visibility_and_symptom_briefing_box(self):
        """TC-822: 브리핑 카드 '기록 변경' 모달 active 클래스 표출 및 주요 증상 상세 인계 브리핑 박스 계약 검증"""
        with open("frontend/templates/briefing_card.html", "r", encoding="utf-8") as f:
            bc_html = f.read()

        # 1. '기록 변경' 버튼 인라인 onclick 및 모달 열림 active 클래스 보장
        self.assertIn("id=\"btnOpenRecordSelectModal\"", bc_html)
        self.assertIn("onclick=\"openRecordSelectModal()\"", bc_html)
        self.assertIn("recordSelectModal.classList.add('active')", bc_html)
        self.assertIn("recordSelectModal.classList.remove('active')", bc_html)
        self.assertIn(".modal-overlay.active", bc_html)
        self.assertIn("window.openRecordSelectModal = openRecordSelectModal", bc_html)
        self.assertIn("window.selectActiveRecord = selectActiveRecord", bc_html)

        # 2. 주요 증상 구급대원·의료진 인계 브리핑 박스 마크업 계약 (통합 간소화 구조)
        self.assertIn("id=\"briefingSymptomSummaryBox\"", bc_html)
        self.assertIn("id=\"txtBriefingSummaryHeaderTitle\"", bc_html)
        self.assertIn("id=\"txtBriefingSummaryHeadline\"", bc_html)
        self.assertIn("id=\"txtBriefingSummaryClinicalNote\"", bc_html)
        self.assertIn("class=\"briefing-symptom-summary-box", bc_html)
        self.assertIn("class=\"briefing-symptom-summary-top\"", bc_html)
        self.assertIn("id=\"briefingSymptomTagBox\"", bc_html)
        self.assertIn("🚨 긴급 구급 인계", bc_html)

        # 3. 임상 주증상 상세/간단 요약 생성기 계약
        self.assertIn("buildSymptomBriefingSummary", bc_html)
        self.assertIn("절단", bc_html)
        self.assertIn("신체 부위 중증 외상·손상으로 15분 이내 전문 접합 및 응급 지혈 처치가 시급합니다", bc_html)
        self.assertIn("경련", bc_html)
        self.assertIn("호흡", bc_html)

        # 4. 전체화면 모드 고대비 인계 브리핑 동기화 계약 (통합 일체형)
        self.assertIn("id=\"fsSymptomHeadline\"", bc_html)
        self.assertIn("id=\"fsSymptomClinicalNote\"", bc_html)
        self.assertIn("id=\"fsSymptomUrgencyBadge\"", bc_html)

    def test_23_paramedic_special_notes_included_in_patient_profile(self):
        """TC-823: Validates that Paramedic Special Notes are embedded inside Patient Profile card."""
        res = self.client.get("/briefing-card")
        self.assertEqual(res.status_code, 200)
        html = res.text

        # 1. 환아 인적사항(cardPatientProfile) 안에 구급대원 필독사항(cardSpecialNotes)이 포함되어 있는지 검증
        patient_profile_start = html.find('id="cardPatientProfile"')
        self.assertNotEqual(patient_profile_start, -1)

        # 다음 메인 섹션인 cardMedicalRecord 시작 위치
        medical_record_start = html.find('id="cardMedicalRecord"')
        self.assertNotEqual(medical_record_start, -1)

        # cardPatientProfile 블록 추출
        patient_profile_html = html[patient_profile_start:medical_record_start]

        # cardSpecialNotes 및 핵심 요소가 patient_profile_html 내부에 존재하는지 검증
        self.assertIn('id="cardSpecialNotes"', patient_profile_html)
        self.assertIn('class="patient-special-notes-box"', patient_profile_html)
        self.assertIn('구급대원 필독 특이사항', patient_profile_html)
        self.assertIn('id="btnEditDirectives"', patient_profile_html)
        self.assertIn('id="boxTransfusionDirective"', patient_profile_html)
        self.assertIn('id="boxDoctorContact"', patient_profile_html)
        self.assertIn('id="badgeTransfusionStatus"', patient_profile_html)
        self.assertIn('id="txtDoctorHospital"', patient_profile_html)

        # 2. 독립된 별개 섹션으로서의 <section class="briefing-card" id="cardSpecialNotes">는 없어야 함
        self.assertNotIn('<section class="briefing-card" id="cardSpecialNotes"', html)

        # 3. 인라인 폼 내 details 특이사항 연동
        self.assertIn('id="detailsSpecialDirectives"', html)
        self.assertIn('+ 구급대원 필독사항 추가 입력', html)

    def test_23_root_serves_splash_as_first_priority_and_session_guard(self):
        """TC-823: Root GET / serves splash.html as 1st priority for browser clients with session guard."""
        # 1. Browser client requesting root / receives splash.html
        res_browser = self.client.get("/", headers={"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"})
        self.assertEqual(res_browser.status_code, 200)
        self.assertIn("text/html", res_browser.headers.get("content-type", ""))
        self.assertIn("splashScreen", res_browser.text)
        self.assertIn("아이숨", res_browser.text)
        self.assertIn("aisum_splash_shown", res_browser.text)

        # 2. Direct /splash endpoint also works reliably
        res_splash = self.client.get("/splash")
        self.assertEqual(res_splash.status_code, 200)
        self.assertIn("splashScreen", res_splash.text)

        # 3. Main home index.html contains session splash guard
        res_home = self.client.get("/home")
        self.assertEqual(res_home.status_code, 200)
        self.assertIn("aisum_splash_shown", res_home.text)
        self.assertIn("window.location.replace('/splash')", res_home.text)

        # 4. API client requesting root / receives JSON metadata
        res_api = self.client.get("/", headers={"accept": "application/json"})
        self.assertEqual(res_api.status_code, 200)
        self.assertEqual(res_api.json()["service"], "MoonlightCare API")

    def test_24_theme_setting_feature_contract(self):
        """TC-824: Ensure theme setting (dark/light/system) UI, modal, tokens and manager contract."""
        # 1. settings.html contains theme row button, display, and theme modal
        res_settings = self.client.get("/settings.html")
        self.assertEqual(res_settings.status_code, 200)
        settings_html = res_settings.text

        self.assertIn("id=\"theme-setting-row-btn\"", settings_html)
        self.assertIn("화면 테마 변경", settings_html)
        self.assertIn("id=\"theme-setting-display\"", settings_html)
        self.assertIn("id=\"theme-setting-modal\"", settings_html)
        self.assertIn("id=\"theme-opt-light\"", settings_html)
        self.assertIn("id=\"theme-opt-dark\"", settings_html)
        self.assertIn("id=\"theme-opt-system\"", settings_html)
        self.assertIn("openThemeModal()", settings_html)
        self.assertIn("closeThemeModal()", settings_html)
        self.assertIn("selectTheme", settings_html)
        self.assertNotIn("id=\"child-info-row-btn\"", settings_html)

        # 2. theme.js module exists and contains AisumThemeManager
        with open("frontend/js/theme.js", "r", encoding="utf-8") as f:
            theme_js = f.read()
        self.assertIn("AisumThemeManager", theme_js)
        self.assertIn("aisum_theme", theme_js)
        self.assertIn("getTheme", theme_js)
        self.assertIn("setTheme", theme_js)
        self.assertIn("applyTheme", theme_js)

        # 3. style.css contains html[data-theme="dark"] tokens & theme-option-card
        with open("frontend/css/style.css", "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("html[data-theme=\"dark\"]", css)
        self.assertIn(".theme-option-card", css)
        self.assertIn(".theme-options-list", css)


if __name__ == "__main__":
    unittest.main()






