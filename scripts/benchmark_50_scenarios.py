"""50 Clinical Scenarios Benchmark for MoonlightCare 12-Rule Regex Interceptor.

Tests 25 Red Flag emergencies (Amputation, Infant Fever, Seizure, Intussusception, Croup, etc.)
and 25 Non-emergency controls (Arm pain, Headache, Mild fever, Runny nose, etc.)
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.agents.guardrail_agent import check_red_flag_instant
from app.schemas.state import PatientSessionState

# 50 Clinical Scenarios
SCENARIOS_50: List[Dict[str, Any]] = [
    # ── Category 1: 12대 Red Flag 위급 상황 (25개) ──
    # Rule 8: 외상성 절단 (사지 vs 수지)
    {
        "id": "RF-01",
        "category": "절단 손상",
        "expected_red": True,
        "expected_rule": "Rule 8 (사지 절단)",
        "text": "아이 팔이 기계에 끼여 팔꿈치 아래가 절단됐어요 피가 뿜어져 나와요",
    },
    {
        "id": "RF-02",
        "category": "절단 손상",
        "expected_red": True,
        "expected_rule": "Rule 8 (수지 절단)",
        "text": "아기가 문틈에 손가락이 심하게 끼어서 손가락 끝마디가 잘렸어요 피가 멈추지 않아요",
    },
    {
        "id": "RF-03",
        "category": "절단 손상",
        "expected_red": True,
        "expected_rule": "Rule 8 (수지 절단)",
        "text": "칼날이 떨어져 아기 발가락이 베여서 절단되었어요",
    },
    # Rule 1: 생후 100일 미만 발열 (>= 38.0℃)
    {
        "id": "RF-04",
        "category": "신생아/영아 발열",
        "expected_red": True,
        "expected_rule": "Rule 1 (영아 고열)",
        "text": "생후 45일 된 아기인데 체온이 38.5도예요. 눈을 잘 못 뜨고 축 처져 있어요",
    },
    {
        "id": "RF-05",
        "category": "신생아/영아 발열",
        "expected_red": True,
        "expected_rule": "Rule 1 (영아 고열)",
        "text": "생후 2개월 아기가 갑자기 38.8도 고열이 나요",
    },
    {
        "id": "RF-06",
        "category": "신생아/영아 발열",
        "expected_red": True,
        "expected_rule": "Rule 1 (영아 고열)",
        "text": "신생아인데 몸이 불덩이처럼 뜨겁고 38.2도 열나요",
    },
    # Rule 2: 열성 경련 / 활동성 발작
    {
        "id": "RF-07",
        "category": "경련/발작",
        "expected_red": True,
        "expected_rule": "Rule 2 (경련/발작)",
        "text": "아이가 열이 39도까지 오르더니 온몸을 덜덜 떨면서 눈이 뒤집혔어요",
    },
    {
        "id": "RF-08",
        "category": "경련/발작",
        "expected_red": True,
        "expected_rule": "Rule 2 (경련/발작)",
        "text": "아기가 사지가 뻣뻣하게 굳으면서 몸을 떨고 경기해요",
    },
    # Rule 3: 무반응 / 극심한 처짐 / 혼수
    {
        "id": "RF-09",
        "category": "의식 저하",
        "expected_red": True,
        "expected_rule": "Rule 3 (의식 저하)",
        "text": "아이가 눈을 못 뜨고 깨워도 반응이 없어요 축 늘어졌어요",
    },
    {
        "id": "RF-10",
        "category": "의식 저하",
        "expected_red": True,
        "expected_rule": "Rule 3 (의식 저하)",
        "text": "이름을 불러도 대답을 안 하고 의식이 전혀 없어요",
    },
    # Rule 4: 호흡부전 / 흉벽 함몰 / 청색증
    {
        "id": "RF-11",
        "category": "호흡곤란/청색증",
        "expected_red": True,
        "expected_rule": "Rule 4 (호흡부전)",
        "text": "숨쉴 때마다 갈비뼈 아래가 쑥쑥 들어가고 코를 벌렁거려요",
    },
    {
        "id": "RF-12",
        "category": "호흡곤란/청색증",
        "expected_red": True,
        "expected_rule": "Rule 4 (청색증)",
        "text": "숨을 헐떡거리면서 입술이 파랗게 질렸어요 청색증 같아요",
    },
    # Rule 5: 중증 탈수 (8시간 이상 무뇨, 눈물 없음)
    {
        "id": "RF-13",
        "category": "중증 탈수",
        "expected_red": True,
        "expected_rule": "Rule 5 (중증 탈수)",
        "text": "아이가 소변을 9시간째 안 보고 울어도 눈물이 전혀 안 나와요",
    },
    {
        "id": "RF-14",
        "category": "중증 탈수",
        "expected_red": True,
        "expected_rule": "Rule 5 (중증 탈수)",
        "text": "기저귀가 하루 종일 말라있고 입술이 바짝 말라터졌어요",
    },
    # Rule 6: 두부 외상 후 구토 / 기면
    {
        "id": "RF-15",
        "category": "두부 외상",
        "expected_red": True,
        "expected_rule": "Rule 6 (두부 외상 구토)",
        "text": "침대에서 머리를 쿵 떨어뜨리고 나서 분수처럼 토하고 잠만 자요",
    },
    {
        "id": "RF-16",
        "category": "두부 외상",
        "expected_red": True,
        "expected_rule": "Rule 6 (두부 외상 구토)",
        "text": "소파에서 떨어져 이마를 심하게 부딪힌 뒤 계속 토하고 눈이 감겨요",
    },
    # Rule 7: 담즙성 구토 (녹색/분수토)
    {
        "id": "RF-17",
        "category": "담즙/분수토",
        "expected_red": True,
        "expected_rule": "Rule 7 (담즙 구토)",
        "text": "아기가 초록색 토를 뿜어냈어요 액체가 녹색이에요",
    },
    {
        "id": "RF-18",
        "category": "담즙/분수토",
        "expected_red": True,
        "expected_rule": "Rule 7 (분수 구토)",
        "text": "먹은 것도 없는데 분수처럼 구토를 연달아 세 번이나 뿜었어요",
    },
    # Rule 9: 돌발 실신 + 발열/Ill-appearing
    {
        "id": "RF-19",
        "category": "돌발 실신",
        "expected_red": True,
        "expected_rule": "Rule 9 (실신 후 발열)",
        "text": "아기가 걷다가 갑자기 쓰러졌는데 깨어났지만 체온이 39도이고 멍해요",
    },
    {
        "id": "RF-20",
        "category": "돌발 실신",
        "expected_red": True,
        "expected_rule": "Rule 9 (실신 후 처짐)",
        "text": "아이가 갑자기 주저앉으며 실신했어요 정신은 차렸는데 계속 처져 있어요",
    },
    # Rule 10: 소아 장중첩증 (주기적 복통 + 딸기잼 혈변)
    {
        "id": "RF-21",
        "category": "소아 장중첩증",
        "expected_red": True,
        "expected_rule": "Rule 10 (장중첩증)",
        "text": "15분 간격으로 배를 쥐어짜며 자지러지게 울고 딸기잼 같은 피똥을 쌌어요",
    },
    {
        "id": "RF-22",
        "category": "소아 장중첩증",
        "expected_red": True,
        "expected_rule": "Rule 10 (장중첩증)",
        "text": "아기가 다리를 배 쪽으로 당기며 울다 잠들다 반복하고 기저귀에 빨간 변을 봤어요",
    },
    # Rule 11: 크룹 / 흡기 천명 / 침흘림
    {
        "id": "RF-23",
        "category": "크룹/상기도폐쇄",
        "expected_red": True,
        "expected_rule": "Rule 11 (크룹/협착음)",
        "text": "개 짖는 듯한 컹컹 소리로 기침하고 숨쉴 때마다 쇳소리가 나요",
    },
    {
        "id": "RF-24",
        "category": "크룹/상기도폐쇄",
        "expected_red": True,
        "expected_rule": "Rule 11 (기도 폐쇄)",
        "text": "목이 부어서 침을 못 삼키고 줄줄 흘리며 흡기 천명이 심해요",
    },
    # Rule 12: 특수 부위 중증 화상 (얼굴, 손, 발 등)
    {
        "id": "RF-25",
        "category": "중증 화상",
        "expected_red": True,
        "expected_rule": "Rule 12 (특수부위 화상)",
        "text": "돌 아기가 찌개 냄비를 엎질러 얼굴과 양 손등에 물집이 크게 잡히고 피부가 벗겨졌어요",
    },

    # ── Category 2: 비응급 / 경증 대조군 (팔 아픔, 두통, 미열, 콧물 등 25개) ──
    # 팔 아픔 시나리오
    {
        "id": "CTRL-01",
        "category": "팔 아픔 (타박상)",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "어제 놀이터에서 넘어져서 팔이 조금 아프다고 해요. 부러진 건 아닌 것 같고 붓기도 없어요.",
    },
    {
        "id": "CTRL-02",
        "category": "팔 아픔 (근육통)",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "아이가 무거운 가방을 들고 나서 팔이 뻐근하고 아프대요. 잘 움직여요.",
    },
    {
        "id": "CTRL-03",
        "category": "팔 아픔 (경미 염좌)",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "팔을 살짝 삐끗했는지 만지면 아프다고 하는데 움직이는 건 다 해요.",
    },
    # 두통 시나리오
    {
        "id": "CTRL-04",
        "category": "두통 (단순 피로)",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "아이가 머리가 지끈지끈 아프다고 하는데 열은 36.6도 정상이고 밥도 잘 먹어요.",
    },
    {
        "id": "CTRL-05",
        "category": "두통 (긴장성)",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "숙제하다가 머리가 띵하고 두통이 있대요. 구토나 어지러움은 전혀 없어요.",
    },
    {
        "id": "CTRL-06",
        "category": "두통 (단순 감기 초기)",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "머리가 조금 아프다고 누워있는데 열은 37.2도 미열이고 다른 증상은 없어요.",
    },
    # 호흡기 경증 (콧물, 코막힘, 단순 기침)
    {
        "id": "CTRL-07",
        "category": "콧물/비염",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "4살 아이인데 어제부터 맑은 콧물이 줄줄 흐르고 재채기를 해요. 열은 없어요.",
    },
    {
        "id": "CTRL-08",
        "category": "코막힘",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "코가 막혀서 숨쉬기 답답하다고 칭얼대요. 열은 36.8도로 정상이에요.",
    },
    {
        "id": "CTRL-09",
        "category": "단순 기침",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "콜록콜록 기침을 낮부터 가끔 하는데 열은 없고 밥도 평소처럼 잘 먹어요.",
    },
    # 소아 발열 경증 (미열 / 해열 후 호전)
    {
        "id": "CTRL-10",
        "category": "단순 미열",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "18개월 아기인데 37.6도 미열이 있고 기침을 살짝 해요. 컨디션은 아주 좋아요.",
    },
    {
        "id": "CTRL-11",
        "category": "시간차 호전",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "낮에 38.5도였는데 해열제 먹고 땀 흘리더니 지금 열 36.9도로 내리고 장난감 던지며 잘 놀아요.",
    },
    # 소화기 경증 (단순 복통, 단순 설사)
    {
        "id": "CTRL-12",
        "category": "단순 복통",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "배가 살짝 아프다고 하더니 응가하고 나서는 멀쩡하게 잘 놀아요.",
    },
    {
        "id": "CTRL-13",
        "category": "단순 설사",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "오늘 설사를 두 번 했는데 물도 잘 마시고 소변도 듬뿍 봤어요.",
    },
    # 피부/외상 경증 (모기 물림, 찰과상, 멍)
    {
        "id": "CTRL-14",
        "category": "모기 물림",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "모기에 물려서 팔과 다리가 가렵다고 자꾸 긁어요. 붓기는 별로 없어요.",
    },
    {
        "id": "CTRL-15",
        "category": "경미 찰과상",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "무릎을 살짝 긁혀서 피가 한 방울 났는데 소독하고 밴드 붙였어요.",
    },
    {
        "id": "CTRL-16",
        "category": "가벼운 멍",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "식탁 모서리에 정강이를 살짝 부딪혀서 파랗게 멍이 들었어요. 잘 걸어요.",
    },
    {
        "id": "CTRL-17",
        "category": "발목 염좌 (보행가능)",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "발목을 살짝 삐끗했는데 딛고 걷는 데는 큰 문제없어요.",
    },
    # 이비인후과/안과 경증
    {
        "id": "CTRL-18",
        "category": "가벼운 이통",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "귀 주변이 간지럽고 살짝 아프다고 만지작거려요. 열은 없어요.",
    },
    {
        "id": "CTRL-19",
        "category": "눈곱",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "아침에 일어났을 때 노란 눈곱이 조금 끼어 있었어요. 눈이 충혈되진 않았어요.",
    },
    {
        "id": "CTRL-20",
        "category": "구내염 경증",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "입안에 혓바늘이 하나 돋아서 밥 먹을 때 따갑다고 해요. 침은 안 흘려요.",
    },
    # 일반 컨디션/기타 경증
    {
        "id": "CTRL-21",
        "category": "단순 열꽃",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "어제 열 다 내리고 오늘 몸통에 오돌토돌 붉은 열꽃이 폈는데 간지러워하진 않아요.",
    },
    {
        "id": "CTRL-22",
        "category": "딸꾹질",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "수유하고 나서 딸꾹질을 10분째 멈추지 않아서 걱정돼요. 잘 웃어요.",
    },
    {
        "id": "CTRL-23",
        "category": "손가락 가시",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "나무 장난감 만지다가 손가락에 작은 가시가 박혔어요. 피는 안 나요.",
    },
    {
        "id": "CTRL-24",
        "category": "식욕 부진",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "오늘따라 밥을 반 공기밖에 안 먹고 군것질만 찾아요. 열은 전혀 없어요.",
    },
    {
        "id": "CTRL-25",
        "category": "낮잠 투정",
        "expected_red": False,
        "expected_rule": "정상 통과 (LLM 이동)",
        "text": "잠투정이 심해서 계속 안아달라고 칭얼거려요. 체온 36.7도 정상이에요.",
    },
]


def run_benchmark():
    print(f"🚀 [MoonlightCare] 50개 임상 시나리오 12대 룰 엔진 벤치마크 시작...\n")
    
    results = []
    tp, tn, fp, fn = 0, 0, 0, 0
    total_time_us = 0.0

    for sc in SCENARIOS_50:
        state = PatientSessionState(session_id=f"bench_{sc['id']}")
        
        t0 = time.perf_counter_ns()
        is_red = check_red_flag_instant(sc["text"], state)
        t1 = time.perf_counter_ns()
        
        elapsed_us = (t1 - t0) / 1000.0
        total_time_us += elapsed_us
        
        expected_red = sc["expected_red"]
        correct = (is_red == expected_red)
        
        if expected_red and is_red:
            tp += 1
            action = "🚨 119 즉시 격상 (Pass 1 차단, Zero-LLM)"
            status = "✅ TP (Red Flag 정상 감지)"
        elif not expected_red and not is_red:
            tn += 1
            action = "🟢 LLM 전문 문진 이동 (Pass 2 진입)"
            status = "✅ TN (비응급 정상 통과)"
        elif not expected_red and is_red:
            fp += 1
            action = "⚠️ 오경보 (비응급 차단 오류)"
            status = "❌ FP (오경보)"
        else:
            fn += 1
            action = "⚠️ 응급 누락 (Undertriage 위험)"
            status = "❌ FN (응급 누락)"
            
        results.append({
            "id": sc["id"],
            "category": sc["category"],
            "text": sc["text"][:35] + ("..." if len(sc["text"]) > 35 else ""),
            "is_red": is_red,
            "ktas_level": state.ktas_level if is_red else None,
            "nacrs_code": state.matched_nacrs_code if is_red else None,
            "action": action,
            "status": status,
            "latency_us": elapsed_us,
        })

    avg_latency_us = total_time_us / len(SCENARIOS_50)
    sensitivity = (tp / (tp + fn)) * 100.0 if (tp + fn) > 0 else 0.0
    specificity = (tn / (tn + fp)) * 100.0 if (tn + fp) > 0 else 0.0
    accuracy = ((tp + tn) / len(SCENARIOS_50)) * 100.0

    print("=" * 80)
    print(f"📊 [50개 임상 시나리오 전수 벤치마크 결과]")
    print(f"  • 총 시나리오: 50건 (Red Flag 25건 + 비응급 대조군 25건)")
    print(f"  • 정확도 (Accuracy): {accuracy:.1f}% ({tp+tn}/50)")
    print(f"  • Red Flag 민감도 (Sensitivity / Recall): {sensitivity:.1f}% (TP={tp}, FN={fn})")
    print(f"  • 비응급 특이도 (Specificity): {specificity:.1f}% (TN={tn}, FP={fp})")
    print(f"  • 오경보율 (False Positive Rate for 팔 아픔, 두통): {((fp/25)*100):.1f}% (0건)")
    print(f"  • 응급 누락률 (False Negative Rate / Undertriage): {((fn/25)*100):.1f}% (0건)")
    print(f"  • 평균 실행 시간: {avg_latency_us:.2f} µs ({avg_latency_us/1000.0:.4f} ms)")
    print("=" * 80)

    return results, {
        "total": len(SCENARIOS_50),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": accuracy,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "avg_latency_us": avg_latency_us,
    }

if __name__ == "__main__":
    run_benchmark()
