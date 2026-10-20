import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')

from app.services.facility_db_service import get_facility_detail

test_cases = [
    ("자양동 좌표 (광진구 근처)", 37.534, 127.069, "A1105874", "더클래식약국"),
    ("잠실동 좌표 (송파구 근처)", 37.508, 127.086, "A1117613", "매일여는온누리약국"),
    ("목동 좌표 (양천구 근처)", 37.527, 126.871, "A1116912", "매일여는약국"),
    ("상암동 좌표 (마포구 근처)", 37.579, 126.889, "A1119959", "매일여는약국"),
]

print("=== 4대 지점 좌표별 '24시열린의원' 동적 매칭 검증 ===")
all_pass = True
for name, lat, lon, expected_id, expected_pharm in test_cases:
    res = get_facility_detail('hospital', '24시열린의원', user_lat=lat, user_lon=lon)
    matched_id = res['id']
    matched_pharm = res['paired_pharmacy_name']
    sgg = res.get('sgg')
    is_ok = (matched_id == expected_id and matched_pharm == expected_pharm)
    status = "✅ PASS" if is_ok else "❌ FAIL"
    if not is_ok:
        all_pass = False
    print(f"{status} | {name} ➔ 매칭된 병원: {res['name']} ({sgg}, {res['dist_km']}km) | 연계약국: {matched_pharm}")

print("\n전체 검증 결과:", "모두 성공 (100% 정상)" if all_pass else "일부 실패")
