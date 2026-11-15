"""Regression tests covering all P0/P1/P2 remediation items in IMPROVEMENT_ROADMAP.md."""

from __future__ import annotations

import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import ASGITransport, AsyncClient

from app.agents.logistics_agent import LogisticsAgent
from app.agents.triage_agent import TriageAgent
from app.orchestrator.session_manager import InMemorySessionStore, SessionManager
from app.orchestrator.supervisor import SupervisorOrchestrator
from app.services.genai_client import build_genai_client, is_genai_configured
from main import app


class TestRoadmapRemediation(unittest.IsolatedAsyncioTestCase):
    """Verifies P0/P1/P2 fixes across agents, orchestrator, auth, and routing."""

    def test_01_vertex_adc_only_auth_and_no_api_key_fallback(self) -> None:
        """GCP GenAI & Firestore strictly authenticate via ADC without API keys or key files."""
        from google.auth.exceptions import DefaultCredentialsError

        from app import config as app_config

        with patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": "legacy-ignored-key",
                "GOOGLE_GENAI_USE_VERTEXAI": "true",
                "GOOGLE_CLOUD_PROJECT": "test-project-id",
                "GOOGLE_CLOUD_LOCATION": "global",
            },
            clear=False,
        ):
            with (
                patch("google.auth.default", return_value=(MagicMock(), "adc-default-project")),
                patch("google.genai.Client", return_value=MagicMock()) as mock_client,
            ):
                triage = TriageAgent(enable_gemini=True)
                logistics = LogisticsAgent(enable_gemini=True)
                self.assertIsNotNone(triage._client)
                self.assertIsNotNone(logistics._client)
                mock_client.assert_any_call(
                    vertexai=True,
                    project="test-project-id",
                    location="global",
                )
                self.assertTrue(is_genai_configured())

            # Without ADC credentials, GEMINI_API_KEY alone must NOT initialize a client
            with (
                patch("google.auth.default", side_effect=DefaultCredentialsError("no adc")),
                patch.dict(os.environ, {"K_SERVICE": ""}, clear=False),
            ):
                self.assertIsNone(build_genai_client(agent_label="Test"))
                self.assertFalse(is_genai_configured())

        # Missing both env project and ADC default project returns None cleanly without hardcoded personal ID
        with (
            patch("google.auth.default", return_value=(MagicMock(), None)),
            patch.dict(
                os.environ,
                {"GOOGLE_CLOUD_PROJECT": "", "GCP_PROJECT": "", "GCLOUD_PROJECT": ""},
                clear=False,
            ),
        ):
            self.assertIsNone(build_genai_client(agent_label="Test"))
            self.assertFalse(is_genai_configured())

        # Firestore get_firestore_client uses ADC only (raises RuntimeError if ADC unavailable)
        prev_client = app_config._firestore_client
        app_config._firestore_client = None
        try:
            with (
                patch("google.auth.default", side_effect=DefaultCredentialsError("no adc")),
                patch.dict(os.environ, {"K_SERVICE": ""}, clear=False),
            ):
                with self.assertRaises(RuntimeError):
                    app_config.get_firestore_client()

            with (
                patch("google.auth.default", return_value=(MagicMock(), "adc-firestore-proj")),
                patch("firebase_admin._apps", new={}),
                patch("firebase_admin.initialize_app") as mock_init_app,
                patch("firebase_admin.firestore.client", return_value=MagicMock()) as mock_fs_client,
                patch.object(app_config.settings, "gcp_project_id", None),
                patch.object(app_config.settings, "firestore_database_id", "isoom"),
                patch.dict(os.environ, {"K_SERVICE": ""}, clear=False),
            ):
                client = app_config.get_firestore_client()
                self.assertIsNotNone(client)
                mock_init_app.assert_called_once_with(options={"projectId": "adc-firestore-proj"})
                mock_fs_client.assert_called_once_with(database_id="isoom")
        finally:
            app_config._firestore_client = prev_client

    async def test_02_supervisor_preserves_followup_and_resets_after_completed(self) -> None:
        """Follow-up question is preserved on incomplete turn, and COMPLETED re-entry resets clinical state."""
        supervisor = SupervisorOrchestrator(session_manager=SessionManager(store=InMemorySessionStore()))
        supervisor.triage_agent._client = None
        supervisor.logistics_agent._client = None

        # Turn 1: Incomplete input should return followup_question in message
        res1 = await supervisor.process_turn(
            user_message="아기가 열이 나요",
            session_id="remed-followup-01",
        )
        self.assertEqual(res1.current_step, "TRIAGE")
        self.assertIn("알려주실 수 있을까요", res1.message)
        self.assertIsNotNone(res1.session_token)

        # Turn 2: Chatter guard should not create duplicate consecutive assistant messages
        res_chatter = await supervisor.process_turn(
            user_message="안녕하세요",
            session_id="remed-chatter-01",
            force_matching=True,
        )
        self.assertEqual(res_chatter.current_step, "TRIAGE")
        sess_chatter = await supervisor.session_manager.get_session("remed-chatter-01")
        self.assertIsNotNone(sess_chatter)
        roles = [m.role for m in sess_chatter.conversation_history]
        self.assertEqual(roles, ["user", "assistant"])

        # Complete consultation, then start a new round in the same session_id
        res_done = await supervisor.process_turn(
            user_message="24개월 아기가 38.5도 열이 나고 기침해요",
            session_id="remed-reentry-01",
        )
        self.assertEqual(res_done.current_step, "COMPLETED")
        self.assertEqual(res_done.turn_count, 1)

        res_new_round = await supervisor.process_turn(
            user_message="이번엔 아이가 조금 보채요",
            session_id="remed-reentry-01",
        )
        self.assertEqual(res_new_round.current_step, "TRIAGE")
        self.assertEqual(res_new_round.turn_count, 1)
        self.assertIsNone(res_new_round.age_months)
        self.assertIsNone(res_new_round.temperature)

    async def test_03_admin_and_session_token_auth_enforcement(self) -> None:
        """Admin and session endpoints enforce tokens when configured."""
        transport = ASGITransport(app=app)
        with patch.dict(
            os.environ,
            {
                "ADMIN_API_TOKEN": "super-secret-admin-token",
                "REQUIRE_SESSION_TOKEN": "true",
                "SESSION_SECRET": "test-hmac-secret",
            },
            clear=False,
        ):
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Admin endpoint without token -> 401
                r_unauth = await client.get("/api/v1/chat/sessions")
                self.assertEqual(r_unauth.status_code, 401)

                # 2. Admin endpoint with wrong token -> 403
                r_forbidden = await client.post(
                    "/api/v1/emergency/sync",
                    headers={"Authorization": "Bearer wrong-token"},
                )
                self.assertEqual(r_forbidden.status_code, 403)

                # 3. Admin endpoint with valid token -> 200
                r_ok = await client.get(
                    "/api/v1/chat/sessions",
                    headers={"Authorization": "Bearer super-secret-admin-token"},
                )
                self.assertEqual(r_ok.status_code, 200)

                # 4. Create chat session and verify X-Session-Token enforcement
                r_chat = await client.post(
                    "/api/v1/chat",
                    json={"user_message": "24개월 아이 38.3도 열나요"},
                )
                self.assertEqual(r_chat.status_code, 200)
                chat_data = r_chat.json()
                sid = chat_data["session_id"]
                stoken = chat_data["session_token"]
                self.assertTrue(stoken)

                r_sess_no_tok = await client.get(f"/api/v1/chat/session/{sid}")
                self.assertEqual(r_sess_no_tok.status_code, 401)

                r_sess_bad_tok = await client.get(
                    f"/api/v1/chat/session/{sid}",
                    headers={"X-Session-Token": "invalid"},
                )
                self.assertEqual(r_sess_bad_tok.status_code, 401)

                r_sess_ok = await client.get(
                    f"/api/v1/chat/session/{sid}",
                    headers={"X-Session-Token": stoken},
                )
                self.assertEqual(r_sess_ok.status_code, 200)

                r_del_ok = await client.delete(
                    f"/api/v1/chat/session/{sid}",
                    headers={"X-Session-Token": stoken},
                )
                self.assertEqual(r_del_ok.status_code, 200)

    async def test_04_sse_error_sanitization_and_consolidated_frontend_routes(self) -> None:
        """SSE error does not expose internal exception text, and consolidated frontend routes serve 200."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            with patch(
                "app.orchestrator.supervisor.SupervisorOrchestrator.process_turn",
                new=AsyncMock(side_effect=RuntimeError("SECRET_INTERNAL_STACK_DETAIL")),
            ):
                res = await client.post(
                    "/api/v1/chat/stream",
                    json={"user_message": "아기가 열나요"},
                )
                self.assertEqual(res.status_code, 200)
                self.assertNotIn("SECRET_INTERNAL_STACK_DETAIL", res.text)
                self.assertIn("event: error", res.text)

            r_first_aid = await client.get("/first-aid")
            self.assertEqual(r_first_aid.status_code, 200)

            r_traversal = await client.get("/img/..%2F..%2Fmain.py")
            self.assertEqual(r_traversal.status_code, 404)

    def test_05_stitch_adc_proxy_uses_adc_and_handles_sse_and_401(self) -> None:
        """Stitch MCP ADC bridge sends Bearer + X-Goog-User-Project without API keys and parses SSE/401."""
        import importlib.util
        import json
        from pathlib import Path

        proxy_path = Path(__file__).resolve().parent.parent / ".agents/plugins/stitch/stitch_adc_proxy.py"
        spec = importlib.util.spec_from_file_location("stitch_adc_proxy", proxy_path)
        assert spec is not None and spec.loader is not None
        proxy_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(proxy_mod)

        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_creds.token = "adc-token-1"

        def _refresh(_req: object) -> None:
            mock_creds.token = "adc-token-2"
            mock_creds.valid = True

        mock_creds.refresh.side_effect = _refresh

        resp_401 = MagicMock(status_code=401, text="Unauthorized", headers={})
        resp_sse = MagicMock(
            status_code=200,
            headers={"content-type": "text/event-stream", "mcp-session-id": "sess-123"},
            text='data: {"jsonrpc":"2.0","id":1,"result":{"tools":[]}}\n\ndata: [DONE]\n',
        )
        resp_json = MagicMock(
            status_code=200,
            headers={"content-type": "application/json"},
            text='{"jsonrpc":"2.0","id":2,"result":{"ok":true}}',
        )
        resp_json.json.return_value = json.loads(resp_json.text)

        mock_client = MagicMock()
        mock_client.post.side_effect = [resp_401, resp_sse, resp_json]

        with patch.object(proxy_mod.google.auth, "default", return_value=(mock_creds, "iceu-songpa10")), \
             patch.object(proxy_mod.httpx, "Client", return_value=mock_client):
            bridge = proxy_mod.StitchAdcBridge()
            out1 = bridge.forward({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
            self.assertEqual(out1, [{"jsonrpc": "2.0", "id": 1, "result": {"tools": []}}])
            self.assertEqual(bridge._session_id, "sess-123")

            first_headers = mock_client.post.call_args_list[0].kwargs["headers"]
            second_headers = mock_client.post.call_args_list[1].kwargs["headers"]
            self.assertEqual(first_headers["Authorization"], "Bearer adc-token-1")
            self.assertEqual(first_headers["X-Goog-User-Project"], "iceu-songpa10")
            self.assertNotIn("X-Goog-Api-Key", first_headers)
            self.assertEqual(second_headers["Authorization"], "Bearer adc-token-2")

            out2 = bridge.forward({"jsonrpc": "2.0", "id": 2, "method": "ping"})
            self.assertEqual(out2, [{"jsonrpc": "2.0", "id": 2, "result": {"ok": True}}])
            third_headers = mock_client.post.call_args_list[2].kwargs["headers"]
            self.assertEqual(third_headers["Mcp-Session-Id"], "sess-123")

    def test_06_templates_have_no_duplicate_assets_and_include_stitch_css(self) -> None:
        """All HTML templates load single canonical style.css, stitch-aisum.css, theme.js, and zero dead assets."""
        import re
        from pathlib import Path

        templates_dir = Path(__file__).resolve().parent.parent / "frontend" / "templates"
        html_files = sorted(templates_dir.glob("*.html"))
        self.assertGreaterEqual(len(html_files), 18)

        for html_file in html_files:
            content = html_file.read_text(encoding="utf-8")
            head_part = content.split("</head>")[0]
            self.assertEqual(len(re.findall(r"css/style\.css", content)), 1, html_file.name)
            self.assertEqual(len(re.findall(r"css/stitch-aisum\.css", content)), 1, html_file.name)
            self.assertEqual(len(re.findall(r"js/theme\.js", content)), 1, html_file.name)
            self.assertIn("/js/theme.js", head_part, html_file.name)
            self.assertLessEqual(len(re.findall(r"js/main\.js", content)), 1, html_file.name)
            self.assertNotIn("public_night_pharmacies", content, html_file.name)
            self.assertEqual(len(re.findall(r"\.\./(?:css|js)/", content)), 0, html_file.name)


if __name__ == "__main__":
    unittest.main()
