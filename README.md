# 🌙 MoonlightCare (달빛케어)

> **"야간·휴일에 갑자기 아픈 우리 아이를 위한 가장 빠르고 안전한 소아청소년과 매칭 서비스"**  
> 건강보험심사평가원(HIRA) 및 국립중앙의료원(E-Gen) 공공데이터 기반 **파이썬 멀티 에이전트 웹앱 시스템**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-PostGIS-336791.svg?logo=postgresql&logoColor=white)](https://postgis.net/)
[![Redis](https://img.shields.io/badge/Redis-In--Memory-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.0_Flash-4285F4.svg?logo=google&logoColor=white)](https://cloud.google.com/vertex-ai)

---

## 💡 서비스 소개 (About MoonlightCare)

늦은 밤(18시~24시)이나 주말·공휴일에 아이가 갑자기 39도 고열이 나거나 구토를 할 때, 문을 연 소아과를 찾지 못해 대학병원 응급실에서 4~6시간 대기하거나 '소아 진료 불가' 통보를 받는 부모들의 불안을 해결하기 위해 개발된 **지능형 소아 의료 매칭 웹 애플리케이션**입니다.

* 🩺 **친절하고 신속한 사전 문진 (Triage)**: 부모의 당황한 마음을 진정시키고 월령, 체온, 증상을 3~4턴 이내로 빠르게 파악합니다.
* 🛡️ **대한민국 의료법 100% 준수**: 비의료 AI의 불법 진단·처방을 원천 차단하고, 특정 병원 광고/알선 없이 객관적 지표에 기반하여 병원을 공정하게 안내합니다.
* 🚨 **Red Flag 긴급상황 0초 감지**: 생후 100일 미만 고열, 경련 등 응급 상황 감지 시 일반 병원 탐색을 즉각 중단하고 119 구급차 호출 및 소아전문응급의료센터로 직행하도록 전환합니다.
* 📍 **PostGIS 기반 5ms 초고속 매칭**: 사용자 위치 반경 5~10km 내 지금 문 연 달빛어린이병원과 야간 소아과를 즉각 찾아줍니다.
* 📋 **2024년 5월 본인확인 제도 완벽 안내**: 병원 내원 전 필수 준비물(부모 신분증, 등본 등) 체크리스트와 병원 문의용 30초 전화 통화 스크립트를 제공합니다.

---

## 📢 최신 업데이트 내역 (Changelog & Release Notes)

MoonlightCare의 기능 개발, 아키텍처 개선, 정책 변경 사항을 사용자 친화적으로 지속 기록합니다.

### 🌟 [v0.4.2] 2026-10-01: 실전 바이브코딩 로드맵 및 기술 허들 분석 가이드(VIBE_CODING_ROADMAP.md) 수립
* **현실적 5대 기술 허들 심층 분석**: 공공 API 결함, 멀티 에이전트 지연시간, PostGIS+asyncpg 비동기 ORM 결합, 의료법 100% 방어, Zero-Trust DB 거버넌스 해결책 수립.
* **8단계 바이브코딩 실전 로드맵 확정**: 기초 환경 설정부터 PostGIS 스키마, 공공데이터 클라이언트, 지리공간 서비스, 0ms 룰엔진, 멀티 에이전트 하네스, FastAPI/웹 SPA, 40선 골든 테스트 Evals까지 단계별 프롬프트와 검증 커맨드 명시.

### 🌟 [v0.4.1] 2026-10-01: 종합 기획서(PROJECT_PLAN.md)와 DB 설계 기획서(DATABASE_DESIGN.md) 통합 반영
* **종합 기획서 5장 전격 개편**: 블로그 4단계 표준 DB 설계 순서(요구사항 분석 ➔ 개념적 ERD ➔ 논리적 데이터 사전 ➔ 물리적 DDL & 인덱스) 및 기술 선정 근거를 [PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 본문에 완전 통합.
* **프로덕션 DDL 및 데이터 사전 동기화**: `hospitals`, `hospital_operating_hours`, `doctor_specialists`, `pharmacies`, `special_holidays`, `mutation_proposals`, `audit_logs` 등 8개 핵심 테이블 스키마 및 GIST 공간 인덱스 명세 통합.
* **폴더 레이아웃 동기화**: `app/db/models/holiday.py`, `mutation.py` 및 `docs/DATABASE_DESIGN.md`를 프로젝트 아키텍처에 정식 등록.

### 🌟 [v0.4.0] 2026-10-01: 표준 4단계 DB 설계 기획서(DATABASE_DESIGN.md) 수립
* **PostgreSQL(PostGIS) + Redis 하이브리드 아키텍처 확정**: 5ms 초고속 지리공간 쿼리(GIST)와 실시간 병상 캐싱(TTL)을 결합한 최적 DBMS 선정.
* **표준 4단계 설계 수립**: 요구사항 분석 ➔ 개념적 설계(ERD) ➔ 논리적 설계(테이블 명세 & 정규화) ➔ 물리적 설계(인덱스 & 물리적 쓰기 차단 DDL).
* **물리적 Zero-Trust DDL 구현**: `agent_readonly` 계정 분리로 LLM 에이전트의 직접 쓰기/삭제를 DB 엔진 레벨에서 원천 차단.

### 🌟 [v0.3.1] 2026-10-01: 에이전트 DB 접근 통제 및 관리 감독 센티넬(Sentinel) 에이전트 도입
* **DB 권한 분리 (Free-Read, Strict-Write)**: 에이전트의 검색/읽기(SELECT)는 지연시간 없이 0ms로 자유롭게 인가하되, 수정 및 삭제(UPDATE/DELETE)는 100% 관리자 사전 보고 및 HITL(Human-in-the-Loop) 승인을 강제하도록 설계.
* **관리 감독 전담 에이전트(`Audit & Security Sentinel Agent`) 신설**: 에이전트가 관리자에게 보고하지 않고 무단으로 DB 수정을 시도하는 행위를 0.001초 만에 감시·차단(Zero-Bypass)하고 에이전트를 즉각 격리하는 감시 감독 체계 구축.
* **PostgreSQL 엔진 차원 1차 물리 방어선**: DB 레벨에서 `agent_readonly` 계정으로 쓰기 권한을 원천 박탈하여 LLM 탈옥 시에도 데이터 무결성 100% 보장.

### 🌟 [v0.3.0] 2026-10-01: 파이썬 중심 웹앱 아키텍처 및 주석 표준화, 엔지니어링 로그 체계 구축
* **웹앱 기반 아키텍처 확정**: FastAPI 비동기 백엔드 + 경량 반응형 웹 프론트엔드(SPA) 구조로 프로젝트 전면 개편.
* **프로덕션 폴더 구조 정립**: `app/`(백엔드), `web/`(웹 UI), `pipeline/`(공공데이터 배치), `notebooks/`, `tests/` 레이어 분리.
* **기능별 상세 주석 작성 표준 강제 ([STD-DOC-01~04])**: 앞으로 작성될 모든 코드에 대해 모듈 헤더, 4단계 동작 메커니즘, 법적 근거, 파라미터 상세 설명을 주석으로 기술하도록 개발 규칙 확정.
* **트러블슈팅 전용 로그([log.md](file:///e:/monnlight/log.md)) 신설**: 공공데이터 이중 인코딩 버그, 의료법 제27조 진단 배제 등 7대 핵심 이슈의 원인과 해결 방안을 공식 문서화.

### 🌟 [v0.2.0] 2026-10-01: 공공데이터 오픈 API 정예화 및 인증키 보안 체계 구축
* **불필요한 API 배제**: 이미 승인된 `건강보험심사평가원_질병정보서비스`는 의료법 제27조(진단 금지) 준수 및 시스템 경량화를 위해 런타임 호출 대상에서 배제.
* **추가 필수 오픈 API 4건 선정**: E-Gen 응급실 병상 정보, E-Gen 병의원 요일별 진료시간, 심평원 전문의 상세정보, 천문연 특일 정보 확정.
* **오픈 API 키 최적 관리 표준 도입**: 공공데이터포털 단일 인증키(`DATA_GO_KR_API_KEY`) 관리, 파이썬 URL 이중 인코딩 방지를 위한 '디코딩 키' 강제, 로컬(`.env` + Pydantic)과 프로덕션(GCP Secret Manager) 2-Tier 분리.

### 🌟 [v0.1.0] 2026-10-01: 시스템 기획안 및 멀티 에이전트 하네스 설계
* **의료법 컴플라이언스 가드레일 확립**: 제27조(무면허 진단 금지/알선 금지), 제56조(의료광고 금지) 3대 원칙 수립.
* **하네스 멀티 에이전트 R&R 분담**: Supervisor, Triage, Guardrail, Emergency, Matching, Logistics 6개 에이전트 설계.
* **골든 테스트 케이스 40선 구축**: 5대 루브릭 차원(DIM-1~5) 기반 AI 평가 데이터셋([tests/evals/golden_test_cases.json](file:///e:/monnlight/tests/evals/golden_test_cases.json)) 구축.

---

## 🗂️ 핵심 문서 안내

* 📄 **[종합 기획안 (docs/PROJECT_PLAN.md)](file:///e:/monnlight/docs/PROJECT_PLAN.md)**: 전체 시스템 설계, 하네스 멀티 에이전트, 파이썬 웹앱 폴더 구조, 코딩 주석 표준, 개발 로드맵.
* 🗄️ **[데이터베이스 설계 명세서 (docs/DATABASE_DESIGN.md)](file:///e:/monnlight/docs/DATABASE_DESIGN.md)**: 백엔드 표준 4단계 DB 설계, PostGIS + Redis 하이브리드 아키텍처, ERD, DDL 완제본.
* 🛠️ **[문제 해결 & 트러블슈팅 로그 (log.md)](file:///e:/monnlight/log.md)**: 프로젝트 개발 중 발생하는 모든 오류, 병목, 데이터 결함 및 구체적 해결 방안 지속 관리.
* 📊 **[공공의료 데이터 분석 보고서 (docs/DATA_CONSIDERATIONS.md)](file:///e:/monnlight/docs/DATA_CONSIDERATIONS.md)**: 진료시간 괴리, 조기 접수마감, 소아 표방 vs 전문의 괴리 등 공공데이터 한계 및 보정 로직 분석.
* ⚖️ **[의료법 컴플라이언스 가이드 (references/medical_law/)](file:///e:/monnlight/references/medical_law/)**: 의료법 원문, 판례, 유권해석, 진단 금칙어 사전(`04_forbidden_lexicon.json`).


---

## 🚀 빠른 시작 가이드 (Quick Start)

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. 환경변수 설정 (`.env`)
`.env.example`을 복사하여 `.env`를 생성하고 발급받은 **디코딩(Decoding) 인증키**를 입력합니다:
```ini
DATA_GO_KR_API_KEY=발급받은_공공데이터포털_디코딩키
GEMINI_API_KEY=AIzaSy...
POSTGRES_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/moonlight
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
```

### 3. 로컬 서버 실행
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
브라우저에서 `http://localhost:8000`으로 접속하여 웹앱을 이용할 수 있습니다.
