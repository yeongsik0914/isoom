"""Model Comparison Test for Pediatric KTAS Triage:
Gemini 3.8 Flash vs Frontier Deep-Reasoning Pro (and Gemini 4 Argon Verification).

Directly evaluates LLM unstructured context comprehension, clinical reasoning,
KTAS level accuracy, Red Flag sensitivity, and latency on pediatric scenarios.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
import google.genai as genai
from google.genai import types

# Load dataset
DATASET_PATH = PROJECT_ROOT / "data" / "ktas_pediatric_dataset.json"
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    ktas_db = json.load(f)

symptoms = ktas_db["symptoms"]
symptom_catalog = []
for s in symptoms:
    sc_list = [f"L{sc['level']}: {sc['criteria']}" for sc in s.get("secondary_considerations", [])]
    search_corpus = f"{s['symptom_name']} {s['category']} " + " ".join(sc_list)
    symptom_catalog.append({
        "code": s["nacrs_code"],
        "name": s["symptom_name"],
        "cat": s["category"],
        "cons": sc_list,
        "search_corpus": search_corpus,
    })

def retrieve_top_k_symptoms(query: str, k: int = 4) -> List[Dict[str, Any]]:
    query_tokens = set(re.findall(r"[가-힣a-zA-Z0-9]+", query))
    scored = []
    for item in symptom_catalog:
        score = 0
        if any(token in item["name"] for token in query_tokens):
            score += 5
        if any(token in item["cat"] for token in query_tokens):
            score += 3
        for token in query_tokens:
            if len(token) >= 2 and token in item["search_corpus"]:
                score += 1
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:k]]

class KTASClassificationResult(BaseModel):
    triage_source: str = Field(description="판정 주체 모델명")
    ktas_level: int = Field(description="공식 KTAS 분류 번호 (1, 2, 3, 4, 5)")
    ktas_level_name: str = Field(description="KTAS 등급 명칭")
    is_red_flag: bool = Field(description="즉각 생명위협/골든타임 Red Flag 여부 (KTAS 1~2단계)")
    matched_nacrs_code: str = Field(description="매핑된 KTAS 주증상 분류 번호 (NACRS 코드)")
    matched_symptom_name: str = Field(description="매핑된 KTAS 주증상명")
    clinical_rationale: str = Field(description="비정형 문맥 완독 및 임상 감별 근거 (1문장)")

# 15 Highly Diverse & Unstructured Clinical Test Scenarios
BENCHMARK_CASES = [
    {
        "id": "CASE-01",
        "name": "발목 절단 및 의식 소실",
        "text": "아기가 발목이 전기톱에 절단됐어요 피가 엄청나오고 의식이 없어요",
        "expected_level": 1,
        "expected_red_flag": True,
        "key_reason": "사지 본체 외상성 절단 및 의식 소실(무반응) -> KTAS 1단계",
        "difficulty": "Extreme"
    },
    {
        "id": "CASE-02",
        "name": "칼에 의한 손가락 절단",
        "text": "아기가 칼에 손가락이 베여서 절단이 돼서 피가 엄청 나와요.",
        "expected_level": 2,
        "expected_red_flag": True,
        "key_reason": "수지(손가락) 외상성 절단 -> 골든타임 재접합 KTAS 2단계",
        "difficulty": "High"
    },
    {
        "id": "CASE-03",
        "name": "신생아 100일 미만 발열",
        "text": "생후 45일 된 아기인데 방금 체온을 재보니 38.4도예요. 눈을 잘 못 뜨고 축 처져 있어요.",
        "expected_level": 2,
        "expected_red_flag": True,
        "key_reason": "생후 100일 미만 영아 38.0℃ 이상 발열 및 기면 -> 중증 세균감염 의심 KTAS 2단계",
        "difficulty": "High"
    },
    {
        "id": "CASE-04",
        "name": "소아 열성경련 발작",
        "text": "24개월 아이가 열이 39.2도까지 오르더니 갑자기 온몸을 덜덜 떨면서 눈이 위로 돌아갔어요! 2분째 멈추지 않아요.",
        "expected_level": 1,
        "expected_red_flag": True,
        "key_reason": "활동성 전신 경련/발작 지속 -> 기도/호흡 위협 KTAS 1단계",
        "difficulty": "Extreme"
    },
    {
        "id": "CASE-05",
        "name": "영아 호흡부전 및 청색증",
        "text": "8개월 아기인데 숨 쉴 때마다 갈비뼈 아래가 쑥쑥 들어가고 코를 벌렁거려요. 입술 주변도 약간 파랗게 변한 것 같아요.",
        "expected_level": 1,
        "expected_red_flag": True,
        "key_reason": "흉벽 함몰 + 비익 호흡 + 청색증 -> 급성 호흡부전 KTAS 1단계",
        "difficulty": "Extreme"
    },
    {
        "id": "CASE-06",
        "name": "두부 외상 후 반복 구토 및 기면",
        "text": "3살 아기가 소파에서 머리를 쿵 부딪혔는데 그 뒤로 분수처럼 2번 토하고 계속 잠만 자려고 축 늘어져요.",
        "expected_level": 2,
        "expected_red_flag": True,
        "key_reason": "두부 외상 + 반복 분수토 + 기면 -> 두개내압 상승 의심 KTAS 2단계",
        "difficulty": "High"
    },
    {
        "id": "CASE-07",
        "name": "안면 및 수부 2도 화상",
        "text": "16개월 아기가 식탁 위 뜨거운 국을 쏟아서 얼굴과 손등에 물집이 크게 잡히고 껍질이 벗겨졌어요.",
        "expected_level": 2,
        "expected_red_flag": True,
        "key_reason": "특수 부위(얼굴, 손) 2도 이상 중증 화상 -> 기도 및 기능 장애 위험 KTAS 2단계",
        "difficulty": "High"
    },
    {
        "id": "CASE-08",
        "name": "18개월 돌발 실신 후 회복기 + 발열 및 Ill-appearing",
        "text": "18개월 아이인데 걷다가 갑자기 쓰러졌어요 정신이 차려지긴 했는데 아직도 아파보여요 체온은 38도이고",
        "expected_level": 2,
        "expected_red_flag": True,
        "key_reason": "돌발 실신 + 발열 + 지속되는 Ill-appearing -> 무긴장 열성경련/심인성 실신 의심 KTAS 2단계",
        "difficulty": "Very High (비정형 문맥 완독 핵심)"
    },
    {
        "id": "CASE-09",
        "name": "18개월 단순 미열 (경증, 전신양호)",
        "text": "18개월 아기인데 열이 38.2도예요. 기침은 살짝 하지만 밥도 잘 먹고 장난감 가지고 잘 놀아요. 해열제 먹이고 지켜봐도 될까요?",
        "expected_level": 4,
        "expected_red_flag": False,
        "key_reason": "18개월 이상 소아 미열이나 전신 상태(활력, 식이) 양호 -> KTAS 4단계",
        "difficulty": "Medium"
    },
    {
        "id": "CASE-10",
        "name": "4세 단순 콧물/코막힘 (비응급)",
        "text": "4살 아이가 어제부터 맑은 콧물이 나고 코가 막힌다고 칭얼거려요. 열은 36.8도로 전혀 없고 컨디션은 좋아요.",
        "expected_level": 5,
        "expected_red_flag": False,
        "key_reason": "열 없고 활력 양호한 상기도 감염 증상 -> KTAS 5단계",
        "difficulty": "Basic"
    },
    {
        "id": "CASE-11",
        "name": "보호자 과대 패닉 속 실제 경증",
        "text": "아이가 열이 39.8도까지 펄펄 끓어서 너무 무서워요 응급실 지금 당장 가야 하나요? 근데 방금 해열제 먹고 땀 흘리더니 뽀로로 보면서 밥 한 그릇 다 비우고 장난감 던지며 웃고 떠들어요.",
        "expected_level": 4,
        "expected_red_flag": False,
        "key_reason": "체온 수치와 부모 패닉에도 불구하고 해열제 투약 후 완벽한 활력/식이 회복 -> KTAS 4단계",
        "difficulty": "Adversarial (감정 표현 vs 임상 객관 상태)"
    },
    {
        "id": "CASE-12",
        "name": "소아 장중첩증 의심 (주기적 복통 + 혈변)",
        "text": "14개월 아기가 며칠 전 감기 앓더니 오늘 아침부터 15분 간격으로 배를 쥐어짜며 자지러지게 울다가 언제 그랬냐는 듯 멀쩡히 잠들기를 반복해요. 방금 기저귀에 딸기잼 같은 피똥이 묻어 나왔어요.",
        "expected_level": 2,
        "expected_red_flag": True,
        "key_reason": "주기적 복통 + 무증상기 + 혈변(currant jelly stool) -> 급성 장중첩증 KTAS 2단계",
        "difficulty": "Very High (복합 비정형 소아 외과 질환)"
    },
    {
        "id": "CASE-13",
        "name": "급성 후두염(크룹) 천명음 및 호흡곤란",
        "text": "새벽 2시에 갑자기 개 짖는 듯한 컹컹 소리로 기침을 하더니 숨 들이마실 때마다 쇳소리가 나고 목소리가 아예 안 나와요. 침도 못 삼키고 흘리고 있어요.",
        "expected_level": 2,
        "expected_red_flag": True,
        "key_reason": "개 짖는 기침 + 안정 시 흡기 천명음(Stridor) + 연하곤란 -> 급성 상기도 폐쇄 의심 KTAS 2단계",
        "difficulty": "Very High"
    },
    {
        "id": "CASE-14",
        "name": "식품 유발 전신 아나필락시스",
        "text": "땅콩 과자를 먹고 15분 뒤 입술과 눈이 퉁퉁 붓고 온몸에 붉은 두드러기가 돋더니 숨소리가 쌕쌕거리고 구토를 시작했어요.",
        "expected_level": 1,
        "expected_red_flag": True,
        "key_reason": "알레르겐 노출 후 피부 점막 + 호흡기 + 소화기 2개 계통 이상 급속 침범 -> 아나필락시스 KTAS 1단계",
        "difficulty": "High"
    },
    {
        "id": "CASE-15",
        "name": "두부 외상 후 지연성 신경학적 결손",
        "text": "오후에 미끄럼틀에서 떨어져 머리를 부딪혔을 땐 괜찮다고 잘 놀았는데, 2시간 지난 지금 한쪽 팔을 잘 못 쓰고 발음이 혀가 꼬인 듯 어눌해지면서 자꾸 넘어져요.",
        "expected_level": 1,
        "expected_red_flag": True,
        "key_reason": "두부 외상 후 명료기(Lucid interval) 거친 편마비/구음장애 -> 급성 두개내 출혈 KTAS 1단계",
        "difficulty": "Extreme (시간차 지연성 위험)"
    }
]

def run_model_inference(
    client: genai.Client,
    model_name: str,
    user_text: str,
    top_symptoms: List[Dict[str, Any]],
    thinking_config: Optional[types.ThinkingConfig] = None
) -> Dict[str, Any]:
    compact_top3 = []
    for s in top_symptoms:
        compact_top3.append({
            "nacrs_code": s["code"],
            "symptom_name": s["name"],
            "category": s["cat"],
            "criteria": s["cons"]
        })
        
    system_instruction = f"""당신은 소아 KTAS 분류 번호 판정 시스템입니다.
