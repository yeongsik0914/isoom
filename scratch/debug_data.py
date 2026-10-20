import json
import re

print("=== 1. Checking frontend/js/hospital_details_data.js ===")
with open("frontend/js/hospital_details_data.js", "r", encoding="utf-8") as f:
    text = f.read()

# Check 24시열린의원 entries
pattern = re.compile(r'\{\s*"id":\s*"([^"]+)",\s*"name":\s*"([^"]+)",[^}]+?"address":\s*"([^"]+)"', re.DOTALL)
matches = pattern.findall(text)
print(f"Total hospitals in hospital_details_data.js regex match: {len(matches)}")
for m in matches:
    if "24시열린의원" in m[1]:
        print(f"ID: {m[0]} | Name: {m[1]} | Addr: {m[2]}")

print("\n=== 2. Checking data/hospital_details.json ===")
with open("data/hospital_details.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for h in data:
    if "24시열린의원" in h.get("name", ""):
        print(f"ID: {h.get('id')} | Name: {h.get('name')} | Addr: {h.get('address')} | Paired Pharmacy: {h.get('paired_pharmacy_name')} | Pharmacy Addr: {h.get('paired_pharmacy_address')}")

print("\n=== 3. Checking frontend/js/national_moonlight_hospitals_156.js ===")
with open("frontend/js/national_moonlight_hospitals_156.js", "r", encoding="utf-8") as f:
    js_text = f.read()
# Extract array
arr_str = js_text[js_text.find('['):js_text.rfind(']')+1]
hosp_156 = json.loads(arr_str)
for h in hosp_156:
    if "24시열린의원" in h.get("병원명", ""):
        print(f"기관코드: {h.get('기관코드')} | 병원명: {h.get('병원명')} | 주소: {h.get('주소')} | 전화: {h.get('대표전화')}")
