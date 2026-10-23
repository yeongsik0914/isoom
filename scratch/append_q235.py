# -*- coding: utf-8 -*-
"""
ISOOM Governance Documentation Updater for Q235
- Updates docs/qa-logs/Answer-영식.md (TOC Q235 + Body Q235)
- Updates docs/qa-logs/q_a.md (Body Q155)
- Updates docs/project-core/log.md (TOC ISSUE-228 + Section ISSUE-228)
- Updates docs/project-core/README.md (Changelog v2.9.38)
- Updates docs/project-core/PLAN.md (Hybrid ADC & Secret Manager Architecture)
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")
import glob
from pathlib import Path

PROJECT_ROOT = Path("e:/isoom")

# 1. Answer-영식.md
answer_files = glob.glob(str(PROJECT_ROOT / "docs" / "qa-logs" / "Answer*.md"))
if not answer_files:
    raise FileNotFoundError("Answer file not found")
answer_file = Path(answer_files[0])

with open(answer_file, "r", encoding="utf-8", errors="ignore") as f:
    answer_text = f.read()

target_toc_234 = "242. [Q234. [Google Cloud Run 삭제 시 환경변수 소멸 원인 분석 및 Secret Manager vs Cloud Run 환경변수 저장 위치 및 Firebase 인증 아키텍처 안내] Secret Manager에 GEMINI_API_KEY만 남아있던 이유, Cloud Run 서비스 환경변수 인라인 주입 메커니즘, 로컬 원본 보존 상태 확인 및 재배포/ADC 무키 인증 가이드](#q234-google-cloud-run-삭제-시-환경변수-소멸-원인-분석-및-secret-manager-vs-cloud-run-환경변수-저장-위치-및-firebase-인증-아키텍처-안내-secret-manager에-gemini_api_key만-남아있던-이유-cloud-run-서비스-환경변수-인라인-주입-메커니즘-로컬-원본-보존-상태-확인-및-재배포adc-무키-인증-가이드)\n"
toc_235 = "243. [Q235. [.env 내 5대 API Key의 Google ADC(Application Default Credentials) 적용 가능성 심층 진단] GCP 네이티브 vs 외부 제3자(공공데이터포털, 카카오) API의 인증 메커니즘 차이 분석 및 하이브리드 엔터프라이즈 보안 아키텍처 가이드](#q235-env-내-5대-api-key의-google-adcapplication-default-credentials-적용-가능성-심층-진단-gcp-네이티브-vs-외부-제3자공공데이터포털-카카오-api의-인증-메커니즘-차이-분석-및-하이브리드-엔터프라이즈-보안-아키텍처-가이드)\n"

if target_toc_234 in answer_text and "243. [Q235." not in answer_text:
    answer_text = answer_text.replace(target_toc_234, target_toc_234 + toc_235)

q235_body = """

---

### Q235. [.env 내 5대 API Key의 Google ADC(Application Default Credentials) 적용 가능성 심층 진단] GCP 네이티브 vs 외부 제3자(공공데이터포털, 카카오) API의 인증 메커니즘 차이 분석 및 하이브리드 엔터프라이즈 보안 아키텍처 가이드

* **기록 일시**: 2026-10-23 14:22
* **질문 내용**:
  > 그러면 .env에 있는 api key들은 다 adc 로직으로 할 수 있어?

---

#### 💡 답변 및 엔지니어링 리포트

팀장님께서 질의하신 **아이숨 프로젝트의 `.env`에 정의된 핵심 API 키들을 Google ADC(Application Default Credentials, 애플리케이션 기본 사용자 인증 정보) 로직으로 전면 전환할 수 있는지 여부**에 대한 클라우드 인증 아키텍처 진단 결과를 명확하게 보고드립니다.

---

#### 1. 📌 핵심 결론: "모두 ADC로 할 수는 없습니다 (Google 리소스만 가능)"

결론부터 말씀드리면, **Google Cloud 내부 리소스(Firebase Firestore, Vertex AI)는 ADC로 100% 무키(Keyless) 인증이 가능**하지만, **외부 제3자 기관의 API(공공데이터포털, 카카오맵)는 구조적으로 ADC를 적용할 수 없습니다.**

