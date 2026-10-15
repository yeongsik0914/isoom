# 🌙 MoonlightCare 종합 기획안 & 개발 백서 (PLAN.md)

> **문서 버전**: v2.1.1 (팀 프로젝트 협업 체계 & 4대 문서 지속 누적 관리 거버넌스 확립)  
> **최종 갱신 일자**: 2026-10-14  
> **핵심 슬로건**: *"야간 소아 응급실 뺑뺑이를 막는 0ms 세이프티 가드레일 & 데이터 기반 2-트랙 지능형 라우터"*  
> **기반 원천**: 주피터 노트북 5권 실증 데이터, 공공데이터포털(NMC/KASI), Firebase Cloud Firestore, Gemini 3.8 Flash (Thinking High) / 3.5 Lite, 2021 공식 소아 KTAS 데이터셋(168개 주증상/841개 세부기준), AsyncCircuitBreaker(3-State FSM), 3-Tier Multi-Storage Fallback(메모리/Firestore/불변JSON)

---

## 📑 목차 (Table of Contents)

1. [프로젝트 기획 배경 & 핵심 문제 정의](#1-프로젝트-기획-배경--핵심-문제-정의)
2. [데이터 분석 기반의 목적별 기능 도출 과정 (Notebook 1~5 Insights)](#2-데이터-분석-기반의-목적별-기능-도출-과정-notebook-15-insights)
3. [현재까지 완료된 개발 모듈 & 소스코드 체계 (Done: Steps 1~7 & Red Flag V2)](#3-현재까지-완료된-개발-모듈--소스코드-체계-done-steps-17--red-flag-v2)
4. [차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)](#4-차세대-2계층-안전-감시망-two-tier-red-flag-v2-architecture)
5. [전체 구현 로드맵 & 누적 테스트 검증 결과 (74개 테스트 전수 통과)](#5-전체-구현-로드맵--누적-테스트-검증-결과-74개-테스트-전수-통과)
   - [5.1 종합 테스트 현황 (총 74개 단위/통합 테스트 100% 무결점 통과)](#51-종합-테스트-현황-총-74개-단위통합-테스트-100-무결점-통과)
   - [5.2 Step 7: 공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback 세부 성과](#52-step-7-공공-api-서킷-브레이커--3-tier-multi-storage-fallback-세부-성과)
6. [시스템 아키텍처 & 2계층 데이터 흐름도](#6-시스템-아키텍처--2계층-데이터-흐름도)
7. [데이터 갱신 및 캐싱 전략 (하이브리드 아키텍처)](#7-데이터-갱신-및-캐싱-전략-하이브리드-아키텍처)
8. [추가 심화 고도화 백로그 (Advanced Backlog)](#8-추가-심화-고도화-백로그-advanced-backlog)
9. [팀 프로젝트 협업 체계 & 4대 문서 지속 누적 관리 거버넌스](#9-팀-프로젝트-협업-체계--4대-문서-지속-누적-관리-거버넌스)
10. [프론트엔드 UI/UX 아키텍처 & 화면 연동 로드맵](#10-프론트엔드-uiux-아키텍처--화면-연동-로드맵)
    - [10.5 '아이숨(i-Soom)' 화이트 & 코발트 블루 디자인 시스템](#105-아이숨i-soom-화이트--코발트-블루-디자인-시스템-및-stitch-화면-자산-2026-10-14-확정)
    - [10.6 '아이숨(Aisum)' 신규 전용 Stitch 프로젝트 및 3대 핵심 화면](#106-아이숨-aisum-신규-전용-stitch-프로젝트-및-calm-harbor-라이트-테마-3대-핵심-화면-2026-10-14-완결)
    - [10.7 '아이숨 (Aisum)' 프론트엔드 전용 워크스페이스(frontend/templates/) 구축 및 HTML/CSS 모듈화 이관](#107-아이숨-aisum-프론트엔드-전용-워크스페이스frontendtemplates-구축-및-htmlcss-모듈화-이관-2026-10-14-완결)
    - [10.8 사전 처치정보 및 법적 안내 모달 다이얼로그(반투명 오버레이, 취소/확인) 화면 구현](#108-사전-처치정보-및-법적-안내-모달-다이얼로그반투명-오버레이-취소확인-화면-구현-2026-10-14-완결)
    - [10.9 사용자 증상 프롬프트 입력 페이지(Underline Input & 확인 CTA) 구현](#109-사용자-증상-프롬프트-입력-페이지underline-input--확인-cta-구현-2026-10-14-완결)

---

## 1. 프로젝트 기획 배경 & 핵심 문제 정의

### 1.1 사회적 배경: "왜 야간 소아 응급실 뺑뺑이가 반복되는가?"
* **소아청소년과 전문의 부족**: 심야 시간대 대학병원 및 권역응급의료센터조차 소아 당직의 부재로 "소아 진료 불가" 공지를 수시로 띄움.
* **경증 환자의 응급실 쏠림 (74%)**: 야간에 문을 여는 동네 의원을 찾지 못한 부모들이 단순 미열/감기 환아를 데리고 권역응급센터로 몰려 대기 시간이 3~5시간으로 폭증하고, 정작 중증 환아(KTAS 1~2)의 골든타임이 침해됨.
* **심야 처방전 조제 사고**: 야간에 진료하는 달빛어린이병원을 간신히 찾아 진료를 받았으나, 인근 약국이 먼저 문을 닫아 처방약을 짓지 못하고 발을 동동 구르는 현장 결함 발생.
* **AI의 임상 오분류(Undertriage) 위험**: 보호자의 일시적 안도성 표현("열은 내렸다", "지금은 깨어났다")에 현혹되어 중증 질환(장중첩증, 크룹, 수지절단, 신생아 발열)을 경증으로 오판하는 안전 위험 존재.

### 1.2 MoonlightCare의 해결책: "결정론적 2-트랙 스마트 라우팅 & 2계층 감시망"
1. **Pass 1 (0ms 정규식 인터셉터)**: 생후 100일 미만 38도 고열, 경련, 청색증, 수지절단, 장중첩증 등 12대 절대적 위급 상황을 LLM 지연 없이 **26µs(0.026ms) 안에 119 구급차 및 소아 가용 응급실로 직행**.
2. **Pass 2 (Direct Grounded Gemini 3.8 Flash Thinking High)**: 0ms 정규식을 우회하는 복합/비정형 문맥을 168개 공식 KTAS 지식 베이스(~8,500 토큰)를 직접 주입받아 완독 감별(언더트리아제 0% 수호).
3. **Track A (중증 / Red Flag / KTAS 1~2)**: 119 구급차 호출, 기도확보 응급처치 가이드, 최단거리 소아전문응급의료센터 매칭 (약국 배제).
4. **Track B (경증 / 일반 야간외래 / KTAS 3~5)**: 부모의 불안을 공감 문진하여 진료 가능한 달빛어린이병원과 **30분 이상 여유 있게 영업하는 심야 약국 세트를 1:1 페어링 매칭**.

---

## 2. 데이터 분석 기반의 목적별 기능 도출 과정 (Notebook 1~5 Insights)

본 프로젝트의 모든 백엔드 기능은 가상의 가정이 아니라, **실제 국립중앙의료원(NMC), 한국천문연구원(KASI) 공공데이터 및 보건복지부 2021 소아 KTAS 데이터셋을 주피터 노트북 5권으로 정밀 분석한 실측 결과**를 기반으로 설계되었습니다.

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

### 2.4 [노트북 4] 소아 KTAS 파이프라인 비교 고찰 (`gemini_ktas_pediatric_redflag_pipeline.ipynb`)
* **분석 데이터**: 168개 소아 KTAS 주증상 및 비정형 보호자 질의 시나리오.
* **실측 발견점**:
  - 구버전 키워드 검색 기반 RAG(`retrieve_top_k_symptoms`)는 비정형 문맥에서 유사도 점수 0.0을 반환하며 관련 없는 엉뚱한 증상(`001: 심정지`, `201: 동상`)을 컨텍스트로 전달하여 환각(오분류)을 유발함.
  - `gemini-4-argon` 모델은 엔터프라이즈 화이트리스트 제한(HTTP 403)이 존재하며, 실시간 트리아제에는 `gemini-3.8-flash`의 Thinking 모드가 최적의 비용 대비 레이턴시/정확도 균형을 제공함.

### 2.5 [노트북 5] 차세대 Direct Grounded KTAS 엔진 (`gemini_ktas_v2.ipynb`)
* **핵심 혁신**:
  - 키워드 검색 RAG를 폐기하고, 168개 공식 주증상 전체(~8,500 토큰)를 **Direct Context Grounding**으로 프롬프트에 직접 주입.
  - Gemini 3.8 Flash Thinking High (`thinking_budget=1024`)를 통해 문장 전반부의 안도성 서술("정신은 차렸다")에 속지 않고 문장 후반부의 전신 상태(Ill-appearing)와 시간 경과를 완독 감별.
  - **실측 성과**: Red Flag 민감도 100%, 언더트리아제 0%, 평균 레이턴시 3.1초 달성.

---

## 3. 현재까지 완료된 개발 모듈 & 소스코드 체계 (Done: Steps 1~7 & Red Flag V2)

프로덕션 백엔드 패키지(`app/`)는 7단계 전 과정 모듈화와 Red Flag V2 고도화, 그리고 공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback 구축을 완료하였으며, 단위/통합 테스트 74건 및 40대 임상 골든 케이스 평가를 100% 완수했습니다.

```
monnlight/
├── app/
│   ├── __init__.py
│   ├── config.py                     # [Step 1] 환경변수 & Firestore 싱글톤 바인딩
│   ├── demo_step1.py ~ demo_step6.py # [Step 1~6] 단계별 인터랙티브 CLI 시연기
│   ├── api/                          # [Step 5, 7] FastAPI REST API 라우터 Layer
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── chat.py               # POST /api/v1/chat & SSE 실시간 스트리밍 (/chat/stream)
│   │       └── emergency.py          # GET /nearby (신선도 메타 & 경고 배지), /pairings, /status & POST /sync
│   ├── schemas/
│   │   ├── emergency.py              # [Step 1, 7] 응급실 병상, DataFreshnessMeta DTO
│   │   ├── state.py                  # [Step 2 & V2] KTAS 정밀 메타데이터 세션 DTO (PatientSessionState)
│   │   ├── supervisor.py             # [Step 4] 클라이언트/API 통신용 정형 응답 DTO (SupervisorResponse)
│   │   ├── chat.py                   # [Step 5] 대화 및 세션 관리 요청/응답 DTO
│   │   └── emergency_api.py          # [Step 5, 7] 응급실 (data_freshness 탑재) 및 3-Track 스케줄러 상태 DTO
│   ├── services/                     # [Step 1, 3, 5, 7] 순수 결정론적 도구 Layer (Zero-LLM)
│   │   ├── circuit_breaker.py        # [Step 7] AsyncCircuitBreaker (3-State FSM, 60s 쿨다운, 3회 임계치, 무의존성)
│   │   ├── holiday_service.py        # KASI 특일 판정 & KST(UTC+9) 타임존 고정 과밀화 리스크 평가
│   │   ├── spatial_service.py        # Haversine 구면거리 5µs 연산 & 반경 10km 소아 응급실 랭킹
│   │   ├── emergency_sync_service.py # [Step 1, 7] E-Gen 실시간 병상, 100% 공지 정규식, Hash Diffing, 3-Tier Fallback Hierarchy
│   │   ├── pairing_service.py        # 전국 29개 달빛병원-심야약국 +30분 안전 마진 페어링 서빙
│   │   └── scheduler.py              # [Step 5, 7] APScheduler 3-Track 데몬 (병상, 정적동기화, 세션정리) & 서킷 오픈 격리
│   ├── agents/                       # [Step 2, 3 & V2] 지능형 에이전트 & 안전 가드레일 Layer
│   │   ├── guardrail_agent.py        # [Step 2 & V2] 0ms 12대 Red Flag 1차 인터셉터 & 의료법 제27조 사후 소독
│   │   ├── triage_agent.py           # [Step 3 & V2] Gemini 3.8 Flash Thinking + 168개 KTAS 주증상 Direct Grounding
│   │   ├── matching_agent.py         # Zero-LLM 2-트랙 임상 라우팅 (소아응급실 vs 달빛병원+약국)
│   │   └── logistics_agent.py        # Gemini 3.5 Lite 30초 통화 확인 스크립트 & 지참서류 체크리스트
│   └── orchestrator/                 # [Step 4 & V2] 메인 오케스트레이션 Layer
│       ├── session_manager.py        # Thread-Safe 세션 인메모리 관리자 & 30분 TTL 자동 만료
│       └── supervisor.py             # 6-State FSM 라우터 & 3턴 무한루프 가드 & Tier 1/2 Red Flag 즉시 긴급 격상
├── data/
│   ├── seoul_emergency_coords.json   # 서울 530개 응급의료기관 위경도 로컬 디스크 캐시 (30배 속도 향상)
│   ├── nationwide_pairings.json      # 전국 17개 시·도 29개 달빛병원-야간약국 30분 마진 페어링 캐시
│   ├── immutable_baseline_beds.json  # [Step 7] 전국 42개 핵심 응급실 불변 기준 병상 JSON (Tier 3 로컬 폴백)
│   └── ktas_pediatric_dataset.json   # [V2] 2021 공식 소아 KTAS 168개 주증상/841개 세부기준 지식 베이스
├── notebooks/
│   ├── egen_pediatric_emergency_analysis.ipynb
│   ├── moonlight_hospital_night_pharmacy_linkage.ipynb
│   ├── emergency_bed_firebase_sync.ipynb
│   ├── gemini_ktas_pediatric_redflag_pipeline.ipynb
│   └── gemini_ktas_v2.ipynb          # [V2] Gemini 3.8 Flash Thinking High & 50대 시나리오 벤치마크 검증 노트북
├── tests/
│   ├── test_step1_services.py        # [Step 1] 7대 핵심 기반 서비스 테스트 (통과)
│   ├── test_step2_guardrail.py       # [Step 2] 12대 가드레일 & 0ms 벤치마크 테스트 (통과, 38µs)
│   ├── test_redflag_v2_upgrade.py    # [V2 고도화] 8대 KTAS 5대 신규룰 & FSM/Thinking 검증 테스트 (통과)
│   ├── test_step3_agents.py          # [Step 3] 7대 멀티 에이전트 결합 & 2-트랙 파이프라인 테스트 (통과)
│   ├── test_step4_orchestrator.py    # [Step 4] 7대 Supervisor FSM 라이프사이클 테스트 (통과)
│   ├── test_step5_api.py             # [Step 5] 10대 FastAPI REST & 3-Track 스케줄러 테스트 (통과)
│   ├── test_step6_e2e.py             # [Step 6] 8대 E2E 핵심 시나리오 통합 테스트 (통과)
│   ├── test_step7_circuit_breaker.py # [Step 7] 8대 서킷브레이커 FSM & 3-Tier Multi-Storage Fallback 테스트 (통과)
│   ├── test_audit_fixes.py           # [Pre-Audit] 7대 잠재 이슈 해결 회귀 검증 테스트 (통과)
│   └── evals/
│       ├── golden_test_cases.json    # 40대 임상 골든 엣지케이스 정의집
│       ├── run_evals.py              # 5대 평가 지표 자동 채점 하네스 (통과)
│       └── eval_report.md            # 40/40 전수 합격 종합 성적표 (100.0%, 평균 99.5점)
├── docs/
│   ├── README.md                     # 기술 기획 문서 허브 목차
│   ├── PROJECT_PLAN.md               # 종합 기획서 (PRD)
│   ├── KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md
│   ├── DATABASE_DESIGN.md
│   ├── DATA_CONSIDERATIONS.md
│   ├── EMERGENCY_DDK_COMPARISON_AND_IMPROVEMENT.md
│   ├── NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md
│   ├── BACKEND_AND_AGENT_IMPLEMENTATION_ROADMAP.md
│   ├── REDFLAG_MODULE_V2_UPGRADE_SPECIFICATION.md              # [V2 고도화 설계서]
│   ├── PUBLIC_API_CIRCUIT_BREAKER_AND_FALLBACK_SPECIFICATION.md # [Step 7 서킷브레이커 & 폴백 설계서]
│   └── VIBE_CODING_ROADMAP.md
├── main.py                           # FastAPI 프로덕션 엔트리포인트
├── CONNECTIVITY_MAP.md               # 모듈 & 에이전트 상호 연결 매트릭스 (v2.1.0)
├── Answer-영식.md                    # 공식 질의응답 아카이브 (Q1~Q36)
└── PLAN.md                           # 종합 기획안 & 개발 백서 (본 문서)
```


---

## 4. 차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)

소아 골든타임 수호를 위해 [REDFLAG_MODULE_V2_UPGRADE_SPECIFICATION.md](file:///e:/monnlight/docs/REDFLAG_MODULE_V2_UPGRADE_SPECIFICATION.md)에 기술된 **2계층 심층 감시선(Two-Tier Deep Defense)**을 프로덕션 백엔드에 완벽히 이식하였습니다.

```
[보호자 자연어 입력]
        │
        ▼
[Tier 1: 0ms 정규식 인터셉터] ──(12대 위급 패턴 매칭)──► 🚨 즉시 119 격상 (KTAS 1~2, 26µs)
        │ (미탐지 / 비정형 문맥)
        ▼
[Tier 2: Gemini 3.8 Flash Thinking + 168개 KTAS Direct Grounding]
        │
        ├──► KTAS 1~2 감별 (비정형 문맥 완독, 시간차 호전 감별) ──► 🚨 Supervisor 긴급 격상
        └──► KTAS 3~5 감별 ──► 일반 트랙 (달빛병원 + 30분 마진 약국 매칭)
```

### 4.1 Tier 1: 0ms 결정론적 인터셉터 (Pass 1)
* **모듈**: `app/agents/guardrail_agent.py` (`check_red_flag_instant`)
* **레이턴시**: 평균 **26.43µs (0.026ms)**, API 비용 0원.
* **12대 절대 위급 규칙**:
  1. 생후 100일 미만 38.0℃ 이상 고열 (`NACRS 852`)
  2. 열성 경련 / 활동성 발작 (`NACRS 405`)
  3. 무반응 / 극심한 의식 저하 (`NACRS 402`)
  4. 흉벽 함몰 / 청색증 / 비익 호흡 (`NACRS 651`)
  5. 8시간 이상 무뇨 중증 탈수 (`NACRS 007`)
  6. 두부 외상 후 반복 구토 / 기면 (`NACRS 407`)
  7. 초록색 담즙성 분수토 (`NACRS 407`)
  8. **[V2 신규] 외상성 사지/수지 절단 (`NACRS 553`)**
  9. **[V2 신규] 돌발 실신 후 발열/비정형 처짐 (`NACRS 008`)**
  10. **[V2 신규] 소아 장중첩증 (주기적 복통 + 딸기잼 혈변, `NACRS 260`)**
  11. **[V2 신규] 상기도 폐쇄 / 크룹 협착음 / 침흘림 (`NACRS 610`)**
  12. **[V2 신규] 안면·수부 2도 이상 중증 화상 (`NACRS 705`)**

### 4.2 Tier 2: Direct Grounded Gemini 3.8 Flash Thinking (Pass 2)
* **모듈**: `app/agents/triage_agent.py` (`TriageAgent`)
* **핵심 원리**:
  - `data/ktas_pediatric_dataset.json`의 168개 주증상 지식 베이스를 인메모리 싱글톤으로 캐싱하여 프롬프트에 직접 주입.
  - `thinking_budget=1024`를 설정하여 다변적 시간 경과와 전신 상태(Ill-appearing vs Well-appearing)를 완독 추론.
  - 고열이 있었으나 해열제 복용 후 땀을 흘리며 식사/놀이가 완전히 회복된 소아는 KTAS 4단계(준응급)로 정확히 감별하여 불필요한 119 출동(False Positive) 방어.
* **오케스트레이터 연동**:
  - `app/orchestrator/supervisor.py`에서 Step 3 Triage 직후 `state.is_red_flag`를 즉시 검사하여, Tier 2에서 감별된 Red Flag도 즉시 `EMERGENCY_ESCALATION`으로 격상.

---

## 5. 전체 구현 로드맵 & 누적 테스트 검증 결과 (74개 테스트 전수 통과)

```
[Step 1: 기반 스토리지 & Zero-LLM 도구] ──────► [완료 (100% 통과)]
         │
         ▼
[Step 2: 0ms 안전 가드레일 & 세션 DTO] ──────► [완료 (100% 통과, 38µs)]
         │
         ▼
[Step 3: AI 에이전트 결합 (Gemini 3.8)] ──────► [완료 (100% 통과)]
         │
         ▼
[Step 4: 메인 오케스트레이터 (Supervisor)] ──► [완료 (100% 통과)]
         │
         ▼
[Step 5: FastAPI REST 서빙 & 데몬]   ────────► [완료 (100% 통과)]
         │
         ▼
[Step 6: E2E 통합 테스트 & 시나리오] ────────► [완료 (100% 통과, 40 Golden Evals 100%)]
         │
         ▼
[V2 Upgrade: 차세대 2계층 Red Flag 결합] ────► [완료 (신규 8개 테스트 100% 통과)]
         │
         ▼
[Step 7: 공공 API 서킷브레이커 & 3계층 Fallback] ► [완료 (신규 8개 테스트 100% 통과)]
```

### 5.1 종합 테스트 현황 (총 74개 단위/통합 테스트 100% 무결점 통과)

| 테스트 스위트 파일 | 검증 영역 및 테스트 케이스 | 테스트 수 | 결과 |
| :--- | :--- | :---: | :---: |
| [**`test_step1_services.py`**](file:///e:/monnlight/tests/test_step1_services.py) | KASI 특일, NMC 병상 파싱, MD5 Hash Diffing, Haversine 정렬 | 7개 | **100% PASS** |
| [**`test_step2_guardrail.py`**](file:///e:/monnlight/tests/test_step2_guardrail.py) | 0ms 가드레일 7대 룰, 의료법 제27조, 1,000회 벤치마크 (38µs) | 12개 | **100% PASS** |
| [**`test_redflag_v2_upgrade.py`**](file:///e:/monnlight/tests/test_redflag_v2_upgrade.py) | **[V2 신규] 5대 신규룰, 스키마 직렬화, FSM 긴급전이, Thinking 결합** | **8개** | **100% PASS** |
| [**`test_step3_agents.py`**](file:///e:/monnlight/tests/test_step3_agents.py) | Triage(Gemini 3.8), Matching(2-Track), Logistics(30초 스크립트) | 7개 | **100% PASS** |
| [**`test_step4_orchestrator.py`**](file:///e:/monnlight/tests/test_step4_orchestrator.py) | 6-State FSM, 3턴 데드락 가드, 중도 급변 감지, 단일 출구 소독 | 7개 | **100% PASS** |
| [**`test_step5_api.py`**](file:///e:/monnlight/tests/test_step5_api.py) | FastAPI 엔드포인트, SSE 실시간 스트리밍, 3-Track 스케줄러 & 클린업 | 10개 | **100% PASS** |
| [**`test_step6_e2e.py`**](file:///e:/monnlight/tests/test_step6_e2e.py) | E2E 사용자 여정, 복합 적대적 공격 방어, 다중턴 세션 연속성 | 8개 | **100% PASS** |
| [**`test_step7_circuit_breaker.py`**](file:///e:/monnlight/tests/test_step7_circuit_breaker.py) | **[Step 7 신규] 3-State FSM, 0ms 차단, 3계층 Fallback, 신선도 배지, 스케줄러 격리** | **8개** | **100% PASS** |
| [**`test_audit_fixes.py`**](file:///e:/monnlight/tests/test_audit_fixes.py) | 최신 모델 바인딩, 병상 TTL 캐시, 전국 17개 시도 동적 매칭 | 7개 | **100% PASS** |
| **단위/통합 테스트 소계** | **전체 프로덕션 백엔드 핵심 파이프라인 전수 검증** | **74개** | **100% OK** |
| [**`tests/evals/run_evals.py`**](file:///e:/monnlight/tests/evals/run_evals.py) | **40대 소아 임상 골든 케이스 전수 평가 (5대 임상 평가 지표)** | **40개** | **100.0% 합격 (평균 99.5점)** |

### 5.2 Step 7: 공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback 세부 성과
국립중앙의료원(NMC) E-Gen 공공 API의 잦은 타임아웃, 서버 점검, 503 에러에 대비하여 **서비스 중단 0초(Zero-Downtime)**를 달성하는 엔지니어링 아키텍처를 완벽 구축하였습니다:

1. **AsyncCircuitBreaker (Zero-Dependency 3-State FSM)**:
   - 외부 라이브러리 없이 순수 파이썬으로 `CLOSED`, `OPEN`, `HALF_OPEN` 상태 기계 구현.
   - 3회 연속 실패/타임아웃 시 서킷 트립 (`CLOSED -> OPEN`), 60초 쿨다운 타이머 시작.
   - `OPEN` 상태에서는 공공 API 호출을 0회로 전면 차단 (0.01ms 미만 초고속 숏서킷).
   - 60초 쿨다운 만료 시 `HALF_OPEN`으로 전이하여 단 1개의 Canary 프로브 요청을 보내 성공 시 `CLOSED`로 자동 복구.
   - `threading.RLock` 기반 멀티스레드 및 비동기 동시성 완벽 보장.
2. **3-Tier Multi-Storage Fallback 계층 구조**:
   - **Tier 1 (Stale In-Memory Cache)**: 최근 300초 TTL 경과된 메모리 병상 캐시 즉시 재사용 (< 0.1ms).
   - **Tier 2 (Firestore Snapshot)**: Cloud Firestore `emergency_beds` 컬렉션의 최근 스냅샷 로드 (15ms).
   - **Tier 3 (Immutable Local Baseline)**: `data/immutable_baseline_beds.json` 42개 병원 불변 기준 데이터셋 (0.5ms).
3. **DataFreshnessMeta & 경고 배지 제공**:
   - `/api/v1/emergency/nearby` 응답에 `is_realtime`, `source_tier`, `elapsed_minutes`, `circuit_status`, `warning_message` 자동 부착.
   - 실시간 연동 지연 시 `[⚠️ 공공 API 연동 지연으로 과거 데이터 제공 중. 출발 전 병원 유선 확인 필수]` 안내 문구 100% 노출.
4. **백그라운드 스케줄러 장애 격리**:
   - 5분 주기 병상 폴러(`poll_realtime_beds`)가 외부 API 다운타임 시 크래시 없이 격리 로깅 및 폴백 데이터셋을 안전하게 서빙.

---

## 6. 시스템 아키텍처 & 2계층 데이터 흐름도

```mermaid
flowchart TD
    User([보호자 사용자]) -->|자연어 증상 입력| Tier1{Pass 1: 0ms 정규식 인터셉터<br/>12대 KTAS 위급 패턴 (38µs)}
    
    %% Tier 1 긴급 격상
    Tier1 -->|Red Flag 즉시 감지| Escalation[🚨 EMERGENCY_ESCALATION<br/>119 즉시 출동 모달 & 기도확보 가이드]
    Escalation --> EmergencyER[🏥 10km 최단거리 소아전문응급의료센터 안내]
    
    %% Tier 2 일반 및 문맥 완독
    Tier1 -->|정상 통과| Supervisor[⚙️ Supervisor FSM 라우터]
    Supervisor --> TriageAgent[🤖 Triage Agent<br/>Gemini 3.8 Flash Thinking High]
    
    %% KTAS 지식 베이스 주입
    KTAS_DB[(2021 공식 소아 KTAS<br/>168개 주증상/841개 세부기준)] -.->|Direct Grounding ~8,500 토큰| TriageAgent
    
    TriageAgent --> Tier2Check{Tier 2 판정<br/>KTAS 1~2단계?}
    Tier2Check -->|비정형 Red Flag 감지| Escalation
    Tier2Check -->|KTAS 3~5단계 / 일반| StateDTO[(PatientSessionState<br/>공유 메모리 DTO)]
    
    StateDTO --> MatchingAgent[🤖 Matching Agent<br/>Zero-LLM 2-Track Router]
    
    %% Tools & Circuit Breaker
    subgraph Zero_LLM_Tools [결정론적 백엔드 도구 Layer]
        KASI[KASI 특일 판정 & 과밀화 리스크]
        EGEN[E-Gen 실시간 병상 & Circuit Breaker]
        SPATIAL[Haversine 10km 구면거리 랭킹]
        PAIRING[달빛병원 + 야간약국 30분 마진 페어링]
    end
    
    MatchingAgent --> Zero_LLM_Tools
    
    subgraph Fallback_Hierarchy [3-Tier Multi-Storage Fallback]
        T1_MEM[(Tier 1: Stale Memory < 0.1ms)]
        T2_FS[(Tier 2: Firestore Snapshot 15ms)]
        T3_JSON[(Tier 3: Local Baseline JSON 0.5ms)]
    end
    
    EGEN -.-> Fallback_Hierarchy
    
    MatchingAgent --> LogisticsAgent[🤖 Logistics Agent<br/>Gemini 3.5 Lite]
    LogisticsAgent --> ResultCard[📋 종합 결과 카드<br/>• 추천 달빛병원 & 30분 마진 약국 세트<br/>• 30초 통화 확인 스크립트<br/>• 2024년 5월 본인확인 의무화 지참 서류<br/>• 데이터 신선도 배지]
    
    ResultCard --> Sanitizer{의료법 제27조 단일 소독 관문}
    Sanitizer --> User
```

---

## 7. 데이터 갱신 및 캐싱 전략 (하이브리드 아키텍처)

안정적인 0ms 레이턴시와 공공 API 쿼터 고갈 방지, 비용 최적화를 위해 데이터 성격에 따라 4계층 하이브리드 캐싱을 적용합니다:

| 데이터 분류 | 데이터 항목 | 보관 위치 | 갱신 주기 & 트리거 | 캐싱 & 최적화 목적 |
| :--- | :--- | :--- | :--- | :--- |
| **정적 마스터** | 서울 530개 응급실 위경도 (`seoul_emergency_coords.json`), 전국 달빛병원-심야약국 페어링 (`nationwide_pairings.json`) | 로컬 파일시스템 (`data/`) + Firestore 정적 컬렉션 | **24시간 주기 (매일 04:00 AM)** 공공 API 호출 갱신 | 병상 조회 시 지오코딩 API 중복 호출 0회 차단 (속도 30배 가속: 7,988ms ➔ 261ms) |
| **KTAS 지식 베이스** | 2021 공식 소아 KTAS 168개 주증상 및 세부 고려사항 (`ktas_pediatric_dataset.json`) | 인메모리 싱글톤 캐시 (`_ktas_grounding_cache`) | 앱 기동 시 1회 메모리 로드 | Triage Agent 호출마다 발생하는 파일 I/O를 0회로 차단하고 프롬프트에 즉시 주입 |
| **동적 실시간 병상** | 실시간 소아 응급실 병상수(`hv28`), 실시간 공지사항(`hpmg`) | 5분 TTL 인메모리 캐시 + Firestore `emergency_beds` | **5분 주기 폴링 (E-Gen API)** | **In-Memory Hash Diffing (MD5)**: 변동된 병상만 Firestore Write를 수행하여 일일 무료 쿼터 초과 방지 (비용 90~100% 절감) |
| **불변 기준 데이터 (Tier 3)** | 전국 42개 핵심 응급의료기관 불변 기준 병상 및 연락처 (`immutable_baseline_beds.json`) | 로컬 디스크 (`data/`) | 영구 보존 (배포 시 패키징) | 공공 API 전면 단절 및 클라우드 DB 장애 시에도 서비스가 절대 중단되지 않는 영구 안전망 (0.5ms 서빙) |
| **세션 데이터** | 멀티턴 대화 세션 및 환아 임상 상태 (`PatientSessionState`) | Thread-Safe 세션 인메모리 딕셔너리 (`SessionManager`) | 사용자 대화 턴마다 갱신 (30분 비활성 시 자동 Eviction) | 세션 무결성 유지 및 메모리 누수 0% 달성 |

---

## 8. 추가 심화 고도화 백로그 (Advanced Backlog)

| 영역           | 고도화 과제명                              | 핵심 구현 내용                                                        |          현재 상태          | 기대 효과                                 |
| :----------- | :----------------------------------- | :-------------------------------------------------------------- | :---------------------: | :------------------------------------ |
| **안전 감시**    | **Red Flag V2 2계층 심층 감시망**           | 0ms 정규식(12대 룰) + 168개 KTAS 주증상 Direct Grounding Gemini Thinking |  **[완료 (V2 Upgrade)]**  | 비정형 문맥 완독, 언더트리아제 0% 수호               |
| **도메인 킬러**   | **달빛병원-약국 30분 마진 서비스**               | 전국 17개 시·도 달빛어린이병원-심야약국 +30분 조제 안전 마진 1:1 페어링                   |    **[완료 (Step 3)]**    | 야간 74% 경증 환아 처방전 조제 실패 사고 원천 방지       |
| **안정성 (HA)** | **공공 API 서킷 브레이커 & 3-Tier Fallback** | 3-State FSM, 3회 임계치, 60s 쿨다운, 3-Tier 멀티스토리지 폴백                  |    **[완료 (Step 7)]**    | 외부 공공 API 전면 장애 시에도 서비스 무중단 0초 가동     |
| **품질 평가**    | **40대 임상 골든 케이스 Evals 하네스**          | 5대 임상 평가지표 자동 채점 및 성적표 생성 (`tests/evals/run_evals.py`)          | **[완료 (Step 6, 100%)]** | 객관적 Evals 합격 성적표(100.0%, 평균 99.5점) 확보 |
| **팀 거버넌스**   | **팀 프로젝트 4대 문서 지속 누적 관리 체계**         | `Answer-영식.md`, `log.md`, `README.md`, `PLAN.md` 및 에이전트 룰 자동화   |    **[완료 (v2.1.1)]**    | 복수 엔지니어 협업 시 문서 누락 및 코드-기획 불일치 원천 차단  |
| **프론트엔드 UI** | **백엔드 100% 결합형 반응형 웹 UI/UX** | SSE 실시간 챗봇, 119 긴급 모달, 1:1 페어링 카드, 30초 통화 스크립트 | **[설계 완료 (착수 대기)]** | 늦은 밤 다급한 부모의 0초 직관성과 절대적 심리적 안정감 제공 |
| **의료 브리핑**   | **119 구급대원용 30초 SBAR 카드**            | Red Flag 감지 시 구급대원 인계용 SBAR(상황/배경/평가/권고) 4줄 요약 출력               |          [대기]           | 패닉 부모 대신 119 구급대원/의료진에 정확한 정보 전달      |
| **실시간 스트림**  | **Firestore ➔ SSE 브릿지 실시간 알림**       | 병상 만실/해제 시 클라이언트 폴링 없이 0.1초 만에 알림 푸시                            |          [대기]           | 부모가 대기 중 병상 변동을 실시간으로 감지              |
| **품질 자동화**   | **GitHub Actions CI/CD 회귀 검증 파이프라인** | Git Push 시 74개 테스트 및 40대 Evals 자동 실행 및 배포 안전 가드                 |       [향후 개선 과제]        | 팀원 코드 병합 시 회귀 버그 및 안전 가드레일 훼손 원천 방지   |

---

## 9. 팀 프로젝트 협업 체계 & 4대 문서 지속 누적 관리 거버넌스

본 프로젝트는 단일 개발 환경에서 **팀장 정영식**과 **팀원 김동준**이 공동으로 엔지니어링을 수행하는 팀 프로젝트로 공식 운영됩니다. 어떤 사용자가 작업을 진행하든 아래의 규율은 영구적이고 예외 없이 준수됩니다:

### 9.1 팀원별 역할 정의 (R&R)
* **정영식 (팀장)**: 프로젝트 총괄, 시스템 기획 및 아키텍처 의사결정, 질의응답 및 요구사항 통제.
* **김동준 (팀원)**: 백엔드 API, 데이터 파이프라인 및 멀티 에이전트 모듈 개발, 단위/통합 테스트 작성 및 트러블슈팅.
* **신규 사용자**: 향후 새로운 팀원이 투입되어도 동일한 규율이 적용됩니다.

### 9.2 4대 핵심 문서 지속 누적 관리 철칙
1. **[Answer-영식.md](file:///e:/monnlight/Answer-영식.md)**:
   - 정영식 팀장의 모든 질문과 AI의 분석·가이드 답변을 순차적 Q&A 번호(`Q1, Q2, ..., Q37, ...`)로 빠짐없이 누적 기록.
   - 기존 질의응답은 절대 삭제/수정하지 않고 영구 보존.
2. **[log.md](file:///e:/monnlight/log.md)**:
   - 각 사용자가 개발/테스트/배포 과정에서 마주친 모든 오류(Errors), 데이터 결함(Data Pitfalls), 컴플라이언스 위험 및 구체적 해결 방안을 `[ISSUE-XXX]` 포맷으로 지속 누적 기록.
3. **[README.md](file:///e:/monnlight/README.md)**:
   - 각 사용자가 개발하면서 업데이트한 신규 기능, 아키텍처 개선, 테스트 성과를 최신 릴리스 체인지로그에 지속 반영.
4. **[PLAN.md](file:///e:/monnlight/PLAN.md)**:
   - 개발 진행 중 프로젝트에 업데이트된 점이 존재하면 기획안 본문을 최신 상태로 동기화(Code-Plan Parity 100%)하고, 향후 개선책 및 백로그를 지속적으로 도출·갱신.

### 9.3 에이전트 시스템 레벨 규칙 파일
* [.agents/rules/team_collaboration_rules.md](file:///e:/monnlight/.agents/rules/team_collaboration_rules.md): Antigravity 워크스페이스 전역 규칙.
* [GEMINI.md](file:///e:/monnlight/GEMINI.md) & [AGENTS.md](file:///e:/monnlight/AGENTS.md): 루트 레벨 최상위 지침 파일로 대화 시작 시 자동 로드되어 AI 에이전트의 불변 준수 보장.

---

## 10. 프론트엔드 UI/UX 아키텍처 & 화면 연동 로드맵

백엔드 파이프라인(Step 1~7 및 Red Flag V2)의 완전한 검증(74개 테스트 100% 통과)을 기반으로, 구축된 백엔드 기능을 100% 사용자 친화적으로 표현하는 프론트엔드 설계 명세서([docs/FRONTEND_UI_UX_SPECIFICATION.md](file:///e:/monnlight/docs/FRONTEND_UI_UX_SPECIFICATION.md))를 공식 수립하였습니다.

### 10.1 UI/UX 디자인 철학 (Design Aesthetics)
* **Midnight Dark & Warm Moonlight Glassmorphism**: 심야 시간대 눈부심 없는 다크 테마(`#0B0F19`), 반투명 글래스모피즘 컨테이너(`rgba(22, 30, 49, 0.75)`), 포근한 달빛 골드(`#FBBF24`) 포인트.
* **Thumb-Zone 모바일 한 손 최적화**: 화면 하단 40% 영역에 핵심 통화 버튼 및 길찾기 액션 배치.

### 10.2 백엔드 1:1 결합형 6대 핵심 화면 컴포넌트
1. **0ms Red Flag 119 긴급 오버레이 모달 (`EmergencyModalOverlay`)**: 26µs 정규식 단락회로 및 `event: emergency` 수신 시 0초 팝업 트리거, 119 즉시 전화, 응급처치(기도확보) 가이드 노출.
2. **SSE 실시간 증상 문진 챗봇 (`TriageChatContainer`)**: 3턴 진행률 인디케이터(1/3 ➔ 2/3 ➔ 3/3), 실시간 토큰 타이핑 스트리밍, 환아 바이탈 캡슐(월령, 체온, 증상) 실시간 추출 뱃지.
3. **[Track B] 달빛병원 + 30분 마진 심야약국 1:1 페어링 카드 (`HospitalPharmacyPairingCard`)**: 병원 정보, 마감 40분 전 조기마감 주의 뱃지, **[🟢 +30분 조제 안전마진]** 약국 세트.
4. **[Track A] 소아전문응급의료센터 실시간 병상 현황판 (`EmergencyDepartmentBoard`)**: 실시간 잔여 병상(`hv28`), 소아 당직의 여부, E-Gen 데이터 신선도 투명성 배지.
5. **2024년 5월 본인확인 준비물 체크리스트 & 30초 통화 스크립트 (`ActionHelper`)**: 부모 신분증/등본 체크박스 및 원클릭 복사 통화 스크립트.
6. **의료법 제27조 안심 풋터**: 비의료 AI의 진단/처방 한계 및 대면 진찰 필수 고지.

### 10.3 프론트엔드 5단계 실행 로드맵
* **[Phase 1] 코어 레이아웃 & 테마 시스템 구축**: CSS 변수, 글래스모피즘, 모바일 반응형 프레임.
* **[Phase 2] SSE 스트리밍 챗봇 & 0ms 긴급 모달 연동**: `/api/v1/chat/stream` 스트림 리스너 및 119 인터셉터.
* **[Phase 3] 2-트랙 결과 카드 렌더링**: Track B 페어링 카드 및 Track A 실시간 병상 게이지 연동.
* **[Phase 4] 내원 지원 툴킷**: 30초 스크립트 복사 및 본인확인 체크리스트 인터랙션.
* **[Phase 5] E2E 통합 브라우저 검증**: 모바일 뷰포트 E2E 시나리오 테스트.

### 10.4 Stitch 모바일 화면 프로토타입 3종 구축 완료 (타다 TADA 스타일)
타다(TADA)의 직관적 온디맨드 디스패치 사용자 경험을 헬스케어에 접목하여 Stitch로 3대 화면을 정밀 생성 완료함:
1. **화면 1: 로딩 & 최초 온보딩 스플래시** (`Screen ID: 5f348380315d4efc934d9a22b283dc36`): 미니멀 다크 모빌리티 감성, 최초 1회 GPS 권한 허용 카드, 의료법 안심 배지, 풀와이드 골드 CTA.
2. **화면 2: 타다 스타일 온디맨드 야간케어 홈** (`Screen ID: fc578206de4a417693297b2603a4e0e1`): 목적지 검색창 스타일 증상 입력 바, 퀵 트리아지 칩, 실시간 슬라이딩 바텀시트, 119 플로팅 펄스 버튼.
3. **화면 3: 병원-약국 1:1 매칭 완료 및 내원 안내** (`Screen ID: 3d395741108845e9b5edcc5fc9589164`): 배차 완료 스타일 미니 라우팅 그래픽, 🏥달빛병원 + 💊약국(+30분 안전마진) 페어링 카드, 2024년 5월 본인확인 서류 체크리스트, 30초 통화 스크립트 복사기, 고정 듀얼 CTA.

### 10.5 '아이숨(i-Soom)' 화이트 & 코발트 블루 디자인 시스템 및 Stitch 화면 자산 (2026-10-14 확정)
* **브랜드명**: **아이숨 (i-Soom)** (우리아이 편안한 숨결을 지키는 24시간 안심 소아 케어)
* **디자인 테마**: Clean Modern Pediatric Reassurance (White & Cobalt Blue Light Mode)
  - **Primary**: #0066FF (코발트 블루 - 신뢰, 전문성)
  - **Background**: #FFFFFF (화이트), #F8FAFC (소프트 뉴트럴 그레이)
  - **Secondary Accent**: #EBF2FF, #DBEAFE (라벤더 소프트 블루)
  - **Status Indicator**: #10B981 (그린 - 실시간 운영 중, +30분 안전조제 마진 확보)
  - **Emergency Alert**: #EF4444 (레드 - 119 즉시연결 숏서킷)
* **Stitch 프로젝트 (projects/15792310540995806418) 화면 자산**:
  1. 아이숨 로딩 & 온보딩 스플래시 (397c4e98ffaf47518e568e04fa60fef7)
  2. 아이숨 메인 홈 (screen.png 100% 동일 컴포넌트 이식) (c0bb4df907b44ddd9ee91bad51a308d6)
  3. 아이숨 병원·약국 1:1 매칭 완료 및 내원 안내 (e41d07bcd314bfcb5f4a7bd97a24850)
  4. 아이숨 처치정보 안내 및 동의창 (21c51275ffb648d19f9f4b90a998f584)
  5. 아이숨 증상 입력창 (3a26f3d0625740398a068636e2aa9548)

### 10.6 '아이숨 (Aisum)' 신규 전용 Stitch 프로젝트 및 Calm Harbor 라이트 테마 3대 핵심 화면 (2026-10-14 완결)
* **신규 Stitch 전용 프로젝트**: `projects/17449043314542457561` ('아이숨 (Aisum) - 소아 야간 의료 매칭 케어')
* **전용 디자인 시스템 (Calm Harbor, `assets/389aad58bc8e4522b6904fb567d60bdf`)**:
  - **기본 베이스**: 소프트 오프화이트/블루그레이 캔버스 (`#F8FAFC` ~ `#F1F5F9`) + 순백색 라운드 카드 (`#FFFFFF`, 18px `rounded-2xl`).
  - **프라이머리 컬러**: 로열 코발트 블루 (`#0066FF`, 눌렀을 때 `#1D4ED8`) - 브랜드 로고, 핵심 CTA 버튼, 하단 활성 탭.
  - **상태 및 안전 배지**: 에메랄드 민트 (`#10B981` / `#ECFDF5`, 실시간 동기화/진료중), 달빛 옐로우 (`#F59E0B`, 달빛병원), 코랄 레드 (`#EF4444`, 고열 38.5°C+/경련 긴급 경고).
* **screen.png 1:1 정밀 이식 3대 핵심 모바일 화면**:
  1. **화면 1: 아이숨 - 홈 (`Screen ID: 65dcc96b817143c3adb7bfdfa545267b`)**:
     - 상단 헤더: 볼드 `아이숨` 로고 + `역삼동 ∨` 알약 드롭다운 + 종/프로필 아이콘.
     - 증상 탐색 히어로: 초록 라이브 닷 `소아 전문 의료 데이터 실시간 동기화` + `아이가 어디가 아픈가요?` 볼드 헤드라인 + 미소 아이 일러스트.
     - 메인 CTA: `+ 아이 증상 입력하고 병원 찾기 →` (54px 로열 블루).
     - 원터치 증상 퀵태그: `# 열나요(고열)`, `# 구토/설사`, `# 기침/호흡`, `# 발진/두드러기`.
     - 실시간 야간 의료시설: `10곳 운영중` + `E-Gen 연동 1분 전` 배지 + `전체 10 / 달빛병원 3 / 심야약국 5` 필터 탭.
     - 시설 카드 3종: 송파어린이병원 (전문의 2명 진료중, 대기 4팀, ~23:00 마감), 강남아이마음병원 (~22:30 마감), 송파달빛약국 (~24:00 마감).
     - 하단 GNB: `홈(활성)` | `응급실 가이드` | `설정`.
  2. **화면 2: 아이숨 - 증상 입력 및 문진 (`Screen ID: 0cdadf1dc86a4c229423b5b02caa8cc1`)**:
     - 상단: 뒤로가기, `아이숨 증상 입력`, 닫기, 진행 바 `Step 1/3 (33%)`.
     - 환아 프로필: `정하은 (생후 18개월 · 11.2kg)` 선택 칩.
     - 체온 인터페이스: `38.6°C` 대형 디지털 디스플레이, 컬러 게이지 슬라이더 & `+/-` 미세조절, `발열 시작: 2시간 전` 태그.
     - KTAS 증상 멀티 셀렉터: 열나요(선택), 기침/호흡(선택), 구토/설사, 처짐, `🚨 경련/의식 저하` 레드 숏서킷 칩.
     - 해열제 복용 기록: 아세트아미노펜 3.5ml(1.5시간 전) 및 **`💡 다음 이부프로펜 교차복용 가능: 23:30 (30분 후)`** 안심 타이머.
     - KTAS 4단계(준응급) 달빛어린이병원 권장 카드 및 `내 주변 진료 가능 병원 매칭하기 →` CTA.
  3. **화면 3: 아이숨 - 야간 병원 상세 및 실시간 접수 (`Screen ID: 3c5db317bb354d02838e5306adfc4f1a`)**:
     - 송파어린이병원 히어로 및 3열 핵심 지표 (`현재 대기 4팀 (20분 예상)` 블루 강조, 거리 1.8km, 무료주차 2시간).
     - 오늘의 야간 당직 전문의: Dr. 김서연 소아호흡기 세부전문의 (현재 14번 환아 진료중 라이브 배지).
     - 안심 심야약국 연계: 송파달빛약국 (도보 1분 80m, 24:00까지 조제 100% 보장, 시럽제/네블라이저 약액 상비).
     - 오시는 길 미니 맵 + 송파대로 345 주소 복사 + **티맵 / 카카오내비** 원클릭 연동.
     - 하단 듀얼 액션 바: `[📞 전화상담]` & `[모바일 야간진료 번호표 접수하기 (대기 4번째) →]`.
* **공식 화면 명세서 보고서**: [AISUM_STITCH_DESIGN_REPORT.md](AISUM_STITCH_DESIGN_REPORT.md) (디자인 토큰, 화면별 세부 스펙, 스크린샷 뷰어 링크 및 백엔드 매핑 집대성)

### 10.7 '아이숨 (Aisum)' 프론트엔드 전용 워크스페이스(`frontend/templates/`) 구축 및 HTML/CSS 모듈화 이관 (2026-10-14 완결)
* **프론트엔드 모듈화 아키텍처 원칙**:
  - `app/`(백엔드), `data/`(데이터셋), `docs/`(명세서), `scripts/`(스크립트), `tests/`(테스트)와 정합성을 이루는 최상위 전용 **`frontend/`** 디렉터리 구축.
  - 외부 프레임워크나 Tailwind CDN 런타임 종속성 없이 완전히 단독(Standalone) 구동 가능한 순수 시맨틱 HTML5 및 바닐라 CSS3(Vanilla CSS) 구조.
  - 웹 표준 규격에 따라 `templates/`, `css/`, `js/`, `assets/` 하위 모듈 계층화 및 상대 경로(`../css/`, `../js/`) 정합성 보장.
* **구축 산출물**:
  1. [frontend/templates/index.html](frontend/templates/index.html): 메인 홈 화면 SPA 템플릿 진입점 (`<link href="../css/style.css">`).
  2. [frontend/css/style.css](frontend/css/style.css): Calm Harbor 디자인 토큰 Vanilla CSS (로열 블루 `#0066FF`, 에메랄드 `#10B981`, 앰버 `#F59E0B`, 코랄 `#EF4444`, 440px 모바일 프리뷰, 글래스모피즘, 펄스 애니메이션).
  3. [frontend/js/main.js](frontend/js/main.js): 클라이언트 인터랙션 및 향후 SSE 챗봇 연동 진입점 (`<script src="../js/main.js">`).
  4. [frontend/assets/](frontend/assets/): `icons/`, `images/` 정적 그래픽 에셋 디렉터리.
  5. [frontend/README.md](frontend/README.md): 프론트엔드 워크스페이스 가이드 문서.
  6. [app/templates/index.html](app/templates/index.html) 및 [app/static/](app/static/): FastAPI 백엔드 패키징 동기화.
  7. [main.py](main.py): `app.mount("/frontend", ...)`, `/css`, `/js`, `/assets`, `GET /home`, `GET /style.css`, `GET /js/main.js` 등록 및 HTTP 200 검증 완료.

### 10.8 사전 처치정보 및 법적 안내 모달 다이얼로그(반투명 오버레이, 취소/확인) 화면 구현 (2026-10-14 완결)
* **모달 화면 명세 및 디자인 시스템 연계**:
  - Stitch 프로젝트: `projects/2692934076926222841` (MoonlightCare / Aisum)
  - 화면명: **`사전 처치정보 및 법적 안내 모달`** (`Screen ID: a03bce9953984334a2f6ffd739d65525`)
  - 디자인 시스템: `MoonlightCare / Calm Harbor Design System` (`assets/ede449b1e12a44f2b4df4a14068b30e1`)
* **핵심 컴포넌트 명세**:
  1. **어두운 반투명 블러 오버레이**: `rgba(15, 23, 42, 0.65)` 및 `backdrop-filter: blur(5px)`.
  2. **모달 다이얼로그 카드**: 328px 너비, `rounded-2xl`(22px), 파란색 강조 텍스트("인근 병원과", "참고용 처치정보").
  3. **처치정보 안내 박스**: 연파랑 배경 박스(`background: #F4F6FB`), 5대 안내 항목 불릿 리스트 (119 즉통 기준, 증상 유동성, 의료법 제27조 한계, 사용자 최종 판단 책임).
  4. **하단 50px 분할 액션 버튼**: 좌측 중립 그레이 `[취소]`, 우측 볼드 로열 블루 `[확인]` (터치 시 모달 닫기).
* **화면 연계 및 인터랙션**:
  - 메인 홈 화면의 `[아이 증상 입력하고 병원 찾기]` CTA 및 증상 칩 터치 시 모달 오픈.
  - `[취소]` 또는 `[확인]` 버튼 터치 시 모달 닫힘.
  - 어두운 배경 오버레이 클릭 또는 ESC 키 입력 시 모달 닫힘.

### 10.9 사용자 증상 프롬프트 입력 페이지(Underline Input) 고도화 (2026-10-15 완결)
* **화면 개요 및 디자인 명세**:
  - Stitch 프로젝트: `projects/2692934076926222841` (MoonlightCare / Aisum)
  - 화면명: **`Aisum 증상 입력 화면`** (`Screen ID: 18441e7efe314c06bb8716493d3d8626`)
  - [Stitch 생성 화면 스크린샷 보기](https://lh3.googleusercontent.com/aida/AEtjO1UPIAr3RvVHLVgX9s6PA6a7N9J-SpiKta1J3bGoAkZZshPCUdkx97XcrLfU_TyXZkazsxj9xaL-cTOyZQzFwhCmXJtN1qAQwwoVOk8a8A5Kom_j8Z5P1NOU_-8xJKEJAYek1Aa0W7gi_3d9oM6gcXXLk0eB3LkamoV4VW-PWsdUCvcOCGaVpr2FAKaGOZ0_CGmrreRr92O8pr6SSbdUruPJAmAE1gVjJnL0QQZZZOIf1coz8Ih-LMA1AxE)
* **핵심 컴포넌트 명세**:
  1. **헤드라인**: `"증상을 구체적으로\n정확하게 입력해주세요"` (26px, 700 볼드, 딥 네이비 `#0F172A`).
  2. **언더라인 인풋 필드**: `2px solid #0066FF` 로열 블루 하단 보더 라인, `"입력"` 플레이스홀더, 타이핑 시 플로팅 레이블 및 우측 지우기(`✕`) 버튼.
  3. **가상 키보드 및 확인 버튼 배제**: 실제 디바이스 입력 시 OS가 호출하는 기능적 자판 그래픽과 중복되는 확인 버튼을 생략하고 쾌적한 화이트 여백 유지.
* **산출물 및 서빙**:
  - [frontend/input.html](frontend/input.html) 및 [frontend/templates/input.html](frontend/templates/input.html) 구축.
  - `GET /input` 엔드포인트 등록 및 HTTP 200 검증 완료.

---

### 📌 결론 및 종합 성과 (Summary & Milestones)

현재 MoonlightCare 프로젝트는 **Step 1(기반 파이프라인)**부터 **Step 6(E2E 통합)**, **차세대 2계층 Red Flag V2 모듈**, **Step 7(공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback 아키텍처)**, 그리고 **팀 프로젝트 협업 및 4대 문서 지속 누적 관리 거버넌스(v2.1.1)**에 이르는 전체 개발 로드맵을 완벽하게 완수하였습니다.

현재 **총 74개 단위/통합 테스트 전수 무결점 통과(`Ran 74 tests, OK`)** 및 **40대 소아 임상 골든 케이스 Evals 100.0% 합격(평균 99.5점)**을 달성하여, 실시간 장애 복원력과 의료 AI 임상 안전성, 법적 방어(의료법 제27조), 클라우드 비용 효율(FinOps), 그리고 팀 협업 코드-문서 무결성 전 영역에서 상용 서비스 론칭 기준을 완전히 충족하였습니다.
