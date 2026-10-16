"""Builds frontend JS bundles for national moonlight hospitals and night pharmacies."""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
JS_DIR = PROJECT_ROOT / "frontend" / "js"

# 1. Moonlight Hospitals 156
with open(DATA_DIR / "national_moonlight_hospitals_156.json", "r", encoding="utf-8") as f:
    hospitals = json.load(f)

hosp_js_content = (
    "// 🌙 전국 17개 시·도 156개 공식 지정 달빛어린이병원 전수 마스터 데이터셋\n"
    "// 공공데이터포털 국립중앙의료원(NMC) 오픈 API 실시간 수집·정제 원천\n"
    "window.NATIONAL_MOONLIGHT_HOSPITALS_DATA = "
    + json.dumps(hospitals, ensure_ascii=False, indent=2)
    + ";\n"
)

hosp_out = JS_DIR / "national_moonlight_hospitals_156.js"
with open(hosp_out, "w", encoding="utf-8") as f:
    f.write(hosp_js_content)
print(f"[OK] Created {hosp_out} ({len(hospitals)} hospitals)")

# 2. Night Pharmacies 2028
with open(DATA_DIR / "national_night_pharmacies_2028.json", "r", encoding="utf-8") as f:
    pharmacies = json.load(f)

pharm_js_content = (
    "// 💊 전국 2,028개 야간·심야·공휴일 운영 약국 전수 마스터 데이터셋\n"
    "// 공공데이터포털 국립중앙의료원(NMC) 오픈 API 실시간 수집·정제 원천\n"
    "window.NATIONAL_NIGHT_PHARMACIES_DATA = "
    + json.dumps(pharmacies, ensure_ascii=False, indent=2)
    + ";\n"
    "window.PUBLIC_NIGHT_PHARMACIES_DATA = window.NATIONAL_NIGHT_PHARMACIES_DATA;\n"
)

pharm_out = JS_DIR / "national_night_pharmacies_2028.js"
with open(pharm_out, "w", encoding="utf-8") as f:
    f.write(pharm_js_content)
print(f"[OK] Created {pharm_out} ({len(pharmacies)} pharmacies)")

# Also synchronize public_night_pharmacies.js for backward-compatibility
legacy_pharm_out = JS_DIR / "public_night_pharmacies.js"
with open(legacy_pharm_out, "w", encoding="utf-8") as f:
    f.write(pharm_js_content)
print(f"[OK] Synchronized {legacy_pharm_out}")
