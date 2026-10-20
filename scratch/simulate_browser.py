import json

print("=== Simulating Browser User Flow ===")

# Step 1: User is at 자양동 (lat: 37.5345, lon: 127.0695)
user_lat = 37.5345
user_lon = 127.0695

with open("frontend/js/national_moonlight_hospitals_156.js", "r", encoding="utf-8") as f:
    text = f.read()

arr_str = text[text.find('['):text.rfind(']')+1]
hosp_156 = json.loads(arr_str)

# Calculate distance to all hospitals
import math
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Filter & sort hospitals as main.js does
hosp_with_dist = []
for h in hosp_156:
    h_lat = float(h.get("위도") or 0.0)
    h_lon = float(h.get("경도") or 0.0)
    dist = haversine(user_lat, user_lon, h_lat, h_lon)
    hosp_with_dist.append({
        "id": h.get("기관코드") or h.get("병원명"),
        "name": h.get("병원명"),
        "address": h.get("주소"),
        "dist": dist,
        "lat": h_lat,
        "lon": h_lon,
        "raw": h
    })

hosp_with_dist.sort(key=lambda x: x["dist"])

# Top 5 hospitals in index.html
print("Top 5 hospitals rendered in index.html:")
for i, h in enumerate(hosp_with_dist[:5]):
    print(f" {i+1}. {h['name']} ({h['id']}) - {h['address']} - {h['dist']:.2f}km")

top_card = hosp_with_dist[0]
print(f"\nUser clicks Top Card: {top_card['name']} (ID: {top_card['id']})")

# Step 2: main.js selectLiveFacilityCard is called!
# onclick="window.selectLiveFacilityCard('${facility.id || ''}', '${escapeSearchHtml(facility.name)}', '${facility.type}')"
# URL generated:
# targetUrl = `hospital_detail.html?name=${encodeURIComponent(top_card['name'])}&type=hospital&id=${encodeURIComponent(top_card['id'])}&from=...`
target_url = f"hospital_detail.html?name={top_card['name']}&type=hospital&id={top_card['id']}"
print(f"Target URL: {target_url}")

# Step 3: hospital_detail.html loads!
# Let's inspect hospital_detail.html logic:
with open("frontend/js/hospital_details_data.js", "r", encoding="utf-8") as f:
    hd_text = f.read()
hd_arr = json.loads(hd_text[hd_text.find('['):hd_text.rfind(']')+1])

qName = top_card['name']
qId = top_card['id']

print(f"\nhospital_detail.html resolves qName='{qName}', qId='{qId}':")

# 1. API fetch (/api/v1/emergency/facility-detail) - if backend running:
from app.services.facility_db_service import get_facility_detail
api_res = get_facility_detail(identifier=qId, facility_type="hospital", user_lat=user_lat, user_lon=user_lon)
print(" 1) Backend API result:")
if api_res:
    print(f"    Name: {api_res.get('name')}")
    print(f"    ID: {api_res.get('id')}")
    print(f"    Address: {api_res.get('address')}")
    print(f"    Paired Pharmacy: {api_res.get('paired_pharmacy_name')}")
    print(f"    Pharmacy Addr: {api_res.get('paired_pharmacy_address')}")
else:
    print("    None!")

# 2. Local JS fallback (window.HOSPITAL_DETAILS_DATA) - if backend NOT running:
print(" 2) Local JS Fallback (window.HOSPITAL_DETAILS_DATA):")
found = None
if qId:
    found = next((item for item in hd_arr if item.get("id") == qId), None)
if not found and qName:
    matches = [item for item in hd_arr if item.get("name") == qName]
    if len(matches) == 1:
        found = matches[0]
    elif len(matches) > 1:
        found = min(matches, key=lambda a: math.hypot((a.get("lat") or 0) - user_lat, (a.get("lon") or 0) - user_lon))

if found:
    print(f"    Found: {found.get('name')} (ID: {found.get('id')})")
    print(f"    Address: {found.get('address')}")
    print(f"    Paired Pharmacy: {found.get('paired_pharmacy_name')}")
    print(f"    Pharmacy Addr: {found.get('paired_pharmacy_address')}")
else:
    print("    Not found!")

# 3. SessionStorage fallback:
# Let's check what main.js saved to sessionStorage:
print(" 3) SessionStorage check in main.js:")
# In main.js:
# const hosp = (master.hospital && master.hospital.find(h => (facilityId ? (h.id === facilityId || h.기관코드 === facilityId) : h.name === facilityName)))
# sessionStorage.setItem('selected_hospital', JSON.stringify(hosp));
# But what did top_card have for pharmacy?
print("    Top card raw keys:", list(top_card['raw'].keys()))
print("    Does top card in 156 list have pharmacy field?", 'pharmacy' in top_card['raw'])
