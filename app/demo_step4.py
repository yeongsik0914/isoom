"""Interactive Demonstration script for Step 4: Master Orchestrator (Supervisor FSM).

Demonstrates:
1. Scenario 1: Multi-Turn Safe Triage (Turn 1 Incomplete ➔ Turn 2 Complete ➔ Matched & Scheduled)
2. Scenario 2: Mid-Turn Red Flag Deterioration (Turn 1 Mild ➔ Turn 2 Seizure ➔ 0ms 119 Escalation)
3. Scenario 3: 3-Turn Loop Guard (Turn 1, 2, 3 Vague ➔ Forced Safe Clinical Routing)
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app.orchestrator.supervisor import SupervisorOrchestrator


async def run_scenario_1() -> None:
    print("\n" + "=" * 80)
    print("🎬 [시나리오 1] 멀티턴 자연어 문진 & 단계별 FSM 전이 (Turn 1 ➔ Turn 2)")
    print("=" * 80)
    supervisor = SupervisorOrchestrator()
    sid = "demo-scenario-1"

    # Turn 1
    msg1 = "서초동인데 아기가 열이 나요 어디로 가야 하나요?"
    print(f"\n[Turn 1] 보호자: \"{msg1}\"")
    res1 = await supervisor.process_turn(user_message=msg1, session_id=sid, user_lat=37.4918, user_lon=127.0079)
    print(f"👉 시스템 상태: {res1.current_step} (Turn {res1.turn_count})")
    print(f"💬 응답 메시지:\n{res1.message}")

    # Turn 2
    msg2 = "아이는 18개월이고 방금 잰 체온은 38.3도예요. 기침하고 2시간 됐어요."
    print(f"\n[Turn 2] 보호자: \"{msg2}\"")
    res2 = await supervisor.process_turn(user_message=msg2, session_id=sid, user_lat=37.4918, user_lon=127.0079)
    print(f"👉 시스템 상태: {res2.current_step} (Turn {res2.turn_count})")
    print(f"💬 종합 안내 메시지:\n{res2.message}")
    if res2.hospitals:
        top_h = res2.hospitals[0]
        print(f"🏥 추천 의료기관: [{top_h.get('유형')}] {top_h.get('기관명')} ({top_h.get('거리_km')}km)")
    if res2.pharmacies:
        top_p = res2.pharmacies[0]
        print(f"💊 연계 심야약국: {top_p.get('약국명')} (+{top_p.get('안전마진_분')}분 마진, 마감 {top_p.get('마감시간')})")
    if res2.call_script:
        print(f"📞 [30초 확인 스크립트]:\n   {res2.call_script}")
    print(f"📋 지참 서류: {res2.checklist}")


async def run_scenario_2() -> None:
    print("\n" + "=" * 80)
    print("🎬 [시나리오 2] 중도 급변(Mid-Turn Deterioration) 0ms Red Flag 긴급 에스컬레이션")
    print("=" * 80)
    supervisor = SupervisorOrchestrator()
    sid = "demo-scenario-2"

    # Turn 1: Mild
    msg1 = "잠실인데 24개월 아이가 37.8도 미열이 있어요."
    print(f"\n[Turn 1] 보호자: \"{msg1}\"")
    res1 = await supervisor.process_turn(user_message=msg1, session_id=sid)
    print(f"👉 시스템 상태: {res1.current_step} (Turn {res1.turn_count})")

    # Turn 2: Sudden Seizure
    msg2 = "선생님 아기가 갑자기 입술이 파래지면서 몸을 떨고 경련을 일으켜요!"
    print(f"\n[Turn 2] 보호자: \"{msg2}\"")
    res2 = await supervisor.process_turn(user_message=msg2, session_id=sid)
    print(f"🚨 [긴급 인터셉트 발동] 시스템 상태: {res2.current_step} (is_emergency={res2.is_emergency})")
    print(f"💬 비상 응답 메시지:\n{res2.message}")
    print(f"🚑 1차 응급처치 가이드:\n{res2.emergency_guide}")
    if res2.hospitals:
        print(f"🏥 인근 소아 가용 응급실: {res2.hospitals[0].get('기관명')} ({res2.hospitals[0].get('거리_km')}km)")


async def run_scenario_3() -> None:
    print("\n" + "=" * 80)
    print("🎬 [시나리오 3] 3턴 상한선 무한 루프 차단 가드 (Deadlock Protection)")
    print("=" * 80)
    supervisor = SupervisorOrchestrator()
    sid = "demo-scenario-3"

    turns = [
        "아기가 그냥 아파요",
        "몰라요 계속 보채요",
        "빨리 병원이나 알려줘요",
    ]

    for idx, msg in enumerate(turns, 1):
        print(f"\n[Turn {idx}] 보호자: \"{msg}\"")
        res = await supervisor.process_turn(user_message=msg, session_id=sid)
        print(f"👉 시스템 상태: {res.current_step} (Turn {res.turn_count})")
        if idx == 3:
            print(f"✅ [3턴 상한 도달 ➔ 강제 전이 완료]: {res.current_step}")
            print(f"💬 안전 안내 메시지:\n{res.message}")
            if res.hospitals:
                print(f"🏥 배정된 안전 의료기관: {res.hospitals[0].get('기관명')}")


async def main() -> None:
    print("=" * 80)
    print("🌙 [MoonlightCare] Step 4: 메인 오케스트레이터 (Supervisor FSM) 통합 데모")
    print("=" * 80)

    await run_scenario_1()
    await run_scenario_2()
    await run_scenario_3()


if __name__ == "__main__":
    asyncio.run(main())
