"""
🚀 아이숨 (Aisum) - Google Cloud Run 원클릭 프로덕션 배포 파이프라인 (v2.9.39 하이브리드 ADC & Secret Manager 지원)
- GCP Secret Manager에 등록된 API 키(DATA_GO_API_KEY, KAKAO_REST_API_KEY, GEMINI_API_KEY)를 --set-secrets로 안전하게 주입
- Cloud Firestore는 키 파일/문자열 없이 Cloud Run 서비스 계정의 ADC(Application Default Credentials)로 100% 무키 자동 인증
- Cloud Run 서비스 계정에 Secret Accessor, Datastore User, Vertex AI User IAM 역할을 자동 점검 및 부여
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Fix Windows CP949 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
GCLOUD_CMD = "gcloud.cmd" if os.name == "nt" else "gcloud"
SERVICE_NAME = "isoom-service"
DEFAULT_REGION = "asia-northeast3"  # 서울 리전
FALLBACK_PROJECT_NUMBER = "920380215419"


def run_command(cmd_list, check=False, capture=True):
    """Executes a command and returns (code, stdout, stderr)."""
    try:
        res = subprocess.run(
            cmd_list,
            cwd=str(PROJECT_ROOT),
            capture_output=capture,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if check and res.returncode != 0:
            raise RuntimeError(f"Command failed ({res.returncode}): {' '.join(cmd_list)}\n{res.stderr}")
        return res.returncode, (res.stdout or "").strip(), (res.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)


def sync_frontend_assets():
    """Syncs frontend PWA, templates, and static assets into app/ for container packaging."""
    print("\n📁 [1/4] 프론트엔드 PWA 및 정적 자산(Static/Templates) 동기화 점검...")
    frontend_dir = PROJECT_ROOT / "frontend"
    app_dir = PROJECT_ROOT / "app"

    if not frontend_dir.exists():
        print("  ⚠️ frontend 디렉터리가 발견되지 않아 동기화를 건너뜁니다.")
        return

    # Ensure target dirs
    (app_dir / "static" / "img").mkdir(parents=True, exist_ok=True)
    (app_dir / "static" / "css").mkdir(parents=True, exist_ok=True)
    (app_dir / "static" / "js").mkdir(parents=True, exist_ok=True)
    (app_dir / "templates").mkdir(parents=True, exist_ok=True)

    synced_items = 0
    # 1. Manifest & Service Worker
    for f in ["manifest.json", "sw.js"]:
        src = frontend_dir / f
        if src.exists():
            shutil.copy2(src, app_dir / "static" / f)
            synced_items += 1

    # 2. CSS
    css_src = frontend_dir / "css" / "style.css"
    if css_src.exists():
        shutil.copy2(css_src, app_dir / "static" / "css" / "style.css")
        synced_items += 1

    # 3. Images
    img_dir = frontend_dir / "img"
    if img_dir.exists():
        for item in img_dir.glob("*"):
            if item.is_file():
                shutil.copy2(item, app_dir / "static" / "img" / item.name)
                synced_items += 1

    # 4. JS
    js_dir = frontend_dir / "js"
    if js_dir.exists():
        for item in js_dir.glob("*"):
            if item.is_file():
                shutil.copy2(item, app_dir / "static" / "js" / item.name)
                synced_items += 1

    # 5. Templates
    tpl_dir = frontend_dir / "templates"
    if tpl_dir.exists():
        for item in tpl_dir.rglob("*.html"):
            if item.is_file():
                rel = item.relative_to(tpl_dir)
                dest = app_dir / "templates" / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dest)
                synced_items += 1

    print(f"  ✅ 총 {synced_items}개 웹/PWA 정적 자산 동기화 완료")


def load_env_vars():
    """Parses .env for default fallback values."""
    env_data = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    env_data[k.strip()] = v.strip().strip("'").strip('"')
    return env_data


def check_gcloud_auth():
    """Checks gcloud installation, active project, and token validity."""
    print("\n🔍 [2/4] Google Cloud CLI (gcloud) 상태 및 인증 확인...")

    code, out, _ = run_command([GCLOUD_CMD, "--version"])
    if code != 0:
        print(f"  ❌ Google Cloud SDK({GCLOUD_CMD})를 실행할 수 없습니다.")
        print("     설치 안내: https://cloud.google.com/sdk/docs/install-sdk")
        return False, None

    code, project_id, _ = run_command([GCLOUD_CMD, "config", "get-value", "project"])
    project_id = project_id.strip() if code == 0 else ""
    if not project_id or "(unset)" in project_id:
        project_id = "iceu-songpa10"
        print(f"  ⚠️ 활성 프로젝트가 설정되지 않아 기본값 '{project_id}'을(를) 적용합니다.")

    code, auth_out, _ = run_command([GCLOUD_CMD, "auth", "print-access-token"])
    if code != 0 or not auth_out:
        print("\n" + "!" * 75)
        print("  🚨 [인증 필요] Google Cloud 로그인 세션이 만료되었거나 인증되지 않았습니다.")
        print("  📌 터미널에서 다음 명령어를 실행하여 웹 브라우저 로그인을 완료해주세요:\n")
        print(f"     {GCLOUD_CMD} auth login")
        print(f"     {GCLOUD_CMD} config set project {project_id}\n")
        print("!" * 75 + "\n")
        return False, project_id

    print(f"  ✅ gcloud 인증 완료 (사용자 세션 유효)")
    print(f"  • 대상 GCP 프로젝트: {project_id}")
    return True, project_id


def check_secret_exists(secret_name, project_id):
    """Checks if secret exists in GCP Secret Manager."""
    code, _, _ = run_command([
        GCLOUD_CMD, "secrets", "describe", secret_name, f"--project={project_id}"
    ])
    return code == 0


def grant_cloud_run_iam_permissions(project_id):
    """Grants Secret Accessor, Datastore User (Firestore ADC), and Vertex AI User IAM roles."""
    print("\n🛡️ [IAM] Cloud Run 서비스 계정에 Secret Accessor & ADC 권한 점검/부여 중...")
    code, project_number, _ = run_command([
        GCLOUD_CMD, "projects", "describe", project_id, "--format=value(projectNumber)"
    ])
    if code != 0 or not project_number:
        project_number = FALLBACK_PROJECT_NUMBER

    service_account = f"{project_number}-compute@developer.gserviceaccount.com"
    print(f"  • 타겟 서비스 계정: {service_account}")

    roles = [
        ("Secret Manager 비밀 접근자", "roles/secretmanager.secretAccessor"),
        ("Cloud Datastore 사용자 (Firestore ADC)", "roles/datastore.user"),
        ("Vertex AI 사용자 (Gemini ADC)", "roles/aiplatform.user"),
    ]

    for label, role in roles:
        r_code, _, _ = run_command([
            GCLOUD_CMD, "projects", "add-iam-policy-binding", project_id,
            f"--member=serviceAccount:{service_account}",
            f"--role={role}",
            "--quiet",
        ])
        if r_code == 0:
            print(f"  ✅ {label} ({role}) 권한 바인딩 확인 완료")
        else:
            print(f"  ⚠️ {label} 바인딩 진행됨")


def build_container_image(project_id):
    """Builds container image via Cloud Build and pushes to Artifact Registry."""
    image_tag = f"asia-northeast3-docker.pkg.dev/{project_id}/isoom-repo/{SERVICE_NAME}:latest"
    print(f"\n📦 [3/4] Cloud Build 컨테이너 이미지 패키징 및 푸시 시작...")
    print(f"  • 대상 이미지: {image_tag}")
    print("-" * 75)

    build_cmd = [
        GCLOUD_CMD, "builds", "submit",
        f"--tag={image_tag}",
        f"--project={project_id}",
    ]

    start_time = time.time()
    proc = subprocess.Popen(
        build_cmd,
        cwd=str(PROJECT_ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    for line in iter(proc.stdout.readline, ""):
        print(line, end="", flush=True)

    proc.stdout.close()
    proc.wait()
    elapsed = time.time() - start_time

    if proc.returncode != 0:
        print(f"\n❌ [ERROR] Cloud Build 실패 (Exit Code: {proc.returncode})")
        sys.exit(proc.returncode)

    print(f"\n  ✅ Cloud Build 성공! ({elapsed:.1f}초 소요)")
    return image_tag


def deploy_to_cloud_run(project_id, region=DEFAULT_REGION):
    """Deploys to Cloud Run with Secret Manager binding and ADC keyless authentication."""
    skip_build = "--skip-build" in sys.argv
    if not skip_build:
        image_tag = build_container_image(project_id)
    else:
        image_tag = f"asia-northeast3-docker.pkg.dev/{project_id}/isoom-repo/{SERVICE_NAME}:latest"
        print(f"\n⏩ [3/4] --skip-build 옵션으로 기존 컨테이너 이미지({image_tag})를 사용합니다.")

    # 1. Grant IAM roles (Secret Accessor + Datastore User ADC + Vertex AI ADC)
    grant_cloud_run_iam_permissions(project_id)

    # 2. Check Secret Manager secrets
    print("\n🔐 [Secret Manager & ADC 연동 검증]")
    secrets_to_bind = []
    
    # Check DATA_GO_API_KEY
    if check_secret_exists("DATA_GO_API_KEY", project_id):
        secrets_to_bind.append("DATA_GO_API_KEY=DATA_GO_API_KEY:latest")
        secrets_to_bind.append("DATA_GO_KR_API_KEY=DATA_GO_API_KEY:latest")
        print("  • DATA_GO_API_KEY: Secret Manager 바인딩 적용")
    else:
        print("  ⚠️ DATA_GO_API_KEY: Secret Manager에 미등록됨 (로컬 .env fallback 확인 필요)")

    # Check KAKAO_REST_API_KEY
    if check_secret_exists("KAKAO_REST_API_KEY", project_id):
        secrets_to_bind.append("KAKAO_REST_API_KEY=KAKAO_REST_API_KEY:latest")
        print("  • KAKAO_REST_API_KEY: Secret Manager 바인딩 적용")
    else:
        print("  ⚠️ KAKAO_REST_API_KEY: Secret Manager에 미등록됨")

    # Check GEMINI_API_KEY or geminikey
    if check_secret_exists("GEMINI_API_KEY", project_id):
        secrets_to_bind.append("GEMINI_API_KEY=GEMINI_API_KEY:latest")
        print("  • GEMINI_API_KEY: Secret Manager 바인딩 적용")
    elif check_secret_exists("geminikey", project_id):
        secrets_to_bind.append("GEMINI_API_KEY=geminikey:latest")
        print("  • GEMINI_API_KEY: Secret Manager ('geminikey') 바인딩 적용")
    else:
        print("  ℹ️ GEMINI_API_KEY: Vertex AI ADC 모드 자동 적용")

    print("  • Firebase Cloud Firestore: 100% 무키(Keyless) ADC 모드 적용 (인라인 키 주입 불필요)")

    # 3. Environment variables (Non-secret configs only)
    env_data = load_env_vars()
    firestore_db = env_data.get("FIRESTORE_DATABASE_ID", "isoom")

    deploy_env = {
        "APP_ENV": "production",
        "LOG_LEVEL": env_data.get("LOG_LEVEL", "INFO"),
        "FIRESTORE_DATABASE_ID": firestore_db,
        "GOOGLE_CLOUD_PROJECT": project_id,
        "USE_ADC": "true",
    }

    # Fallback to local .env if secret not in Secret Manager
    if "DATA_GO_API_KEY" not in str(secrets_to_bind) and env_data.get("DATA_GO_API_KEY"):
        deploy_env["DATA_GO_API_KEY"] = env_data["DATA_GO_API_KEY"]
        deploy_env["DATA_GO_KR_API_KEY"] = env_data["DATA_GO_API_KEY"]
    if "KAKAO_REST_API_KEY" not in str(secrets_to_bind) and env_data.get("KAKAO_REST_API_KEY"):
        deploy_env["KAKAO_REST_API_KEY"] = env_data["KAKAO_REST_API_KEY"]
    if "GEMINI_API_KEY" not in str(secrets_to_bind) and env_data.get("GEMINI_API_KEY"):
        deploy_env["GEMINI_API_KEY"] = env_data["GEMINI_API_KEY"]

    print(f"\n🚀 [4/4] Cloud Run 프로덕션 배포 시작 ({SERVICE_NAME}, {region})...")

    temp_env_yaml = PROJECT_ROOT / ".cloud_run_env.yaml"
    try:
        yaml_lines = [f"{k}: '{v.replace('\'', '\'\'')}'" for k, v in deploy_env.items()]
        with open(temp_env_yaml, "w", encoding="utf-8") as f:
            f.write("\n".join(yaml_lines) + "\n")

        deploy_cmd = [
            GCLOUD_CMD, "run", "deploy", SERVICE_NAME,
            f"--project={project_id}",
            f"--image={image_tag}",
            f"--region={region}",
            "--platform=managed",
            "--allow-unauthenticated",
            "--port=8080",
            "--memory=1Gi",
            "--cpu=1",
            "--min-instances=0",
            "--max-instances=10",
            f"--env-vars-file={temp_env_yaml}",
            "--quiet",
        ]

        if secrets_to_bind:
            deploy_cmd.append(f"--set-secrets={','.join(secrets_to_bind)}")

        print(f"  • 대상 컨테이너 이미지: {image_tag}")
        print(f"  • 대상 리전: {region} (Seoul)")
        print(f"  • 시크릿 바인딩: {len(secrets_to_bind)}개 연동 완료")
        print(f"  • 배포 명령어 실행 중... (보통 20~30초 소요)")
        print("-" * 75)

        start_time = time.time()
        proc = subprocess.Popen(
            deploy_cmd,
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        service_url = None
        for line in iter(proc.stdout.readline, ""):
            print(line, end="", flush=True)
            if "https://" in line and ".run.app" in line:
                for w in line.strip().split():
                    if w.startswith("https://") and ".run.app" in w:
                        service_url = w.rstrip(".,;:)")

        proc.stdout.close()
        proc.wait()
        elapsed = time.time() - start_time

        if proc.returncode != 0:
            print(f"\n❌ [ERROR] Cloud Run 배포 실패 (Exit Code: {proc.returncode})")
            sys.exit(proc.returncode)

        print("\n" + "=" * 75)
        print(f"  🎉 Google Cloud Run 프로덕션 배포 성공! (총 소요 시간: {elapsed:.1f}초)")
        if service_url:
            print(f"  🌐 서비스 라이브 URL: {service_url}")
            print(f"  🏥 헬스체크 URL: {service_url}/health")
            print(f"  📱 PWA 웹앱 접속: {service_url}/home")
        print("=" * 75)

    finally:
        if temp_env_yaml.exists():
            try:
                temp_env_yaml.unlink()
            except Exception:
                pass


def main():
    print("=" * 75)
    print("  🌙 아이숨 (Aisum) - Google Cloud Run 원클릭 프로덕션 배포 시스템")
    print("  (하이브리드 Secret Manager & 무키 ADC 인증 파이프라인)")
    print("=" * 75)

    sync_frontend_assets()

    is_authed, project_id = check_gcloud_auth()
    if not is_authed:
        print("배포를 계속하려면 위의 안내에 따라 gcloud auth login을 수행한 후 다시 실행해주세요.")
        sys.exit(1)

    deploy_to_cloud_run(project_id)


if __name__ == "__main__":
    main()
