# -*- coding: utf-8 -*-
"""CLI script for manual on-demand execution of national dataset incremental delta sync.

Usage:
    python scripts/sync_national_datasets_delta.py [--force]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.national_dataset_sync_service import sync_national_datasets_with_diffing


def main():
    parser = argparse.ArgumentParser(description="24-Hour National Hospitals & Pharmacies Delta Sync CLI")
    parser.add_argument("--force", action="store_true", help="Force rewrite JSON files and JS bundles even if 0 diffs")
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🌙 [아이숨 i-Soom] 전국 달빛어린이병원 & 야간약국 24시간 증분 동기화(Delta Sync)")
    print("=" * 70)
    print(f"• 실행 모드: {'[강제 갱신 Force Mode]' if args.force else '[In-Memory Hash Diffing 모드]'}")
    print("• 공공데이터포털(E-Gen) API 실시간 조회 및 변경분 감지 중...\n")

    result = sync_national_datasets_with_diffing(force=args.force)

    status = result.get("status")
    print("-" * 70)
    if status == "UPDATED":
        print("✅ [동기화 성공 - 변경분 감지 및 갱신 완료]")
        print(f"• 메시지: {result.get('message')}")
        h_diff = result.get("hospitals_diff", {})
        p_diff = result.get("pharmacies_diff", {})
        print(f"• 🏥 달빛어린이병원: 신규 +{h_diff.get('added', 0)}개, 수정 ~{h_diff.get('modified', 0)}개, 삭제 -{h_diff.get('removed', 0)}개 (총 {h_diff.get('total', 0)}개소)")
        print(f"• 💊 심야약국: 신규 +{p_diff.get('added', 0)}개, 수정 ~{p_diff.get('modified', 0)}개, 삭제 -{p_diff.get('removed', 0)}개 (총 {p_diff.get('total', 0)}개소)")
        print("• 🔨 data/*.json 및 frontend/js/*.js 번들 자동 컴파일 완료")
    elif status == "UNCHANGED":
        print("⏭️ [동기화 완료 - 변경 사항 없음 (0ms Skip 유지)]")
        print(f"• 메시지: {result.get('message')}")
        print(f"• 현재 데이터셋: 달빛병원 {result.get('hospitals_total', 0)}개소, 심야약국 {result.get('pharmacies_total', 0)}개소 완벽 일치")
        print("• 🛡️ 불필요한 디스크 쓰기 및 브라우저 캐시 무효화 0회 달성")
    else:
        print("❌ [동기화 실패]")
        print(f"• 원인: {result.get('message')}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