| 환경 변수명 | 공급 기관 | 용도 | ADC 지원 가능 여부 | 불가능/가능 원인 및 동작 메커니즘 |
| :--- | :--- | :--- | :---: | :--- |
| **`FIREBASE_KEY_PATH`**<br>(또는 `FIREBASE_KEY_JSON`) | **Google Cloud**<br>(Firestore) | 환자 세션, 실시간 병상 캐시, 페어링 조회 | **⭕ 100% 가능** | **GCP 자체 네이티브 데이터베이스**이므로 Cloud Run 서비스 계정에 `roles/datastore.user` IAM 권한만 부여하면 JSON 키 파일 없이 ADC로 완벽 자동 인증. |
| **`GEMINI_API_KEY`** | **Google Cloud**<br>(Gemini 3.8 Flash) | KTAS 소아 사전 문진, 임상 변수 추출 | **🔺 조건부 가능**<br>(Vertex AI 전환 시) | • **현재 방식 (Google AI Studio)**: `api_key` 전용이므로 불가.<br>• **GCP Vertex AI 방식**: `google.genai` SDK에 `vertexai=True`를 설정하면 GCP IAM(`roles/aiplatform.user`)을 통해 **ADC 100% 무키 인증 가능**. |
| **`DATA_GO_API_KEY`** | **대한민국 행정안전부**<br>(국립중앙의료원 E-Gen) | 전국 실시간 소아 응급실 병상, 공휴일 API | **❌ 절대 불가능** | **Google Cloud 외부의 대한민국 정부 전산망**이므로 GCP IAM/ADC를 전혀 인식하지 못함. 행안부 발급 문자열 키(`serviceKey`) 전송 필수. |
| **`KAKAO_REST_API_KEY`** | **(주)카카오**<br>(Kakao Developers) | 법정동 주소/좌표 변환, 키워드 장소 검색 | **❌ 절대 불가능** | **Google 외부의 제3자 사기업 서비스**이므로 GCP IAM/ADC와 무관함. 카카오 HTTP 헤더(`Authorization: KakaoAK ...`)로 키 전송 필수. |
| **`FIRESTORE_DATABASE_ID`** | **Google Cloud** | Firestore DB 이름 식별자 (`isoom`) | **해당 없음**<br>(설정값) | 비밀키가 아닌 단순 데이터베이스 이름 문자열이므로 환경 변수로 지정. |

---

#### 2. 🔍 왜 외부 API는 ADC가 불가능한가? (ADC의 작동 원리와 한계)

* **Google ADC의 정의**:
  - Google Cloud 인프라(Cloud Run, GCE, GKE 등)에서 코드가 실행될 때, Google 메타데이터 서버(`http://metadata.google.internal`)로부터 현재 인프라에 할당된 **Google IAM 서비스 계정의 OAuth 2.0 액세스 토큰**을 자동으로 받아와 Google API 서버와 통신하는 **"Google 전용 무키(Keyless) 인증 프로토콜"**입니다.
* **타사 API에서 작동하지 않는 물리적 이유**:
  - 공공데이터포털(`apis.data.go.kr`)과 카카오(`dapi.kakao.com`)는 Google의 서비스 계정이나 IAM 토큰을 검증할 수 있는 통로가 전혀 없습니다.
  - 이들 서버는 오직 자신들이 발급한 고유 문자열 API 키를 HTTP 요청(URL 쿼리 파라미터 또는 헤더)에 실어 보냈을 때만 인가를 승인합니다.

---

#### 3. 🏛️ 클라우드 엔터프라이즈 권장 표준: 하이브리드 보안 아키텍처

따라서 현업 엔터프라이즈 환경에서는 이러한 이종 시스템 API들을 관리할 때 **하이브리드 보안 모델(Hybrid Security Model)**을 정석으로 채택합니다:

```mermaid
flowchart TD
    subgraph CloudRun ["Google Cloud Run (아이숨 백엔드 컨테이너)"]
        App["FastAPI App (app/config.py)"]
    end

    subgraph GoogleNative ["1. Google 네이티브 리소스 (ADC 무키 인증)"]
        IAM["Cloud Run 서비스 계정 (IAM Role)"]
        FS["Cloud Firestore ('isoom' DB)"]
        VX["GCP Vertex AI (Gemini 3.8 Flash)"]
        IAM -->|roles/datastore.user| FS
        IAM -->|roles/aiplatform.user| VX
    end

    subgraph ThirdParty ["2. 외부 제3자 리소스 (GCP Secret Manager 안전 주입)"]
        SM["GCP Secret Manager"]
        DG["DATA_GO_API_KEY"]
        KK["KAKAO_REST_API_KEY"]
        EGEN["공공데이터포털 E-Gen 응급의료 서버"]
        KAKAO["카카오맵 로컬 REST 서버"]
        SM --> DG
        SM --> KK
    end

    App -.->|ADC Keyless 자동 인증| GoogleNative
    SM -->|배포 시 환경변수로 안전 주입| App
    App -->|serviceKey 전송| EGEN
    App -->|KakaoAK 전송| KAKAO
```

