"""
🚀 아이숨 (Aisum) - Google Cloud Run 원클릭 프로덕션 배포 파이프라인
.env 파일 및 서비스 계정 키(FIREBASE_KEY_PATH)를 자동 로드/파싱하여
Cloud Run에 안전하게 주입하고 서버리스 컨테이너를 빌드 및 배포합니다.
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


def load_env_and_secrets():
    """Parses .env and resolves Firebase service account credentials."""
    print("\n🔑 [2/4] .env 파일 및 환경 변수 / 보안 키 검증...")
    if not ENV_FILE.exists():
        raise FileNotFoundError(f".env 파일이 {ENV_FILE} 경로에 존재하지 않습니다.")

    env_data = {}
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env_data[k.strip()] = v.strip().strip("'").strip('"')

    data_go_key = env_data.get("DATA_GO_API_KEY", "")
    gemini_key = env_data.get("GEMINI_API_KEY", "")
    kakao_key = env_data.get("KAKAO_REST_API_KEY", "")
    firestore_db = env_data.get("FIRESTORE_DATABASE_ID", "isoom")
    firebase_key_path = env_data.get("FIREBASE_KEY_PATH", "")

    print(f"  • DATA_GO_API_KEY: {'등록됨 (길이: ' + str(len(data_go_key)) + ')' if data_go_key else '⚠️ 누락'}")
    print(f"  • GEMINI_API_KEY: {'등록됨 (길이: ' + str(len(gemini_key)) + ')' if gemini_key else '⚠️ 누락'}")
    print(f"  • KAKAO_REST_API_KEY: {'등록됨 (길이: ' + str(len(kakao_key)) + ')' if kakao_key else '⚠️ 누락'}")
    print(f"  • FIRESTORE_DATABASE_ID: {firestore_db}")

    # Resolve Firebase Service Account JSON
    firebase_json_str = None
    candidate_paths = [
        firebase_key_path,
        r"E:\FIREBASE_API_KEY\serviceAccountKey.json",
        str(PROJECT_ROOT / "serviceAccountKey.json"),
        str(PROJECT_ROOT.parent / "serviceAccountKey.json"),
        r"C:\AI-Native-Agent\key\serviceAccountKey.json",
        r"C:\AI-Native-Agent\backup\serviceAccountKey.json.json",
    ]

    for p in candidate_paths:
        if p and os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as jf:
                    parsed_json = json.load(jf)
                    firebase_json_str = json.dumps(parsed_json, separators=(",", ":"))
                    print(f"  • Firebase 서비스 계정 키 로드 성공: {p} (Project: {parsed_json.get('project_id')})")
                    break
            except Exception as e:
                print(f"  ⚠️ {p} 파싱 실패: {e}")

    # Build injection dictionary
    deploy_env = {
        "APP_ENV": "production",
        "LOG_LEVEL": env_data.get("LOG_LEVEL", "INFO"),
        "DATA_GO_API_KEY": data_go_key,
        "DATA_GO_KR_API_KEY": data_go_key,
        "GEMINI_API_KEY": gemini_key,
        "KAKAO_REST_API_KEY": kakao_key,
        "FIRESTORE_DATABASE_ID": firestore_db,
    }
    if firebase_json_str:
        deploy_env["FIREBASE_KEY_JSON"] = firebase_json_str
    elif env_data.get("FIREBASE_KEY_JSON"):
        deploy_env["FIREBASE_KEY_JSON"] = env_data.get("FIREBASE_KEY_JSON")
    else:
        print("  ⚠️ FIREBASE_KEY_JSON을 생성하지 못했습니다. Cloud Run 기본 IAM (ADC) 인증 모드를 적용합니다.")

    return deploy_env


def check_gcloud_auth():
    """Checks gcloud installation, active project, and token validity."""
    print("\n🔍 [3/4] Google Cloud CLI (gcloud) 상태 및 인증 확인...")

    # Check CLI presence
    code, out, _ = run_command([GCLOUD_CMD, "--version"])
    if code != 0:
        print(f"  ❌ Google Cloud SDK({GCLOUD_CMD})를 실행할 수 없습니다.")
        print("     설치 안내: https://cloud.google.com/sdk/docs/install-sdk")
        return False, None

    # Check active project
    code, project_id, _ = run_command([GCLOUD_CMD, "config", "get-value", "project"])
    project_id = project_id.strip() if code == 0 else ""
    if not project_id or "(unset)" in project_id:
        project_id = "iceu-songpa10"
        print(f"  ⚠️ 활성 프로젝트가 설정되지 않아 기본값 '{project_id}'을(를) 적용합니다.")

    # Check auth status
    code, auth_out, auth_err = run_command([GCLOUD_CMD, "auth", "print-access-token"])
    if code != 0 or not auth_out:
        print("\n" + "!" * 75)
        print("  🚨 [인증 필요] Google Cloud 로그인 세션이 만료되었거나 인증되지 않았습니다.")
        print(f"  📌 터미널에서 다음 명령어를 실행하여 웹 브라우저 로그인을 완료해주세요:\n")
        if os.name == "nt":
            print(f"     gcloud.cmd auth login")
            print(f"     gcloud.cmd config set project {project_id}\n")
            print("  ※ PowerShell 스크립트 보안 정책 에러 발생 시:")
            print("     Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force")
            print("     gcloud auth login")
        else:
            print(f"     gcloud auth login")
            print(f"     gcloud config set project {project_id}")
        print("!" * 75 + "\n")
        return False, project_id

    print(f"  ✅ gcloud 인증 완료 (사용자 세션 유효)")
    print(f"  • 대상 GCP 프로젝트: {project_id}")
    return True, project_id


def build_container_image(project_id):
    """Builds container image via Cloud Build and pushes to Artifact Registry."""
    image_tag = f"asia-northeast3-docker.pkg.dev/{project_id}/isoom-repo/{SERVICE_NAME}:latest"
    print(f"\n📦 [3.5/4] Cloud Build 컨테이너 이미지 패키징 및 푸시 시작...")
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


def deploy_to_cloud_run(project_id, deploy_env, region=DEFAULT_REGION):
    """Deploys application to Cloud Run using --env-vars-file to avoid CLI quoting issues."""
    skip_build = "--skip-build" in sys.argv
    if not skip_build:
        image_tag = build_container_image(project_id)
    else:
        image_tag = f"asia-northeast3-docker.pkg.dev/{project_id}/isoom-repo/{SERVICE_NAME}:latest"
        print(f"\n⏩ [3.5/4] --skip-build 옵션으로 기존 컨테이너 이미지({image_tag})를 사용합니다.")

    print(f"\n🚀 [4/4] Cloud Run 프로덕션 배포 시작 ({SERVICE_NAME}, {region})...")

    # Generate a temporary YAML file for environment variables
    temp_env_yaml = PROJECT_ROOT / ".cloud_run_env.yaml"
    try:
        yaml_lines = []
        for k, v in deploy_env.items():
            # Escape single quotes in value
            safe_v = v.replace("'", "''")
            yaml_lines.append(f"{k}: '{safe_v}'")

        with open(temp_env_yaml, "w", encoding="utf-8") as f:
            f.write("\n".join(yaml_lines) + "\n")

        # Check if we should build or if image already exists
        print(f"  • 대상 컨테이너 이미지: {image_tag}")
        print(f"  • 대상 리전: {region} (Seoul)")

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
        # Securely remove temporary YAML secret file
        if temp_env_yaml.exists():
            try:
                temp_env_yaml.unlink()
            except Exception:
                pass


def main():
    print("=" * 75)
    print("  🌙 아이숨 (Aisum) - Google Cloud Run 원클릭 프로덕션 배포 시스템")
    print("=" * 75)

    # 1. PWA & Static Assets Sync
    sync_frontend_assets()

    # 2. Load Secrets & Env
    deploy_env = load_env_and_secrets()

    # 3. Check Auth & Project
    is_authed, project_id = check_gcloud_auth()
    if not is_authed:
        print("배포를 계속하려면 위의 안내에 따라 gcloud auth login을 수행한 후 다시 실행해주세요.")
        sys.exit(1)

    # 4. Deploy
    deploy_to_cloud_run(project_id, deploy_env)


if __name__ == "__main__":
    main()
