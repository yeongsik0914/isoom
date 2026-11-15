# isoom (아이숨 / MoonlightCare) 개선 및 고도화 로드맵

> **작성 기준**: 프로젝트 전체 코드베이스 정적 분석 및 아키텍처·보안·배포 관점 점검 결과  
> **목표**: 프로덕션(Cloud Run) 실서비스 배포 및 현업 코드 리뷰 기준을 통과할 수 있는 완성도 확보

---

## 0. 현재 상태 요약

* **강점**: 2-Tier 안전 가드레일(0ms Red-Flag 인터셉터 + 의료법 제27조 출력 필터), Zero-LLM 결정론적 병원·약국 매칭(Haversine + 30분 약국 조제 마진), `AsyncCircuitBreaker` + 3단계 Fallback, Firestore MD5 Hash Diffing(FinOps), `Dockerfile` 및 GCP Secret Manager 배포 스크립트 등 실서비스 핵심 구조가 잘 갖춰져 있습니다.
* **핵심 보완 필요 영역**: Vertex AI 분기 런타임 크래시 버그, 환경변수 오타 및 의존성 누락, Cloud Run 멀티 인스턴스 환경에서의 인메모리 세션·스케줄러 충돌, 관리/세션 API 인증 부재, 프론트엔드 자산 중복 및 대형 단일 파일 구조.

---

## 1. P0 — 치명적 결함 (즉시 수정 필수)

### 1-1. Vertex AI ADC 분기 `import os` 누락으로 인한 `NameError`
* **현상**: `GEMINI_API_KEY`가 없고 Cloud Run(`K_SERVICE`) 또는 Vertex AI ADC(`GOOGLE_APPLICATION_CREDENTIALS`, `USE_VERTEX_AI=true`) 환경으로 기동될 때 `NameError: name 'os' is not defined`가 발생합니다.
* **위치**:
  * `app/agents/triage_agent.py` (라인 143~148: `elif os.getenv("K_SERVICE") ...` 호출, 파일 상단에 `import os` 누락)
  * `app/agents/logistics_agent.py` (라인 72~77: `elif os.getenv("K_SERVICE") ...` 호출, 파일 상단에 `import os` 누락)
* **해결 방안**:
  * 두 파일 상단에 `import os` 추가.
  * `TriageAgent.__init__`과 `LogisticsAgent.__init__`에 중복된 GenAI 클라이언트 초기화 로직을 공통 헬퍼(예: `app/services/genai_client.py`)로 통합해 중복 제거.

### 1-2. `requirements.txt`에 직접 의존성 `httpx` 누락
* **현상**: `app/api/v1/location.py`(라인 9)에서 `import httpx`를 직접 사용하지만, 프로덕션 컨테이너가 설치하는 `requirements.txt`에는 `httpx`가 없고 `requirements-dev.txt`(라인 19)에만 선언되어 있습니다.
* **위치**: `requirements.txt`, `Dockerfile`(라인 22~24), `app/api/v1/location.py`
* **해결 방안**:
  * `requirements.txt`에 `httpx>=0.27.0` 추가.
  * 클린 가상환경 또는 `docker build` 후 기동 테스트로 런타임 `ImportError` 여부 검증.

### 1-3. `.env.example` 환경변수 키 오타 (`KAKAKO_REST_API_KEY`)
* **현상**: `.env.example` 라인 18에 `KAKAKO_REST_API_KEY`로 오타가 있어, 이를 복사해 `.env`를 구성하면 `app/api/v1/location.py`(라인 15, 102)가 읽는 `KAKAO_REST_API_KEY`가 빈 문자열로 처리되어 항상 로컬 Fallback DB로만 동작합니다.
* **위치**: `.env.example` (라인 18)
* **해결 방안**:
  * `.env.example`의 `KAKAKO_REST_API_KEY`를 `KAKAO_REST_API_KEY`로 수정.

