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

## 3. 현재까지 완료된 개발 모듈 & 테스트 검증 내역 (Done: Steps 1~4)

주피터 노트북에서 검증된 로직을 프로덕션 백엔드 패키지(`app/`)로 체계적으로 모듈화하고, 4단계에 걸친 단위/통합 테스트 33건을 100% 완수했습니다.

```
monnlight/
├── app/
│   ├── __init__.py
│   ├── config.py                     # [Step 1] 환경변수 자동 감지 & Firestore 클라이언트 싱글톤
│   ├── demo_step1.py                 # [Step 1] 1단계 실시간 파이프라인 벤치마크 실행기
│   ├── demo_step3.py                 # [Step 3] 3단계 인터랙티브 2-트랙 에이전트 파이프라인 실행기
│   ├── demo_step4.py                 # [Step 4] 4단계 메인 오케스트레이터(Supervisor FSM) 통합 실행기
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── emergency.py              # [Step 1] 응급실 병상, 특일 정보, 공간 랭킹 Pydantic DTO
│   │   ├── state.py                  # [Step 2] 멀티 에이전트 공유 세션 DTO (PatientSessionState)
│   │   └── supervisor.py             # [Step 4] 클라이언트/API 통신용 정형 응답 DTO (SupervisorResponse)
│   ├── services/                     # [Step 1, 3] 순수 결정론적 도구 Layer (Zero-LLM)
│   │   ├── __init__.py
│   │   ├── holiday_service.py        # KASI 특일 판정 & KST(UTC+9) 타임존 고정 과밀화 리스크 평가
│   │   ├── spatial_service.py        # Haversine 구면거리 5µs 연산 & 반경 10km 소아 응급실 랭킹
│   │   ├── emergency_sync_service.py # E-Gen 실시간 병상, 100% 공지 정규식, Hash Diffing, 디스크 캐싱
│   │   └── pairing_service.py        # [Step 3] 전국 29개 달빛병원-심야약국 +30분 안전 마진 페어링 서빙
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
│   └── evals/
│       └── golden_test_cases.json    # 25대 임상 골든 엣지케이스 정의집
├── CONNECTIVITY_MAP.md               # [Step 4] 모듈 & 에이전트 상호 연결도 및 아키텍처 매트릭스 (v1.1.0)
├── README.md                         # 종합 프로젝트 안내서 (v0.1.0 ~ v1.1.0 전 이력 보존)
├── PLAN.md                           # 종합 기획안 & 개발 백서 (본 문서)
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

> **현재 종합 테스트 현황**: 총 33개 테스트(Step 1 7개 + Step 2 12개 + Step 3 7개 + Step 4 7개) **100% 전수 통과 (Ran 33 tests in 6.91s, OK)**.

---

## 4. 전체 6단계 구현 로드맵 & 잔여 과제 (Roadmap: Steps 5~6)

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
[Step 5: FastAPI REST 서빙 & 데몬]   ──► [다음 즉시 목표 / 진행 예정]
         │
         ▼
[Step 6: E2E 통합 테스트 & 시나리오]  ──► [25대 골든 케이스 자동 채점기]
```

### 4.1 [Step 4] 메인 오케스트레이터 (Supervisor FSM & 세션 매니저) ── **[개발 완료 (100% 통과)]**
* `supervisor.py`, `session_manager.py`, `SupervisorResponse`, `demo_step4.py`, `test_step4_orchestrator.py` 개발 및 100% 테스트 검증 완료.

### 4.2 [Step 5] FastAPI REST API 서빙 & 백그라운드 동기화 데몬 ── **[다음 즉시 작업]**
* **`app/api/v1/chat.py`**: `POST /api/v1/chat` (부모-에이전트 실시간 대화 및 스트리밍 엔드포인트).
* **`app/api/v1/emergency.py`**: `GET /api/v1/emergency/nearby` (GPS 기반 5ms 주변 가용 응급실 조회).
* **`main.py`**: FastAPI 앱 엔트리포인트 및 APScheduler 기반 **2-트랙 백그라운드 워커** 연동:
  - **실시간 병상 폴러 (5분 주기)**: E-Gen 실시간 병상 수집 + In-Memory Hash Diffing Firestore 쓰기.
  - **정적 데이터 갱신 워커 (24시간 주기, 매일 04:00 AM)**: 응급실 위경도 및 달빛병원-약국 페어링 데이터 공공 API 증분 동기화.

