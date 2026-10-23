# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
import glob
from pathlib import Path

PROJECT_ROOT = Path("e:/isoom")

# 2. q_a.md 업데이트
qa_file = PROJECT_ROOT / "docs" / "qa-logs" / "q_a.md"
if qa_file.exists():
    with open(qa_file, "r", encoding="utf-8", errors="ignore") as f:
        qa_text = f.read()

    q154_entry = """

---

### Q154. [Google Cloud Run 삭제 시 환경변수 소멸 원인 분석 및 Secret Manager vs Cloud Run 환경변수 저장 위치 및 Firebase 인증 아키텍처 안내] Secret Manager에 GEMINI_API_KEY만 남아있던 이유, Cloud Run 서비스 환경변수 인라인 주입 메커니즘, 로컬 원본 보존 상태 확인 및 재배포/ADC 무키 인증 가이드

* **기록 일시**: 2026-10-23 14:15
* **질문 내용**:
  > cloud run 배포하고 파이어베이스에서 정보를 가져올때 serviceAccountKey.json을 읽어서 접근권한을 얻어야 하는데 내가 이전에 secretmanager에 .env 파일들을 다 올려달라고 했었단 말이야. 근데 secretmanager 들어가서 확인해보니까 geminikey만 등록되어있는데 나머지들은 어디에 저장되어 있는 거야? 내가 클라우드런을 오늘 삭제하긴 했는데 그러면서 다 사라진 건가?

* **핵심 답변 및 결론**:
  1. **원인 규명**: 로컬의 `.env`와 `serviceAccountKey.json`은 100% 안전하게 보존되어 있으나, 이전 배포 시 Secret Manager가 아닌 Cloud Run 서비스 자체의 "컨테이너 환경 변수"로 인라인 주입(`--env-vars-file`)되었기 때문에 Cloud Run 서비스를 삭제하면서 해당 환경 변수들도 서비스와 함께 삭제된 것입니다.
  2. **Secret Manager 잔존 이유**: `GEMINI_API_KEY`만 과거에 Secret Manager 독립 시크릿으로 등록되었고 나머지 키들은 Cloud Run 환경변수로만 존재했었습니다.
  3. **Firebase 인증 원리**: 컨테이너에 파일이 없어도 `deploy_cloud_run.py`가 JSON을 문자열(`FIREBASE_KEY_JSON`)로 압축 주입하여 메모리에서 `credentials.Certificate(json.loads(...))`로 인증했습니다.
  4. **향후 가이드**: `python scripts/deploy_cloud_run.py`로 즉시 재배포 가능하며, 영구 보존을 원할 시 `python scripts/setup_gcp_secrets.py`로 Secret Manager에 등록하거나, IAM `roles/datastore.user` 권한을 부여해 JSON 키 없는 무키(Keyless ADC) 인증을 적용할 수 있습니다.
"""
    if "### Q154." not in qa_text:
        qa_text += q154_entry
        with open(qa_file, "w", encoding="utf-8") as f:
            f.write(qa_text)
        print("q_a.md Q154 추가 완료")