### 1-4. `SupervisorOrchestrator`에서 `followup_question` 유실 및 대화 이력/다회차 상태 버그
* **현상**:
  1. `TriageAgent.triage_message()` (`app/agents/triage_agent.py` 라인 222~226)는 `empathy_message` 뒤에 `followup_question`을 붙여 `state.conversation_history`에 저장하지만, `SupervisorOrchestrator.process_turn()` (`app/orchestrator/supervisor.py` 라인 139, 239~243)은 `triage_res.empathy_message`만 꺼내 `sanitized_inquiry`를 만들고 `conversation_history[-1].content`까지 덮어써 **추가 문진 질문(`followup_question`)이 응답에서 사라집니다.**
  2. `supervisor.py` 라인 188~192(`if not has_symptoms and not turn_limit_reached:`) 분기에서는 `triage_agent`가 이미 `assistant` 메시지를 추가한 상태에서 `state.add_message(role="assistant", ...)`를 한 번 더 호출해 `assistant` 메시지가 연속 2개 쌓입니다.
  3. `supervisor.py` 라인 126~127(`if state.current_step == "COMPLETED": state.current_step = "TRIAGE"`)에서 이전 상담의 `age_months`, `temperature`, `symptoms`, `turn_count`가 초기화되지 않아, 동일 세션에서 새 증상을 물으면 즉시 `is_triage_complete()` 또는 `turn_count >= 3`에 걸립니다.
* **위치**: `app/orchestrator/supervisor.py`, `app/agents/triage_agent.py`
* **해결 방안**:
  * `SupervisorOrchestrator`가 `triage_res.empathy_message`와 `triage_res.followup_question`을 명시적으로 결합하거나, `TriageAgent`가 생성한 `assistant` 메시지를 단일 소스로 사용하도록 흐름 정리.
  * `TriageAgent`는 데이터 추출/판정만 담당하고 `conversation_history` 기록은 `SupervisorOrchestrator` 한 곳에서만 수행하도록 책임을 단일화.
  * `COMPLETED` 이후 새 상담 라운드 진입 시 임상 변수 초기화 정책(신규 세션 발급 권장 또는 명시적 리셋) 정의 및 단위 테스트 추가.

### 1-5. 하드코딩된 GCP 프로젝트 ID·개발 DB ID·개인 PC 경로 제거
* **현상**:
  * GCP 프로젝트 ID `"iceu-songpa10"`이 `app/config.py`(라인 200), `app/agents/triage_agent.py`(라인 147), `app/agents/logistics_agent.py`(라인 76), `scripts/deploy_cloud_run.py`(라인 136)에 기본값으로 하드코딩되어 있습니다.
  * `app/config.py` 라인 138에서 Firestore DB fallback이 `"data-test01"`인 반면, `scripts/deploy_cloud_run.sh` 라인 38은 `"isoom"`을 기본값으로 사용합니다.
  * `app/config.py` 라인 96~98에 개인 Windows 경로(`C:\AI-Native-Agent\key\...`, `E:\FIREBASE_API_KEY\...`)가 하드코딩되어 있습니다.
* **해결 방안**:
  * 프로젝트 ID/DB ID 하드코딩 기본값을 제거하고 `.env` / 환경변수(`GOOGLE_CLOUD_PROJECT`, `FIRESTORE_DATABASE_ID`) 누락 시 명확한 설정 에러 또는 표준 기본값(`(default)`)으로 통일.
  * Windows 레지스트리 스캔 및 개인 드라이브 경로 fallback은 제거하거나 `APP_ENV=development`일 때만 제한적으로 허용.

---

## 2. P1 — 프로덕션 아키텍처, 보안 및 확장성 개선