긴 설명, 브리핑, 행동요령을 일절 작성하지 마십시오!
오직 환아의 증상에 가장 부합하는 KTAS 분류 번호(1~5단계)와 주증상 코드(NACRS), 핵심 임상 근거만 간결하게 반환하십시오.

[후보 주증상 및 세부 기준]:
{json.dumps(compact_top3, ensure_ascii=False)}

[비정형 문맥 완독 및 임상 보수주의 원칙]:
1. 문맥 완독 원칙: 문장 후반부의 전신 상태, 시간 경과, 잔존 위험 징후를 끝까지 완독하십시오.
2. 실신 + 발열/아파보임: 걷다가 갑자기 쓰러진 후 정신이 돌아왔더라도, '아직도 아파 보인다(Ill-appearing)'거나 '38.0℃ 이상의 발열'이 동반되면 단순 실신(3단계)이 아니라 무긴장 열성경련 후 상태, 심인성 실신, 급성 패혈증 의심으로 KTAS 2단계(긴급)로 판정하십시오.
3. 두부 외상 + 구토/처짐/지연성 마비: 초기에는 괜찮았더라도 반복 분수토나 신경학적 이상(마비, 어눌함) 발생 시 KTAS 1~2단계로 즉시 상향하십시오.
4. 생후 100일 미만 발열(38.0℃ 이상): 즉시 KTAS 2단계(긴급)로 판정하십시오.
5. 단순 미열(18개월 이상)이고 아이가 잘 먹고 잘 놀며 전신 상태가 완전히 양호한 경우에만 KTAS 4단계(준응급)로 판정하십시오.
6. triage_source 필드에는 모델명을 기입하십시오."""

    config_args = {
        "system_instruction": system_instruction,
        "response_mime_type": "application/json",
        "response_schema": KTASClassificationResult,
        "temperature": 0.1,
    }
    if thinking_config is not None:
        config_args["thinking_config"] = thinking_config

    start_t = time.perf_counter()
    response = client.models.generate_content(
        model=model_name,
        contents=f"보호자 호소 증상:\n\"{user_text}\"",
        config=types.GenerateContentConfig(**config_args)
    )
    elapsed_ms = (time.perf_counter() - start_t) * 1000

    parsed = json.loads(response.text)
    parsed["latency_ms"] = elapsed_ms
    return parsed

def main():
    api_key = settings.gemini_api_key
    client = genai.Client(api_key=api_key)

    print("=" * 90)
    print("🏥 [MoonlightCare] Gemini 3.8 Flash vs Frontier Pro/Argon 임상 Triage 비교 벤치마크")
    print("=" * 90)

    # 1. First, check Gemini 4 Argon availability
    print("\n🔍 [Step 1: Gemini 4 Argon 권한 및 가용성 진단]")
    argon_available = False
    try:
        test_r = client.models.generate_content(model="gemini-4-argon", contents="Ping")
        print("✅ gemini-4-argon 호출 성공!")
        argon_available = True
    except Exception as e:
        print(f"⚠️ gemini-4-argon 호출 불가 (예상된 정책 제한): {e}")

    # Models to test
    models_to_test = [
        {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash (Standard)", "thinking": None},
        {"id": "gemini-3.8-flash", "label": "Gemini 3.8 Flash (Thinking High)", "thinking": types.ThinkingConfig(thinking_budget=1024)},
        {"id": "gemini-3.1-pro-preview", "label": "Gemini 3.1 Pro (Frontier Deep Reasoning)", "thinking": None},
    ]
    if argon_available:
        models_to_test.append({"id": "gemini-4-argon", "label": "Gemini 4 Argon", "thinking": None})

    results_by_model: Dict[str, List[Dict[str, Any]]] = {m["label"]: [] for m in models_to_test}

    print(f"\n🚀 [Step 2: 15대 고난도 비정형 임상 시나리오 전수 추론 실행 (총 {len(BENCHMARK_CASES)}개 케이스)]")

    for case_idx, case in enumerate(BENCHMARK_CASES, 1):
        print(f"\n--------------------------------------------------------------------------------")
        print(f"[{case['id']}] {case['name']} (난이도: {case['difficulty']})")
        print(f"입력: \"{case['text']}\"")
        print(f"기준 정답: KTAS {case['expected_level']}단계 | Red Flag: {'YES' if case['expected_red_flag'] else 'NO'}")
        print(f"감별 포인트: {case['key_reason']}")

        top_symptoms = retrieve_top_k_symptoms(case["text"], k=4)

        for m_info in models_to_test:
            model_label = m_info["label"]
            model_id = m_info["id"]
            thinking = m_info["thinking"]

            try:
                res = run_model_inference(client, model_id, case["text"], top_symptoms, thinking_config=thinking)
                pred_level = res.get("ktas_level")
                pred_red = res.get("is_red_flag")
                nacrs = res.get("matched_nacrs_code")
                symptom_name = res.get("matched_symptom_name")
                rationale = res.get("clinical_rationale", "")
                lat = res.get("latency_ms", 0.0)

                level_match = (pred_level == case["expected_level"])
                red_match = (pred_red == case["expected_red_flag"])
                # Undertriage: expected red flag (L1-2), but predicted normal (L3-5)
                is_undertriage = (case["expected_red_flag"] and not pred_red)
                # Overtriage: expected normal (L3-5), but predicted red flag (L1-2)
                is_overtriage = (not case["expected_red_flag"] and pred_red)

                eval_entry = {
                    "case_id": case["id"],
                    "case_name": case["name"],
                    "difficulty": case["difficulty"],
                    "expected_level": case["expected_level"],
                    "predicted_level": pred_level,
                    "level_match": level_match,
                    "expected_red": case["expected_red_flag"],
                    "predicted_red": pred_red,
                    "red_match": red_match,
                    "is_undertriage": is_undertriage,
                    "is_overtriage": is_overtriage,
                    "nacrs": f"{nacrs} ({symptom_name})",
                    "rationale": rationale,
                    "latency_ms": lat
                }
                results_by_model[model_label].append(eval_entry)

                status_icon = "✅" if level_match else ("⚠️" if red_match else "❌")
                print(f"  [{model_label}]: {status_icon} KTAS {pred_level}단계 (Red: {pred_red}) | 소요: {lat:.1f}ms | NACRS: {nacrs} | 근거: {rationale[:45]}...")
            except Exception as e:
                print(f"  [{model_label}]: ❌ 실패 ({e})")
                results_by_model[model_label].append({
                    "case_id": case["id"],
                    "case_name": case["name"],
                    "error": str(e),
                    "level_match": False,
                    "red_match": False,
                    "is_undertriage": True,
                    "is_overtriage": False,
                    "latency_ms": 0.0
                })

    # Summary Statistics
    print("\n" + "=" * 90)
    print("📊 [Step 3: 모델별 종합 비교 분석표 및 성적표]")
    print("=" * 90)

    summary_rows = []
    for model_label, res_list in results_by_model.items():
        total = len(res_list)
        correct_levels = sum(1 for r in res_list if r.get("level_match"))
        correct_reds = sum(1 for r in res_list if r.get("red_match"))
        undertriage_count = sum(1 for r in res_list if r.get("is_undertriage"))
        overtriage_count = sum(1 for r in res_list if r.get("is_overtriage"))
        avg_lat = sum(r.get("latency_ms", 0.0) for r in res_list) / max(1, total)

        level_acc = (correct_levels / total) * 100
        red_sensitivity = ((total - undertriage_count) / total) * 100 if total > 0 else 0

        summary_rows.append({
            "model": model_label,
            "total": total,
            "level_acc": level_acc,
            "red_sensitivity": red_sensitivity,
            "undertriage": undertriage_count,
            "overtriage": overtriage_count,
            "avg_lat_ms": avg_lat,
            "results": res_list
        })

        print(f"[{model_label}]")
        print(f"  • KTAS 등급 정확도 (Level Accuracy): {correct_levels}/{total} ({level_acc:.1f}%)")
        print(f"  • Red Flag 민감도 (Red Flag Sensitivity): {(total - undertriage_count)}/{total} ({red_sensitivity:.1f}%)")
        print(f"  • 과소평가(치명적 Undertriage): {undertriage_count}건")
        print(f"  • 과대평가(Overtriage): {overtriage_count}건")
        print(f"  • 평균 지연시간 (Latency): {avg_lat:.1f}ms")
        print("-" * 60)

    # Save to JSON artifact
    output_path = PROJECT_ROOT / "tests" / "evals" / "model_comparison_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary_rows, f, ensure_ascii=False, indent=2)
    print(f"\n💾 결과 데이터 저장 완료: {output_path}")

if __name__ == "__main__":
    main()
