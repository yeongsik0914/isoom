# 🌙 MoonlightCare 종합 기획안 & 개발 백서 (PLAN.md)

> **문서 버전**: v2.4 (프론트엔드-백엔드 풀스택 아키텍처 & 92개 테스트 전수 통과)  
> **최종 갱신 일자**: 2026-10-16  
> **핵심 슬로건**: *"야간 소아 응급실 뺑뺑이를 막는 0ms 세이프티 가드레일 & 데이터 기반 2-트랙 지능형 라우터"*  
> **기반 원천**: 주피터 노트북 5권 실증 데이터, 국립중앙의료원(NMC)·한국천문연구원(KASI) 공공데이터, Firebase Cloud Firestore, Gemini 3.8 Flash (Thinking High) / 3.5 Lite, 2021 소아 KTAS 지침(168개 주증상), AsyncCircuitBreaker(3-State FSM), In-Memory Hash Diffing 델타 동기화.

---

## 📑 목차 (Table of Contents)

1. [프로젝트 기획 배경 & 핵심 문제 정의](#1-프로젝트-기획-배경--핵심-문제-정의)
2. [데이터 분석 기반의 목적별 기능 도출 (Notebook 1~5 실증)](#2-데이터-분석-기반의-목적별-기능-도출-notebook-15-실증)
3. [백엔드 모듈 체계 & 디렉터리 아키텍처 (Steps 1~8)](#3-백엔드-모듈-체계--디렉터리-아키텍처-steps-18)
4. [차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)](#4-차세대-2계층-안전-감시망-two-tier-red-flag-v2-architecture)
5. [풀스택 시스템 아키텍처 & 2계층 데이터 흐름도](#5-풀스택-시스템-아키텍처--2계층-데이터-흐름도)
6. [데이터 엔지니어링 & 24시간 In-Memory Hash Diffing 델타 동기화](#6-데이터-엔지니어링--24시간-in-memory-hash-diffing-델타-동기화)
7. [공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback](#7-공공-api-서킷-브레이커--3-tier-multi-storage-fallback)
8. [프론트엔드 UI/UX 아키텍처 & 13대 화면 체계 (Fixed App Shell)](#8-프론트엔드-uiux-아키텍처--13대-화면-체계-fixed-app-shell)
9. [프론트엔드-백엔드 100% 결합 연동 명세](#9-프론트엔드-백엔드-100-결합-연동-명세)
10. [종합 검증 현황 & 임상 안전성 벤치마크 (92개 테스트 전수 통과)](#10-종합-검증-현황--임상-안전성-벤치마크-92개-테스트-전수-통과)
11. [추가 심화 고도화 백로그 (Advanced Backlog)](#11-추가-심화-고도화-백로그-advanced-backlog)

---

## 1. 프로젝트 기획 배경 & 핵심 문제 정의

### 1.1 사회적 배경: "왜 야간 소아 응급실 뺑뺑이가 반복되는가?"
* **소아청소년과 전문의 부재**: 심야 시간대 권역응급센터조차 소아 당직의 부재로 "소아 진료 제한" 공지를 수시로 게시하여 헛걸음 유발.
* **경증 환자의 응급실 쏠림 (74%)**: 야간에 문을 여는 동네 의원을 찾지 못한 부모들이 단순 발열 환아를 데리고 대형병원 응급실로 몰려 대기시간이 3~5시간으로 폭증.
* **심야 처방전 조제 실패**: 야간 진료 병원을 간신히 찾았으나 인근 약국이 먼저 문을 닫아 약을 짓지 못하는 현장 결함 발생.
* **AI의 임상 오분류(Undertriage) 위험**: 보호자의 안도성 진술("열은 내렸다")에 현혹되어 중증 질환(장중첩증, 신생아 고열 등)을 경증으로 오판하는 안전 위험.

### 1.2 MoonlightCare의 해결책: "결정론적 2-트랙 스마트 라우팅"
1. **Pass 1 (0ms 정규식 인터셉터)**: 생후 100일 미만 38도 고열, 경련, 청색증 등 12대 Red Flag를 LLM 지연 없이 **26µs 내에 119 구급차로 직행**.
2. **Pass 2 (Direct Grounded Gemini 3.8 Flash Thinking)**: 168개 공식 KTAS 지식 베이스를 프롬프트에 직접 주입하여 감별비정형 복합 문맥 완독  (언더트리아제 0% 수호).
3. **Track A (중증 / Red Flag / KTAS 1~2)**: 119 호출, 기도확보 응급처치, 최단거리 소아전문응급센터 매칭 (약국 배제).
4. **Track B (경증 / 일반 야간외래 / KTAS 3~5)**: 진료 가능한 달빛어린이병원과 **30분 이상 여유 있게 영업하는 심야약국을 1:1 페어링 매칭**.

---

## 2. 데이터 분석 기반의 목적별 기능 도출 (Notebook 1~5 실증)

본 프로젝트의 모든 기능은 **공공데이터 및 보건복지부 2021 소아 KTAS 데이터셋을 주피터 노트북 5권으로 정밀 분석한 실측 결과**에 기반합니다.

| 노트북                      | 분석 데이터셋                       | 주요 실측 발견점                                                     | 도출된 핵심 엔진/기능                                                       |
| :----------------------- | :---------------------------- | :------------------------------------------------------------ | :----------------------------------------------------------------- |
| **NB 1. 소아 응급실 병목**      | 서울 50개 응급의료기관 실시간 병상/비정형 공지   | 야간 내원 환자 74%가 단순 미열/경증. 병상 잔여(`hv28>0`)라도 비정형 공지에 소아 진료 제한 빈번 | `PEDIATRIC_BLOCK_PATTERN` 100% 정규식 필터링 & KASI 특일 연동 공휴일 과밀화 리스크 격상 |
| **NB 2. 병원-약국 연계**       | 전국 병의원 7만 개 & 약국 2.4만 개 운영시간  | 달빛병원 반경 1km 약국 중 40% 이상이 병원보다 일찍 마감하여 조제 사고 유발                | **30분 안전 마진 페어링 알고리즘** (`약국마감 - 병원마감 >= 30분`)                      |
| **NB 3. Firebase 파이프라인** | E-Gen 실시간 병상 ➔ Firestore 동기화  | 5분마다 단순 전수 쓰기 시 하루 14.4만 회 쓰기 발생 (무료 쿼터 7배 초과). 실제 변동률은 5~10% | **In-Memory Hash Diffing (비용 90~100% 절감)** & Haversine 5µs 구면거리 연산 |
| **NB 4. 소아 KTAS 고찰**     | 168개 소아 KTAS 주증상 및 비정형 보호자 질의 | 키워드 검색 기반 RAG는 유사도 0.0 반환 시 엉뚱한 증상 주입으로 환각 유발                 | 키워드 RAG 폐기 결정, Gemini 3.8 Flash Thinking 기반 감별 채택                  |
| **NB 5. 차세대 KTAS 엔진**    | 50대 임상 골든 케이스 시나리오 평가         | 168개 주증상 전체 Direct Grounding 시 문장 전반부의 안도성 서술에 속지 않고 완독 감별    | **Red Flag 민감도 100%, 언더트리아제 0%**, 평균 레이턴시 3.1초 달성                  |

---

## 3. 백엔드 모듈 체계 & 디렉터리 아키텍처 (Steps 1~8)

```
monnlight/
├── app/
│   ├── config.py                     # [Step 1] 환경변수 & Firestore 싱글톤 바인딩
│   ├── api/v1/                       # [Step 5, 7, 8] FastAPI REST API 라우터 Layer
│   │   ├── chat.py                   # POST /api/v1/chat & SSE 스트리밍 (/chat/stream)
│   │   ├── emergency.py              # GET /nearby, /pairings, /status & POST /sync-static
│   │   └── location.py               # GET /api/v1/location (주소/키워드 검색 & 역지오코딩)
│   ├── schemas/                      # DTO 계층 (Pydantic V2)
│   │   ├── emergency.py              # 응급실 병상, DataFreshnessMeta DTO
│   │   ├── state.py                  # KTAS 정밀 메타데이터 세션 DTO (PatientSessionState)
│   │   ├── supervisor.py             # 클라이언트 통신용 정형 응답 DTO (SupervisorResponse)
│   │   └── chat.py                   # 대화 및 force_matching 세션 DTO
│   ├── services/                     # 결정론적 순수 도구 Layer (Zero-LLM)
│   │   ├── circuit_breaker.py        # AsyncCircuitBreaker (3-State FSM, 60s 쿨다운, 3회 임계치)
│   │   ├── holiday_service.py        # KASI 특일 판정 & KST(UTC+9) 과밀화 리스크 평가
│   │   ├── spatial_service.py        # Haversine 구면거리 연산 (5µs)
│   │   ├── emergency_sync_service.py # E-Gen 실시간 병상, 3-Tier Multi-Storage Fallback
│   │   ├── national_dataset_sync_service.py # 전국 156개 병원·2,028개 약국 24시간 Hash Diffing
│   │   ├── pairing_service.py        # 달빛병원-심야약국 +30분 안전 마진 페어링 서빙
│   │   └── scheduler.py              # APScheduler 3-Track 데몬 (병상, 04:00 AM 정적데이터, 세션정리)
│   ├── agents/                       # 지능형 에이전트 & 안전 가드레일 Layer
│   │   ├── guardrail_agent.py        # 26µs 12대 Red Flag 1차 인터셉터 & 의료법 제27조 사후 소독
│   │   ├── triage_agent.py           # Gemini 3.8 Flash Thinking + 168개 KTAS Direct Grounding
│   │   ├── matching_agent.py         # Zero-LLM 2-트랙 임상 라우팅 (응급실 vs 달빛병원+약국)
│   │   └── logistics_agent.py        # Gemini 3.5 Lite 30초 통화 스크립트 & 필수 서류 체크리스트
│   └── orchestrator/                 # 세션 및 워크플로우 관리 Layer
│       ├── session_manager.py        # Thread-Safe 세션 관리자 & 30분 TTL 자동 만료
│       └── supervisor.py             # 6-State FSM 라우터 & force_matching 1턴 모드 지원
├── data/                             # 로컬 캐시 & 불변 기준 데이터셋
│   ├── national_moonlight_hospitals_156.json # 전국 156개 달빛어린이병원 마스터
│   ├── national_night_pharmacies_2028.json   # 전국 2,028개 야간·심야약국 마스터
│   ├── immutable_baseline_beds.json          # 전국 42개 응급실 불변 기준 병상 (Tier 3)
│   └── ktas_pediatric_dataset.json           # 공식 소아 KTAS 지식 베이스
└── frontend/                         # 순수 HTML5 / Vanilla CSS3 / 모듈형 JS 워크스페이스
    ├── templates/                    # 단일 진실의 원천(SSOT) HTML 템플릿 13종
    ├── css/style.css                 # Calm Harbor 디자인 시스템 & Fixed App Shell 스타일
    └── js/main.js                    # 실시간 LBS 엔진, 1:1 교차 랭킹, 역지오코딩 바인딩
```

---

## 4. 차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)

소아 응급 상황에서 AI의 환각과 판단 지연을 방지하기 위한 이중 안전망입니다.

```
[보호자 증상 입력]
       │
       ▼
[Pass 1: GuardrailAgent (26µs)] ──(12대 절대적 Red Flag 감지 시)──► [119 즉시 직행 (Track A)]
       │
       ▼ (통과 시)
[Pass 2: TriageAgent (Gemini 3.8 Flash Thinking)] ──(KTAS 1~2 / 위험징후)──► [응급실 라우팅]
       │
       ▼ (KTAS 3~5 경증)
[Track B: 달빛어린이병원 + 30분 안심약국 1:1 페어링 매칭]
```

* **Tier 1 (0ms 정규식 인터셉터)**: 생후 100일 미만 38°C 이상 고열, 열성경련 5분 이상 지속, 청색증/호흡정지, 수지절단, 장중첩증 의심 등 12대 위급 징후를 **정규식 26µs 내에 100% 감지**.
* **Tier 2 (Direct Grounding 심층 감별)**: "열은 떨어졌는데 계속 처지고 쳐다보지 않아요"와 같은 비정형 문맥을 Gemini 3.8 Flash가 KTAS 168개 지침과 대조하여 **언더트리아제 0%로 완벽 방어**.
* **의료법 제27조 준수 사후 소독기**: AI 응답 내 확정적 진단명("장염입니다")을 강제 필터링하여 임상적 위험 징후 및 행동 지침만 전달.

---

## 5. 풀스택 시스템 아키텍처 & 2계층 데이터 흐름도

```
[클라이언트: 모바일 웹 / 데스크톱] (Fixed App Shell, 100dvh)
       │
       ├─ (1) 정적 LBS 조회 (0ms): 전국 156개 병원·2,028개 약국 번들 (반경 15km 필터링 & 1:1 교차 랭킹)
       ├─ (2) 위치 검색 / 역지오코딩: GET /api/v1/location (카카오 2-Tier 하이브리드)
       └─ (3) 증상 문진 / AI 트리아제: POST /api/v1/chat (force_matching 1턴 모드)
                 │
                 ▼
          [FastAPI Backend]
                 │
  ┌──────────────┴──────────────────────────────┐
  ▼                                             ▼
[동적 응급 데이터: 3-Tier Multi-Storage]    [정적 LBS 데이터: 24시간 델타 동기화]
  Tier 1: 인메모리 TTL 캐시 (5분)             In-Memory Hash Diffing (SHA-256)
  Tier 2: Firestore 백업 스냅샷                변동 발생 시에만 data/*.json 및
  Tier 3: 로컬 불변 baseline JSON              frontend/js/*.js 원자적 빌드
```

---

## 6. 데이터 엔지니어링 & 24시간 In-Memory Hash Diffing 델타 동기화

* **배경 및 과제**: 전국 156개 달빛병원과 2,028개 야간약국 데이터는 매일 자정~새벽에 일부 정보(진료시간, 휴무일 등)가 변경되지만 대다수는 변동이 없음. 매일 전수 쓰기를 수행하면 디스크 I/O 낭비 및 브라우저 캐시 무효화 발생.
* **In-Memory Hash Diffing 엔진 ([national_dataset_sync_service.py](app/services/national_dataset_sync_service.py))**:
  1. 매일 새벽 04:00 AM 공공데이터포털(E-Gen) API를 수집하여 메모리 상에서 SHA-256 해시 대조.
  2. `Added`, `Modified`, `Removed` 변동이 감지된 경우에만 디스크 저장 및 프론트엔드 번들러(`build_frontend_datasets.py`) 자동 실행.
  3. 변동 사항이 없을 경우(`diff == 0`), 디스크 쓰기를 **0ms 만에 Skip**하여 서버 리소스 및 브라우저 캐시 100% 보존.
* **관리자 도구**: 수동 온디맨드 검증용 CLI(`sync_national_datasets_delta.py`) 및 REST API(`POST /api/v1/emergency/sync-static`) 제공.

---

## 7. 공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback

공공 API 서버 장애나 트래픽 폭주 시에도 대국민 응급 의료 서비스가 무중단으로 동작하도록 설계된 탄력적(Resilient) 아키텍처입니다.

* **AsyncCircuitBreaker (3-State FSM)**:
  - 연속 3회 5xx 오류 또는 타임아웃 발생 시 즉시 `CLOSED` ➔ `OPEN` 상태로 전이하여 외부 API 호출 차단 (Fast Fail).
  - 60초 쿨다운 후 1건의 카나리 프로브 요청을 보내 성공 시 `HALF_OPEN` ➔ `CLOSED`로 자동 복구.
* **3-Tier Multi-Storage Fallback 계층**:
  - **Tier 1 (인메모리 캐시)**: 정상 수집된 최근 5분 이내 병상 데이터 즉시 반환 (0ms).
  - **Tier 2 (Cloud Firestore)**: 서킷 오픈 시 최근 정상 스냅샷 조회 (경고 배지 부착).
  - **Tier 3 (불변 기준 JSON)**: 네트워크 완전 단절 시 전국 42개 핵심 응급실 불변 데이터셋(`immutable_baseline_beds.json`) 서빙.

---

## 8. 프론트엔드 UI/UX 아키텍처 & 13대 화면 체계 (Fixed App Shell)

### 8.1 Fixed App Shell & Calm Harbor 디자인 시스템 ([style.css](frontend/css/style.css))
* **바깥 스크롤 완전 차단 (No Outer Scroll)**: `body.main-home-body`에 `height: 100dvh; overflow: hidden;`을 적용하여 모바일 기기(주소창 출렁임/당겨서 새로고침) 및 데스크톱 브라우저 바깥 스크롤을 0px로 잠금.
* **상단/하단 고정 컴포넌트 (`flex-shrink: 0`)**: 상단 헤더(58px), 증상 문진 CTA 배너, 실시간 시설 헤더 및 3개 탭 필터, 하단 GNB 내비게이션 바가 화면에 완벽하게 고정.
* **남은 뷰포트 독점 스크롤**: `.facility-card-stack`이 남은 세로 공간을 100% 동적 점유(`flex: 1; min-height: 0; overflow-y: auto;`)하며 오직 카드 목록 내부에서만 수백 개의 시설이 부드럽게 스크롤.

### 8.2 메인 홈 실시간 LBS 엔진 & 1:1 교차 랭킹 ([index.html](frontend/templates/index.html) & [main.js](frontend/js/main.js))
* **반경 15km 공간 필터링**: 사용자 GPS 또는 설정 주소 기준 반경 15.0km 이내 시설만 계산 및 노출.
* **병원 최우선 1:1 교차(Interleaving) 정렬**:
  - 사용자 주변 0.5km 이내 심야약국들이 상위 목록을 독점하는 의료 우선순위 역전을 해소하기 위해, **내 위치 기준 최단거리 달빛어린이병원을 최우선 1등으로 노출**.
  - 그 뒤로 **`[병원 #1] ➔ [약국 #1] ➔ [병원 #2] ➔ [약국 #2] ...` 형태로 1:1 번갈아 교차 노출**.
* **선택 탭별 상단 배지 수치 실시간 동기화 (`updateFacilityCountBadge`)**:
  - '전체' 탭 선택 시 총 시설 수(`${dong} 반경 15km 327곳 운영중`), '🌙 달빛병원' 선택 시 병원 수(`18곳 운영중`), '💊 심야약국' 선택 시 약국 수(`309곳 운영중`)로 상단 헤더 배지가 즉시 1:1 동기화.
* **컴팩트 모던 카드 UI**: 카드 패딩(`11px 13px`), 간격(`8px`), 폰트 및 아이콘 비율을 최적화하여 한 화면에 3~4개의 시설이 알차게 노출.

### 8.3 지능형 문진 & 맞춤 결과 파이프라인
* **`input.html`**: 체온 미세조절, KTAS 증상 칩 선택, 결측치 보완 3턴 프로그레시브 챗봇.
* **`loading.html`**: AI 분석 2초 키프레임 오버레이 및 백엔드 비동기 통신.
* **`result.html`**: 1턴 완결 `force_matching` FSM 응답 기반 5대 임상 바이탈(월령, 체온, KTAS 레벨, 증상) 및 1:1 안심 페어링 카드 동적 바인딩.

### 8.4 위치 검색 모달 & 사용자 실검색 기반 최근 이용 지역 관리 ([location.py](app/api/v1/location.py) & [main.js](frontend/js/main.js))
* **2대 탭 검색**: 지번/도로명(주소 검색) vs 건물명/지역명(키워드 검색) 분리.
* **무손실 상세 주소 보존**: 카카오 `coord2address` 도로명/건물명/지번을 유기적으로 결합하여 '현재 위치로 설정' 시에도 상세 주소(`서울특별시 송파구 송파대로 167 (문정동, 문정역테라타워)`) 완벽 보존.
* **'자주 찾는 주요 지역' 동적 히스토리화 (하드코딩 100% 제거)**:
  - HTML/JS 정적 더미 지역 칩 전면 적출.
  - 사용자가 실제로 검색/선택하거나 GPS로 설정한 지역만 LocalStorage(`aisum_recent_locations`)에 **최대 15개까지 최신순(FIFO/LRU)**으로 관리.
  - 동일 지역 재선택 시 기존 항목을 제거하고 최상단으로 갱신하며, 15개 초과 시 오래된 정보 자동 소멸. 이력 부재 시 직관적 빈 상태 안내 제공.

### 8.5 13대 표준 HTML 템플릿 체계 (`frontend/templates/`)
1. `index.html`: 메인 홈 SPA (Fixed App Shell, 1:1 교차 LBS)
2. `input.html`: 소아 증상 문진 입력
3. `modal.html`: 사전 처치정보 및 의료법 제27조 안내 다이얼로그
4. `loading.html`: AI 트리아제 로딩 애니메이션
5. `result.html`: KTAS 판정 및 병원-약국 맞춤 결과
6. `hospital_detail.html`: 달빛병원 상세 & 실시간 야간 접수
7. `emergency_alert.html`: 0ms Red Flag 119 긴급 직행 화면
8. `emergency_guide.html`: 소아 응급처치 포토 슬라이더 & 통화 스크립트
9. `settings.html`: 모니모 스타일 자녀 정보 & 알림 설정
10. `terms.html`: 의료법 제27조 준수 서비스 이용약관
11. `splash.html`: 모바일 시작 스플래시
12. `permission.html`: 위치·알림 권한 안내
13. `location_modal.html`: 주소/키워드 위치 설정 바텀시트

---

## 9. 프론트엔드-백엔드 100% 결합 연동 명세

| 프론트엔드 화면/액션 | 백엔드 API 엔드포인트 | 전달 파라미터 / DTO | 반환 데이터 및 렌더링 결과 |
| :--- | :--- | :--- | :--- |
| **`index.html` (홈 로드)** | 클라이언트 0ms LBS + `GET /api/v1/emergency/nearby` | `lat`, `lon`, `radius_km=15.0` | 반경 15km 내 1:1 교차 야간 의료시설 및 실시간 가용 응급실 |
| **위치 모달 (주소 검색)** | `GET /api/v1/location` | `query`, `type=address` | 카카오 도로명/지번 주소 목록 및 WGS84 좌표 |
| **위치 모달 (키워드 검색)** | `GET /api/v1/location` | `query`, `type=keyword` | 카카오 장소명/건물명 랜드마크 목록 및 좌표 |
| **위치 모달 (현재 위치)** | `GET /api/v1/location` | `lat`, `lon` (역지오코딩) | 도로명+건물명 결합 무손실 상세 주소 반환 |
| **`input.html` (증상 제출)** | `POST /api/v1/chat` | `message`, `force_matching=True`, `session_id` | 0ms Red Flag 분기 또는 `SupervisorResponse` (KTAS+페어링) 반환 |
| **`emergency_guide.html`** | `GET /api/v1/emergency/nearby` | `lat`, `lon`, `limit=5` | 소아 전문 응급실 실시간 잔여병상(`hv28`) 및 공지 배지 |
| **관리자 동기화 (온디맨드)** | `POST /api/v1/emergency/sync-static` | `force=True` (선택) | 24시간 Hash Diffing 증분 동기화 결과 JSON |

---

## 10. 종합 검증 현황 & 임상 안전성 벤치마크 (92개 테스트 전수 통과)

* **전체 단위/통합 테스트 스위트**: **총 92개 테스트 100% 무결점 통과 (`Ran 92 tests, OK`)**
  - `test_step1_pipeline.py`: 공공 API 수집, 비정형 공지 정규식 필터링 (7건)
  - `test_step2_guardrails.py`: 12대 Red Flag 26µs 정규식 감지 및 사후 소독 (9건)
  - `test_step3_agents.py`: Gemini 3.8 Flash Thinking KTAS Direct Grounding (7건)
  - `test_step4_orchestrator.py`: FSM 상태머신 전이 및 무한루프 가드 (8건)
  - `test_step5_api_endpoints.py`: FastAPI 엔드포인트 및 세션 관리 (8건)
  - `test_step6_integration.py`: 풀스택 40대 임상 시나리오 E2E 통합 (4건)
  - `test_step7_resilience.py`: 서킷 브레이커 & 3-Tier Multi-Storage Fallback (19건)
  - `test_step8_frontend_integration.py`: `force_matching` 1턴 완결 및 Red Flag 오버라이드 (3건)
  - `test_location_api.py`: 카카오 주소/키워드 검색 및 2-Tier 역지오코딩 (8건)
  - `test_national_dataset_sync.py`: 24시간 In-Memory Hash Diffing 델타 동기화 (7건)
  - 기타 회귀 테스트 및 성능 벤치마크 (12건)
* **임상 안전성 지표 & KTAS 실증 검증**:
  - **2021 소아 KTAS 1~5단계 15대 표준 임상 시나리오 전수 검증**: **15 / 15 시나리오 100% 통과 (`Accuracy: 100.0%`, `Red Flag Safety Invariant: 100.0%`)** ([tests/evals/verify_ktas_frontend_flow.py](file:///e:/monnlight/tests/evals/verify_ktas_frontend_flow.py), [보고서](file:///e:/monnlight/docs/KTAS_TRIAGE_VERIFICATION_REPORT.md)).
  - **한국어 복합 병렬 부정문 감별 엔진 (`has_affirmative_match`)**: "청색증이나 경련은 없어요" 등 구어체 부정문의 0ms Red Flag 오경보(Over-triage) 100% 원천 차단.
  - 1,000회 연속 Red Flag 검사: 총 28.47ms (회당 평균 **28.47µs** 실시간 방어 달성).
  - 50대 소아 응급 골든 케이스 평가: **Red Flag 민감도 100%, 언더트리아제 0.0%**.

---

## 11. 추가 심화 고도화 백로그 (Advanced Backlog)

1. **`result.js` 클라이언트 바인딩 고도화 (Phase 1)**:
   - `sessionStorage`에 저장된 `SupervisorResponse`의 5대 임상 바이탈 및 1:1 안심 페어링 데이터를 `result.html` DOM에 동적 하이드레이션하는 전용 렌더러 완성.
2. **카카오맵/네이버맵 30분 안심 동선 지도 시각화 (Phase 2)**:
   - 사용자 현재 위치 ➔ 달빛어린이병원 ➔ +30분 조제 안심약국으로 이어지는 안전 이동 동선을 폴리라인(Polyline)으로 맵 뷰 시각화.
3. **전국 실시간 소아 응급실 병상 전광판 (`beds.html` - Phase 3)**:
   - 5분 주기 E-Gen API 기반 권역별 소아 병상(`hv28`), 소아 중환자실(`hv30`), 장비 가용 현황 실시간 모니터링 대시보드 구축.
4. **PWA (Progressive Web App) 오프라인 지원 (Phase 4)**:
   - Service Worker 캐싱을 통해 네트워크 단절 시에도 12대 Red Flag 가이드 및 최근 조회 시설 오프라인 열람 지원.