### 2-1. 멀티 인스턴스(Cloud Run 오토스케일링) 대응을 위한 세션 저장소 외부화
* **현상**: `SessionManager` (`app/orchestrator/session_manager.py`)가 환자 세션을 로컬 프로세스 메모리(`self._sessions: dict[str, PatientSessionState]`)에만 보관합니다. Cloud Run에서 인스턴스가 2개 이상으로 확장되거나 콜드 스타트/재배포가 발생하면 진행 중인 문진 대화 맥락이 소실됩니다.
* **위치**: `app/orchestrator/session_manager.py`
* **해결 방안**:
  * `SessionStore` 추상 인터페이스를 두고, 프로덕션에서는 **Redis(Memorystore)** 또는 **Cloud Firestore**(`sessions` 컬렉션 + TTL 정책)에 `PatientSessionState`를 JSON 직렬화해 저장하도록 교체.
  * 로컬 개발/테스트 환경에서는 기존 `InMemorySessionStore`를 주입해 테스트 속도 유지.

### 2-2. Cloud Run 스케줄러 중복 실행 방지
* **현상**: `main.py`(라인 58~65)와 `app/services/scheduler.py`가 앱 프로세스 내부에서 `APScheduler`를 실행합니다. 인스턴스 수가 N개로 늘어나면 5분 주기 E-Gen API 폴링과 04:00 KST 정적 데이터 동기화가 N배 중복 실행되어 API 쿼터 낭비 및 경합을 유발합니다.
* **위치**: `main.py`, `app/services/scheduler.py`
* **해결 방안**:
  * Cloud Run 환경에서는 **Cloud Scheduler → 인증된 내부 트리거 엔드포인트(`POST /api/v1/emergency/sync`)** 구조로 전환하거나, Firestore 분산 락(Lease Document)을 획득한 인스턴스 1대만 실행하도록 개선.

### 2-3. API 인증, 세션 접근 통제 및 CORS 강화
* **현상**:
  1. 외부 API 호출과 서버 상태를 변경하는 `POST /api/v1/emergency/sync`, `POST /api/v1/emergency/sync-static` (`app/api/v1/emergency.py` 라인 134~183)에 인증이 없어 누구나 강제 동기화를 연타(DoS)할 수 있습니다.
  2. `GET /api/v1/chat/session/{session_id}`, `DELETE /api/v1/chat/session/{session_id}`, `GET /api/v1/chat/sessions` (`app/api/v1/chat.py` 라인 136~194)에 소유권/토큰 검증이 없습니다. 민감한 아동 증상 이력이 `session_id`만으로 조회·삭제될 수 있습니다.
  3. `main.py` 라인 93~99에 `allow_origins=["*"]`와 `allow_credentials=True`가 함께 설정되어 있습니다.
* **해결 방안**:
  * `/sync`, `/sync-static`에 관리자/내부 스케줄러 전용 Bearer 토큰 또는 OIDC 검증(Cloud Scheduler 서비스 계정) + Rate Limiting 적용.
  * 세션 조회/삭제 시 최소한 클라이언트별 서명된 세션 토큰(`X-Session-Token` 또는 HttpOnly Signed Cookie) 검증을 추가하고, 세션 목록/통계 엔드포인트는 운영자 전용으로 보호.
  * `ALLOWED_ORIGINS` 환경변수 기반으로 CORS 허용 도메인 제한 (`*` + `allow_credentials=True` 조합 제거).

### 2-4. 에러 응답 노출 차단 및 SSE 진정한 스트리밍 개선
* **현상**:
  * `app/api/v1/chat.py` 라인 85~87에서 `except Exception as e:`의 `str(e)`를 그대로 SSE `error` 이벤트로 클라이언트에 반환해 내부 스택/API 오류가 노출될 수 있습니다.
  * `app/api/v1/chat.py` 라인 72~77은 `supervisor.process_turn()`이 전부 완료된 뒤 응답 문자열을 공백 단위로 `split(" ")`해 `0.01s` 간격으로 전송하는 의사(Pseudo) 스트리밍입니다.
