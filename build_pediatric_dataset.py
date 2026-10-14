# -*- coding: utf-8 -*-
"""Builder script to extract and assemble the dedicated Pediatric KTAS Dataset from PPTX and full bundle."""

import json
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

PPTX_PATH = r"e:\monnlight\2021_KTAS_guideline_ver1.6.pptx"
BUNDLE_PATH = r"e:\monnlight\data\ktas_full_bundle.json"
OUTPUT_PATH = r"e:\monnlight\data\ktas_pediatric_dataset.json"

NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}

def get_slide_tables(z, slide_idx):
    filename = f"ppt/slides/slide{slide_idx}.xml"
    if filename not in z.namelist():
        return []
    tree = ET.fromstring(z.read(filename))
    tables = []
    for tbl in tree.iterfind('.//a:tbl', NS):
        rows = []
        for tr in tbl.iterfind('.//a:tr', NS):
            cells = [''.join(tc.itertext()).strip() for tc in tr.iterfind('.//a:tc', NS)]
            rows.append(cells)
        tables.append(rows)
    return tables

def main():
    print("[1/4] Loading compiled KTAS bundle...")
    with open(BUNDLE_PATH, "r", encoding="utf-8") as f:
        bundle = json.load(f)

    # Filter pediatric symptoms
    ped_raw_symptoms = [s for s in bundle["symptoms"] if s.get("age") == "소아"]
    print(f"[2/4] Found {len(ped_raw_symptoms)} pediatric symptoms.")

    # Sort by slide number
    ped_raw_symptoms.sort(key=lambda x: x["slide"])

    # Standardize symptom objects
    formatted_symptoms = []
    for idx, s in enumerate(ped_raw_symptoms, 1):
        formatted_symptoms.append({
            "id": f"KTAS-PED-{idx:03d}",
            "slide_number": s["slide"],
            "age_group": "소아",
            "category": s["category"],
            "symptom_name": s["name"],
            "nacrs_code": s["code"],
            "levels_available": s["levels"],
            "secondary_considerations": [
                {"level": item["level"], "criteria": item["text"]}
                for item in s.get("secondary", [])
            ],
            "primary_considerations": [
                {"level": item["level"], "indicator": item["text"]}
                for item in s.get("primary", [])
            ],
            "clinical_notes": s.get("notes", [])
        })

    # Extract Pediatric Clinical Reference Tables from PPTX slides
    print("[3/4] Extracting pediatric clinical reference tables from PPTX slides 192~203 and 390~393...")
    with zipfile.ZipFile(PPTX_PATH) as z:
        # Slide 195: Consciousness / GCS
        t_195 = get_slide_tables(z, 195)
        mental_status_table = t_195[1] if len(t_195) > 1 else (t_195[0] if t_195 else [])

        # Slide 196: Hemodynamics / Circulation
        t_196 = get_slide_tables(z, 196)
        hemodynamic_table = t_196[1] if len(t_196) > 1 else (t_196[0] if t_196 else [])

        # Slide 197: Respiratory
        t_197 = get_slide_tables(z, 197)
        respiratory_table = t_197[1] if len(t_197) > 1 else (t_197[0] if t_197 else [])

        # Slide 198: Fever Guidelines
        t_198 = get_slide_tables(z, 198)
        fever_table = t_198[1] if len(t_198) > 1 else (t_198[0] if t_198 else [])

        # Slide 200: Bleeding Disorders
        t_200 = get_slide_tables(z, 200)
        bleeding_table = t_200[1] if len(t_200) > 1 else (t_200[0] if t_200 else [])

        # Slide 201: Trauma Mechanisms
        t_201 = get_slide_tables(z, 201)
        trauma_table = t_201[1] if len(t_201) > 1 else (t_201[0] if t_201 else [])

        # Slide 390: Respiratory Rate by Age
        t_390 = get_slide_tables(z, 390)
        resp_rate_age_table = t_390[0] if t_390 else []

        # Slide 391: Heart Rate by Age
        t_391 = get_slide_tables(z, 391)
        heart_rate_age_table = t_391[0] if t_391 else []

        # Slide 392: Body surface area by age (Burns)
        t_392 = get_slide_tables(z, 392)
        burn_area_table = t_392[0] if t_392 else []

        # Slide 393: Pediatric GCS
        t_393 = get_slide_tables(z, 393)
        ped_gcs_table = t_393[0] if t_393 else []

    # Format clinical reference sections
    first_considerations = {
        "fever_rules_slide198": {
            "title": "소아 체온 및 발열 중증도 판정 기준 (열 ≥38.0°C, 나이 < 15세)",
            "rules": [
                {"level": 2, "condition": "면역 저하 상태 (중성구감소증 의증, 장기이식, 항암 화학요법, 면역억제제 사용)"},
                {"level": 2, "condition": "<3개월(100일 미만) 영아에서 저체온(T<36°C) 또는 발열(T≥38°C) [MoonlightCare Rule 1]"},
                {"level": 2, "condition": "3-18개월이면서 T≥38°C 이고 아파 보임 (Toxic appearance)"},
                {"level": 3, "condition": "3-18개월이면서 T≥38°C 이고 건강해 보임"},
                {"level": 3, "condition": ">18개월이면서 T≥38°C 이고 아파 보임"},
                {"level": 4, "condition": ">18개월이면서 T≥38°C 이지만 건강해 보임"}
            ]
        },
        "mental_status_slide195": {
            "title": "소아 의식수준 및 GCS/AVPU 판정 기준",
            "rules": [
                {
                    "level": 1,
                    "state": "무의식 (U, GCS 3-8)",
                    "description": "반응 없음; 통증/큰 소음에 무의미한 움직임만 보임; 굴곡/신전 자세; 지속 발작; 기도 유지 불가 [MoonlightCare Rule 2 & 3]"
                },
                {
                    "level": 2,
                    "state": "의식수준 변화 (V/P, GCS 9-13)",
                    "description": "평소 의식수준에서 변화; 기면; 둔감; 착란; 지남력 상실; 달랠 수 없고 잘 먹지 않는 영아; 기도 유지는 가능함"
                },
                {
                    "level": 3,
                    "state": "명료 (A, GCS 14-15)",
                    "description": "정상 의식 상태 또는 경미한 보챔 후 진정"
                }
            ]
        },
        "respiratory_status_slide197": {
            "title": "소아 호흡 상태 및 산소포화도 기준",
            "rules": [
                {
                    "level": 1,
                    "severity": "중증 호흡곤란 (SpO2 < 90%)",
                    "description": "과도한 호흡 노력, 청색증, 심한 흉부함몰, 코 벌렁임, 그렁거림, 호흡음 소실, 상부기도 폐쇄, 기도유지 불가 [MoonlightCare Rule 4]"
                },
                {
                    "level": 2,
                    "severity": "중등도 호흡곤란 (SpO2 < 92%)",
                    "description": "증가된 호흡 노력, 안절부절못함, 불안, 빈호흡, 경도 흉부함몰, 코 벌렁임, 끊어진 문장 발화, 협착음"
                },
                {
                    "level": 3,
                    "severity": "경증 호흡곤란 (SpO2 92-94%)",
                    "description": "경미한 호흡곤란, 운동 시 숨참, 완전한 문장 발화 가능, 잦은 기침"
                }
            ]
        },
        "hemodynamic_status_slide196": {
            "title": "소아 혈역학적 상태 및 순환/탈수 기준",
            "rules": [
                {
                    "level": 1,
                    "status": "쇼크 (Shock)",
                    "description": "중증 종말장기 순환부전, 매우 창백함, 차가운 피부, 발한, 약한 맥박, 심각한 빈맥/서맥, 의식 저하, 패혈성 쇼크"
                },
                {
                    "level": 2,
                    "status": "혈역학적 장애 (Borderline Perfusion / 탈수)",
                    "description": "모세혈관 재충혈 시간 지연, 빈맥, 소변량 감소(8시간 이상 무뇨), 영유아 중증 탈수 [MoonlightCare Rule 5]"
                },
                {
                    "level": 3,
                    "status": "체액량 부족",
                    "description": "비정상 활력징후에 동반된 경미한 체액량 부족"
                }
            ]
        },
        "trauma_mechanisms_slide201": {
            "title": "소아 고위험성 사고기전",
            "high_risk_criteria": [
                "보행자/자전거 대 자동차 충돌 사고",
                "차량 밖으로 튕겨 나간 사고",
                "동승자 사망 사고",
                "3미터(소아 키의 2~3배) 이상 높이에서의 추락/낙상",
                "두부 외상 후 반복 구토, 분수토 또는 기면 동반 [MoonlightCare Rule 6]"
            ]
        }
    }

    # Format Vital Signs by Age tables
    vital_signs_by_age = {
        "respiratory_rate_by_age_table": {
            "headers": resp_rate_age_table[1] if len(resp_rate_age_table) > 1 else [],
            "rows": resp_rate_age_table[2:] if len(resp_rate_age_table) > 2 else []
        },
        "heart_rate_by_age_table": {
            "headers": heart_rate_age_table[1] if len(heart_rate_age_table) > 1 else [],
            "rows": heart_rate_age_table[2:] if len(heart_rate_age_table) > 2 else []
        },
        "body_surface_burn_percentage": {
            "headers": burn_area_table[0] if len(burn_area_table) > 0 else [],
            "rows": burn_area_table[1:] if len(burn_area_table) > 1 else []
        }
    }

    # MoonlightCare 7 Red Flag definitions and mapping
    moonlightcare_7_red_flags = [
        {
            "rule_id": "RULE-1",
            "name": "생후 100일(3개월) 미만 영아 38.0℃ 이상 고열",
            "ktas_level": 2,
            "clinical_reason": "혈액-뇌 장벽(BBB) 미성숙으로 인한 신생아 패혈증, 세균성 뇌수막염, 요로감염 등 중증 세균성 감염(SBI) 위험",
            "immediate_action": "119 호출 또는 대학병원/소아전문응급의료센터 직행, 해열제 임의 투약 금지",
            "matched_symptoms": ["열", "발열", "감염 가능성 확인"]
        },
        {
            "rule_id": "RULE-2",
            "name": "소아 경련 / 열성경련 / 사지 경직 / 눈 돌아감",
            "ktas_level": 1,
            "clinical_reason": "5분 이상 지속 시 뇌 손상 위험(뇌전증 지속상태) 및 구토물 흡인 질식 위험",
            "immediate_action": "119 신고, 고개 옆으로 돌려 기도 확보, 입안에 물건 넣지 않기, 경련 시간 측정",
            "matched_symptoms": ["발작", "열성경련", "떨림(Tremor)"]
        },
        {
            "rule_id": "RULE-3",
            "name": "중증 의식 저하 / 극심한 처짐(기면) / 무반응",
            "ktas_level": 1,
            "clinical_reason": "신경계/대사 응급 질환(뇌염, 뇌수막염, 두개내 출혈, 저혈당 쇼크)",
            "immediate_action": "119 즉시 호출, 어깨 가볍게 두드리며 호흡 확인, 음식물/수분 강제 섭취 금지",
            "matched_symptoms": ["의식수준의 변화", "착란"]
        },
        {
            "rule_id": "RULE-4",
            "name": "중증 호흡곤란 및 청색증 (흉벽 함몰, 비익 호흡)",
            "ktas_level": 1,
            "clinical_reason": "급성 호흡 부전 및 저산소성 뇌 손상 직전 위급 상태 (SpO2 < 90%)",
            "immediate_action": "119 구조 요청, 조이는 옷/기저귀 풀고 상체 세워 기도 유지",
            "matched_symptoms": ["숨참", "호흡 정지", "천명음", "과다호흡증후군"]
        },
        {
            "rule_id": "RULE-5",
            "name": "중증 탈수 (8시간 이상 무뇨, 눈물 없음, 입술 마름)",
            "ktas_level": 2,
            "clinical_reason": "급성 신손상(AKI) 및 순환기 저혈량성 쇼크 징후",
            "immediate_action": "정맥 수액 처치 가능한 응급실 방문, 억지로 물 먹이지 말기",
            "matched_symptoms": ["설사", "구토 / 구역질", "소변 배출장애", "핍뇨증"]
        },
        {
            "rule_id": "RULE-6",
            "name": "두부 외상 후 반복 구토, 기면, 의식 저하",
            "ktas_level": 2,
            "clinical_reason": "두개내 출혈(경막하혈종), 뇌압 상승(IICP) 위험 징후",
            "immediate_action": "소아 CT 촬영 가능 응급의료센터 이송, 목 무리하게 꺾지 않기",
            "matched_symptoms": ["두부 손상", "안면 외상"]
        },
        {
            "rule_id": "RULE-7",
            "name": "담즙성 구토 (초록색 구토) 및 분수토",
            "ktas_level": 2,
            "clinical_reason": "장폐색, 장중첩증, 중장 염전증 등 응급 소아 외과 수술 적응증",
            "immediate_action": "즉시 금식(물/음식물 일체 중단) 후 종합병원 응급실 직행",
            "matched_symptoms": ["구토 / 구역질", "복통"]
        }
    ]

    # Categories breakdown
    categories_summary = {}
    for sym in formatted_symptoms:
        cat = sym["category"]
        categories_summary[cat] = categories_summary.get(cat, 0) + 1

    pediatric_dataset = {
        "metadata": {
            "title": "2021 KTAS 소아 응급환자 분류도구 임상 데이터셋 (Pediatric KTAS Dataset)",
            "version": "1.6.0 (2021년 최신 개정판)",
            "target_population": "소아청소년 (신생아~만 15세 미만)",
            "total_symptoms_count": len(formatted_symptoms),
            "categories_count": len(categories_summary),
            "source_documents": [
                "2021_KTAS_guideline_ver1.6.pptx (대한응급의학회 / 국립중앙의료원 중앙응급의료센터)",
                "2021년 KTAS 분류도구 PPT 사용방법.pdf",
                "보건복지부 고시 한국 응급환자 중증도 분류기준"
            ],
            "linked_project": "MoonlightCare (야간 소아 응급실 스마트 2-트랙 지능형 라우팅 시스템)",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "moonlightcare_7_red_flags": moonlightcare_7_red_flags,
        "categories_summary": categories_summary,
        "first_considerations": first_considerations,
        "vital_signs_by_age": vital_signs_by_age,
        "symptoms": formatted_symptoms
    }

    # Save to JSON
    print(f"[4/4] Saving to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(pediatric_dataset, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"✅ Successfully created {OUTPUT_PATH} (Size: {file_size:,} bytes, {len(formatted_symptoms)} symptoms)")

if __name__ == "__main__":
    main()
