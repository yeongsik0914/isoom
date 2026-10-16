# 🌙 MoonlightCare 종합 기획안 & 개발 백서 (PLAN.md)

> **문서 버전**: v2.59 (병원 상세 화면의 공공 API 미제공 가상 대기 시간 지표 완전 삭제 및 2열 실측 메트릭 바(거리·주차) 개편 아키텍처 확립, v2.4.80)  
> **최종 갱신 일자**: 2026-10-16  
> **핵심 슬로건**: *"야간 소아 응급실 뺑뺑이를 막는 0ms 세이프티 가드레일 & 데이터 기반 2-트랙 지능형 라우터"*  
> **기반 원천**: 주피터 노트북 5권 실증 데이터, 국립중앙의료원(NMC)·한국천문연구원(KASI) 공공데이터, Firebase Cloud Firestore, Gemini 3.8 Flash (Thinking High) / 3.5 Lite, 2021 소아 KTAS 지침(168개 주증상), AsyncCircuitBreaker(3-State FSM), In-Memory Hash Diffing 델타 동기화, data/ 폴더 캐노니컬 JSON 상세 데이터셋, 5-Layer Smart Back Navigation & < 0.05ms 초고속 인메모리 인덱스.

---

## 📑 목차 (Table of Contents)

1. [프로젝트 기획 배경 & 핵심 문제 정의](#1-프로젝트-기획-배경--핵심-문제-정의)
2. [데이터 분석 기반의 목적별 기능 도출 (Notebook 1~5 실증)](#2-데이터-분석-기반의-목적별-기능-도출-notebook-15-실증)
3. [백엔드 모듈 체계 & 디렉터리 아키텍처 (Steps 1~9)](#3-백엔드-모듈-체계--디렉터리-아키텍처-steps-19)
4. [차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)](#4-차세대-2계층-안전-감시망-two-tier-red-flag-v2-architecture)
5. [풀스택 시스템 아키텍처 & 2계층 데이터 흐름도](#5-풀스택-시스템-아키텍처--2계층-데이터-흐름도)
6. [데이터 엔지니어링 & 24시간 In-Memory Hash Diffing 델타 동기화](#6-데이터-엔지니어링--24시간-in-memory-hash-diffing-델타-동기화)
7. [공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback](#7-공공-api-서킷-브레이커--3-tier-multi-storage-fallback)
8. [프론트엔드 UI/UX 아키텍처 & 14대 화면 체계 (Fixed App Shell)](#8-프론트엔드-uiux-아키텍처--14대-화면-체계-fixed-app-shell)
9. [프론트엔드-백엔드 100% 결합 연동 명세](#9-프론트엔드-백엔드-100-결합-연동-명세)
10. [종합 검증 현황 & 임상 안전성 벤치마크 (100개 테스트 전수 통과)](#10-종합-검증-현황--임상-안전성-벤치마크-100개-테스트-전수-통과)
11. [추가 심화 고도화 백로그 (Advanced Backlog)](#11-추가-심화-고도화-백로그-advanced-backlog)

---

## 1. 프로젝트 기획 배경 & 핵심 문제 정의

### 1.1 사회적 배경: "왜 야간 소아 응급실 뺑뺑이가 반복되는가?"
* **소아청소년과 전문의 부족**: 심야 시간대 대학병원 및 권역응급의료센터조차 소아 당직의 부재로 "소아 진료 불가" 공지를 수시로 띄움.
* **경증 환자의 응급실 쏠림 (74%)**: 야간에 문을 여는 동네 의원을 찾지 못한 부모들이 단순 미열/감기 환아를 데리고 권역응급센터로 몰려 대기 시간이 3~5시간으로 폭증하고, 정작 중증 환아(KTAS 1~2)의 골든타임이 침해됨.
* **심야 처방전 조제 사고**: 야간에 진료하는 달빛어린이병원을 간신히 찾아 진료를 받았으나, 인근 약국이 먼저 문을 닫아 처방약을 짓지 못하고 발을 동동 구르는 현장 결함 발생.
* **AI의 임상 오분류(Undertriage) 위험**: 보호자의 일시적 안도성 표현("열은 내렸다", "지금은 깨어났다")에 현혹되어 중증 질환(장중첩증, 크룹, 수지절단, 신생아 발열)을 경증으로 오판하는 안전 위험 존재.

### 1.2 MoonlightCare의 해결책: "결정론적 2-트랙 스마트 라우팅"
1. **Pass 1 (0ms 정규식 인터셉터)**: 생후 100일 미만 38도 고열, 경련, 청색증 등 12대 Red Flag를 LLM 지연 없이 **26µs 내에 119 구급차로 직행**.
2. **Pass 2 (Direct Grounded Gemini 3.8 Flash Thinking)**: 168개 공식 KTAS 지식 베이스를 프롬프트에 직접 주입하여 비정형 복합 문맥 완독 감별 (언더트리아제 0% 수호).
3. **Track A (중증 / Red Flag / KTAS 1~2)**: 119 호출, 기도확보 응급처치, 최단거리 소아전문응급센터 매칭 (약국 배제).
4. **Track B (경증 / 일반 야간외래 / KTAS 3~5)**: 진료 가능한 달빛어린이병원과 **30분 이상 여유 있게 영업하는 심야약국을 1:1 페어링 매칭**.
5. **의료법 제27조 준수**: 특정 병원 알선/유인을 배제하고 진단 확정이 아닌 전문의 대면 진찰의 필요성을 명시하는 안전 가드레일 확립.

---

## 2. 데이터 분석 기반의 목적별 기능 도출 (Notebook 1~5 실증)

본 프로젝트의 모든 기능은 **공공데이터 및 보건복지부 2021 소아 KTAS 데이터셋을 주피터 노트북 5권으로 정밀 분석한 실측 결과**에 기반합니다.

| 노트북 | 분석 데이터셋 | 주요 실측 발견점 | 도출된 핵심 엔진/기능 |
| :--- | :--- | :--- | :--- |
| **NB 1. 소아 응급실 병목** | 서울 50개 응급의료기관 실시간 병상/비정형 공지 | 야간 내원 환자 74%가 단순 미열/경증. 병상 잔여(`hv28>0`)라도 비정형 공지에 소아 진료 제한 빈번 | `PEDIATRIC_BLOCK_PATTERN` 100% 정규식 필터링 & KASI 특일 연동 공휴일 과밀화 리스크 격상 |
| **NB 2. 병원-약국 연계** | 전국 병의원 7만 개 & 약국 2.4만 개 운영시간 | 달빛병원 반경 1km 약국 중 40% 이상이 병원보다 일찍 마감하여 조제 사고 유발 | **30분 안전 마진 페어링 알고리즘** (`약국마감 - 병원마감 >= 30분`) |
| **NB 3. Firebase 파이프라인** | E-Gen 실시간 병상 ➔ Firestore 동기화 | 5분마다 단순 전수 쓰기 시 하루 14.4만 회 쓰기 발생 (무료 쿼터 7배 초과). 실제 변동률은 5~10% | **In-Memory Hash Diffing (비용 90~100% 절감)** & Haversine 5µs 구면거리 연산 |
| **NB 4. 소아 KTAS 고찰** | 168개 소아 KTAS 주증상 및 비정형 보호자 질의 | 키워드 검색 기반 RAG는 유사도 0.0 반환 시 엉뚱한 증상 주입으로 환각 유발 | 키워드 RAG 폐기 결정, Gemini 3.8 Flash Thinking 기반 감별 채택 |
| **NB 5. 차세대 KTAS 엔진** | 50대 임상 골든 케이스 시나리오 평가 | 168개 주증상 전체 Direct Grounding 시 문장 전반부의 안도성 서술에 속지 않고 완독 감별 | **Red Flag 민감도 100%, 언더트리아제 0%**, 평균 레이턴시 3.1초 달성 |

---

## 3. 백엔드 모듈 체계 & 디렉터리 아키텍처 (Steps 1~9)

```text
monnlight/
├── app/
│   ├── config.py                     # [Step 1] 환경변수 & Firestore 싱글톤 바인딩
│   ├── api/v1/                       # [Step 5, 7, 8] FastAPI REST API 라우터 Layer
│   │   ├── chat.py                   # POST /api/v1/chat & SSE 스트리밍 (/chat/stream)
│   │   ├── emergency.py              # GET /nearby, /pairings, /status, /facility-detail & POST /sync-static
│   │   └── location.py               # GET /api/v1/location (주소/키워드 검색 & 역지오코딩)
│   ├── schemas/                      # DTO 계층 (Pydantic V2)
│   │   ├── emergency.py              # 응급실 병상, DataFreshnessMeta DTO
│   │   ├── chat.py                   # 사용자 질의 및 바이탈 DTO
│   │   └── supervisor.py             # 5대 바이탈, 매칭 시설, 30초 대본, clinical_rationale DTO
│   ├── agents/                       # 4대 지능형 에이전트 계층
│   │   ├── guardrail_agent.py        # [Step 2] 12대 Red Flag 26µs 즉각 차단 & 의료법 제27조 소독
│   │   ├── triage_agent.py           # [Step 3] Gemini 3.8 Flash KTAS Grounding & 임상 변수 추출
│   │   ├── matching_agent.py         # [Step 4] 달빛병원 +30분 안심약국 1:1 페어링 & 소아 응급실 매칭
│   │   └── logistics_agent.py        # [Step 4] 30초 유선 확인 통화 스크립트 & 본인확인 서류 안내
│   ├── orchestrator/                 # 멀티 에이전트 총괄 오케스트레이터
│   │   ├── supervisor.py             # 6-State FSM, 3턴 교착 방어, 1턴 완결 force_matching & 임상 가드레일
│   │   └── session_manager.py        # Firestore / In-Memory 세션 지속성 관리자
│   └── services/                     # 코어 데이터 & 인프라 서비스
│       ├── circuit_breaker.py        # [Step 7] 공공 API 3-State FSM 비동기 서킷 브레이커
│       ├── fallback_storage.py       # [Step 7] L1 메모리 / L2 Firestore / L3 불변 JSON 3계층 스토리지
│       ├── facility_db_service.py    # [Step 9] data/ 폴더 캐노니컬 JSON 기반 < 0.05ms 인메모리 인덱서
│       ├── national_dataset_sync_service.py # [Step 8, 9] 24시간 In-Memory Hash Diffing 증분 동기화
│       └── scheduler.py              # [Step 6, 8] APScheduler 3-Track 백그라운드 워커
├── data/                             # 불변 캐노니컬 마스터 데이터셋 (Git 추적 관리)
│   ├── README.md                     # 데이터셋 명세서
│   ├── hospital_details.json         # 전국 156개 달빛병원 상세 메타데이터 (255KB)
│   ├── pharmacy_details.json         # 전국 2,028개 야간약국 상세 메타데이터 (2.8MB)
│   ├── national_moonlight_hospitals_156.json # 전국 156개 달빛어린이병원 (107KB)
│   ├── national_night_pharmacies_2028.json    # 전국 2,028개 야간심야약국 (1.4MB)
│   ├── ktas_pediatric_dataset.json   # 2021 공식 소아 KTAS 168개 주증상 지식 베이스 (388KB)
│   ├── nationwide_pairings.json      # 전국 병원-약국 30분 마진 안심 페어링 (252KB)
│   ├── seoul_emergency_coords.json   # 서울 530개 응급의료기관 위경도 (37KB)
│   └── moonlight.db                  # 로컬 SQLite 캐시 DB (2MB)
├── frontend/                         # 순수 HTML5/CSS3/Vanilla JS 프론트엔드
│   ├── templates/                    # 단일 진실의 원천(SSOT) HTML 템플릿 14종
│   ├── css/style.css                 # Calm Harbor 디자인 시스템 & Fixed App Shell 스타일
│   └── js/                           # 실시간 LBS 엔진 및 24시간 자동 빌드 JS 번들 4종
│       ├── hospital_details_data.js  # [Step 9] 달빛병원 상세 클라이언트 오프라인 듀얼 로더 번들
│       ├── pharmacy_details_data.js  # [Step 9] 야간약국 상세 클라이언트 오프라인 듀얼 로더 번들
│       ├── national_moonlight_hospitals_156.js
│       ├── national_night_pharmacies_2028.js
│       └── main.js                   # 실시간 LBS 엔진, 1:1 교차 랭킹, 역지오코딩 바인딩
└── tests/                            # 100개 단위/통합 테스트 스위트 (100% 무결점 통과)
```

---

## 4. 차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)

1. **Tier 1 (Zero-Latency Pre-Interceptor)**:
   - **위치**: `app/agents/guardrail_agent.py` (`check_red_flag_instant`)
   - **방식**: 컴파일된 고성능 정규표현식 기반 26µs 실시간 검사 및 한국어 복합 부정문 감별 엔진(`has_affirmative_match`).
   - **대상**: 호흡부전(청색증), 경련(발작), 의식저하, 생후 100일 미만 38℃ 고열, 수지절단, 안면/수부 화상 등 12대 응급 징후.
   - **동작**: 감지 즉시 LLM 호출을 건너뛰고 119 구급차 호출 화면(`emergency_alert.html`)으로 직행.
2. **Tier 2 (Post-LLM Safety Sanitizer)**:
   - **위치**: `app/agents/guardrail_agent.py` (`sanitize_output`)
   - **방식**: 모든 에이전트 응답이 클라이언트로 전송되기 직전에 통과하는 단일 출구 게이트웨이.
   - **동작**: 불법 질병 진단, 특정 복용 용량 지시, 위험 민간요법을 소독하고 의료법 제27조 고지 문구 자동 주입.

---

## 5. 풀스택 시스템 아키텍처 & 2계층 데이터 흐름도

```mermaid
graph TD
    Client["웹 프론트엔드 (input.html / index.html)"] -->|POST /api/v1/chat| Supervisor["Supervisor Orchestrator (FSM)"]
    Supervisor -->|1차 검사 (26µs)| Guardrail["Guardrail Agent (Tier 1 Red Flag)"]
    Guardrail -->|위급 감지| Emergency["119 긴급 직행 (emergency_alert.html)"]
    Guardrail -->|안전 통과| Triage["Triage Agent (소아 KTAS 직접 대조)"]
    Triage -->|임상 변수 완성| Matching["Matching Agent (병원-약국 30분 안심 페어링)"]
    Matching --> Logistics["Logistics Agent (30초 통화 대본 & 본인확인 서류)"]
    Logistics -->|출구 소독| Sanitizer["Guardrail Agent (Tier 2 의료법 소독)"]
    Sanitizer -->|SupervisorResponse| Result["맞춤 결과 화면 (result.html)"]
```

---

## 6. 데이터 엔지니어링 & 24시간 In-Memory Hash Diffing 델타 동기화

* **배경 및 과제**: 전국 156개 달빛병원과 2,028개 야간약국 데이터는 매일 자정~새벽에 일부 정보(진료시간, 휴무일 등)가 변경되지만 대다수는 변동이 없음. SQLite 파일 DB 의존성을 배제하고, `data/` 디렉터리에 사람이 읽고 검증 가능한 캐노니컬 JSON 데이터셋을 단일 진실의 원천(SSOT)으로 확립.
* **In-Memory Hash Diffing 엔진 ([national_dataset_sync_service.py](file:///e:/monnlight/app/services/national_dataset_sync_service.py))**:
  1. 매일 새벽 04:00 AM 공공데이터포털(NMC) 국립중앙의료원 API를 수집하여 메모리 상에서 SHA-256 해시 대조.
  2. `Added`, `Modified`, `Removed` 변동이 감지된 경우에만:
     - 코어 JSON 2종(`national_moonlight_hospitals_156.json`, `national_night_pharmacies_2028.json`) 저장
     - 상세 JSON 2종(`hospital_details.json`, `pharmacy_details.json`) 동시 가공 및 저장
     - 프론트엔드 JS 번들 4종(`hospital_details_data.js`, `pharmacy_details_data.js`, `national_moonlight_hospitals_156.js`, `national_night_pharmacies_2028.js`) 일제히 동시 빌드
     - In-Memory 캐시 핫 리로드(`reload_dataset_cache()`) 트리거.
  3. 변동 사항이 없을 경우(`diff == 0`), 디스크 쓰기를 **0ms 만에 Skip**하여 서버 리소스 및 브라우저 캐시 100% 보존.
* **관리자 도구**: 수동 온디맨드 검증용 CLI(`sync_national_datasets_delta.py`) 및 REST API(`POST /api/v1/emergency/sync-static`) 제공.

---

## 7. 공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback

* **서킷 브레이커**: 공공 API 연속 3회 실패 시 `OPEN` 상태로 전이하여 60초간 외부 호출을 차단하고 로컬 폴백 모드로 즉시 전환.
* **3계층 스토리지 전략**:
  - **L1 (In-Memory)**: 5분 TTL 인메모리 캐시 (0ms 초고속 서빙).
  - **L2 (Firestore)**: 최근 정상 동기화된 클라우드 NoSQL 스토리지.
  - **L3 (Local JSON)**: 서버에 영구 보관된 156개 달빛병원·2,028개 심야약국 불변 마스터셋.
* **성과**: 공공 API 장애 및 서버 점검 중에도 **가용성 100% 무중단 서비스** 유지.

---

## 8. 프론트엔드 UI/UX 아키텍처 & 14대 화면 체계 (Fixed App Shell)

### 8.1 고정 앱 셸 (Fixed App Shell) 아키텍처
* **바깥 스크롤 0px 원천 차단**: 모바일 및 데스크톱 뷰포트에서 상단 헤더, 증상 배너, 탭 필터, 하단 GNB를 완벽 고정(`flex-shrink: 0`).
* **내부 독립 스크롤**: 오직 실시간 시설 카드 목록(`.facility-card-stack`) 내부에서만 수백 개의 시설이 부드럽게 스크롤되도록 격리.

### 8.2 메인 홈 실시간 LBS 엔진 & 1:1 교차 랭킹 ([index.html](file:///e:/monnlight/frontend/templates/index.html) & [main.js](file:///e:/monnlight/frontend/js/main.js))
* **반경 15km 공간 필터링**: 사용자 GPS 또는 설정 주소 기준 반경 15.0km 이내 시설만 계산 및 노출.
* **병원 최우선 1:1 교차(Interleaving) 정렬**:
  - 사용자 주변 근거리 심야약국의 상단 독점을 방지하고, **내 위치 기준 최단거리 달빛어린이병원을 최우선 1등으로 노출**.
  - 그 뒤로 **`[병원 #1] ➔ [약국 #1] ➔ [병원 #2] ➔ [약국 #2] ...` 형태로 1:1 번갈아 교차 노출**.
* **선택 탭별 상단 배지 수치 실시간 동기화 (`updateFacilityCountBadge`)**:
  - '전체', '🌙 달빛병원', '💊 심야약국' 탭 전환 시 상단 헤더 배지 수치가 즉시 1:1 동기화.

### 8.3 지능형 문진 & 맞춤 결과 파이프라인
* **`input.html`**:
  - 소아 임상 2단계 가드레일: 초성(`ㅋㅋㅋ`), 잡담(`안녕`, `배고파`), 무의미어 필터링 차단 및 60여 종 소아 임상 표준 증상 필수 검증.
  - 나이/체온 미입력 시 강제 기본값(24개월, 38℃) 변조 방지 및 회색 뱃지(`체온 미측정(모름)`) 무손실 연동.
  - 180도 부채꼴 게이지 다이얼 체온계(기본 36.5℃ 정상 체온), 연령 슬라이더, 해열제 성분별 정밀 카테고리화.
* **`loading.html`**: AI 분석 2초 키프레임 오버레이 및 백엔드 비동기 통신.
* **`result.html`**: 1턴 완결 `force_matching` FSM 응답 기반 5대 임상 바이탈(월령, 체온, KTAS 레벨, 증상) 및 1:1 안심 페어링 카드 동적 바인딩. Gemini 3.8 Flash 임상 감별 소견(`clinical_rationale`) 실시간 표출 및 미입력 바이탈 '모름' 무손실 렌더링.

### 8.4 위치 검색 모달 & 사용자 실검색 기반 최근 이용 지역 관리 ([location.py](file:///e:/monnlight/app/api/v1/location.py) & [main.js](file:///e:/monnlight/frontend/js/main.js))
* **2대 탭 검색**: 지번/도로명(주소 검색) vs 건물명/지역명(키워드 검색) 분리.
* **무손실 상세 주소 보존**: 카카오 `coord2address` 기반 상세 주소 완벽 보존.
* **'자주 찾는 주요 지역' 동적 히스토리화**: LocalStorage(`aisum_recent_locations`) 기반 최대 15개 최신순(FIFO/LRU) 관리.

### 8.5 14대 표준 HTML 템플릿 체계 (`frontend/templates/`)
1. `index.html`: 메인 홈 SPA (Fixed App Shell, 1:1 교차 LBS)
2. `input.html`: 소아 증상 문진 입력 (2단계 증상 가드레일)
3. `modal.html`: 사전 처치정보 및 의료법 제27조 안내 다이얼로그
4. `loading.html`: AI 트리아제 로딩 애니메이션
5. `result.html`: KTAS 판정 및 병원-약국 맞춤 결과
6. `hospital_detail.html`: 달빛어린이병원 전용 상세 페이지 (소아 전문의/일반의 현황, 주차 면수/요금/안내, 요일별 진료시간표, 인-페이지 카카오 지도 매핑, 22:30 조기마감 주의 배너, 2열 실측 메트릭 바(내 위치 거리·주차 지원), 5-Layer Smart Back Navigation, 하단 고정 통화 CTA)
7. `pharmacy_detail.html`: 심야약국 전용 상세 페이지 (상주 약사 현황, 복약지도 안내, +30분 조제 안전마진 표시, 요일별 심야 운영시간표, 인-페이지 카카오 지도 매핑, 1:1 연계 달빛어린이병원 카드, 5-Layer Smart Back Navigation, 하단 고정 통화 CTA)
8. `emergency_alert.html`: 0ms Red Flag 119 긴급 직행 화면
9. `emergency_guide.html`: 소아 응급처치 포토 슬라이더 & 통화 스크립트
10. `settings.html`: 모니모 스타일 자녀 정보 & 알림 설정
11. `terms.html`: 의료법 제27조 준수 서비스 이용약관
12. `splash.html`: 모바일 시작 스플래시
13. `permission.html`: 위치·알림 권한 안내
14. `location_modal.html`: 주소/키워드 위치 설정 바텀시트

---

## 9. 프론트엔드-백엔드 100% 결합 연동 명세

| 프론트엔드 화면/액션 | 백엔드 API 엔드포인트 | 전달 파라미터 / DTO | 반환 데이터 및 렌더링 결과 |
| :--- | :--- | :--- | :--- |
| **`index.html` (홈 로드)** | 클라이언트 0ms LBS + `GET /api/v1/emergency/nearby` | `lat`, `lon`, `radius_km=15.0` | 반경 15km 내 1:1 교차 야간 의료시설 및 실시간 가용 응급실 |
| **`index.html` (병원 카드 클릭)** | `/hospital_detail` 이동 & `GET /api/v1/emergency/facility-detail` | `type=hospital`, `name`, `lat`, `lon` | 전문의/일반의, 주차(면수/요금/안내), 내 위치 거리·주차 2열 실측 메트릭, 22:30 조기마감, 카카오 지도, 통화 번호 (0.05ms) |
| **`index.html` (약국 카드 클릭)** | `/pharmacy_detail` 이동 & `GET /api/v1/emergency/facility-detail` | `type=pharmacy`, `name`, `lat`, `lon` | 상주 약사, 복약지도, +30분 조제 안전마진, 연계 달빛병원, 카카오 지도, 통화 번호 (0.05ms) |
| **위치 모달 (주소 검색)** | `GET /api/v1/location` | `query`, `type=address` | 카카오 도로명/지번 주소 목록 및 WGS84 좌표 |
| **위치 모달 (키워드 검색)** | `GET /api/v1/location` | `query`, `type=keyword` | 카카오 장소명/건물명 랜드마크 목록 및 좌표 |
| **위치 모달 (현재 위치)** | `GET /api/v1/location` | `lat`, `lon` (역지오코딩) | 도로명+건물명 결합 무손실 상세 주소 반환 |
| **`input.html` (증상 제출)** | `POST /api/v1/chat` | `user_message`, `force_matching=True`, `patient_vitals` | 0ms Red Flag(사지절단 등) 최우선 분기, 네거티브 블랙리스트 필터링, Gemini 3.8 Flash 168개 소아 KTAS 1~5단계 및 추천 시설 100% 동적 바인딩 |
| **`emergency_guide.html`** | `GET /api/v1/emergency/nearby` | `lat`, `lon`, `limit=5` | 소아 전문 응급실 실시간 잔여병상(`hv28`) 및 공지 배지 |
| **관리자 동기화 (온디맨드)** | `POST /api/v1/emergency/sync-static` | `force=True` (선택) | 24시간 Hash Diffing 증분 동기화 결과 JSON |

---

## 10. 종합 검증 현황 & 임상 안전성 벤치마크 (100개 테스트 전수 통과)

* **전체 단위/통합 테스트 스위트**: **총 100개 테스트 100% 무결점 통과 (`Ran 100 tests in 236.787s, OK`)**
  - `test_step1_pipeline.py`: 공공 API 수집, 비정형 공지 정규식 필터링 (7건)
  - `test_step2_guardrails.py`: 12대 Red Flag 26µs 정규식 감지 및 사후 소독 (9건)
  - `test_step3_agents.py`: Gemini 3.8 Flash Thinking KTAS Direct Grounding (7건)
  - `test_step4_orchestrator.py`: FSM 상태머신 전이 및 무한루프 가드 (8건)
  - `test_step5_api_endpoints.py`: FastAPI 엔드포인트 및 세션 관리 (8건)
  - `test_step6_integration.py`: 풀스택 40대 임상 시나리오 E2E 통합 (4건)
  - `test_step7_resilience.py`: 서킷 브레이커 & 3-Tier Multi-Storage Fallback (19건)
  - `test_step8_frontend_integration.py`: `force_matching` 1턴 완결 및 Red Flag 오버라이드 (3건)
  - `test_facility_db_and_detail_api.py`: data/ 폴더 상세 JSON 2종, JS 번들 2종 무결성 및 <0.05ms In-Memory 인덱스 조회 검증 (8건)
  - `test_location_api.py`: 카카오 주소/키워드 검색 및 2-Tier 역지오코딩 (8건)
  - `test_national_dataset_sync.py`: 24시간 In-Memory Hash Diffing 델타 동기화 (7건)
  - 기타 회귀 테스트 및 성능 벤치마크 (12건)
* **임상 안전성 지표 & KTAS 실증 검증**:
  - **2021 소아 KTAS 1~5단계 15대 표준 임상 시나리오 전수 검증**: **15 / 15 시나리오 100% 통과 (`Accuracy: 100.0%`, `Red Flag Safety Invariant: 100.0%`)** ([tests/evals/verify_ktas_frontend_flow.py](file:///e:/monnlight/tests/evals/verify_ktas_frontend_flow.py), [보고서](file:///e:/monnlight/docs/KTAS_TRIAGE_VERIFICATION_REPORT.md)).
  - **한국어 복합 병렬 부정문 감별 엔진 (`has_affirmative_match`)**: "청색증이나 경련은 없어요" 등 구어체 부정문의 0ms Red Flag 오경보(Over-triage) 100% 원천 차단.
  - 1,000회 연속 Red Flag 검사: 총 32.90ms (회당 평균 **32.90µs** 실시간 방어 달성).
  - 50대 소아 응급 골든 케이스 평가: **Red Flag 민감도 100%, 언더트리아제 0.0%**.

---

## 11. 추가 심화 고도화 백로그 (Advanced Backlog)

1. **[완료] 의료시설(병원/약국) 2-트랙 상세 페이지 및 data/ 폴더 공공데이터 JSON 상세 데이터셋 + 24시간 동기화 파이프라인 (Phase 1)**:
   - SQLite DB 완전 폐지 ➔ `data/hospital_details.json`, `data/pharmacy_details.json` 캐노니컬 정적 데이터셋 구축.
   - 24시간 주기 Hash Diffing 스케줄러와 연동하여 data/ JSON 및 `frontend/js/` 번들 4종 동시 생성 & In-Memory 인덱스(<0.05ms) 서빙 완결.
   - `hospital_detail.html` (전문의, 주차, 대기시간, 22:30 조기마감 배너, 카카오맵, 하단 통화 CTA, 오프라인 듀얼 로더).
   - `pharmacy_detail.html` (상주 약사, 복약지도, +30분 조제 안전마진, 연계 달빛병원 카드, 카카오맵, 하단 통화 CTA, 오프라인 듀얼 로더).
2. **[완료] `result.html` 백엔드 임상 감별 소견 실시간 바인딩 & 미입력 바이탈 무손실 전달 (Phase 2)**:
   - `result.html` 내 JS SyntaxError 완전 복구, `SupervisorResponse.clinical_rationale` 실시간 표출, 미입력 바이탈 '모름' 무손실 렌더링 파이프라인 완결.
3. **[완료] 필수 캐노니컬 데이터셋 Git 형상관리 복원 & `.gitignore` 최적화 (Phase 3)**:
   - GitHub 클론 및 협업 환경에서 데이터 유실 방지를 위해 `data/` 내 핵심 JSON 7종 및 DB 파일 Git 추적 대상 정상 포함.
4. **카카오맵/네이버맵 30분 안심 동선 지도 시각화 (Phase 4)**:
   - 사용자 현재 위치 ➔ 달빛어린이병원 ➔ +30분 조제 안심약국으로 이어지는 안전 이동 동선을 폴리라인(Polyline)으로 맵 뷰 시각화.
5. **전국 실시간 소아 응급실 병상 전광판 (`beds.html` - Phase 5)**:
   - 5분 주기 E-Gen API 기반 권역별 소아 병상(`hv28`), 소아 중환자실(`hv30`), 장비 가용 현황 실시간 모니터링 대시보드 구축.
6. **PWA (Progressive Web App) 오프라인 지원 (Phase 6)**:
   - Service Worker 캐싱을 통해 네트워크 단절 시에도 12대 Red Flag 가이드 및 최근 조회 시설 오프라인 열람 지원.
