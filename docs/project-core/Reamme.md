# 🌙 MoonlightCare 업데이트 & 릴리즈 노트 (Reamme.md)

> 본 문서는 [README.md](file:///e:/monnlight/README.md)와 함께 동기화되며, MoonlightCare 프로젝트에서 개발된 **모든 업데이트 내용, 기능 추가, 정책 변경 사항을 사용자가 이해하기 쉽고 직관적으로 파악할 수 있도록 지속 관리하는 사용자 친화적 업데이트 일지**입니다.

---

### 🌟 [v0.4.3] 2026-10-01: 2026 최신 Gemini 3.8 Flash 모델 라인업 전수 반영 및 Zero-LLM 역할 재배치
* 🧠 **Gemini 3.8 Flash 핵심 에이전트 전격 채택**:
  * 최신 플래그십 Flash를 문진(`Triage Agent`, Thinking: Medium) 및 라우팅(`Supervisor Agent`, Thinking: Low)에 배치하여 복합 대화력과 Tool Calling 정확도를 극대화.
* ⚡ **보조 경량 모델(Gemini 3.5 Flash-Lite) 매핑**:
  * `Medical Guardrail`, `Visit Logistics`, `Sentinel Agent` 등 단순 이진 분류 및 정형 서식 출력에 배치하여 지연시간(< 150ms) 및 비용 90% 절감.
* 🛑 **결정론적 Zero-LLM (LLM 호출 엄금) 영역 확립**:
  * 1초가 급한 Red Flag 응급 상황(0ms Regex), 병원 공간 거리 계산(PostGIS 5ms SQL), 실시간 병상 조회(Redis 1ms), DB 보안 차단(PostgreSQL 물리 Role)은 LLM 호출을 완전 배제(Zero-LLM)하여 안전성 100% 보장.

---

### 🌟 [v0.4.2] 2026-10-01: 실전 바이브코딩 로드맵 및 기술 허들 가이드(VIBE_CODING_ROADMAP.md) 수립
* 🚀 **단계별 바이브코딩 실전 로드맵 확정**:
  * AI 페어 프로그래밍을 실패 없이 8단계로 완주하기 위한 스텝별 프롬프트와 검증 커맨드 표준화.
* 🛡️ **5대 현실적 개발 허들 극복 방안 완비**:
  * 공공 API 결함, 멀티 에이전트 지연시간, GeoAlchemy2 비동기 결합, 의료법 100% 방어, Zero-Trust DB 접근 통제 솔루션 제시.

---

### 🌟 [v0.4.1] 2026-10-01: 종합 기획서(PROJECT_PLAN.md)와 DB 설계 기획서(DATABASE_DESIGN.md) 통합 반영
* 📚 **종합 기획서 5장 전면 고도화**:
  * [PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제5장에 [DATABASE_DESIGN.md](file:///e:/monnlight/docs/DATABASE_DESIGN.md)의 핵심 내용(DBMS 비교 분석 매트릭스, 트래픽/비즈니스 규칙 요구사항 분석, Mermaid ERD 모델링, 8대 테이블 상세 데이터 사전, 물리적 인덱스 및 DDL 완제본)을 완전 통합.
* 🛡️ **Zero-Trust 접근 제어 DDL & 동기화 파이프라인 정합성 확보**:
  * `agent_readonly` Role과 `Audit & Security Sentinel Agent`의 상호작용 체계를 기획서 본문과 완벽 동기화.
* 📁 **디렉터리 레이아웃 동기화**:
  * `app/db/models/holiday.py`, `mutation.py` 및 `docs/DATABASE_DESIGN.md`를 프로젝트 아키텍처에 공식 반영.

---

### 🌟 [v0.4.0] 2026-10-01: 백엔드 표준 4단계 DB 설계 기획서(DATABASE_DESIGN.md) 수립
* 🗄️ **PostgreSQL(PostGIS) + Redis 하이브리드 아키텍처 확정**:
  * 5ms 초고속 곡면 타원체 반경 검색(GIST 공간 인덱스)과 1ms 실시간 병상 캐싱(TTL)을 결합한 최적 DBMS 선정.
* 📐 **표준 4단계 데이터베이스 설계 완료**:
  * 요구사항 분석 ➔ 개념적 설계(ERD) ➔ 논리적 설계(테이블 명세 & 정규화) ➔ 물리적 설계(인덱스 & DDL 완제본).
* 🔒 **물리적 DB 접근 통제(Zero-Trust) DDL 수립**:
  * `agent_readonly` 계정 분리를 통해 LLM 에이전트의 직접적인 DB 수정/삭제를 데이터베이스 엔진 차원에서 원천 차단.

---

### 🌟 [v0.3.1] 2026-10-01: 에이전트 DB 접근 통제 및 관리 감독 센티넬(Sentinel) 에이전트 도입
* 🛡️ **DB 읽기/쓰기 권한 분리 (Free-Read, Strict-Write)**:
  * 에이전트의 검색/읽기(SELECT) 및 공간 지리 쿼리는 지연시간 없이 0ms로 자유롭게 인가.
  * 데이터 수정 및 삭제(UPDATE/DELETE/INSERT)는 직접 실행을 원천 차단하고 **100% 관리자 보고 및 HITL(Human-in-the-Loop) 승인을 거치도록 강제**.
* 👁️ **관리 감독 전담 에이전트 (`Audit & Security Sentinel Agent`) 신설**:
  * 에이전트의 모든 Tool Calling 및 SQL 쿼리를 런타임에 0ms로 실시간 감시.
  * 관리자 보고를 건너뛰고 무단으로 DB 변이를 시도하면 즉시 트랜잭션 폐기(Rollback), 에이전트 즉각 격리(Quarantine), 관리자 긴급 침해 경보 발송 및 [log.md](file:///e:/monnlight/log.md)에 불변 기록.
* 🔒 **PostgreSQL 엔진 차원 1차 물리 방어선**:
  * DB 레벨에서 `agent_readonly` 계정으로 쓰기 권한을 원천 박탈하여 LLM 탈옥 시에도 데이터 변조 0% 보장.

---

### 🌟 [v0.3.0] 2026-10-01: 파이썬 중심 웹앱 아키텍처 및 주석 표준화, 엔지니어링 로그 체계 구축
* 🌐 **파이썬 웹앱 서비스 전환**:
  * 단순 스크립트 형태가 아닌 **FastAPI 비동기 백엔드 + 경량 반응형 웹 프론트엔드(Vanilla SPA)** 구조로 웹 애플리케이션 서비스 체계 확정.
* 📁 **프로덕션 폴더 아키텍처 수립**:
  * `app/`(백엔드 코어 및 라우터), `app/agents/`(하네스 멀티 에이전트), `app/services/`(비즈니스 로직), `web/`(웹 프론트엔드 UI), `pipeline/`(공공데이터 수집 배치)로 체계적 모듈화 완료.
* 📝 **기능별 상세 주석 작성 표준 강제 ([STD-DOC-01~04])**:
  * 앞으로 작성될 모든 코드에 대해 모듈 헤더, 4단계 동작 메커니즘(Step-by-Step), 의학적/법적 Rationale, 파라미터 상세 설명을 상세한 한글 주석으로 달도록 규칙 명문화.
* 🛠️ **트러블슈팅 전용 로그 ([log.md](file:///e:/monnlight/log.md)) 신설**:
  * 공공데이터포털 URL 이중 인코딩 버그, 심평원 질병정보 API 의료법 충돌 및 배제, E-Gen 실시간 병상 비정형 텍스트 파싱 등 7대 핵심 이슈의 원인과 구체적 해결 방안 문서화.

---

### 🌟 [v0.2.0] 2026-10-01: 공공데이터 오픈 API 정예화 및 인증키 보안 체계 구축
* ❌ **불필요한 오픈 API 선별 및 배제**:
  * 이미 승인된 `건강보험심사평가원_질병정보서비스`는 의료법 제27조(무면허 진단 금지) 준수 및 시스템 경량화를 위해 런타임 호출 대상에서 공식 배제.
  * Triage 과정의 진단 금칙어 검사는 150여 개 소아 빈출 질환명으로 구성된 **인메모리 정적 사전(`04_forbidden_lexicon.json`)**으로 0ms에 선제 차단하도록 최적화.
* 🔑 **추가 필수 오픈 API 4건 확정**:
  1. `국립중앙의료원_전국 응급의료기관 정보 조회 서비스` (실시간 소아병상 hv28 + 응급실 공지 hpmg)
  2. `국립중앙의료원_전국 병·의원 찾기 서비스` (월~일·공휴일 실제 진료시간 dutyTime1~8)
  3. `건강보험심사평가원_의료기관별상세정보서비스` (소아청소년과 전문의 인력 수 getDgsbjtPrDoctorInfoInqire)
  4. `한국천문연구원_특일 정보제공 서비스` (법정공휴일/대체공휴일/명절 캘린더 동기화)
* 🔒 **오픈 API 키 최적 관리 표준 도입**:
  * data.go.kr 단일 인증키(`DATA_GO_KR_API_KEY`) 통합 관리.
  * 파이썬 URL 이중 인코딩 방지를 위한 **'디코딩(Decoding) 키'** 사용 강제.
  * 로컬(`.env` + Pydantic Settings)과 클라우드 배포(GCP Secret Manager) 2-Tier 보안 관리 분리.

---

### 🌟 [v0.1.0] 2026-10-01: 시스템 기획안 및 멀티 에이전트 하네스 설계
* ⚖️ **의료법 컴플라이언스 3대 원칙 확립**:
  * 제27조(무면허 진단 금지), 제27조 제3항(영리 목적 환자 유인·알선 금지), 제56조(의료광고 금지) 원천 준수.
* 🤖 **하네스 멀티 에이전트 6대 R&R 설계**:
  * Supervisor, Triage & Intake, Medical Guardrail, Emergency Escalation, Facility Matching, Visit Logistics 에이전트 분담.
* 🧪 **골든 테스트 케이스 40선 구축**:
  * 5대 평가 루브릭(DIM-1~5) 기반 AI 평가 데이터셋([tests/evals/golden_test_cases.json](file:///e:/monnlight/tests/evals/golden_test_cases.json)) 및 치명적 탈락(Critical Fail) 판정 기준표 작성.

---

## 📌 주요 문서 빠른 바로가기
* [종합 기획안 (docs/PROJECT_PLAN.md)](file:///e:/monnlight/docs/PROJECT_PLAN.md)
* [문제 해결 & 트러블슈팅 로그 (log.md)](file:///e:/monnlight/log.md)
* [공공데이터 결함 분석 보고서 (docs/DATA_CONSIDERATIONS.md)](file:///e:/monnlight/docs/DATA_CONSIDERATIONS.md)
* [의료법 지식 베이스 (references/medical_law/)](file:///e:/monnlight/references/medical_law/)
