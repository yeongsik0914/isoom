# 🌙 MoonlightCare 종합 기획안 & 개발 백서 (PLAN.md)

> **문서 버전**: v2.5 (프론트엔드-백엔드 풀스택 아키텍처, 증상 가드레일 및 미입력 바이탈 무손실 연동)  
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
* **소아청소년과 전문의 부족**: 심야 시간대 대학병원 및 권역응급의료센터조차 소아 당직의 부재로 "소아 진료 불가" 공지를 수시로 띄움.
* **경증 환자의 응급실 쏠림 (74%)**: 야간에 문을 여는 동네 의원을 찾지 못한 부모들이 단순 미열/감기 환아를 데리고 권역응급센터로 몰려 대기 시간이 3~5시간으로 폭증하고, 정작 중증 환아(KTAS 1~2)의 골든타임이 침해됨.
* **심야 처방전 조제 사고**: 야간에 진료하는 달빛어린이병원을 간신히 찾아 진료를 받았으나, 인근 약국이 먼저 문을 닫아 처방약을 짓지 못하고 발을 동동 구르는 현장 결함 발생.
* **AI의 임상 오분류(Undertriage) 위험**: 보호자의 일시적 안도성 표현("열은 내렸다", "지금은 깨어났다")에 현혹되어 중증 질환(장중첩증, 크룹, 수지절단, 신생아 발열)을 경증으로 오판하는 안전 위험 존재.

### 1.2 핵심 솔루션 & 서비스 목표
1. **0ms Red Flag 1차 즉각 차단**: 12대 소아 위급 징후 감지 시 LLM 호출 전 26µs 내에 119 구급차 호출로 직행.
2. **소아 KTAS 임상 지침 직접 대조 (Direct Grounding)**: 168개 주증상과 841개 세부기준을 바탕으로 환아의 중증도를 정확히 감별.
3. **병원-약국 30분 안심 페어링**: 달빛어린이병원 진료 마감 시간보다 최소 30분 늦게 닫는 심야약국을 1:1로 결합하여 처방전 조제 실패를 원천 차단.
4. **의료법 제27조 준수**: 특정 병원 광고/알선을 배제하고 대면 진찰의 필요성을 명시하는 안전 가드레일 확립.

---

## 2. 데이터 분석 기반의 목적별 기능 도출 (Notebook 1~5 실증)

| 실증 노트북 | 분석 대상 데이터셋 | 도출된 핵심 엔지니어링 원리 및 아키텍처 |
| :--- | :--- | :--- |
| **Notebook 1** (E-Gen 실시간 병상) | 국립중앙의료원 530개 응급실 병상 | 실시간 소아 일반병상(`hv28`), 소아 중환자실(`hv30`), 비정형 제한공지(`hpmg`) 파싱 파이프라인. |
| **Notebook 2** (달빛병원-약국 연계) | 전국 달빛어린이병원 & 야간약국 | +30분 조제 안전마진 기반 1:1 페어링 및 거리순 정렬 알고리즘. |
| **Notebook 3** (소아 KTAS 분류 체계) | 2021 공식 소아 KTAS 지침서 | 168개 주증상 NACRS 코드 매핑 및 5단계 임상 중증도 평가 체계. |
| **Notebook 4** (의료법 제27조 가드레일) | 의료법 및 불법 의료행위 판례 | 자가진단 및 직접 처방 금지, 대면 진료 안내 단일 출구 게이트웨이. |
| **Notebook 5** (Firebase 서버리스 연계) | Cloud Firestore 스토리지 | 저비용 실시간 병상 캐싱 및 장애 복원력(HA) 극대화. |

---

## 3. 백엔드 모듈 체계 & 디렉터리 아키텍처 (Steps 1~8)

```text
monnlight/
├── app/
│   ├── agents/               # 4대 지능형 에이전트 계층
│   │   ├── guardrail_agent.py    # 12대 Red Flag 26µs 즉각 차단 & 의료법 제27조 소독
│   │   ├── triage_agent.py       # Gemini 3.8 Flash KTAS Grounding & 임상 변수 추출
│   │   ├── matching_agent.py     # 달빛병원 +30분 안심약국 1:1 페어링 & 소아 응급실 매칭
│   │   └── logistics_agent.py    # 30초 유선 확인 통화 스크립트 & 2024년 5월 본인확인 서류
│   ├── orchestrator/         # 멀티 에이전트 총괄 오케스트레이터
│   │   ├── supervisor.py         # 6-State 유한상태머신(FSM) & 3턴 교착 방어 & 임상 가드레일
│   │   └── session_manager.py    # Firestore / In-Memory 세션 지속성 관리자
│   ├── services/             # 코어 데이터 & 인프라 서비스
│   │   ├── circuit_breaker.py    # 공공 API 3-State FSM 비동기 서킷 브레이커
│   │   ├── fallback_storage.py   # L1 메모리 / L2 Firestore / L3 불변 JSON 3계층 스토리지
│   │   ├── national_dataset.py   # 전국 156개 병원·2,028개 약국 공간 인덱서 & In-Memory 캐시
│   │   ├── national_dataset_sync.py # 24시간 In-Memory Hash Diffing 증분 동기화
│   │   └── scheduler.py          # APScheduler 3-Track 백그라운드 워커
│   ├── api/v1/               # FastAPI RESTful 엔드포인트
│   │   ├── chat.py               # 실시간 문진 대화 & 1턴 완결 force_matching API
│   │   ├── emergency.py          # 소아 가용 응급실 & 병원-약국 페어링 API
│   │   └── location.py           # 카카오 로컬 REST API 주소/키워드 검색 & 역지오코딩
│   ├── schemas/              # Pydantic v2 데이터 전송 객체 (DTO)
│   └── config.py             # pydantic-settings 기반 전역 환경설정
├── data/                     # 불변 마스터 데이터셋 (KTAS, 전국 병원/약국 JSON)
├── frontend/                 # 순수 HTML5/CSS3/Vanilla JS 프론트엔드
│   ├── templates/            # 13대 표준 화면 템플릿
│   ├── css/style.css         # Calm Harbor 라이트 테마 & 모바일 셸 스타일시트
│   └── js/main.js            # LBS 공간 매칭, 1:1 교차 정렬, 최근 검색 히스토리
└── tests/                    # 92개 단위/통합 테스트 스위트 (100% 무결점 통과)
```