1. **Google 네이티브 리소스 (Firestore, Vertex AI)**:
   - ➔ **ADC (IAM 서비스 계정)** 적용: 코드나 환경 변수에 어떠한 키도 두지 않으므로 키 유실 및 보안 유출 위험 **0%**.
2. **외부 제3자 리소스 (공공데이터포털, 카카오맵)**:
   - ➔ **GCP Secret Manager** 적용: Cloud Run을 삭제하거나 재배포하더라도 시크릿은 GCP에 안전하게 영구 보존되며, 컨테이너 기동 시에만 안전하게 주입받음.

---

#### 📌 요약 결론
팀장님, 정리해 드리면 다음과 같습니다:
1. **Firebase Firestore**는 이미 [`app/config.py`](file:///e:/isoom/app/config.py)에 ADC 로직이 준비되어 있으므로, 서비스 계정에 권한만 주면 `serviceAccountKey.json` 없이 **100% 무키(ADC) 인증이 가능**합니다.
2. 반면 **공공데이터포털(E-Gen)**과 **카카오맵**은 Google 외부 서버이므로 기술적으로 ADC를 적용할 수 없으며, **GCP Secret Manager에 보관하여 주입하는 방식이 가장 안전한 클라우드 표준 해법**입니다.
"""

answer_text += q235_body

with open(answer_file, "w", encoding="utf-8") as f:
    f.write(answer_text)
print("Answer-영식.md Q235 추가 완료")

# 2. q_a.md
qa_file = PROJECT_ROOT / "docs" / "qa-logs" / "q_a.md"
if qa_file.exists():
    with open(qa_file, "r", encoding="utf-8", errors="ignore") as f:
        qa_text = f.read()

    q155_entry = """

---

### Q155. [.env 내 5대 API Key의 Google ADC(Application Default Credentials) 적용 가능성 심층 진단] GCP 네이티브 vs 외부 제3자(공공데이터포털, 카카오) API의 인증 메커니즘 차이 분석 및 하이브리드 엔터프라이즈 보안 아키텍처 가이드

* **기록 일시**: 2026-10-23 14:22
* **질문 내용**:
  > 그러면 .env에 있는 api key들은 다 adc 로직으로 할 수 있어?

* **핵심 답변 및 결론**:
  1. **지원 가능 여부**: Google 내부 리소스인 **Firebase Firestore(100% 가능)**와 **Gemini(Vertex AI 전환 시 가능)**는 ADC 적용이 가능하나, 외부 제3자 기관인 **공공데이터포털(E-Gen)**과 **카카오맵**은 구조적으로 ADC 적용이 불가능합니다.
  2. **동작 차이**: ADC는 Google IAM 서비스 계정의 OAuth 토큰을 기반으로 하므로, 자체 API Key 규격을 요구하는 정부/카카오 외부 서버는 Google IAM 토큰을 인식할 수 없습니다.
  3. **엔터프라이즈 권장 표준**: Google 리소스는 **ADC(무키 Keyless)**로 처리하고, 외부 타사 API 키는 **GCP Secret Manager**에 영구 보관하여 주입하는 **하이브리드 보안 아키텍처**를 적용하는 것이 가장 안전합니다.
"""
    if "### Q155." not in qa_text:
        qa_text += q155_entry
        with open(qa_file, "w", encoding="utf-8") as f:
            f.write(qa_text)
        print("q_a.md Q155 추가 완료")

# 3. log.md
log_file = PROJECT_ROOT / "docs" / "project-core" / "log.md"
if log_file.exists():
    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
        log_text = f.read()

    table_target = "| `[ISSUE-227]` | 클라우드/인프라 | Cloud Run 서비스 삭제 시 환경변수 동반 소멸 현상 분석 및 Secret Manager/ADC 인증 체계 정립 | 완료 | 2026-10-23 |"
    table_new_row = """| `[ISSUE-227]` | 클라우드/인프라 | Cloud Run 서비스 삭제 시 환경변수 동반 소멸 현상 분석 및 Secret Manager/ADC 인증 체계 정립 | 완료 | 2026-10-23 |
| `[ISSUE-228]` | 클라우드/보안 | .env 내 5대 보안 키의 Google ADC 적용 가능성 분석 및 외부 API 분리 관리 아키텍처 수립 | 완료 | 2026-10-23 |"""

    if table_target in log_text and "[ISSUE-228]" not in log_text:
        log_text = log_text.replace(table_target, table_new_row)

    issue_section = """

---

### [ISSUE-228] .env 내 5대 보안 키의 Google ADC 적용 가능성 분석 및 외부 API 분리 관리 아키텍처 수립

* **발생 일자**: 2026-10-23
* **작업자**: 정영식 팀장, AI 페어 프로그래머
* **영역**: 클라우드 보안 & API 인증 아키텍처 (Google ADC / Secret Manager / Third-party APIs)
* **문제 현상 및 질의**:
  - Cloud Run 배포 시 `.env`의 모든 API 키(공공데이터포털, 카카오맵, Gemini, Firebase 등)를 Google ADC(Application Default Credentials) 로직으로 일원화 가능한지에 대한 기술적 검토 필요.
* **원인 및 아키텍처 분석**:
  1. **Google 네이티브 리소스 (Firestore, Vertex AI)**: GCP IAM 서비스 계정 토큰 메타데이터를 사용하므로 ADC 100% 무키 인증 가능.
  2. **외부 제3자 리소스 (data.go.kr, kakao.com)**: 대한민국 정부 및 카카오 고유 인증 규격(HTTP 쿼리 파라미터/헤더)을 사용하므로 Google IAM/ADC 인식 불가.
* **해결 및 표준 지침 (하이브리드 보안 아키텍처)**:
  1. **Firestore**: Cloud Run 서비스 계정에 `roles/datastore.user` IAM 권한을 부여하여 ADC 무키 인증 적용.
  2. **Gemini**: 필요 시 Vertex AI SDK 모드로 전환하여 `roles/aiplatform.user` 기반 ADC 무키 인증 적용 가능.
  3. **공공데이터포털 & 카카오맵**: `setup_gcp_secrets.py`를 통해 GCP Secret Manager에 영구 보관 후 컨테이너 기동 시 환경변수로 주입하는 표준 절차 확립.
* **적용 파일**:
  - `docs/qa-logs/Answer-영식.md` (Q235)
  - `docs/qa-logs/q_a.md` (Q155)
  - `app/config.py`
"""
    if "[ISSUE-228]" not in log_text:
        log_text += issue_section
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(log_text)
        print("log.md ISSUE-228 추가 완료")

# 4. docs/project-core/README.md
readme_file = PROJECT_ROOT / "docs" / "project-core" / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
        readme_text = f.read()

    target_changelog = "### 🌟 [v2.9.37-cloud-run-secret-lifecycle]"
    new_changelog = """### 🌟 [v2.9.38-hybrid-adc-and-secret-architecture] 2026-10-23: .env 내 5대 보안 키의 Google ADC 적용 가능성 분석 & 하이브리드 보안 아키텍처 가이드라인 정립 (정영식 팀장, 김동준 팀원)
* **🔐 Google ADC vs 외부 API(공공데이터·카카오) 인증 경계 명확화**:
  - Google Cloud 네이티브 리소스(Firestore, Vertex AI)의 ADC 무키(Keyless) 인증 메커니즘과 외부 제3자 서비스(data.go.kr, kakao.com)의 문자열 API Key 인증 필수성 분석.
  - Google 내부 리소스는 ADC(IAM 기반), 외부 API는 Secret Manager를 활용하는 엔터프라이즈 하이브리드 보안 모델 표준화.
* **📜 4대 거버넌스 문서 지속 누적 동기화**: `Answer-영식.md` Q235 등록, `q_a.md` Q155 등록, `log.md` [ISSUE-228] 등록, `PLAN.md` 하이브리드 보안 절차 동기화.

""" + target_changelog

    if target_changelog in readme_text and "v2.9.38" not in readme_text:
        readme_text = readme_text.replace(target_changelog, new_changelog)
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_text)
        print("docs/project-core/README.md v2.9.38 업데이트 완료")

# 5. docs/project-core/PLAN.md
plan_file = PROJECT_ROOT / "docs" / "project-core" / "PLAN.md"
if plan_file.exists():
    with open(plan_file, "r", encoding="utf-8", errors="ignore") as f:
        plan_text = f.read()

    plan_note = """
> **[2026-10-23 보안 백서 업데이트] 하이브리드 API 인증 아키텍처 (ADC + Secret Manager)**  
> Google 네이티브 리소스(Firestore, Vertex AI)는 IAM 기반 무키 ADC(Application Default Credentials)를 적용하고, 외부 타사 서비스(공공데이터포털, 카카오맵)는 GCP Secret Manager를 통해 주입하는 2-트랙 하이브리드 보안 체계를 공식 표준으로 명세함.
"""
    if "[2026-10-23 보안 백서 업데이트]" not in plan_text:
        if "# " in plan_text:
            parts = plan_text.split("\n\n", 1)
            plan_text = parts[0] + "\n\n" + plan_note + "\n\n" + parts[1]
            with open(plan_file, "w", encoding="utf-8") as f:
                f.write(plan_text)
            print("docs/project-core/PLAN.md 업데이트 완료")