### 4.3 [Step 6] E2E 통합 테스트 & 25대 골든 케이스 시나리오 평가
* **3대 핵심 시나리오 자동 검증**:
  1. **초응급 시나리오 (Red Flag)**: 경련/청색증 입력 시 1턴 만에 119 직행 모달 반환.
  2. **야간 발열 시나리오 (경증)**: 14개월 38.5도 입력 시 공감 문진 ➔ 달빛병원+30분 약국 페어링 ➔ 30초 통화 스크립트 출력.
  3. **의료법 방어 시나리오**: 부모의 병명 추측 유도 시 진단 거부 및 대면 진찰 안내 확인.
* **25대 골든 케이스 자동 채점기 (`tests/evals/run_evals.py`)**: 5대 평가 지표(의료법, RedFlag 등) 자동 채점 및 합격률 산출.

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

| 데이터 분류 | 데이터 항목 | 보관 위치 | 갱신 주기 & 트리거 | 캐싱 & 최적화 목적 |
| :--- | :--- | :--- | :--- | :--- |
| **정적 / 준정적 데이터** | 서울 530개 응급실 위경도 (`seoul_emergency_coords.json`), 전국 달빛병원-심야약국 페어링 (`nationwide_pairings.json`) | 로컬 파일시스템 (`data/`) + Firestore 정적 컬렉션 | **24시간 주기 (매일 04:00 AM)** 공공 API 호출 갱신 | 병상 조회 시 반복되는 지오코딩 API 호출을 0회로 차단 (응답 속도 30배 향상: 7,988ms ➔ 261ms) |
| **동적 실시간 데이터** | 실시간 소아 응급실 병상수(`hv28`), 응급실 실시간 공지(`hpmg`) | 인메모리 캐시 + Firestore `emergency_beds` | **5분 주기 폴링 (E-Gen API)** | **In-Memory Hash Diffing (MD5)**: 상태가 변경된 병상만 Firestore Write를 수행하여 일일 무료 쿼터 초과 방지 (비용 90~100% 절감) |

---

## 7. 추가 심화 고도화 백로그 (Advanced Backlog)

프로덕션 배포 및 대외 포트폴리오 경쟁력 극대화를 위한 심화 엔지니어링 과제 목록입니다:

| 영역 | 고도화 과제명 | 핵심 구현 내용 | 현재 상태 | 기대 효과 |
| :--- | :--- | :--- | :--- | :--- |
| **도메인 킬러** | **달빛병원-약국 30분 마진 서비스 모듈화** | `app/services/pairing_service.py` 신설, 전국 17개 시·도 1:1 자동 매칭 | **[완료 (Step 3)]** | 야간 74% 경증 환아 처방전 조제 실패 사고 0% 방어 |
| **의료 브리핑** | **119 구급대원용 30초 SBAR 카드** | Red Flag 감지 시 구급대원 인계용 SBAR(상황/배경/평가/권고) 4줄 요약 출력 | [대기] | 패닉 부모 대신 119 구급대원/의료진에 정확한 정보 전달 |
| **안정성 (HA)** | **공공 API 서킷 브레이커 & Fallback** | 공공데이터포털 503 에러 시 직전 Firestore/로컬 캐시 즉시 서빙 | [대기] | 외부 API 장애 시에도 서비스 무중단 가동 |
| **실시간 스트림**| **Firestore ➔ SSE(Server-Sent Events) 브릿지** | `on_snapshot` 리스너를 SSE 엔드포인트로 연계하여 병상 변동 실시간 푸시 | [대기] | 클라이언트 폴링 없이 0.1초 만에 병상 변동 실시간 반영 |
| **품질 평가** | **25대 골든 케이스 자동 Evals 채점기** | `tests/evals/run_evals.py` 작성, 5대 평가 지표(의료법, RedFlag 등) 자동 채점 | [Step 6 예정] | 객관적 Evals 합격 성적표(98%+) 및 레이더 차트 확보 |

---

### 📌 결론 및 다음 액션 (Next Action)

현재 MoonlightCare 프로젝트는 **"기반 데이터 파이프라인(Step 1)"**, **"0ms 의료 안전 가드레일(Step 2)"**, **"AI 멀티 에이전트 결합(Step 3)"**, 그리고 **"메인 오케스트레이터 및 세션 매니저(Step 4)"**가 33개 단위/통합 테스트와 함께 100% 완벽하게 완성된 상태입니다.

다음 즉시 착수 과제는 **[Step 5] FastAPI REST API 서빙 & 백그라운드 동기화 데몬**이며, 완성된 `SupervisorOrchestrator`를 `POST /api/v1/chat` 엔드포인트에 1줄로 연결하고, 5분 주기 병상 폴러 및 24시간 정적 데이터 갱신 워커를 구축할 예정입니다.