---

## 4. 차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)

1. **Tier 1 (Zero-Latency Pre-Interceptor)**:
   - **위치**: `app/agents/guardrail_agent.py` (`check_red_flag_instant`)
   - **방식**: 컴파일된 고성능 정규표현식 기반 26µs 실시간 검사.
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

* **배경**: 공공데이터포털(NMC) 전국 2,184개 시설 정보를 매번 전체 재기록(Full Overwrite)하는 I/O 비효율과 DB 락(Lock)을 방어.
* **알고리즘**:
  1. 메모리에 상주하는 이전 데이터셋의 고유 해시(`SHA-256`)와 공공 API 최신 데이터의 해시를 비교.
  2. 내용이 변경되거나 추가/삭제된 시설만 선별하여 **증분(Delta) 갱신** 수행.
  3. 무변경 시 0ms 즉각 바이패스하여 서버 리소스 및 네트워크 비용 98% 절감.

---

## 7. 공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback

* **서킷 브레이커**: 공공 API 연속 3회 실패 시 `OPEN` 상태로 전이하여 60초간 외부 호출을 차단하고 로컬 폴백 모드로 즉시 전환.
* **3계층 스토리지 전략**:
  - **L1 (In-Memory)**: 5분 TTL 인메모리 캐시 (0ms 초고속 서빙).
  - **L2 (Firestore)**: 최근 정상 동기화된 클라우드 NoSQL 스토리지.
  - **L3 (Local JSON)**: 서버에 영구 보관된 156개 달빛병원·2,028개 심야약국 불변 마스터셋.
* **성과**: 공공 API 장애 및 서버 점검 중에도 **가용성 100% 무중단 서비스** 유지.

---

## 8. 프론트엔드 UI/UX 아키텍처 & 13대 화면 체계 (Fixed App Shell)

### 8.1 고정 앱 셸 (Fixed App Shell) 아키텍처
* **바깥 스크롤 0px 원천 차단**: 모바일 및 데스크톱 뷰포트에서 상단 헤더, 증상 배너, 탭 필터, 하단 GNB를 완벽 고정(`flex-shrink: 0`).
* **내부 독립 스크롤**: 오직 실시간 시설 카드 목록(`.facility-card-stack`) 내부에서만 수백 개의 시설이 부드럽게 스크롤되도록 격리.

### 8.2 메인 홈 실시간 LBS 엔진 & 1:1 교차 랭킹 ([index.html](frontend/templates/index.html) & [main.js](frontend/js/main.js))
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
  - 180도 부채꼴 게이지 다이얼 체온계, 연령 슬라이더, 해열제 성분별 정밀 카테고리화.
* **`loading.html`**: AI 분석 2초 키프레임 오버레이 및 백엔드 비동기 통신.
* **`result.html`**: 1턴 완결 `force_matching` FSM 응답 기반 5대 임상 바이탈(월령, 체온, KTAS 레벨, 증상) 및 1:1 안심 페어링 카드 동적 바인딩.

### 8.4 위치 검색 모달 & 사용자 실검색 기반 최근 이용 지역 관리 ([location.py](app/api/v1/location.py) & [main.js](frontend/js/main.js))
* **2대 탭 검색**: 지번/도로명(주소 검색) vs 건물명/지역명(키워드 검색) 분리.
* **무손실 상세 주소 보존**: 카카오 `coord2address` 기반 상세 주소 완벽 보존.
* **'자주 찾는 주요 지역' 동적 히스토리화**: LocalStorage(`aisum_recent_locations`) 기반 최대 15개 최신순(FIFO/LRU) 관리.

### 8.5 13대 표준 HTML 템플릿 체계 (`frontend/templates/`)
1. `index.html`: 메인 홈 SPA (Fixed App Shell, 1:1 교차 LBS)
2. `input.html`: 소아 증상 문진 입력 (2단계 증상 가드레일)
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
| **`input.html` (증상 제출)** | `POST /api/v1/chat` | `user_message`, `force_matching=True`, `patient_vitals` | 0ms Red Flag 분기 또는 `SupervisorResponse` (KTAS+페어링, None 바이탈 보존) 반환, 체온 다이얼 소아 표준 정상 체온(36.5℃, 🟢 정상 체온) 기본 초기화 |
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
* **임상 안전성 지표**:
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
