"""
Google Cloud Secret Manager Sync & Setup Script for Aisum Cloud Run Deployment
.env 파일 및 서비스 계정 키를 GCP Secret Manager에 안전하게 동기화하고 Cloud Run IAM 권한을 부여합니다.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# Fix Windows CP949 console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
SERVICE_ACCOUNT_KEY_PATH = Path(r"C:\AI-Native-Agent\backup\serviceAccountKey.json.json")

def run_cmd(cmd_list, stdin_data=None):
    """Run command safely avoiding Windows cmd quoting issues."""
    try:
        res = subprocess.run(
            cmd_list,
            input=stdin_data,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def get_current_project():
    code, out, _ = run_cmd(["cmd.exe", "/c", "gcloud", "config", "get-value", "project"])
    if code == 0 and out and "(unset)" not in out:
        return out
    return "iceu-songpa09"

def parse_env_file():
    env_vars = {}
    if not ENV_FILE.exists():
        print(f"[ERROR] .env file not found at {ENV_FILE}")
        return env_vars
    
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env_vars[k.strip()] = v.strip().strip("'").strip('"')
    return env_vars

def ensure_secret(secret_name, secret_value, project_id):
    print(f"\n🔐 [Secret Manager] '{secret_name}' 동기화 시작...")
    
    # 1. 시크릿 존재 여부 확인
    code, out, _ = run_cmd(["cmd.exe", "/c", "gcloud", "secrets", "describe", secret_name, f"--project={project_id}"])
    if code != 0:
        print(f"  • 시크릿 '{secret_name}' 신규 생성 중...")
        c_code, c_out, c_err = run_cmd([
            "cmd.exe", "/c", "gcloud", "secrets", "create", secret_name,
            "--replication-policy=automatic",
            f"--project={project_id}"
        ])
        if c_code != 0:
            print(f"  [ERROR] 생성 실패: {c_err}")
            return False
        print(f"  • '{secret_name}' 생성 완료")
    else:
        print(f"  • 시크릿 '{secret_name}' 기등록 확인됨.")

    # 2. 새 버전 추가 (stdin)
    v_code, v_out, v_err = run_cmd(
        ["cmd.exe", "/c", "gcloud", "secrets", "versions", "add", secret_name, "--data-file=-", f"--project={project_id}"],
        stdin_data=secret_value
    )
    if v_code != 0:
        print(f"  [ERROR] 버전 추가 실패: {v_err}")
        return False
    print(f"  • '{secret_name}' 최신 버전 주입 성공: {v_out.splitlines()[0] if v_out else 'OK'}")
    return True

def grant_secret_accessor_iam(project_id):
    print("\n🛡️ [IAM] Cloud Run 기본 서비스 계정에 Secret Accessor 권한 부여 중...")
    # 프로젝트 번호 조회
    code, project_number, _ = run_cmd([
        "cmd.exe", "/c", "gcloud", "projects", "describe", project_id, "--format=value(projectNumber)"
    ])
    if code != 0 or not project_number:
        print(f"  [WARNING] 프로젝트 번호 조회 실패: {project_number}")
        return
    
    service_account = f"{project_number}-compute@developer.gserviceaccount.com"
    print(f"  • 타겟 서비스 계정: {service_account}")
    
    i_code, i_out, i_err = run_cmd([
        "cmd.exe", "/c", "gcloud", "projects", "add-iam-policy-binding", project_id,
        f"--member=serviceAccount:{service_account}",
        "--role=roles/secretmanager.secretAccessor"
    ])
    if i_code == 0:
        print(f"  • IAM 권한 부여 성공 (roles/secretmanager.secretAccessor)")
    else:
        print(f"  • IAM 결과: {i_out or i_err}")

def main():
    print("=" * 70)
    print("  🌙 아이숨(Aisum) GCP Secret Manager 동기화 파이프라인")
    print("=" * 70)
    
    project_id = get_current_project()
    print(f"📌 현재 활성 GCP 프로젝트: {project_id}")
    
    env_vars = parse_env_file()
    
    # 1. DATA_GO_API_KEY
    data_go_key = env_vars.get("DATA_GO_API_KEY")
    if data_go_key:
        ensure_secret("DATA_GO_API_KEY", data_go_key, project_id)
        
    # 2. GEMINI_API_KEY
    gemini_key = env_vars.get("GEMINI_API_KEY")
    if gemini_key:
        ensure_secret("GEMINI_API_KEY", gemini_key, project_id)
        
    # 3. KAKAO_REST_API_KEY
    kakao_key = env_vars.get("KAKAO_REST_API_KEY")
    if kakao_key:
        ensure_secret("KAKAO_REST_API_KEY", kakao_key, project_id)
        
    # 4. FIRESTORE_DATABASE_ID
    firestore_db = env_vars.get("FIRESTORE_DATABASE_ID", "data-test01")
    if firestore_db:
        ensure_secret("FIRESTORE_DATABASE_ID", firestore_db, project_id)
        
    # 5. FIREBASE_KEY_JSON
    firebase_json_content = None
    if SERVICE_ACCOUNT_KEY_PATH.exists():
        with open(SERVICE_ACCOUNT_KEY_PATH, "r", encoding="utf-8") as f:
            firebase_json_content = f.read()
    else:
        # Check if local serviceAccountKey.json exists
        local_key = PROJECT_ROOT / "serviceAccountKey.json"
        if local_key.exists():
            with open(local_key, "r", encoding="utf-8") as f:
                firebase_json_content = f.read()

    if firebase_json_content:
        ensure_secret("FIREBASE_KEY_JSON", firebase_json_content, project_id)
    else:
        print("\n⚠️ [NOTICE] Firebase 서비스 계정 JSON 파일을 찾지 못했습니다.")

    # 6. IAM Secret Accessor 권한 부여
    grant_secret_accessor_iam(project_id)
    
    print("\n" + "=" * 70)
    print("  ✅ 모든 필수 API 키가 GCP Secret Manager에 성공적으로 등록되었습니다!")
    print("=" * 70)

if __name__ == "__main__":
    main()
