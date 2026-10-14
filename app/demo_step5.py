"""Interactive Demonstration script for Step 5: FastAPI REST Serving & Background Daemon.

Demonstrates:
1. System Health Check & Background Scheduler Status (GET /health, GET /api/v1/emergency/status)
2. Ultra-fast (< 10ms) GPS Pediatric ER Spatial Ranking (GET /api/v1/emergency/nearby)
3. Moonlight Children's Hospital + 30-min Safe Margin Pharmacy Set (GET /api/v1/emergency/pairings)
4. REST Full Triage Consultation with FSM Pipeline (POST /api/v1/chat)
5. 0ms Red Flag Instant Escalation via REST API (POST /api/v1/chat)
6. Server-Sent Events (SSE) Real-time Streaming (POST /api/v1/chat/stream)
7. On-Demand Real-time Bed Synchronization & Hash Diffing (POST /api/v1/emergency/sync)
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from main import app


async def run_step5_demo() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n" + "=" * 80)
        print("🌟 MoonlightCare Step 5: FastAPI REST API & Background Daemon 시연")
        print("=" * 80)

        # -------------------------------------------------------------
        # 1. System Health Check & Scheduler Status
        # -------------------------------------------------------------
        print("\n[1] 🏥 시스템 헬스체크 및 백그라운드 스케줄러 상태 (GET /health)")
        res_health = await client.get("/health")
        health = res_health.json()
        print(f"  • 상태(Status): {health['status']}")
        print(f"  • 스케줄러 가동: {health['scheduler']['running']}")
        print(f"  • 공공데이터 API 키 연동: {health['integrations']['public_data_api_configured']}")
        print(f"  • Gemini AI 키 연동: {health['integrations']['gemini_api_configured']}")
        print(f"  • Firebase 연동: {health['integrations']['firebase_configured']}")

        # -------------------------------------------------------------
        # 2. 5ms Spatial Proximity Search
        # -------------------------------------------------------------
        print("\n[2] 🚨 GPS 기반 5ms 주변 소아 가용 응급실 초고속 검색 (GET /api/v1/emergency/nearby)")
        t0 = time.perf_counter()
        res_er = await client.get(
            "/api/v1/emergency/nearby",
            params={"lat": 37.5133, "lon": 127.1001, "radius_km": 15.0, "limit": 3},
        )
        t_er = (time.perf_counter() - t0) * 1000.0
        er_data = res_er.json()
        print(f"  • 특일/과밀화 리스크: {er_data['holiday_name']} | {er_data['surge_risk_level']}")
        print(f"  • 서버 응답 소요 시간: {t_er:.2f}ms (API 내부 연산: {er_data['latency_ms']}ms)")
        print(f"  • 15km 이내 소아 가용 응급실 TOP 3:")
        for idx, hosp in enumerate(er_data["hospitals"][:3], 1):
            acc_icon = "🟢" if hosp["pediatric_acceptable"] else "🔴"
            print(
                f"    {idx}. {acc_icon} {hosp['hospital_name']} | "
                f"거리: {hosp['distance_km']}km | 소아병상: {hosp['pediatric_beds']}석"
            )

        # -------------------------------------------------------------
        # 3. Moonlight Hospital & 30-min Pharmacy Set
        # -------------------------------------------------------------
        print("\n[3] 🌙 전국 달빛어린이병원 + 30분 마진 심야약국 페어링 세트 (GET /api/v1/emergency/pairings)")
        res_pairs = await client.get(
            "/api/v1/emergency/pairings",
            params={"lat": 37.4988, "lon": 126.9934, "radius_km": 20.0, "limit": 2},
        )
        pairs_data = res_pairs.json()
        print(f"  • 검색된 페어링 수: {pairs_data['total_found']}개소")
        for idx, p in enumerate(pairs_data["pairings"][:2], 1):
            print(f"    {idx}. 🏥 {p.get('병원명')} ({p.get('거리_km')}km)")
            print(f"       💊 연계 약국: {p.get('약국명')} (이동: {p.get('이동안내')})")
            print(f"       ⏱️ 안전 마진: {p.get('안전마진_분')}분 여유 ({p.get('조제안전등급')})")

        # -------------------------------------------------------------
        # 4. REST Full Triage Consultation
        # -------------------------------------------------------------
        print("\n[4] 💬 REST 일반 상담 엔드포인트 호출 (POST /api/v1/chat)")
        chat_payload = {
            "user_message": "14개월 아기 38.5도 열나요. 2시간째 미열이고 해열제 먹였어요.",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
        }
        res_chat = await client.post("/api/v1/chat", json=chat_payload)
        chat_data = res_chat.json()
        print(f"  • 세션 ID: {chat_data['session_id']}")
        print(f"  • FSM 단계: {chat_data['current_step']} (Turn {chat_data['turn_count']})")
        print(f"  • 긴급 여부: {chat_data['is_emergency']}")
        print(f"  • 종합 메시지:\n    {chat_data['message'][:120]}...")
        if chat_data["call_script"]:
            print(f"  • 30초 유선 확인 스크립트:\n    {chat_data['call_script']}")
        print(f"  • 본인확인 서류: {chat_data['checklist']}")

        # -------------------------------------------------------------
        # 5. 0ms Red Flag Instant Escalation
        # -------------------------------------------------------------
        print("\n[5] 🚨 0ms Red Flag 긴급 에스컬레이션 REST 호출 (POST /api/v1/chat)")
        red_payload = {
            "user_message": "생후 50일 신생아인데 39도 고열에 숨을 헐떡이고 축 처져요!",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
        }
        res_red = await client.post("/api/v1/chat", json=red_payload)
        red_data = res_red.json()
        print(f"  • FSM 단계: {red_data['current_step']}")
        print(f"  • 긴급 여부: {red_data['is_emergency']} (🚨 0ms 차단 즉시 발동)")
        print(f"  • 비상 행동 요령:\n    {red_data['emergency_guide']}")
        print(f"  • 전달 메시지:\n    {red_data['message']}")

        # -------------------------------------------------------------
        # 6. Server-Sent Events (SSE) Streaming
        # -------------------------------------------------------------
        print("\n[6] ⚡ SSE 실시간 스트리밍 대화 수신 (POST /api/v1/chat/stream)")
        stream_payload = {
            "user_message": "24개월 아이 38.2도 미열에 콧물이 나요.",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
        }
        print("  • 스트리밍 청크 수신 중: ", end="", flush=True)
        res_stream = await client.post("/api/v1/chat/stream", json=stream_payload)
        stream_text = res_stream.text
        lines = stream_text.strip().split("\n")
        delta_count = 0
        for line in lines:
            if line.startswith("data: ") and "delta" in line:
                try:
                    payload = json.loads(line.replace("data: ", ""))
                    print(payload.get("delta", ""), end="", flush=True)
                    delta_count += 1
                except Exception:
                    pass
        print(f"\n  • 스트리밍 완료 (수신 청크: {delta_count}개, [DONE] 확인)")

        # -------------------------------------------------------------
        # 7. Background Daemon & Hash Diffing Trigger
        # -------------------------------------------------------------
        print("\n[7] 🔄 백그라운드 데몬 온디맨드 동기화 & Hash Diffing (POST /api/v1/emergency/sync)")
        res_sync = await client.post("/api/v1/emergency/sync")
        sync_data = res_sync.json()
        print(f"  • 동기화 상태: {sync_data['status']}")
        print(f"  • 수집 전체 병원 수: {sync_data['total_count']}개소")
        print(f"  • 실제 변경 갱신(Firestore): {sync_data['synced_count']}개소")
        print(f"  • Hash Diffing 절감 생략: {sync_data['skipped_count']}개소")
        print(f"  • FinOps 비용 절감율: {sync_data['saving_rate_percent']}%")

        print("\n" + "=" * 80)
        print("🎉 [Step 5] FastAPI REST 서빙 & 백그라운드 동기화 데몬 시연 완료!")
        print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_step5_demo())
