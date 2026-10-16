import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. input.html에서 체온/나이를 건드리지 않고 '아이가 갑자기 구토를 여러 번 해요' 제출 시 생성되는 정확한 페이로드
chat_payload = {
    "user_message": "나이는 미입력(모름) 상태이고 체온은 미측정(모름) 상태입니다. 주요 증상: 아이가 갑자기 구토를 여러 번 해요, 투약/동반: 해열제 미복용",
    "user_lat": 37.5133,
    "user_lon": 127.1001,
    "user_address": None,
    "force_matching": True,
    "stream": False,
    "age_months": None,
    "temperature": None,
    "patient_vitals": {
        "age": "나이 미입력(모름)",
        "temp": "체온 미측정(모름)",
        "symptom": "아이가 갑자기 구토를 여러 번 해요",
        "companion": "해열제 미복용"
    }
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/chat",
    data=json.dumps(chat_payload, ensure_ascii=False).encode("utf-8"),
    headers={"Content-Type": "application/json; charset=utf-8"}
)

with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

print("=" * 60)
print(" MoonLightCare 백엔드 KTAS 및 바이탈 모름 E2E 파이프라인 검증")
print("=" * 60)
print(f"HTTP Status: {resp.status}")
print(f"KTAS Level: KTAS {data.get('ktas_level')}단계 ({data.get('ktas_level_name')})")
print(f"환아 월령 (age_months): {data.get('age_months')} (None = 모름 보존)")
print(f"환아 체온 (temperature): {data.get('temperature')} (None = 모름 보존)")
print(f"추출 증상 (symptoms): {data.get('symptoms')}")
print(f"소아 임상 감별 소견 (clinical_rationale):\n-> {data.get('clinical_rationale')}")
print(f"추천 달빛병원 수: {len(data.get('hospitals', []))}개")
print(f"추천 안심약국 수: {len(data.get('pharmacies', []))}개")
print("=" * 60)

# 2. result.html 바인딩 검증
age_display = "나이 미입력(모름)" if (data.get('age_months') is None) else f"{data.get('age_months')}개월"
temp_display = "체온 미측정(모름)" if (data.get('temperature') is None) else f"{data.get('temperature')}℃"
ktas_title = f"KTAS {data.get('ktas_level')}단계 ({data.get('ktas_level_name')})"
ktas_desc = f"소아 임상 감별 소견: {data.get('clinical_rationale')}"

print("[result.html DOM 바인딩 시뮬레이션]")
print(f"1. 바이탈 칩 - 나이 (#vital-age-text): '{age_display}'")
print(f"2. 바이탈 칩 - 체온 (#vital-temp-text): '{temp_display}'")
print(f"3. 바이탈 칩 - 증상 (#vital-symptom-text): '#{', '.join(data.get('symptoms', []))}'")
print(f"4. KTAS 등급 타이틀 (#ktas-grade-text): '{ktas_title}'")
print(f"5. KTAS 상세 설명 (#ktas-desc-detail): '{ktas_desc[:80]}...'")
print("=" * 60)
