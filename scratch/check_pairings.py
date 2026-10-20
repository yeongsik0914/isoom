import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/nationwide_pairings.json', 'r', encoding='utf-8') as f:
    pairings = json.load(f)

for p in pairings:
    if '24시열린의원' in p.get('병원명', ''):
        print(f"병원명: {p.get('병원명')} | 주소: {p.get('병원주소')}")
        print(f"약국명: {p.get('약국명')} | 주소: {p.get('약국주소')}")
        print(f"거리: {p.get('거리_m')}m")
        print("-" * 50)