# 3. log.md 업데이트
log_file = PROJECT_ROOT / "docs" / "project-core" / "log.md"
if log_file.exists():
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        log_text = f.read()

    # Table entry
    table_target = "| `[ISSUE-226]` | 프론트엔드/상세 | 상세 페이지 3대 결함 전수 해소 | 완료 | 2026-10-20 |"
    table_new_row = """| `[ISSUE-226]` | 프론트엔드/상세 | 상세 페이지 3대 결함 전수 해소 | 완료 | 2026-10-20 |
| `[ISSUE-227]` | 클라우드/인프라 | Cloud Run 서비스 삭제 시 환경변수 동반 소멸 현상 분석 및 Secret Manager/ADC 인증 체계 정립 | 완료 | 2026-10-23 |"""

    if table_target in log_text and "[ISSUE-227]" not in log_text:
        log_text = log_text.replace(table_target, table_new_row)

    issue_section = """

---

### [ISSUE-227] Cloud Run 서비스 삭제 시 인라인 주입 환경변수 동반 소멸 현상 분석 및 Secret Manager 영구 보존/ADC 무키 인증 아키텍처 정립

* **발생 일자**: 2026-10-23
* **작업자**: 정영식 팀장, AI 페어 프로그래머
* **영역**: 클라우드 인프라 (Google Cloud Run / Secret Manager / Firebase Firestore)
* **문제 현상**:
  - GCP 콘솔에서 기존 `isoom-service` Cloud Run 서비스를 삭제한 후 Secret Manager를 확인한 결과, `GEMINI_API_KEY`만 존재하고 `.env`의 공공데이터 포털 키, 카카오맵 키, Firebase 서비스 계정 키(`FIREBASE_KEY_JSON`)가 보이지 않아 키 유실 우려 발생.
* **원인 분석**:
  1. 기존 원클릭 배포 파이프라인(`scripts/deploy_cloud_run.py`)은 보안 키들을 Secret Manager가 아닌 Cloud Run 서비스 자체의 **컨테이너 환경 변수(`--env-vars-file`)**로 직접 주입하여 배포함.
  2. Cloud Run 환경 변수는 서비스 리소스에 종속되어 있어 서비스를 삭제하는 순간 해당 환경 변수들도 서비스와 함께 영구 소멸됨.
  3. `GEMINI_API_KEY`는 과거 Secret Manager에 독립 리소스로 등록되어 있어 살아남았으나, 나머지 키들은 등록되지 않았었음.
  4. 다행히 로컬 `.env`와 `E:\\FIREBASE_API_KEY\\serviceAccountKey.json`에 원본 파일이 100% 안전하게 보존되어 있어 데이터 유실은 없음.
* **구체적 해결 및 향후 표준 방안**:
  1. **로컬 원본 무결성 검증**: `.env` 5대 키 및 `serviceAccountKey.json` 실제 존재 확인 완료.
  2. **Secret Manager 영구 동기화 파이프라인(`scripts/setup_gcp_secrets.py`) 가동 준비**: Cloud Run 서비스 삭제 시에도 키가 보존되도록 5대 키를 Secret Manager에 사전 등록하는 절차 수립.
  3. **IAM 무키(ADC) 인증 표준화 권고**: Cloud Run 기본 서비스 계정에 `roles/datastore.user` 역할을 부여하여 JSON 키 파일/환경변수 주입 없이도 Firestore에 무키(Keyless) 접근 가능한 체계 확립.
* **적용 파일**:
  - `scripts/setup_gcp_secrets.py`
  - `scripts/deploy_cloud_run.py`
  - `app/config.py`
  - `docs/qa-logs/Answer-영식.md` (Q234)
"""
    if "[ISSUE-227] Cloud Run" not in log_text:
        log_text += issue_section
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_text)
        print("log.md ISSUE-227 추가 완료")

# 4. README.md 업데이트
readme_file = PROJECT_ROOT / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
        readme_text = f.read()

    target_changelog = "### [2026-10-20] - v2.9.36"
    new_changelog = """### [2026-10-23] - v2.9.37 (클라우드 인프라 보안 및 시크릿 수명주기 아키텍처 정립)
* **Cloud Run & Secret Manager 보안 아키텍처 가이드라인 정립**: Cloud Run 서비스 삭제 시 인라인 주입 환경변수 소멸 메커니즘을 분석하고, 로컬 키 원본 무결성 확인 및 GCP Secret Manager 영구 보존/Keyless ADC(Application Default Credentials) 무키 인증 표준 절차 명세.
* **Q&A 및 트러블슈팅 엔지니어링 거버넌스 동기화**: `Answer-영식.md` Q234 등록, `q_a.md` Q154 등록, `log.md` [ISSUE-227] 등록 완료.

""" + target_changelog

    if target_changelog in readme_text and "v2.9.37" not in readme_text:
        readme_text = readme_text.replace(target_changelog, new_changelog)
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_text)
        print("README.md v2.9.37 업데이트 완료")

# 5. PLAN.md 업데이트
plan_file = PROJECT_ROOT / "docs" / "project-core" / "PLAN.md"
if plan_file.exists():
    with open(plan_file, "r", encoding="utf-8", errors="ignore") as f:
        plan_text = f.read()

    plan_note = """
> **[2026-10-23 인프라 보안 업데이트] Cloud Run 시크릿 수명주기 & ADC 무키 인증 체계**  
> Cloud Run 서비스 삭제 시 인라인 환경변수 동반 소멸을 방지하기 위해, Secret Manager 독립 시크릿 등록 파이프라인(`setup_gcp_secrets.py`) 및 Cloud Datastore 사용자(`roles/datastore.user`) IAM 바인딩을 통한 무키(Keyless) Firebase Firestore 인증 체계를 표준 백서에 반영함.
"""
    if "[2026-10-23 인프라 보안 업데이트]" not in plan_text:
        if "# " in plan_text:
            parts = plan_text.split("\n\n", 1)
            plan_text = parts[0] + "\n\n" + plan_note + "\n\n" + parts[1]
            with open(plan_file, "w", encoding="utf-8") as f:
                f.write(plan_text)
            print("PLAN.md 업데이트 완료")