* **해결 방안**:
  * 클라이언트에는 정제된 일반 오류 코드/메시지만 전달하고 상세 예외는 서버 구조화 로그에만 기록.
  * 체감 응답 속도 개선을 위해 단계별 진행 상태(`Guardrail` → `Triage` → `Matching` → `Logistics`)를 실제 에이전트 완료 시점마다 이벤트로 방출하거나, 공감/안내 문구는 Gemini `generate_content_stream` 연동 검토.

### 2-5. 배포 스크립트와 `.dockerignore` 불일치 해소
* **현상**: `scripts/deploy_cloud_run.sh`(라인 77)는 `./serviceAccountKey.json`을 루트로 복사해 이미지에 넣으려 하지만, `.dockerignore`(라인 34)는 `*serviceAccountKey*.json`을 빌드 컨텍스트에서 제외합니다(보안상 `.dockerignore` 정책이 맞으며, 키 파일 번들링 시도 자체가 불필요한 혼선을 줌).
* **위치**: `scripts/deploy_cloud_run.sh`, `.dockerignore`
* **해결 방안**:
  * `scripts/deploy_cloud_run.py`처럼 `deploy_cloud_run.sh`도 키 파일 복사 로직을 완전히 제거하고 Cloud Run ADC + Secret Manager 방식으로 단일화.
  * `Dockerfile`에 비루트(non-root) 사용자 실행(`USER appuser`) 및 `/health` 기반 `HEALTHCHECK` 추가.

---

## 3. P2 — 코드 품질, 프론트엔드 구조 및 리포지토리 위생

### 3-1. 프론트엔드 정적 자산 중복 제거 (Single Source of Truth)
* **현상**: `frontend/`가 원본이고 `scripts/deploy_cloud_run.py`·`deploy_cloud_run.sh`가 배포 시 `app/static/` 및 `app/templates/`로 복사하지만, 복사본(`app/static/`, `app/templates/`)이 Git 저장소에도 함께 존재해 파일 수정 시 버전 불일치(Drift) 위험이 큽니다. 실제로 `emergency_alert.html`, `emergency_guide.html`처럼 한쪽에만 존재하는 템플릿 차이가 발생하고 있으며, Docker 이미지에도 양쪽이 모두 복사됩니다.
* **해결 방안**:
  * `frontend/`만 Git으로 추적(Single Source of Truth)하고, `app/static/`과 `app/templates/`는 제거하거나 `.gitignore` 및 `main.py` 라우팅을 `frontend/` 단일 경로로 통일.

### 3-2. 프론트엔드 대형 파일 모듈화 및 데이터 번들 분리
* **현상**: `frontend/js/main.js`(3,144줄), `frontend/css/style.css`(6,116줄)가 단일 파일로 비대하며, `frontend/js/` 내 정적 데이터 JS 파일 7개가 약 14만 줄 규모를 차지합니다.
* **해결 방안**:
  * `main.js`를 ES Modules(`api.js`, `triage.js`, `map.js`, `pwa.js`, `ui.js`) 단위로 분리.
  * 14만 줄 규모의 정적 JS 데이터 번들은 API 온디맨드 조회 또는 경량 JSON 압축 서빙(`gzip`/Brotli)으로 전환해 초기 로딩 및 브라우저 파싱 비용 절감.

### 3-3. 리포지토리 불필요 파일 정리 및 코드 품질 자동화(CI)
* **현상**:
  * 루트에 42MB `2021_KTAS_guideline_ver1.6.pptx`, `scratch/` 내 21개 임시 파이썬 스크립트(2,371줄)가 남아 있습니다.
  * CI/CD(`.github/workflows`) 및 린터/타입체커(`ruff`, `mypy`, `pytest` 자동 실행) 설정이 없습니다.
