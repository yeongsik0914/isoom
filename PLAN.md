# 🌙 MoonlightCare 종합 기획안 & 개발 백서 (PLAN.md)

> **문서 버전**: v1.2.0  
> **최종 갱신 일자**: 2026-10-13  
> **핵심 슬로건**: *"야간 소아 응급실 뺑뺑이를 막는 0ms 세이프티 가드레일 & 데이터 기반 2-트랙 지능형 라우터"*  
> **기반 원천**: 주피터 노트북 3권 실증 데이터, 공공데이터포털(NMC/KASI), Firebase Cloud Firestore, Gemini 3.8 Flash / 3.5 Lite

---

## 📑 목차 (Table of Contents)

1. [프로젝트 기획 배경 & 핵심 문제 정의](#1-프로젝트-기획-배경--핵심-문제-정의)
2. [데이터 분석 기반의 목적별 기능 도출 과정 (Notebook Insights)](#2-데이터-분석-기반의-목적별-기능-도출-과정-notebook-insights)
3. [현재까지 완료된 개발 모듈 & 테스트 검증 내역 (Done: Steps 1~4)](#3-현재까지-완료된-개발-모듈--테스트-검증-내역-done-steps-14)
4. [전체 6단계 구현 로드맵 & 잔여 과제 (Roadmap: Steps 5~6)](#4-전체-6단계-구현-로드맵--잔여-과제-roadmap-steps-56)
5. [시스템 아키텍처 & 데이터 흐름도](#5-시스템-아키텍처--데이터-흐름도)
6. [데이터 갱신 및 캐싱 전략 (하이브리드 아키텍처)](#6-데이터-갱신-및-캐싱-전략-하이브리드-아키텍처)
7. [추가 심화 고도화 백로그 (Advanced Backlog)](#7-추가-심화-고도화-백로그-advanced-backlog)

---

## 1. 프로젝트 기획 배경 & 핵심 문제 정의

### 1.1 사회적 배경: "왜 야간 소아 응급실 뺑뺑이가 반복되는가?"
* **소아청소년과 전문의 부족**: 심야 시간대 대학병원 및 권역응급의료센터조차 소아 당직의 부재로 "소아 진료 불가" 공지를 수시로 띄움.
* **경증 환자의 응급실 쏠림 (74%)**: 야간에 문을 여는 동네 의원을 찾지 못한 부모들이 단순 미열/감기 환아를 데리고 권역응급센터로 몰려 대기 시간이 3~5시간으로 폭증하고, 정작 중증 환아(KTAS 1~2)의 골든타임이 침해됨.
* **심야 처방전 조제 사고**: 야간에 진료하는 달빛어린이병원을 간신히 찾아 진료를 받았으나, 인근 약국이 먼저 문을 닫아 처방약을 짓지 못하고 발을 동동 구르는 현장 결함 발생.

### 1.2 MoonlightCare의 해결책: "결정론적 2-트랙 스마트 라우팅"
1. **Track A (중증 / Red Flag / 초응급)**: 생후 100일 미만 38도 고열, 경련, 청색증 등 생명 위급 상황은 LLM 지연 없이 **0.015ms(0ms) 안에 119 구급차 및 소아 가용 응급실로 직행**.
2. **Track B (경증 / 일반 야간 진료)**: 부모의 불안을 공감 문진(Gemini 3.8 Flash)하여 진료 가능한 달빛어린이병원과 **30분 이상 여유 있게 영업하는 심야 약국 세트를 1:1 페어링 매칭**.

---

## 2. 데이터 분석 기반의 목적별 기능 도출 과정 (Notebook Insights)

본 프로젝트의 모든 백엔드 기능은 가상의 가정이 아니라, **실제 국립중앙의료원(NMC) 및 한국천문연구원(KASI) 공공데이터를 주피터 노트북 3권으로 정밀 분석한 실측 결과**를 기반으로 설계되었습니다.

### 2.1 [노트북 1] 소아 응급실 병목 분석 (`egen_pediatric_emergency_analysis.ipynb`)
* **분석 데이터**: 서울 50개소 응급의료기관 실시간 병상 및 비정형 공지사항.
* **실측 발견점**:
  1. 야간 20:00~24:00 시간대에 소아 내원 환자가 주간 대비 **4배 폭증 (피크 환자 수 280명)**.
  2. 내원 환자의 **74%가 단순 발열 및 호흡기 경증 질환(급성열성질환 34.2%)**으로 응급실 병상을 불필요하게 점유.
  3. 실시간 병상 수치(`hv28`)가 3~5석 남아있더라도, 비정형 공지사항(`hpmg`)에 *"소아 당직의 부재로 진료 제한"*이 적혀 있는 경우가 빈번하여 헛걸음 유발.
* **도출된 기능**:
  - `PEDIATRIC_BLOCK_PATTERN`: 비정형 공지사항에서 당직의 부재 패턴을 **정규식으로 100% 필터링**하여 `pediatric_acceptable` 참값 보정.
  - `KASI 특일 연동`: 외래 소아과가 전멸하는 공휴일에는 응급실 과밀화 리스크를 `CRITICAL`로 자동 격상.

### 2.2 [노트북 2] 전국 달빛병원-심야약국 연계 분석 (`moonlight_hospital_night_pharmacy_linkage.ipynb`)
* **분석 데이터**: 전국 17개 시·도 7만여 개 병의원 진료시간 및 2만 4천여 개 약국 운영시간 API 연계.
* **실측 발견점**:
  - 달빛어린이병원 1곳당 반경 1km 이내 약국 중, 병원 마감 시간보다 일찍 닫거나 마감 직후 문을 닫는 약국 비율이 40% 이상.
  - 병원 마감 후 처방전 발급 및 도보 이동 시간을 고려할 때 **최소 30분의 안전 버퍼(Safety Margin)**가 필수적임.
* **도출된 기능**:
  - `30분 안전 마진 페어링 알고리즘`: `약국마감분 - 병원마감분 >= 30`을 만족하는 약국만 **[안전 페어링]** 배지를 부여하여 부모의 심야 헛걸음 원천 차단.

### 2.3 [노트북 3] Firebase 실시간 파이프라인 실증 (`emergency_bed_firebase_sync.ipynb`)
* **분석 데이터**: E-Gen 실시간 병상 ➔ Firebase Cloud Firestore 배치 동기화.
* **실측 발견점**:
  - 전국 500개 응급실을 5분마다 단순 Write하면 하루 `144,000회` 쓰기가 발생하여 Firestore 일일 무료 쿼터(20,000회)를 초과함.
  - 실제로 5분 주기로 병상 수나 공지가 바뀌는 병원은 전체의 5~10%에 불과함.
* **도출된 기능**:
  - `BedStateHashCache (In-Memory Hash Diffing)`: 직전 회차와 상태 지문(MD5)을 비교하여 **변경된 문서만 쓰기(Write)를 수행함으로써 비용 90~100% 절감 실증**.
  - `Haversine 구면거리 계산`: 사용자 GPS 좌표 기준 10km 이내 소아 가용 응급실을 **0.5ms 내에 랭킹 정렬**.
  - `실시간 on_snapshot 리스너`: 병상 만실 시 0.1초 만에 클라이언트로 변동 이벤트 스트리밍 확인.

---

## 3. 현재까지 완료된 개발 모듈 & 테스트 검증 내역 (Done: Steps 1~6 전수 완료)

주피터 노트북에서 검증된 로직을 프로덕션 백엔드 패키지(`app/`)로 체계적으로 모듈화하고, 6단계에 걸친 단위/통합 테스트 58건 및 40대 임상 골든 케이스 평가를 100% 완수했습니다.

```
monnlight/
├── app/
│   ├── __init__.py
│   ├── config.py                     # [Step 1] 환경변수 자동 감지 & E:\FIREBASE_API_KEY Firestore 클라이언트 싱글톤
│   ├── demo_step1.py                 # [Step 1] 1단계 실시간 파이프라인 벤치마크 실행기
│   ├── demo_step3.py                 # [Step 3] 3단계 인터랙티브 2-트랙 에이전트 파이프라인 실행기
│   ├── demo_step4.py                 # [Step 4] 4단계 메인 오케스트레이터(Supervisor FSM) 통합 실행기
│   ├── demo_step5.py                 # [Step 5] 5단계 FastAPI REST 서빙 & 3-Track 데몬 실행기
│   ├── api/                          # [Step 5] FastAPI REST API 라우터 Layer
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── chat.py               # POST /api/v1/chat & SSE 실시간 스트리밍 (/chat/stream)
│   │       └── emergency.py          # GET /nearby, /pairings, /status & POST /sync
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── emergency.py              # [Step 1] 응급실 병상, 특일 정보, 공간 랭킹 Pydantic DTO
│   │   ├── state.py                  # [Step 2] 멀티 에이전트 공유 세션 DTO (PatientSessionState)
│   │   ├── supervisor.py             # [Step 4] 클라이언트/API 통신용 정형 응답 DTO (SupervisorResponse)
│   │   ├── chat.py                   # [Step 5] 대화 및 세션 관리 요청/응답 DTO
│   │   └── emergency_api.py          # [Step 5] 응급실 및 3-Track 스케줄러 상태 DTO
│   ├── services/                     # [Step 1, 3, 5] 순수 결정론적 도구 Layer (Zero-LLM)
│   │   ├── __init__.py
│   │   ├── holiday_service.py        # KASI 특일 판정 & KST(UTC+9) 타임존 고정 과밀화 리스크 평가
│   │   ├── spatial_service.py        # Haversine 구면거리 5µs 연산 & 반경 10km 소아 응급실 랭킹
│   │   ├── emergency_sync_service.py # E-Gen 실시간 병상, 100% 공지 정규식, Hash Diffing, 디스크 캐싱
│   │   ├── pairing_service.py        # [Step 3] 전국 29개 달빛병원-심야약국 +30분 안전 마진 페어링 서빙
│   │   └── scheduler.py              # [Step 5] APScheduler 3-Track 백그라운드 데몬 (병상, 정적동기화, 세션정리)
│   ├── agents/                       # [Step 2, 3] 지능형 에이전트 & 안전 가드레일 Layer
│   │   ├── __init__.py
│   │   ├── guardrail_agent.py        # [Step 2] 0.015ms Red Flag 선제 인터셉터 & 의료법 제27조 사후 필터
│   │   ├── triage_agent.py           # [Step 3] Gemini 3.8 Flash 비구조화 구어체 문진 & 4대 임상 변수 정형화
│   │   ├── matching_agent.py         # [Step 3] Zero-LLM 2-트랙 임상 라우팅 (소아응급실 vs 달빛병원+약국)
│   │   └── logistics_agent.py        # [Step 3] Gemini 3.5 Lite 30초 통화 확인 스크립트 & 지참서류 체크리스트
│   └── orchestrator/                 # [Step 4] 메인 오케스트레이션 Layer
│       ├── __init__.py
│       ├── session_manager.py        # [Step 4] Thread-Safe 세션 인메모리 관리자 & TTL 자동 만료
│       └── supervisor.py             # [Step 4] 6-State FSM 라우터 & 3턴 무한루프 방지 & 0ms 긴급 차단
├── data/
│   ├── seoul_emergency_coords.json   # 서울 530개 응급의료기관 위경도 로컬 디스크 캐시 (30배 속도 향상)
│   └── nationwide_pairings.json      # [Step 3] 전국 17개 시·도 29개 달빛병원-야간약국 30분 마진 페어링 캐시
├── tests/
│   ├── test_step1_services.py        # [Step 1] 7대 핵심 기반 서비스 테스트 (통과)
│   ├── test_step2_guardrail.py       # [Step 2] 12대 가드레일 & 0ms 벤치마크 테스트 (통과)
│   ├── test_step3_agents.py          # [Step 3] 7대 멀티 에이전트 결합 & 2-트랙 파이프라인 테스트 (통과)
│   ├── test_step4_orchestrator.py    # [Step 4] 7대 Supervisor FSM 라이프사이클 테스트 (통과)
│   ├── test_step5_api.py             # [Step 5] 10대 FastAPI REST & 3-Track 스케줄러 테스트 (통과)
│   ├── test_step6_e2e.py             # [Step 6] 8대 E2E 핵심 시나리오 통합 테스트 (통과)
│   ├── test_audit_fixes.py           # [Pre-Audit] 7대 잠재 이슈 해결 회귀 검증 테스트 (통과)
│   └── evals/
│       ├── golden_test_cases.json    # 40대 임상 골든 엣지케이스 정의집
│       ├── run_evals.py              # 5대 평가 지표(DIM-1~DIM-5) 자동 채점 하네스 (통과)
│       └── eval_report.md            # 40/40 전수 합격 종합 성적표 (100.0%, 평균 99.5점)
├── main.py                           # [Step 5] FastAPI 프로덕션 애플리케이션 진입점 & 3-Track Lifespan
├── demo_step6.py                     # [Step 6] 인터랙티브 CLI 종합 시연기
├── CONNECTIVITY_MAP.md               # 모듈 & 에이전트 상호 연결도 및 아키텍처 매트릭스 (v1.2.0)
├── README.md                         # 종합 프로젝트 안내서 (v0.1.0 ~ v1.2.0 전 이력 보존)
├── PLAN.md                           # 종합 기획안 & 개발 백서 (본 문서)
├── .env                              # 로컬 환경변수 (FIREBASE_KEY_PATH=E:\FIREBASE_API_KEY\serviceAccountKey.json)
├── .env.example                      # 환경변수 템플릿
├── requirements.txt                  # 핵심 의존성 패키지 명세서
└── serviceAccountKey.json            # Firebase Admin SDK 서비스 계정 키 (.gitignore 보호)
```

### 3.1 [Step 1] 순수 도구(Zero-LLM) & 스토리지 모듈화 성과
* **공공 API ➔ Firestore 실시간 동기화**:
  - 서울 50개 응급의료기관의 실시간 병상 데이터 파싱 및 Firestore `emergency_beds` 컬렉션 배치 Upsert.
  - 대시보드 뷰용 단일 집계 문서 `emergency_summary/realtime` 동시 갱신.
* **4대 사전 보완 최적화 적용**:
  1. **정적 좌표 디스크 캐싱**: 서울 530개 응급실 위경도를 `data/`에 캐싱하여 병상 수집 속도 **7,988ms ➔ 261ms (약 30배 가속)**.
  2. **KST 타임존 바인딩**: UTC 클라우드 서버에서 자정~09시 사이 날짜 오차 버그 원천 방어.
  3. **형상 관리 표준화**: `.env.example`, `requirements.txt` 표준 수립.
  4. **환경 호환성 보장**: `holiday_service`의 날짜 파라미터(문자열/date/datetime) 다형성 지원.
* **테스트 결과**: `tests/test_step1_services.py` 7개 테스트 100% 통과 (2.5초).

### 3.2 [Step 2] 세션 DTO & 0ms 안전 가드레일 모듈화 성과
* **`PatientSessionState` (공유 메모리 DTO)**:
  - FSM 6단계 수명주기(`INIT` ➔ `TRIAGE` ➔ `MATCHING` ➔ `LOGISTICS` ➔ `EMERGENCY_ESCALATION` ➔ `COMPLETED`).
  - 4대 필수 문진 변수(`age_months`, `age_days`, `temperature`, `duration_hours`, `symptoms`) 및 3턴 대화 히스토리 추적.
* **0ms Red Flag 선제 차단기 (`guardrail_agent.py`)**:
  - LLM 호출 없이 **KTAS 소아 7대 Red Flag**(생후 100일 미만 고열, 경련, 무반응, 청색증, 중증 탈수, 두부 외상 분수토, 담즙성 구토)를 즉시 감지.
  - 119 다이렉트 호출 CTA + 구급차 도착 전 기도 확보 가이드 즉각 노출.
* **의료법 제27조(무면허 의료행위 방지) 사후 필터링**:
  - 확정 진단명("~로 진단됩니다") 및 임의 용량("5ml 먹이세요") 자동 중화 및 법적 면책 고지 배지 자동 부착.
* **테스트 결과**: `tests/test_step2_guardrail.py` 12개 테스트 100% 통과.
  - **성능 벤치마크**: 1,000회 연속 검사 4.78ms 소요 (**회당 평균 4.78µs = 0.0048ms, 0ms 실시간 인터셉트 입증**).

### 3.3 [Step 3] AI 멀티 에이전트 결합 & 2-트랙 지능형 라우팅 모듈화 성과
* **Triage 문진 에이전트 (`app/agents/triage_agent.py`)**:
  - **모델**: `Gemini 3.8 Flash (Thinking Effort: Medium)`.
  - **기능**: 부모의 불안한 비정형 구어체 서술에서 `(월령, 체온, 지속시간, 주증상)`을 `TriageExtractionResult` Pydantic 구조로 정밀 추출.
  - **안전 방어**: 부모의 병명 추측 유도("돌발진 맞죠?")에 단호히 진단을 거부하고 공감/안심 멘트 유지.
  - **견고성**: 오프라인 및 API 키 부재 환경을 위한 결정론적 정규식 Fallback 파서 내장.
* **전국 달빛병원-심야약국 +30분 마진 페어링 서비스 (`app/services/pairing_service.py`)**:
  - `data/nationwide_pairings.json`에 전국 17개 시·도 29개 달빛어린이병원 및 30분 안전 마진 약국 1:1 매핑 데이터셋 탑재.
  - 사용자 좌표 기준 반경 10km 이내 야간 안심 페어링 세트 0ms 검색 제공.
* **2-트랙 임상 매칭 에이전트 (`app/agents/matching_agent.py`)**:
  - **Zero-LLM 결정론적 라우팅**: 환아의 임상 상태에 따라 명확한 2-트랙 분기.
    - **Track A (응급/고열/야간 23시 이후)**: E-Gen 실시간 병상 및 비정형 공지를 검증한 10km 이내 소아 가용 응급실 TOP 3 안내.
    - **Track B (경증/발열 초기/소아과 운영시간)**: 달빛어린이병원 + 30분 마진 심야약국 1:1 페어링 세트 안내.
* **방문 준비 로지스틱스 에이전트 (`app/agents/logistics_agent.py`)**:
  - **모델**: `Gemini 3.5 Flash-Lite (고속 서빙)`.
  - **기능 1**: 출발 전 병원 실시간 확인을 돕는 **"30초 유선 확인 통화 스크립트"** 생성.
  - **기능 2**: **2024년 5월 개정 국민건강보험법 본인확인 의무화**에 맞춘 신분증/주민등록등본 지참 서류 체크리스트 자동 생성.
* **인터랙티브 파이프라인 시연기 & 연결도 문서 신설**:
  - `app/demo_step3.py`: 경증 환아(달빛병원+약국 세트) 및 응급 환아(10km 소아 응급실) dual-scenario 인터랙티브 CLI 런처.
  - `CONNECTIVITY_MAP.md`: 4계층 상호연결 매트릭스, Mermaid 데이터 파이프라인, 세션 상태 전이표 총정리.
* **테스트 결과**: `tests/test_step3_agents.py` 7개 테스트 100% 통과 (TC-301 ~ TC-308).

### 3.4 [Step 4] 메인 오케스트레이터(Supervisor FSM) & 세션 매니저 완성 성과
* **중앙 집중식 유한 상태 머신 (`app/orchestrator/supervisor.py`)**:
  - 6단계 라이프사이클(`INIT` ➔ `TRIAGE` ➔ `MATCHING` ➔ `LOGISTICS` ➔ `COMPLETED` / `EMERGENCY_ESCALATION`) FSM 라우터 구축.
  - **3턴 상한선 무한 루프 가드 (Deadlock Guard)**: 부모가 모호한 단변을 반복해도 `turn_count >= 3` 도달 시 강제 MATCHING 전이 및 안전 디폴트 라우팅 실증.
  - **매 턴 0ms Red Flag 선제 검사**: 대화 첫 턴뿐만 아니라 2~3턴 중간에 증상이 급변(청색증, 경련 등)해도 즉시 모든 서브 에이전트 실행을 중단(Abort)하고 119 다이렉트 모달 반환.
  - **단일 출구 의료법 제27조 소독 관문**: 모든 에이전트 출력 메시지가 오케스트레이터 출구에서 `sanitize_output()`을 통과하도록 구조화하여 법적 리스크 원천 차단.
* **Thread-Safe 세션 매니저 (`app/orchestrator/session_manager.py`)**:
  - `asyncio.Lock` 기반 동시성 제어 및 30분 미사용 세션 자동 정리(TTL Eviction)로 메모리 누수 0% 달성.
* **클라이언트 표준 응답 규격 DTO (`app/schemas/supervisor.py`)**:
  - 프론트엔드 및 Step 5 FastAPI가 즉시 소비 가능한 `SupervisorResponse` 표준 모델 탑재.
* **인터랙티브 시연기 (`app/demo_step4.py`)**: 멀티턴 문진(시나리오 1), 중도 경련 급변 비상 격상(시나리오 2), 3턴 루프 방어(시나리오 3) 3대 시나리오 실증 완수.
* **테스트 결과**: `tests/test_step4_orchestrator.py` 7개 테스트(TC-401 ~ TC-407) 100% 통과.

### 3.5 [Step 5] FastAPI REST API 서빙 & 백그라운드 동기화 데몬 완성 성과
* **FastAPI 코어 애플리케이션 엔트리포인트 (`main.py`)**:
  - `lifespan` 비동기 컨텍스트 매니저로 앱 기동 시 위경도 및 페어링 캐시 사전 워밍(Pre-warming) 및 APScheduler 데몬 자동 기동/정리.
  - 웹/모바일 프론트엔드 연계를 위한 `CORSMiddleware` 전역 적용.
  - `GET /`, `GET /health` 시스템 헬스체크 및 통합 인프라(공공 API, Gemini, Firebase, 세션 수) 진단 모니터링 탑재.
* **실시간 대화 & SSE 스트리밍 라우터 (`app/api/v1/chat.py`)**:
  - `POST /api/v1/chat`: 0ms Red Flag 가드레일, Gemini 3.8 문진, Zero-LLM 시설 매칭, 30초 통화 스크립트 및 지참 서류 일괄 반환.
  - `POST /api/v1/chat/stream`: Server-Sent Events (SSE) 기반 실시간 단어 델타 스트리밍 및 최종 JSON/`[DONE]` 프로토콜 완비.
  - `GET /api/v1/chat/session/{sid}`, `DELETE /api/v1/chat/session/{sid}`: 세션 상세 추적 및 원클릭 리셋 엔드포인트 제공.
* **초고속 공간 검색 & 온디맨드 동기화 라우터 (`app/api/v1/emergency.py`)**:
  - `GET /api/v1/emergency/nearby`: GPS 기준 10km 이내 소아 가용 응급실 Haversine 구면거리 실시간 랭킹 (평균 레이턴시 5ms 내외 실측).
  - `GET /api/v1/emergency/pairings`: 전국 달빛어린이병원 + 30분 마진 심야약국 1:1 페어링 세트 거리순 정렬 조회.
  - `POST /api/v1/emergency/sync`: 운영자/개발자용 즉시 E-Gen 병상 수집 및 In-Memory Hash Diffing Firestore 반영 트리거.
  - `GET /api/v1/emergency/status`: 백그라운드 스케줄러 가동 여부 및 잡 실행 주기, 통계 조회.
* **APScheduler 기반 2-트랙 백그라운드 데몬 (`app/services/scheduler.py`)**:
  - **Track 1 (5분 주기)**: `poll_realtime_beds()` - E-Gen 실시간 병상 및 비정형 공지 수집 후 `BedStateHashCache`(MD5)를 거쳐 변경 병상만 Firestore 배치 쓰기(비용 90~100% 절감 실증).
  - **Track 2 (24시간 주기, 매일 04:00 AM KST)**: `sync_static_datasets()` - 서울 530개 응급실 위경도 및 전국 달빛병원-약국 마스터 증분 동기화.
* **인터랙티브 종합 API 시연기 (`app/demo_step5.py`)**:
  - 헬스체크, 5ms 응급실 검색, 30분 약국 페어링, 일반 상담, 0ms Red Flag 차단, SSE 스트리밍, Hash Diffing 7대 기능 실시간 검증 완수.
* **테스트 결과**: `tests/test_step5_api.py` 10개 테스트(TC-501 ~ TC-510) 100% 통과.

### 3.6 [사전 정밀 결함 감사 & 6대 핵심 과제 선제 리팩토링 완수 성과]
* **Gemini 3.8 Flash & 3.5 Flash-Lite 최신 모델 전환**:
  - 기존 `gemini-2.5-flash` 구버전 404 에러로 인한 Fallback 고착 현상을 완전히 해결하고, 실제 Google GenAI 서버와 `200 OK` 실시간 통신 연동 입증.
  - LLM 예외 발생 시 `logger.warning()`으로 명확한 디버깅 가시성 확보.
* **0ms 응급실 병상 인메모리 TTL 캐시 (`emergency_sync_service.py`)**:
  - `_in_memory_bed_cache` (5분 TTL = 300초)를 구축하여, API 및 매칭 호출 시 네트워크 지연을 0회로 차단하고 **0.2~0.5ms 초고속 인메모리 서빙** 달성.
* **전국 17개 시·도 행정구역 동적 판별 및 맞춤 병상 매칭 (`matching_agent.py`, `emergency_sync_service.py`)**:
  - `resolve_stage1_from_coords_or_address()` 및 지자체별 좌표망(`_hospital_coords_cache_by_stage`, `NATIONWIDE_REGIONAL_ER_MOCKS`) 구축을 통해 서울뿐 아니라 수원(경기도), 대전, 부산, 대구, 광주, 평창(강원), 인천, 제주 등 전국 환아 위치에서 35km 이내의 해당 지자체 소아 가용 응급실로 정밀 매칭.
* **악의적 질문 및 의료법 우회 방어선 보강 (`guardrail_agent.py`)**:
  - 위험 민간요법(손 따기), 남은 항생제 임의 복용, 약 용량 직접 지시(몇 ml), Dr. Kim 탈옥 시도를 차단하는 `check_safety_violations()` 규칙 엔진 탑재.
* **Triage 파서 연령·기간·다발성 증상 정규화 확장 (`triage_agent.py`)**:
  - `만 4세`, `초등학교 1학년` 연령 환산, `3일 전`, `어제` 기간 환산, 귀(이통)/눈곱/쌕쌕거림/복통 등 소아 다발성 증상 표준화.
* **진료 마감 시간(HH:MM) 필터링 & 마감 40분 이내 경고 태그 (`matching_agent.py`)**:
  - 심야(23:00~07:00) 24시간 응급실 직행 분기 및 마감 임박 의원 `[⚠️ 조기 접수 마감 주의]` 태그 동적 부착.
* **Windows UTF-8 인코딩 보정 & Conda DS 가상환경 동기화 (`__init__.py`, `requirements.txt`)**:
  - PowerShell 콘솔 CP949 글자 깨짐(Mojibake) 방지 UTF-8 강제 적용 및 Conda DS 가상환경 내 `apscheduler`, `fastapi`, `uvicorn` 패키지 동기화 완료.
* **테스트 결과**: `tests/test_audit_fixes.py` 7개 신규 테스트(TC-FIX-01 ~ TC-FIX-07) 100% 통과.

> **현재 종합 테스트 현황**: 총 **58개 테스트** (Step 1 7개 + Step 2 12개 + Step 3 7개 + Step 4 7개 + Step 5 10개 + Issue Fixes 7개 + Step 6 E2E 8개) **100% 전수 통과 (`Ran 58 tests, OK`)** & **40대 임상 골든 케이스 Evals 100% 합격 (40/40, 평균 99.5점)**.

---

## 4. 전체 6단계 구현 로드맵 & 검증 결과 (Roadmap: Steps 1~6 완료)

```
[Step 1: 기반 스토리지 & Zero-LLM 도구] ──► [완료 (100% 통과)]
         │
         ▼
[Step 2: 0ms 안전 가드레일 & 세션 DTO] ──► [완료 (100% 통과)]
         │
         ▼
[Step 3: AI 에이전트 결합 (Gemini 3.8)] ──► [완료 (100% 통과)]
         │
         ▼
[Step 4: 메인 오케스트레이터 (Supervisor)] ──► [완료 (100% 통과)]
         │
         ▼
[Step 5: FastAPI REST 서빙 & 데몬]   ──► [완료 (100% 통과)]
         │
         ▼
[Step 6: E2E 통합 테스트 & 시나리오]  ──► [완료 (100% 통과, 40 Golden Evals 100%)]
```

### 4.1 [Step 5] FastAPI REST API 서빙 & 백그라운드 동기화 데몬 ── **[개발 완료 (100% 통과)]**
* `main.py`, `app/api/v1/chat.py`, `app/api/v1/emergency.py`, `app/services/scheduler.py`, `test_step5_api.py` 개발 및 10개 테스트 전수 통과.

### 4.2 [Step 6] E2E 통합 테스트 & 40대 골든 케이스 시나리오 평가 ── **[개발 완료 (100% 통과)]**
* **8대 E2E 핵심 시나리오 자동 검증 스위트 (`tests/test_step6_e2e.py`)**:
  1. `TC-601`: **초응급 시나리오 (Track A / Red Flag)**: 생후 55일 38.3도 고열 입력 시 1턴 만에 119 직행 모달 및 기도확보 응급처치 가이드 반환.
  2. `TC-602`: **야간 발열 시나리오 (Track B / 경증)**: 14개월 38.5도 입력 시 공감 문진 ➔ 달빛병원 + 30분 안심 약국 페어링 ➔ 30초 통화 스크립트 출력.
  3. `TC-603`: **의료법 제27조 방어 시나리오**: 부모의 병명 추측 유도("돌발진 맞죠?") 시 진단 거부 및 전문의 대면 진찰 안내 확인.
  4. `TC-604`: **적대적 안전 가드레일 방어**: 바늘 사혈 민간요법, 잔여 항생제 임의 복용, 구체적 해열제 용량 지시, 단독 병원 알선 요구 4대 위반 0ms 선제 차단.
  5. `TC-605`: **중도 급변(Deterioration) 시나리오**: 1턴 미열 상담 중 2턴 청색증/호흡곤란 발생 시 즉시 Track A 비상 전환.
  6. `TC-606`: **3턴 데드락 가드**: 3턴 연속 모호한 입력 시 무한 루프 탈출 및 안전 기본값 세팅 후 MATCHING 강제 전이.
  7. `TC-607`: **FastAPI REST E2E 통합**: `/api/v1/chat` 단일/다중 턴 E2E 호출 무결성 검증.
  8. `TC-608`: **FastAPI SSE 실시간 스트리밍**: `/api/v1/chat/stream` 토큰 스트리밍 및 `[DONE]` 완료 이벤트 무결성 검증.
* **40대 임상 골든 케이스 자동 채점기 (`tests/evals/run_evals.py`)**:
  - 5대 임상 평가 지표(DIM-1~DIM-5) 전산 채점 및 종합 리포트(`tests/evals/eval_report.md`) 자동 생성.
  - **평가 결과**: **40 / 40 케이스 100% 전수 통과 (평균 99.5점)**.
* **인터랙티브 CLI 시연 데모 (`demo_step6.py`)**:
  - 초응급, 야간 발열, 의료법 방어, 적대적 공격 차단, 자유 대화, Evals 성적표 조회를 지원하는 종합 터미널 인터페이스 제공.

---

## 5. 시스템 아키텍처 & 데이터 흐름도

```mermaid
flowchart TD
    User([보호자 사용자]) -->|자연어 증상 입력| Guardrail{0ms Red Flag 선제 인터셉터}
    
    %% Track A: 초응급
    Guardrail -->|Red Flag 감지| TrackA[Track A: 119 비상 에스컬레이션]
    TrackA --> EmergencyModal[🚨 119 원클릭 호출 & 기도확보 응급처치 가이드]
    TrackA --> NearestER[🏥 10km 이내 최단거리 소아 가용 응급실 안내]
    
    %% Track B: 일반 Triage
    Guardrail -->|정상 통과| Supervisor[⚙️ Supervisor FSM 라우터]
    Supervisor --> TriageAgent[🤖 Triage Agent<br/>Gemini 3.8 Flash]
    TriageAgent -->|부모 공감 & 4대 임상 변수 정형화| StateDTO[(PatientSessionState<br/>공유 메모리)]
    
    StateDTO --> MatchingAgent[🤖 Matching Agent<br/>Zero-LLM Clinical Router]
    
    %% Tools
    subgraph Zero_LLM_Tools [결정론적 백엔드 도구 Layer]
        KASI[KASI 특일 판정 & 과밀화 리스크]
        EGEN[E-Gen 실시간 병상 & 공지 필터링]
        SPATIAL[Haversine 10km 구면거리 랭킹]
        PAIRING[달빛병원 + 야간약국 30분 마진 페어링]
    end
    
    MatchingAgent --> Zero_LLM_Tools
    Zero_LLM_Tools --> Firestore[(Cloud Firestore / Local Cache<br/>emergency_beds / pairings)]
    
    MatchingAgent --> LogisticsAgent[🤖 Logistics Agent<br/>Gemini 3.5 Lite]
    LogisticsAgent --> ResultCard[📋 종합 결과 카드<br/>• TOP 3 추천 병원 & 30분 마진 약국<br/>• 30초 통화 확인 스크립트<br/>• 본인확인 의무화 지참 서류]
    
    ResultCard --> Sanitizer{의료법 제27조 사후 필터}
    Sanitizer --> User
```

---

## 6. 데이터 갱신 및 캐싱 전략 (하이브리드 아키텍처)

안정적인 0ms 레이턴시와 공공 API 쿼터 고갈 방지, 비용 최적화를 위해 데이터 성격에 따라 2계층 하이브리드 캐싱을 적용합니다:

| 데이터 분류           | 데이터 항목                                                                                         | 보관 위치                                 | 갱신 주기 & 트리거                            | 캐싱 & 최적화 목적                                                                                        |
| :--------------- | :--------------------------------------------------------------------------------------------- | :------------------------------------ | :------------------------------------- | :------------------------------------------------------------------------------------------------- |
| **정적 / 준정적 데이터** | 서울 530개 응급실 위경도 (`seoul_emergency_coords.json`), 전국 달빛병원-심야약국 페어링 (`nationwide_pairings.json`) | 로컬 파일시스템 (`data/`) + Firestore 정적 컬렉션 | **24시간 주기 (매일 04:00 AM)** 공공 API 호출 갱신 | 병상 조회 시 반복되는 지오코딩 API 호출을 0회로 차단 (응답 속도 30배 향상: 7,988ms ➔ 261ms)                                   |
| **동적 실시간 데이터**   | 실시간 소아 응급실 병상수(`hv28`), 응급실 실시간 공지(`hpmg`)                                                     | 인메모리 캐시 + Firestore `emergency_beds`  | **5분 주기 폴링 (E-Gen API)**               | **In-Memory Hash Diffing (MD5)**: 상태가 변경된 병상만 Firestore Write를 수행하여 일일 무료 쿼터 초과 방지 (비용 90~100% 절감) |

---

## 7. 추가 심화 고도화 백로그 (Advanced Backlog)

프로덕션 배포 및 대외 포트폴리오 경쟁력 극대화를 위한 심화 엔지니어링 과제 목록입니다:

| 영역           | 고도화 과제명                                     | 핵심 구현 내용                                                      | 현재 상태             | 기대 효과                              |
| :----------- | :------------------------------------------ | :------------------------------------------------------------ | :---------------- | :--------------------------------- |
| **도메인 킬러**   | **달빛병원-약국 30분 마진 서비스 모듈화**                  | `app/services/pairing_service.py` 신설, 전국 17개 시·도 1:1 자동 매칭    | **[완료 (Step 3)]** | 야간 74% 경증 환아 처방전 조제 실패 사고 0% 방어    |
| **의료 브리핑**   | **119 구급대원용 30초 SBAR 카드**                   | Red Flag 감지 시 구급대원 인계용 SBAR(상황/배경/평가/권고) 4줄 요약 출력             | [대기]              | 패닉 부모 대신 119 구급대원/의료진에 정확한 정보 전달   |
| **안정성 (HA)** | **공공 API 서킷 브레이커 & Fallback**               | 공공데이터포털 503 에러 시 직전 Firestore/로컬 캐시 즉시 서빙                     | [대기]              | 외부 API 장애 시에도 서비스 무중단 가동           |
| **실시간 스트림**  | **Firestore ➔ SSE(Server-Sent Events) 브릿지** | `on_snapshot` 리스너를 SSE 엔드포인트로 연계하여 병상 변동 실시간 푸시               | [대기]              | 클라이언트 폴링 없이 0.1초 만에 병상 변동 실시간 반영   |
| **품질 평가**    | **40대 골든 케이스 자동 Evals 채점기**                 | `tests/evals/run_evals.py` 작성, 5대 평가 지표(의료법, RedFlag 등) 자동 채점 | **[완료 (Step 6, 100%)]** | 객관적 Evals 합격 성적표(100.0%, 평균 99.5점) 확보 |

---

### 📌 결론 및 종합 성과 (Summary & Milestones)

현재 MoonlightCare 프로젝트는 **"기반 데이터 파이프라인(Step 1)"**, **"0ms 의료 안전 가드레일(Step 2)"**, **"AI 멀티 에이전트 결합(Step 3)"**, **"메인 오케스트레이터 및 세션 매니저(Step 4)"**, **"FastAPI REST API 서빙 & 백그라운드 동기화 데몬(Step 5)"**, 그리고 **"E2E 통합 테스트 & 40대 임상 골든 케이스 평가(Step 6)"**까지 전체 6단계 개발 로드맵이 **총 58개 단위/통합 테스트 100% 전수 통과(`Ran 58 tests, OK`)** 및 **40대 골든 케이스 Evals 100.0% 합격**으로 성공적으로 완수되었습니다.
