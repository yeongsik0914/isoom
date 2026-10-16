"""KTAS Pediatric Triage Full-Spectrum Verification Suite.

Executes 15 comprehensive clinical scenarios across KTAS Levels 1-5 via POST /api/v1/chat
simulating the exact payload from the frontend input.html form.
Collects classification accuracy, Red Flag sensitivity, 2-track routing, latency, and compliance.
"""

from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from main import app

BENCHMARK_SCENARIOS = [
    # --- KTAS 1: Resuscitation (소생) ---
    {
        "id": "TC-KTAS-01",
        "category": "KTAS 1단계 (소생)",
        "expected_level": 1,
        "expected_emergency": True,
        "expected_track": "Track A (소아전문응급센터/119)",
        "payload": {
            "user_message": "14개월 아기이고 체온은 39.5℃입니다. 주요 증상: 중증 호흡곤란 및 청색증, 입술이 파랗게 질리고 숨을 헐떡이며 갈비뼈 사이가 쑥 들어가요, 투약/동반: 응급 헐떡임",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "중증 호흡부전 및 청색증 0ms Red Flag 감지"
    },
    {
        "id": "TC-KTAS-02",
        "category": "KTAS 1단계 (소생)",
        "expected_level": 1,
        "expected_emergency": True,
        "expected_track": "Track A (소아전문응급센터/119)",
        "payload": {
            "user_message": "24개월 아기이고 체온은 38.8℃입니다. 주요 증상: 소아 경련, 눈이 위로 돌아가고 입에 거품을 물며 5분째 온몸을 굳히고 떨고 있어요, 투약/동반: 의식 없음",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "소아 경련/열성경련 지속 0ms Red Flag 감지"
    },
    {
        "id": "TC-KTAS-03",
        "category": "KTAS 1단계 (소생)",
        "expected_level": 1,
        "expected_emergency": True,
        "expected_track": "Track A (소아전문응급센터/119)",
        "payload": {
            "user_message": "18개월 아기이고 체온은 39.0℃입니다. 주요 증상: 의식 저하, 아이가 완전히 축 늘어져서 이름을 부르고 꼬집어도 눈을 안 뜨고 축 처져있어요, 투약/동반: 무반응 기면",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "중증 의식저하(기면/무반응) 0ms Red Flag 감지"
    },

    # --- KTAS 2: Emergent (긴급) ---
    {
        "id": "TC-KTAS-04",
        "category": "KTAS 2단계 (긴급)",
        "expected_level": 2,
        "expected_emergency": True,
        "expected_track": "Track A (소아전문응급센터/119)",
        "payload": {
            "user_message": "생후 55일 신생아이고 체온은 38.3℃입니다. 주요 증상: 발열, 아기 몸이 뜨거워서 쟀더니 38.3도예요, 투약/동반: 해열제 미복용",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "생후 100일 미만 38도 고열(신생아 패혈증 의심) Red Flag"
    },
    {
        "id": "TC-KTAS-05",
        "category": "KTAS 2단계 (긴급)",
        "expected_level": 2,
        "expected_emergency": True,
        "expected_track": "Track A (소아전문응급센터/119)",
        "payload": {
            "user_message": "10개월 아기이고 체온은 37.6℃입니다. 주요 증상: 소아 장중첩증, 10분 간격으로 자지러지게 울며 다리를 배 쪽으로 끌어당기고 딸기잼 같은 피똥(혈변)을 봤어요, 투약/동반: 심한 보챔",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "소아 장중첩증(주기적 복통+딸기잼 혈변) Red Flag"
    },
    {
        "id": "TC-KTAS-06",
        "category": "KTAS 2단계 (긴급)",
        "expected_level": 2,
        "expected_emergency": True,
        "expected_track": "Track A (소아전문응급센터/119)",
        "payload": {
            "user_message": "20개월 아기이고 체온은 38.5℃입니다. 주요 증상: 크룹(흡기 쇳소리), 컹컹 개 짖는 기침을 하고 숨쉴 때 쇳소리가 나며 침을 삼키지 못해 줄줄 흘려요, 투약/동반: 호흡 곤란",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "소아 크룹(쇳소리+침흘림 기도폐쇄 위험) Red Flag"
    },

    # --- KTAS 3: Urgent (응급) ---
    {
        "id": "TC-KTAS-07",
        "category": "KTAS 3단계 (응급)",
        "expected_level": 3,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "14개월 아기이고 체온은 39.1℃입니다. 주요 증상: 고열 지속, 해열제를 교차 복용해도 39.1도 밑으로 잘 안 떨어지고 오늘 구토를 2번 했어요. 청색증이나 경련은 없어요, 투약/동반: 고열 지속",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "영아 39도 고열 지속 및 구토 동반 KTAS 3단계 외래/응급"
    },
    {
        "id": "TC-KTAS-08",
        "category": "KTAS 3단계 (응급)",
        "expected_level": 3,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "30개월 아기이고 체온은 38.8℃입니다. 주요 증상: 천명음(쌕쌕거림), 숨 쉴 때 가슴에서 쌕쌕거리는 소리가 들리고 기침을 해요. 입술은 분홍색이고 의식은 또렷해요, 투약/동반: 식욕 저하",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "소아 급성 천명음/천식/모세기관지염 KTAS 3단계"
    },
    {
        "id": "TC-KTAS-09",
        "category": "KTAS 3단계 (응급)",
        "expected_level": 3,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "36개월 아기이고 체온은 38.5℃입니다. 주요 증상: 복통, 배를 움켜쥐고 계속 아프다고 칭얼거려요. 혈변이나 구토는 없어요, 투약/동반: 보챔",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "소아 급성 복통 KTAS 3단계 감별"
    },

    # --- KTAS 4: Less Urgent (준응급) ---
    {
        "id": "TC-KTAS-10",
        "category": "KTAS 4단계 (준응급)",
        "expected_level": 4,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "24개월 아기이고 체온은 38.2℃입니다. 주요 증상: 발열, 아까 38.8도였는데 해열제 먹이고 땀 흠뻑 흘리며 38.2도로 떨어졌고 밥도 먹고 장난감 가지고 잘 놀아요, 투약/동반: 해열제 후 호전, 활동성 양호",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "가역적 시간차 호전 (Well-appearing) KTAS 4단계"
    },
    {
        "id": "TC-KTAS-11",
        "category": "KTAS 4단계 (준응급)",
        "expected_level": 4,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "18개월 아기이고 체온은 37.8℃입니다. 주요 증상: 미열과 묽은 변 2회, 설사를 두 번 했는데 보채지 않고 보리차도 꿀꺽꿀꺽 잘 마셔요, 투약/동반: 수분 섭취 양호",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "경증 위장관염 및 양호한 수분 섭취 KTAS 4단계"
    },
    {
        "id": "TC-KTAS-12",
        "category": "KTAS 4단계 (준응급)",
        "expected_level": 4,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "4세 소아이고 체온은 38.0℃입니다. 주요 증상: 기침 및 콧물, 기침을 콜록거리고 맑은 콧물이 나요. 밤에 잘 자고 밥도 잘 먹어요, 투약/동반: 전신 상태 양호",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "단순 상기도 감염(감기) KTAS 4단계"
    },

    # --- KTAS 5: Non-Urgent (비응급) ---
    {
        "id": "TC-KTAS-13",
        "category": "KTAS 5단계 (비응급)",
        "expected_level": 5,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "5세 소아이고 체온은 36.8℃입니다. 주요 증상: 가벼운 콧물과 재채기, 열은 전혀 없고 콧물이 조금 나서 약국 감기약이나 병원 확인하고 싶어요, 투약/동반: 정상 체온, 활발함",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "열 없는 단순 콧물/재채기 KTAS 5단계 비응급"
    },
    {
        "id": "TC-KTAS-14",
        "category": "KTAS 5단계 (비응급)",
        "expected_level": 5,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "6세 소아이고 체온은 36.6℃입니다. 주요 증상: 가벼운 무릎 찰과상, 넘어져서 무릎이 살짝 까졌는데 피는 멎었고 소독약이나 연고 살 곳 찾아요, 투약/동반: 정상 체온, 걷기 가능",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "경미한 표재성 찰과상 KTAS 5단계 비응급"
    },
    {
        "id": "TC-KTAS-15",
        "category": "KTAS 5단계 (비응급)",
        "expected_level": 5,
        "expected_emergency": False,
        "expected_track": "Track B (달빛어린이병원 & 안심약국)",
        "payload": {
            "user_message": "3세 소아이고 체온은 36.9℃입니다. 주요 증상: 피부 건조증, 팔 접히는 부위가 건조하고 조금 긁어요. 열이나 발진은 전혀 없어요, 투약/동반: 정상 체온",
            "user_lat": 37.5133,
            "user_lon": 127.1001,
            "user_address": "서울특별시 송파구 잠실동",
            "force_matching": True,
            "stream": False
        },
        "clinical_focus": "만성 피부 건조증/가려움 KTAS 5단계 비응급"
    }
]


def run_ktas_verification():
    print(f"🚀 [KTAS Triage Verification] Starting evaluation of {len(BENCHMARK_SCENARIOS)} pediatric clinical scenarios...")
    client = TestClient(app)
    results = []

    for i, scenario in enumerate(BENCHMARK_SCENARIOS, 1):
        sc_id = scenario["id"]
        cat = scenario["category"]
        exp_lvl = scenario["expected_level"]
        exp_emg = scenario["expected_emergency"]
        payload = scenario["payload"]

        print(f"\n[{i}/{len(BENCHMARK_SCENARIOS)}] Executing {sc_id} ({cat})...")
        t0 = time.perf_counter()
        resp = client.post("/api/v1/chat", json=payload)
        latency_ms = (time.perf_counter() - t0) * 1000

        if resp.status_code != 200:
            print(f"❌ HTTP {resp.status_code} Error: {resp.text}")
            results.append({
                "id": sc_id,
                "category": cat,
                "status": "FAIL_HTTP",
                "status_code": resp.status_code,
                "error": resp.text
            })
            continue

        data = resp.json()
        actual_level = data.get("ktas_level")
        actual_emergency = data.get("is_emergency", False)
        actual_red_flag = data.get("is_red_flag", False)
        hospitals = data.get("hospitals", [])
        pharmacies = data.get("pharmacies", [])
        disclaimer = data.get("disclaimer", "")
        call_script = data.get("call_script")
        checklist = data.get("checklist", [])
        current_step = data.get("current_step")

        # Routing check
        if exp_emg:
            routing_correct = actual_emergency is True and current_step == "EMERGENCY_ESCALATION"
            actual_track = "Track A (소아전문응급센터/119)"
        else:
            routing_correct = actual_emergency is False and current_step == "COMPLETED"
            actual_track = "Track B (달빛어린이병원 & 안심약국)"

        # Level Match Check
        level_match = (actual_level == exp_lvl)
        # Clinical Safety Check: Level 1 and 2 must ALWAYS trigger emergency (Safety Invariant)
        safety_invariant_held = True
        if exp_lvl in (1, 2) and not actual_emergency:
            safety_invariant_held = False

        status_str = "PASS" if (level_match and routing_correct and safety_invariant_held) else "FAIL"

        print(f"   ⏱️ Latency: {latency_ms:.1f}ms | Level: Exp {exp_lvl} vs Act {actual_level} | Emergency: Exp {exp_emg} vs Act {actual_emergency} -> {status_str}")

        results.append({
            "id": sc_id,
            "category": cat,
            "focus": scenario["clinical_focus"],
            "expected_level": exp_lvl,
            "actual_level": actual_level,
            "level_match": level_match,
            "expected_emergency": exp_emg,
            "actual_emergency": actual_emergency,
            "expected_track": scenario["expected_track"],
            "actual_track": actual_track,
            "routing_correct": routing_correct,
            "safety_invariant_held": safety_invariant_held,
            "latency_ms": round(latency_ms, 2),
            "hospitals_count": len(hospitals),
            "pharmacies_count": len(pharmacies),
            "has_call_script": call_script is not None,
            "checklist_count": len(checklist),
            "has_art27_disclaimer": "의료법 제27조" in disclaimer,
            "status": status_str,
            "server_message_sample": (data.get("message") or "")[:80]
        })

    # Summary Statistics
    total_count = len(results)
    passed_count = sum(1 for r in results if r["status"] == "PASS")
    accuracy_pct = (passed_count / total_count) * 100
    avg_latency = sum(r.get("latency_ms", 0) for r in results) / total_count
    red_flag_sensitivity = 100.0 if all(r["safety_invariant_held"] for r in results) else 0.0

    print("\n" + "="*70)
    print(f"📊 [TEST SUMMARY] Total: {total_count} | Passed: {passed_count} | Accuracy: {accuracy_pct:.1f}%")
    print(f"🛡️ Red Flag Clinical Safety Invariant: {red_flag_sensitivity:.1f}%")
    print(f"⚡ Average End-to-End Latency: {avg_latency:.1f}ms")
    print("="*70)

    # Save output to json
    output_path = Path("tests/evals/ktas_verification_output.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "executed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_count": total_count,
            "passed_count": passed_count,
            "accuracy_pct": accuracy_pct,
            "avg_latency_ms": round(avg_latency, 2),
            "red_flag_sensitivity_pct": red_flag_sensitivity,
            "scenarios": results
        }, f, ensure_ascii=False, indent=2)
    print(f"💾 Results saved to {output_path}")

if __name__ == "__main__":
    run_ktas_verification()
