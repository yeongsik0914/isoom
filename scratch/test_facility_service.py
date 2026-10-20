import sys
sys.stdout.reconfigure(encoding='utf-8')

from app.services.facility_db_service import get_facility_detail

# 자양동 좌표: 37.534, 127.069
jayang_lat, jayang_lon = 37.534, 127.069

# 1. Search by name with Jayang-dong coords
result = get_facility_detail('hospital', '24시열린의원', user_lat=jayang_lat, user_lon=jayang_lon)
if result:
    print("=== 자양동 좌표로 '24시열린의원' 이름 조회 결과 ===")
    print(f"병원 ID: {result['id']}")
    print(f"병원명: {result['name']} ({result.get('sgg')})")
    print(f"병원 주소: {result.get('address')}")
    print(f"계산된 거리: {result.get('dist_km')}km")
    print(f"연계 약국: {result.get('paired_pharmacy_name')}")
    print(f"연계 약국 주소: {result.get('paired_pharmacy_address')}")
else:
    print("조회 실패")
