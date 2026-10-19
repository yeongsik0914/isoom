"""
Google Cloud Run Deployment Script for Aisum
Secret Manager에 등록된 비밀 키들을 연동하여 Cloud Run에 컨테이너를 빌드 및 배포합니다.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Fix Windows CP949 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROJECT_ID = "iceu-songpa09"
SERVICE_NAME = "isoom-service"
REGION = "asia-northeast3"

def main():
    print("=" * 75)
    print("  🚀 아이숨 (Aisum) - Google Cloud Run 프로덕션 배포 파이프라인")
    print("=" * 75)
    print(f"  • 대상 GCP 프로젝트: {PROJECT_ID}")
    print(f"  • 배포 서비스 이름: {SERVICE_NAME}")
    print(f"  • 배포 리전: {REGION} (서울)")

    image_tag = f"gcr.io/{PROJECT_ID}/{SERVICE_NAME}:latest"

    # 1. Cloud Build 컨테이너 빌드 & GCR 푸시
    build_cmd = [
        "gcloud.cmd", "builds", "submit",
        f"--tag={image_tag}",
        f"--project={PROJECT_ID}",
    ]

    print("\n📦 [1/2] Cloud Build 컨테이너 이미지 빌드 및 GCR 푸시 시작...")
    print(f"  • 대상 이미지: {image_tag}")
    print("-" * 75)

    start_time = time.time()
    build_proc = subprocess.run(build_cmd, cwd=str(PROJECT_ROOT))
    if build_proc.returncode != 0:
        print(f"\n❌ [ERROR] Cloud Build 실패 (Exit Code: {build_proc.returncode})")
        sys.exit(build_proc.returncode)

    # 2. Secret Manager 바인딩 구성
    secret_bindings = [
        "DATA_GO_API_KEY=DATA_GO_API_KEY:latest",
        "DATA_GO_KR_API_KEY=DATA_GO_API_KEY:latest",
        "GEMINI_API_KEY=GEMINI_API_KEY:latest",
        "KAKAO_REST_API_KEY=KAKAO_REST_API_KEY:latest",
        "FIRESTORE_DATABASE_ID=FIRESTORE_DATABASE_ID:latest",
        "FIREBASE_KEY_JSON=FIREBASE_KEY_JSON:latest",
    ]
    secrets_arg = ",".join(secret_bindings)

    env_vars = [
        "APP_ENV=production",
        "LOG_LEVEL=INFO",
    ]
    env_vars_arg = ",".join(env_vars)

    deploy_cmd = [
        "gcloud.cmd", "run", "deploy", SERVICE_NAME,
        f"--project={PROJECT_ID}",
        f"--image={image_tag}",
        f"--region={REGION}",
        "--platform=managed",
        "--allow-unauthenticated",
        "--port=8080",
        "--memory=1Gi",
        "--cpu=1",
        f"--set-secrets={secrets_arg}",
        f"--set-env-vars={env_vars_arg}",
    ]

    print("\n🚀 [2/2] Google Cloud Run 프로덕션 배포 및 시크릿 연동...")
    print("-" * 75)

    proc = subprocess.Popen(
        deploy_cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    deployed_url = None
    for line in iter(proc.stdout.readline, ''):
        print(line, end='', flush=True)
        if "https://" in line and ".run.app" in line:
            parts = [w for w in line.strip().split() if w.startswith("https://") and ".run.app" in w]
            if parts:
                deployed_url = parts[0]

    proc.stdout.close()
    proc.wait()
    elapsed = time.time() - start_time

    if proc.returncode != 0:
        print(f"\n❌ [ERROR] Cloud Run 배포 실패 (Exit Code: {proc.returncode})")
        sys.exit(proc.returncode)

    print("\n" + "=" * 75)
    print(f"  🎉 Cloud Run 배포 성공! (총 소요 시간: {elapsed:.1f}초)")
    if deployed_url:
        print(f"  🌐 라이브 프로덕션 서비스 URL: {deployed_url}")
    print("=" * 75)

if __name__ == "__main__":
    main()

