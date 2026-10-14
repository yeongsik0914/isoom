"""Interactive Demonstration script for Step 3: AI Multi-Agent Layer.

Demonstrates:
1. Scenario A: Mild fever & cough (Moonlight Children's Clinic + 30-min pharmacy pairing).
2. Scenario B: High fever & vomiting (Pediatric Emergency Center priority routing).
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.agents.guardrail_agent import check_red_flag_instant
from app.agents.logistics_agent import LogisticsAgent
from app.agents.matching_agent import MatchingAgent
from app.agents.triage_agent import TriageAgent
from app.schemas.state import PatientSessionState


async def run_scenario(title: str, user_msg: str, user_lat: float, user_lon: float) -> None:
    print("\n" + "=" * 75)
    print(f"🎬 [시나리오 실행] {title}")
    print("=" * 75)
    print(f"💬 보호자 입력: \"{user_msg}\"")
    print(f"📍 보호자 GPS 위치: ({user_lat}, {user_lon})")

    state = PatientSessionState(
        session_id=f"demo-{title}",
        user_lat=user_lat,
        user_lon=user_lon,
    )

    triage_agent = TriageAgent()
    matching_agent = MatchingAgent()
    logistics_agent = LogisticsAgent()

    # Step 2: 0ms Guardrail Interceptor
    is_red = check_red_flag_instant(user_msg, state)
    if is_red:
        print(f"\n🚨 [0ms Guardrail 긴급 차단] Red Flag 감지: {state.red_flag_reason}")
        print(f"   처치 가이드: {state.emergency_action_guide}")
        return

    # Step 3-1: Triage Agent
    print("\n🤖 [1단계: Triage Agent 가동 - 부모 공감 & 4대 임상 변수 정형화]")
    triage_res = await triage_agent.triage_message(user_msg, state)
    print(f"   - 추출 월령: {state.age_months}개월")
    print(f"   - 추출 체온: {state.temperature}℃")
    print(f"   - 경과 시간: {state.duration_hours}시간")
    print(f"   - 주요 증상: {state.symptoms}")
    print(f"   - 공감 메시지: {triage_res.empathy_message}")
    print(f"   - FSM 전이 상태: {state.current_step}")

    # Step 3-2: Matching Agent
    print("\n🤖 [2단계: Matching Agent 가동 - 결정론적 실시간 병원 & 약국 페어링]")
    await matching_agent.match_destinations(state)
    print(f"   - 추천 병원 수: {len(state.matched_hospitals)}개소")
    for idx, h in enumerate(state.matched_hospitals[:2], 1):
        print(f"     {idx}. [{h.get('유형', '병원')}] {h.get('기관명', '')} (거리: {h.get('거리_km', 0.0)}km)")

    if state.matched_pharmacies:
        print(f"   - 30분 안심 마진 연계 약국: {len(state.matched_pharmacies)}개소")
        p = state.matched_pharmacies[0]
        print(f"     👉 {p.get('약국명')} (마감: {p.get('마감시간')}, 안전마진: +{p.get('안전마진_분')}분, {p.get('조제안전등급')})")
    print(f"   - FSM 전이 상태: {state.current_step}")

    # Step 3-3: Logistics Agent
    print("\n🤖 [3단계: Logistics Agent 가동 - 30초 통화 스크립트 & 필수 지참 서류]")
    await logistics_agent.generate_logistics(state)
    print("   📞 [병원 출발 전 30초 유선 확인 통화 스크립트]:")
    print(f"      {state.call_script}")
    print("   📋 [2024년 5월 본인확인 의무화 지참 서류 체크리스트]:")
    for doc in state.document_checklist:
        print(f"      • {doc}")
    print(f"\n✅ [최종 FSM 상태]: {state.current_step} (총 소요 턴 수: {state.turn_count}턴)")


async def main() -> None:
    print("=" * 75)
    print("🌙 [MoonlightCare] Step 3: AI 멀티 에이전트 결합 레이어 통합 데모")
    print("=" * 75)

    # 시나리오 1: 야간 경증 발열 (달빛어린이병원 + 30분 마진 야간약국 페어링)
    await run_scenario(
        title="야간 경증 발열 ➔ 달빛어린이병원 & 30분 협약약국 연계",
        user_msg="서초구 방배동인데 36개월 아이가 38.0도 미열나고 2시간째 기침해요. 어디로 가야 할까요?",
        user_lat=37.4988,
        user_lon=126.9934,
    )

    # 시나리오 2: 심야 고열 및 구토 (소아전문응급센터 우선 라우팅)
    await run_scenario(
        title="심야 고열 및 구토 ➔ 소아 가용 응급실 최단거리 라우팅",
        user_msg="잠실동인데 14개월 아기가 39.5도 불덩이고 2시간째 토해요. 응급실 바로 갈 수 있나요?",
        user_lat=37.5133,
        user_lon=127.1001,
    )


if __name__ == "__main__":
    asyncio.run(main())
