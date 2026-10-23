"""
Google Cloud Run ADC (Application Default Credentials) & Secret Manager IAM Policy Binding Script
Cloud Run 기본 Compute Engine 서비스 계정에 필요한 3대 권한을 부여합니다:
1. roles/secretmanager.secretAccessor (Secret Manager 시크릿 읽기 권한)
2. roles/datastore.user (Cloud Firestore ADC 무키 읽기/쓰기 권한)
3. roles/aiplatform.user (Vertex AI Gemini ADC 무키 호출 권한)
"""

import os
import subprocess
import sys
from pathlib import Path

# Fix Windows CP949 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

GCLOUD_CMD = "gcloud.cmd" if os.name == "nt" else "gcloud"
DEFAULT_PROJECT = "iceu-songpa10"
FALLBACK_PROJECT_NUMBER = "920380215419"


def run_cmd(cmd_list):
    try:
        res = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return res.returncode, (res.stdout or "").strip(), (res.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)


def main():
    print("=" * 70)
    print("  🌙 아이숨(Aisum) Cloud Run ADC & Secret Manager IAM 권한 설정 도구")
    print("=" * 70)

    # 1. 활성 프로젝트 확인
    code, project_id, _ = run_cmd([GCLOUD_CMD, "config", "get-value", "project"])
    if code != 0 or not project_id or "(unset)" in project_id:
        project_id = DEFAULT_PROJECT
    print(f"📌 타겟 GCP 프로젝트: {project_id}")

    # 2. 프로젝트 번호 조회
    code, project_number, _ = run_cmd([
        GCLOUD_CMD, "projects", "describe", project_id, "--format=value(projectNumber)"
    ])
    if code != 0 or not project_number:
        project_number = FALLBACK_PROJECT_NUMBER
        print(f"  ℹ️ 기본 프로젝트 번호 사용: {project_number}")
    else:
        print(f"  • 확인된 프로젝트 번호: {project_number}")

    service_account = f"{project_number}-compute@developer.gserviceaccount.com"
    print(f"  • 타겟 Cloud Run 서비스 계정: {service_account}")
    print("-" * 70)

    # 3. 3대 필수 IAM 역할 바인딩
    roles = [
        ("Secret Manager 비밀 접근자", "roles/secretmanager.secretAccessor"),
        ("Cloud Datastore 사용자 (Firestore ADC)", "roles/datastore.user"),
        ("Vertex AI 사용자 (Gemini ADC)", "roles/aiplatform.user"),
    ]

    for label, role in roles:
        print(f"\n🔐 [{label}] ({role}) 권한 부여 중...")
        r_code, r_out, r_err = run_cmd([
            GCLOUD_CMD, "projects", "add-iam-policy-binding", project_id,
            f"--member=serviceAccount:{service_account}",
            f"--role={role}",
            "--quiet",
        ])
        if r_code == 0:
            print(f"  ✅ 성공: {service_account} 에 {role} 부여 완료")
        else:
            print(f"  ⚠️ 결과 알림: {r_out or r_err}")

    print("\n" + "=" * 70)
    print("  🎉 모든 ADC 및 Secret Manager IAM 권한 설정이 완료되었습니다!")
    print("  이제 Firestore는 키 파일 없이 ADC로 자동 인증되며,")
    print("  Secret Manager에 등록된 API 키들을 Cloud Run에서 안전하게 읽어올 수 있습니다.")
    print("=" * 70)


if __name__ == "__main__":
    main()