* **해결 방안**:
  * 대용량 PPTX 및 `scratch/` 실험 코드는 아카이브/삭제 후 `.gitignore`에 반영.
  * `pyproject.toml` 또는 `ruff.toml`을 도입해 `ruff check`, `mypy` 적용.
  * `.github/workflows/ci.yml`을 추가해 PR/Push 시 `pytest` 128개 테스트 + `ruff` + `docker build` 검증 자동화.
  * `main.py`의 `/health` 엔드포인트(라인 497)가 `settings.gemini_api_key`만 확인하지 않고 Vertex AI ADC 활성화 여부까지 함께 보고하도록 개선.

---

## 4. P3 — 도메인·제품 가치 고도화 (현업 의료/헬스케어 기준)

1. **브랜드 명칭 일관화**: 코드/문서 전반에 `MoonlightCare`, `Aisum`, `isoom`, `아이숨`이 혼용되어 있음(`main.py`, `app/agents/triage_agent.py`, `app/agents/logistics_agent.py`). API 메타데이터·프롬프트·문서 브랜딩을 `isoom (아이숨)`으로 통일.
2. **실시간 데이터 신뢰도/면책 UX 강화**: E-Gen 실시간 병상 데이터는 현장 상황과 5~15분 시차가 날 수 있으므로, `DataFreshnessMeta`의 `last_updated` 시각과 "출발 전 유선 확인 필수" 배지를 결과 카드 최상단에 항상 명시.
3. **모니터링·관측성(Observability) 확보**: Cloud Run 로그에 `session_id`, `ktas_level`, `is_red_flag`, `circuit_status`, `triage_latency_ms`를 JSON 구조화 로깅으로 남기고, Red-Flag 오탐/미탐 모니터링 대시보드 지표(예: Triage Fallback 발생률) 추가.

---

## 5. 실행 체크리스트 (진행 현황)

- [x] **Step 1 (P0)**: `app/services/genai_client.py` 공통 팩토리 신설, `triage_agent.py`·`logistics_agent.py` `import os` 누락 수정 및 중복 제거, Fallback 파서(`토해요`→`구토`, 보수적 KTAS 등급) 보완
- [x] **Step 2 (P0)**: `requirements.txt`에 `httpx>=0.27.0` 추가, `.env.example` `KAKAO_REST_API_KEY` 오타 수정 및 환경변수 정리
- [x] **Step 3 (P0)**: `app/config.py`·`deploy_cloud_run.py` 내 개인 GCP 프로젝트/DB ID·Windows 경로 하드코딩 제거, `holiday_service.py`·`national_dataset_sync_service.py` 미정의 타입(`F821`) 수정
- [x] **Step 4 (P0)**: `supervisor.py`의 `followup_question` 유실 및 `COMPLETED` 재진입 상태 초기화(`reset_for_new_consultation`)·중복 어시스턴트 메시지 버그 수정
- [x] **Step 5 (P1)**: `SessionManager` 추상화(`InMemorySessionStore` + `FirestoreSessionStore`), `scheduler.py` 동시 실행 방지 락 및 `ENABLE_IN_PROCESS_SCHEDULER` 플래그 추가
- [x] **Step 6 (P1)**: `app/services/auth.py` 신설(`/sync*`, `/sessions` Bearer 토큰 인증, `/session/{id}` HMAC `X-Session-Token` 검증), `main.py` CORS·경로 탐색 방어 및 SSE 에러 정제
- [x] **Step 7 (P1/P2)**: `frontend/` 단일 원천 통합(`app/static/`, `app/templates/` 중복 제거), `Dockerfile` 비루트(`appuser`)·`HEALTHCHECK` 추가, `deploy_cloud_run.sh` 키 복사 제거, `pyproject.toml`·`.github/workflows/ci.yml`·`tests/test_roadmap_remediation.py` 구축
- [ ] **Step 8 (선택/후속)**: `frontend/js/main.js` ES Modules 분리 및 `scratch/`·42MB `.pptx` 아카이브 여부 결정
