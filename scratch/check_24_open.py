import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/hospital_details.json', 'r', encoding='utf-8') as f:
    hospitals = json.load(f)

for h in hospitals:
    if '24시열린의원' in h.get('name', ''):
        print(f"ID: {h['id']}")
        print(f"이름: {h['name']} ({h.get('sgg')})")
        print(f"병원주소: {h.get('address')}")
        print(f"연계약국 ID: {h.get('paired_pharmacy_id')}")
        print(f"연계약국 이름: {h.get('paired_pharmacy_name')}")
        print(f"연계약국 주소: {h.get('paired_pharmacy_address')}")
        print("-" * 50)
