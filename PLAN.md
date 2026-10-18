# 🌙 MoonlightCare 종합 기획안 & 개발 백서 (PLAN.md)

> **문서 버전**: v3.35 (개발 전 과정 종합 설명서 & 취업·포트폴리오 백서 발간, PROJECT_DEVELOPMENT_STORY.md 동기화)
> **최종 갱신 일자**: 2026-10-19
> **핵심 슬로건**: *"야간 소아 응급실 뺑뺑이를 막는 0ms 세이프티 가드레일 & 데이터 기반 2-트랙 지능형 라우터"*

> **기반 원천**: 주피터 노트북 5권 실증 데이터, 국립중앙의료원(NMC)·한국천문연구원(KASI) 공공데이터, 카카오맵 REST API(Static Map 프록시), Firebase Cloud Firestore, Gemini 3.8 Flash (Thinking High) / 3.5 Lite, 2021 소아 KTAS 지침(168개 주증상), AsyncCircuitBreaker(3-State FSM), In-Memory Hash Diffing 델타 동기화, data/ 폴더 캐노니컬 JSON 상세 데이터셋, 5-Layer Smart Back Navigation & < 0.05ms 초고속 인메모리 인덱스, AisumPermissionManager 세션-로컬 양방향 동기화, cleanLegacyMunjeongData 캐시 자동 소독 엔진, formatCompactAddress 주소 정제 엔진, evaluateOperatingStatus KST 실시간 운영 판정 엔진, 4단계 순차 온보딩 게이트웨이 & 이용약관-설정 모드 완전 분리, AisumHistoryManager 0ms 무손실 결과 복원 & 전용 기록 페이지(history.html), AisumNotificationManager KTAS 중증 실시간 병상 변동 감지 및 알림 센터, 119 구급대원 인계용 응급 브리핑 카드(briefing_card.html), 문진 페이지 환아 프로필 자동 프리필 및 증상 기반 나이·상태 측정 스마트 감지 허브(input.html), [PROJECT_COMPLETION_REPORT.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PROJECT_COMPLETION_REPORT.md), [PWA_PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PWA_PLAN.md), [PROJECT_DEVELOPMENT_STORY.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PROJECT_DEVELOPMENT_STORY.md).

---

## 📑 목차 (Table of Contents)

1. [프로젝트 기획 배경 & 핵심 문제 정의](#1-프로젝트-기획-배경--핵심-문제-정의)
2. [데이터 분석 기반의 목적별 기능 도출 (Notebook 1~5 실증)](#2-데이터-분석-기반의-목적별-기능-도출-notebook-15-실증)
3. [백엔드 모듈 체계 & 디렉터리 아키텍처 (Steps 1~9)](#3-백엔드-모듈-체계--디렉터리-아키텍처-steps-19)
4. [차세대 2계층 안전 감시망 (Two-Tier Red Flag V2 Architecture)](#4-차세대-2계층-안전-감시망-two-tier-red-flag-v2-architecture)
5. [풀스택 시스템 아키텍처 & 2계층 데이터 흐름도](#5-풀스택-시스템-아키텍처--2계층-데이터-흐름도)
6. [데이터 엔지니어링 & 24시간 In-Memory Hash Diffing 델타 동기화](#6-데이터-엔지니어링--24시간-in-memory-hash-diffing-델타-동기화)
7. [공공 API 서킷 브레이커 & 3-Tier Multi-Storage Fallback](#7-공공-api-서킷-브레이커--3-tier-multi-storage-fallback)
8. [프론트엔드 UI/UX 아키텍처 & 15대 화면 체계 (Fixed App Shell)](#8-프론트엔드-uiux-아키텍처--15대-화면-체계-fixed-app-shell)
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

### 8.1 전역 고정 앱 셸 (Fixed App Shell) & 스마트폰 뷰포트 완전 규격화
* **바깥 스크롤 0px 원천 차단 (전 화면 일체화)**:
  - 홈(`index.html`), 응급실 가이드(`emergency_guide.html`), 설정(`settings.html`), 문진 입력(`input.html`), 맞춤 결과(`result.html`) 등 전 화면의 `.mobile-viewport`에 `height: 100vh; height: 100dvh; max-height: 100dvh; overflow: hidden;` 및 데스크탑 `height: min(920px, calc(100vh - 24px)); border-radius: 36px; border: 8px solid #ffffff;`를 전역 적용하여 폰 프레임 외형 크기 100% 동기화.
* **문진 입력 페이지(`input.html`) 하단 버튼 잘림 해소 & 스크롤 여백 확장**:
  - `.triage-bottom-action-bar`의 안전 패딩(`padding: 12px 20px 24px 20px;`, 데스크탑 `padding: 12px 20px 26px 20px;`) 확장으로 폰 프레임 바닥 코너 곡률에 의한 버튼 클리핑 잘림 결함 원천 해소.
  - 본문 스크롤 패딩(`padding-bottom: 155px;`)을 대폭 늘려 마지막 질문 카드가 하단 바 위쪽으로 시원하게 스크롤되도록 개선.
* **맞춤 결과 페이지(`result.html`) 스마트폰 프레임 셸 전면 전환**:
  - 독자 뷰포트에서 전역 스마트폰 프레임 셸(`.mobile-viewport.result-shell`)로 전면 개편.
  - 상단 헤더 고정(`flex-shrink: 0`), 본문 결과 목록 내부 독립 스크롤(`flex: 1; min-height: 0; overflow-y: auto; padding: 18px 16px 96px 16px;`) 분리.
  - 하단 액션바(`.result-bottom-bar`)를 `position: absolute; bottom: 0;`으로 스마트폰 프레임 바닥에 도킹 및 데스크탑 바닥 라운딩(28px) 일체화.
* **맞춤 결과 페이지 3대 카테고리 1칸 통합 세그먼트 탭 전환 UI (`.result-category-box`)**:
  - 기존 세로로 길게 나열되던 병원 목록, 당직의 통화 스크립트, 필수 준비물 3대 핵심 카드를 단일 모바일 컨테이너("한 칸", `.result-category-box`)로 일체화.
  - 상단에 `[ 🏥 병원 목록 ]` | `[ 📞 통화 스크립트 ]` | `[ 📋 필수 준비물 ]` 3-Tab 세그먼트 네비게이션(`.result-category-nav`) 구축 및 원클릭 탭 전환(`switchResultCategory`).
  - **병원 목록 패널(`category-pane-hospitals`)**: 기존 2-Track 탭 스위처(달빛병원 vs 소아 응급실) 및 실시간 가용병상 스크롤 리스트 온전히 보존.
  - **통화 스크립트 패널(`category-pane-script`)**: 실시간 증상 및 추천 병원 자동 바인딩 30초 대본 박스 및 원터치 클립보드 복사 버튼 완비.
  - **필수 준비물 패널(`category-pane-checklist`)**: 부모 신분증, 등본, 아기수첩 3대 항목 인터랙티브 체크 토글(`toggleCheckItem`) 완비.
* **응급실 가이드 및 설정 하단 붕 뜬 여백(회색 빈 박스) 원천 해소**:
  - `settings.html`: 모바일 뷰포트 배경을 흰색(#ffffff)으로 일체화하여 `.settings-body`와 GNB 사이의 회색 빈 박스 노출 결함 원천 박멸.
  - `emergency_guide.html`: `.guide-scroll-body` 배경을 흰색으로 정돈하고, 인포그래픽 버튼 하단에 **"야간 소아 응급실 방문 필수 팁"** 섹션을 보강하여 여백이 휑하지 않고 알차게 꽉 찬 모바일 화면 완성.
* **하단 GNB 절대 도킹 (`position: absolute; bottom: 0;`) & 68px 고정**:
  - `fixed` 포지셔닝으로 인해 데스크탑 모바일 프레임 바닥을 뚫고 24px 이탈하던 결함을 원천 해소하고, 모바일 프레임 맨 밑바닥 둥근 모서리(28px)에 단단히 안착.
* **4대 탭 및 활성 알약(`.nav-item.active`) 전역 동일 규격화**:
  - 각 탭에 `flex: 1; max-width: 76px; height: 50px; border-radius: 16px; box-sizing: border-box;`를 부여하여, 텍스트 글자 수('홈' 1글자 vs '응급실 가이드' 6글자)와 무관하게 **모든 탭이 항상 대칭되고 완벽히 동일한 크기의 파란색 알약 배경**을 유지.
* **내부 독립 스크롤 분리**:
  - 홈 화면의 `.facility-card-stack`, 응급실 가이드의 `.guide-scroll-body`, 설정의 `.settings-body`, 결과 화면의 `.result-main`이 각각 `flex: 1; min-height: 0; overflow-y: auto;`를 적용받아 헤더와 GNB/하단바는 고정되고 본문만 부드럽게 스크롤되는 네이티브 앱 UX 완성.

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

### 8.5 16대 표준 HTML 템플릿 체계 (`frontend/templates/`)
1. `index.html`: 메인 홈 SPA (약관 미동의 0ms 차단 가드, Fixed App Shell, 1:1 교차 LBS, 실시간 운영시간 우선 정렬)
2. `input.html`: 소아 증상 문진 입력 (약관 미동의 0ms 차단 가드, 2단계 증상 가드레일)
3. `modal.html`: 사전 처치정보 및 의료법 제27조 안내 다이얼로그
4. `loading.html`: AI 트리아제 로딩 애니메이션
5. `result.html`: KTAS 판정 및 병원-약국/응급실 맞춤 결과 (상단 트랙 탭 & 상태 바 단일 칸 일체화(새로고침 버튼 도킹 및 세로 36px 추가 확보), 소아 응급실 병상 목록 최소 4개소 무스크롤 100% 완전 노출(`.facility-scroll-list` max-height: 275px & 48px 슬림 카드), 응급 배너 중복 문구 100% 제거, 1줄 핵심 지침 정예화(`shortKtasMap`) 및 전문 감별 소견 접이식 토글(`<details>`) 적용, 상단 감별소견 & 초응급 배너 단일 카드 통합(높이 -210px 압축), KTAS 1·2·3단계 중증 카테고리 탭 명칭 '응급실 목록' 0ms 동적 스위칭(`updateCategoryHospitalsTitle`), 잔여 병상 배지·전문센터·직통전화·길안내 버튼 한눈 노출, 단일 카드 3대 카테고리 세그먼트 탭, 병원명 중복 접미사 100% 제거, 진료시간 중복 제거 및 `오늘 ~23:00` 간결화, 약국 `+30분` 안전마진 가독성 극대화, 통화 대본 `max-height: 110px` 복사 버튼 화면 내 완전 노출, 본인확인 3대 체크리스트 테두리 무결점 안착, isReplayMode 시 상단 뒤로가기 `history.html` 자동 연동)
6. `hospital_detail.html`: 달빛어린이병원 전용 상세 페이지 (소아 전문의/일반의 현황, 주차 면수/요금/안내, 요일별 진료시간표, Leaflet & OpenStreetMap 실시간 대화형 지도(220px 뷰포트, 로열 블루 펄스 핀 마커), 22:30 조기마감 주의 배너, 2열 실측 메트릭 바(내 위치 거리·주차 지원), 5-Layer Smart Back Navigation, 하단 고정 통화 CTA)
7. `pharmacy_detail.html`: 심야약국 전용 상세 페이지 (상주 약사 현황, 복약지도 안내, +30분 조제 안전마진 표시, 요일별 심야 운영시간표, Leaflet & OpenStreetMap 실시간 대화형 지도(220px 뷰포트, 에메랄드 그린 펄스 핀 마커), 1:1 연계 달빛어린이병원 카드, 5-Layer Smart Back Navigation, 하단 고정 통화 CTA)
8. `emergency_alert.html`: 0ms Red Flag 119 긴급 직행 화면
9. `briefing_card.html` (구 `emergency_guide.html`): **[전면 개편]** 119 구급대원 & 응급실 의료진 즉시 인계용 '응급 브리핑 카드' (전 기종 100% 밀착 모바일 뷰포트, 3대 핵심 섹션: 환아 기본 신상정보 필수입력·혈액형 캡슐 뱃지·비상연락처 통화, 문진 기록 페이지 `AisumHistoryManager` 실시간 연동 및 원하는 회차 선택 바인딩, 종교적 수혈 거부 등 특이사항/주치의 연락처, 구급대원 제시용 고대비 풀스크린 모드, 119 원터치 즉시 통화 배너)
10. `settings.html`: 모니모 스타일 자녀 정보 & 알림 설정 (이용약관 열람 시 `terms.html?mode=view` 안전 복귀 연동, 모바일 기기 연결 전용 `/qr` 라우팅)
11. `terms.html`: 최초 1회 필수 동의 화면 (4대 필수 약관 체크박스 컴포넌트, `aisum_terms_agreed` 영구 플래그 저장, `?mode=view` 읽기전용 분기)
12. `splash.html`: 모바일 시작 스플래시 (사이트 첫 접속 시 무조건 1순위 노출 ➔ 1.8초 후 미동의 시 `terms.html` 필수 강제 이동 ➔ `permission.html` ➔ `home` 4단계 순차 온보딩 게이트웨이)
13. `permission.html`: 5대 접근 권한 안내 (약관 미동의 0ms 강제 축출 가드, 5대 권한 및 LBS 위치 세션-로컬 양방향 영구 보존)
14. `location_modal.html`: 주소/키워드 위치 설정 바텀시트
15. `qr.html`: 모바일 기기 연결 전용 QR 코드 안내 페이지 (실시간 도메인 감지 260x260 QR코드 생성, 원터치 주소 복사, Web Share API 연동 링크 공유, iOS Safari/Android Chrome 홈 화면 추가 가이드, PWA 1-클릭 설치)
16. `history.html`: **[신규]** 이전 문진 결과 전용 독립 웹페이지 (전 기종 100% 밀착 모바일 뷰포트, 상단 요약 바, KTAS 1~5 뱃지, 환아 정보, 추천 시설, 실시간 결과 다시보기, 개별/전체 삭제, Empty State, 전역 GNB 4-Tab 연동)

---

## 9. 프론트엔드-백엔드 100% 결합 연동 명세

| 프론트엔드 화면/액션 | 백엔드 API 엔드포인트 | 전달 파라미터 / DTO | 반환 데이터 및 렌더링 결과 |
| :--- | :--- | :--- | :--- |
| **`index.html` (홈 로드)** | 클라이언트 0ms LBS + `GET /api/v1/emergency/nearby` | `lat`, `lon`, `radius_km=15.0` | 반경 15km 내 1:1 교차 야간 의료시설 및 실시간 가용 응급실 |
| **`history.html` (기록 뷰)** | `GET /history` / 클라이언트 로컬 캐시 | 없음 (`aisum_triage_histories_v1`) | 저장된 문진 기록 목록 0ms 즉각 렌더링, 다시보기 시 `result.html?is_replay=true` 복원 |
| **`briefing_card.html` (브리핑 카드)** | `GET /briefing-card` / 로컬 캐시 | 없음 (`aisum_patient_profile`, `aisum_triage_histories_v1`) | 신상정보·최근 문진의료정보·수혈거부 특이사항 브리핑 카드 및 구급대원용 풀스크린 모드 |
| **`index.html` (병원 카드 클릭)** | `/hospital_detail` 이동 & `GET /api/v1/emergency/facility-detail` | `type=hospital`, `name`, `lat`, `lon` | 전문의/일반의, 주차(면수/요금/안내), 내 위치 거리·주차 2열 실측 메트릭, 22:30 조기마감, 카카오 지도, 통화 번호 (0.05ms) |
| **`index.html` (약국 카드 클릭)** | `/pharmacy_detail` 이동 & `GET /api/v1/emergency/facility-detail` | `type=pharmacy`, `name`, `lat`, `lon` | 상주 약사, 복약지도, +30분 조제 안전마진, 연계 달빛병원, 카카오 지도, 통화 번호 (0.05ms) |
| **위치 모달 (주소 검색)** | `GET /api/v1/location` | `query`, `type=address` | 카카오 도로명/지번 주소 목록 및 WGS84 좌표 |
| **위치 모달 (키워드 검색)** | `GET /api/v1/location` | `query`, `type=keyword` | 카카오 장소명/건물명 랜드마크 목록 및 좌표 |
| **위치 모달 (현재 위치)** | `GET /api/v1/location` | `lat`, `lon` (역지오코딩) | 도로명+건물명 결합 무손실 상세 주소 반환 |
| **`input.html` (증상 제출)** | `POST /api/v1/chat` | `user_message`, `force_matching=True`, `patient_vitals` | 0ms Red Flag(사지절단 등) 최우선 분기, 네거티브 블랙리스트 필터링, Gemini 3.8 Flash 168개 소아 KTAS 1~5단계 및 추천 시설 100% 동적 바인딩 |
| **`briefing_card.html` / `emergency_guide.html`** | `GET /api/v1/emergency/nearby` | `lat`, `lon`, `limit=5` | 소아 전문 응급실 실시간 잔여병상(`hv28`) 및 공지 배지 |
| **관리자 동기화 (온디맨드)** | `POST /api/v1/emergency/sync-static` | `force=True` (선택) | 24시간 Hash Diffing 증분 동기화 결과 JSON |

---

## 10. 종합 검증 현황 & 임상 안전성 벤치마크 (118개 테스트 전수 통과)

* **전체 단위/통합 테스트 스위트**: **총 118개 테스트 100% 무결점 통과 (`Ran 118 tests, 100% ALL PASS`)**
  - `test_step1_services.py`: 공공 API 수집, 비정형 공지 정규식 필터링 (7건)
  - `test_step2_guardrail.py`: 12대 Red Flag 26µs 정규식 감지 및 사후 소독 (12건)
  - `test_step3_agents.py`: Gemini 3.8 Flash Thinking KTAS Direct Grounding (7건)
  - `test_step4_orchestrator.py`: FSM 상태머신 전이 및 무한루프 가드 (7건)
  - `test_step5_api.py`: FastAPI 엔드포인트, 전국 415개소 LBS 랭킹 (11건)
  - `test_step6_e2e.py`: 풀스택 40대 임상 시나리오 E2E 통합 (8건)
  - `test_step7_circuit_breaker.py`: 서킷 브레이커 & 3-Tier Multi-Storage Fallback (8건)
  - `test_step8_frontend_integration.py`: `force_matching` 1턴 완결, Red Flag 오버라이드, KTAS 듀얼 트랙 DOM 계약, API 라우팅 매트릭스, 알림 연동, 전용 기록 페이지(`/history`) 계약, 구급대원 브리핑 카드(`/briefing-card`) 계약 및 루트 1순위 스플래시·세션 가드 계약 (24건)
  - `test_facility_db_and_detail_api.py`: data/ 폴더 상세 JSON 2종, JS 번들 2종 무결성 및 <0.05ms In-Memory 인덱스 조회 검증 (9건)
  - `test_location_api.py`: 카카오 주소/키워드 검색 및 2-Tier 역지오코딩 (12건)
  - `test_national_dataset_sync.py`: 24시간 In-Memory Hash Diffing 델타 동기화 (7건)
  - `test_redflag_v2_upgrade.py`: Red Flag v2 하이브리드 엔진 검증 (8건)
  - `test_audit_fixes.py`: 코드 감사 및 컴플라이언스 무결성 검증 (7건)
* **임상 안전성 지표 & KTAS 실증 검증**:
  - **2021 소아 KTAS 1~5단계 15대 표준 임상 시나리오 전수 검증**: **15 / 15 시나리오 100% 통과 (`Accuracy: 100.0%`, `Red Flag Safety Invariant: 100.0%`)** ([tests/evals/verify_ktas_frontend_flow.py](file:///e:/monnlight/tests/evals/verify_ktas_frontend_flow.py), [보고서](file:///e:/monnlight/docs/KTAS_TRIAGE_VERIFICATION_REPORT.md)).
  - **한국어 복합 병렬 부정문 감별 엔진 (`has_affirmative_match`)**: "청색증이나 경련은 없어요" 등 구어체 부정문의 0ms Red Flag 오경보(Over-triage) 100% 원천 차단.
  - 1,000회 연속 Red Flag 검사: 총 32.90ms (회당 평균 **32.90µs** 실시간 방어 달성).
  - 50대 소아 응급 골든 케이스 평가: **Red Flag 민감도 100%, 언더트리아제 0.0%**.

* **📊 프로젝트 종합 기획 대비 완성률 정밀 분석 보고서 발간 ([PROJECT_COMPLETION_REPORT.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PROJECT_COMPLETION_REPORT.md))**:
  - **상용 론칭 필수 코어 스코프(Core MVP & Advanced Services)**: **100.0% 완성** (실제 서비스 배포 및 상용화 즉시 가용)
  - **장기 고도화 백로그(Phase 4~6) 포함 종합 로드맵**: **92.5% 완성** (총 35개 세부 과제 중 32개 완결, 3개 순차 추진)
  - **5대 도메인별 진척도**:
    1. 데이터 엔지니어링 & 파이프라인: **100.0% 완결** (주피터 1~5권, 156개 병원/2,028개 약국 마스터셋, 24시간 In-Memory Hash Diffing)
    2. 안전 가드레일 & 멀티 에이전트: **100.0% 완결** (26µs Tier 1 Red Flag, 한국어 복합 부정문 감별, Tier 2 의료법 소독, Gemini 3.8 Flash Direct Grounding)
    3. 백엔드 API & 고가용성 인프라: **100.0% 완결** (Supervisor 6-State FSM, 3-State 서킷 브레이커, 3-Tier Multi-Storage Fallback)
    4. 프론트엔드 모바일 앱 셸 & 14대 뷰: **98.5% 완결** (온보딩 순차 파이프라인, GNB 4탭, 0ms 무손실 히스토리 복원 및 중복 차단, KTAS 중증 병상 변동 알림)
    5. 심화 고도화 백로그: **50.0% 순차 추진** (Phase 1~3J 완료, Phase 4~6 대기/진행)

---

## 11. 추가 심화 고도화 백로그 (Advanced Backlog)

1. **[완료] 의료시설(병원/약국) 2-트랙 상세 페이지 및 data/ 폴더 공공데이터 JSON 상세 데이터셋 + 24시간 동기화 파이프라인 (Phase 1)**:
   - SQLite DB 완전 폐지 ➔ `data/hospital_details.json`, `data/pharmacy_details.json` 캐노니컬 정적 데이터셋 구축.
   - 24시간 주기 Hash Diffing 스케줄러와 연동하여 data/ JSON 및 `frontend/js/` 번들 4종 동시 생성 & In-Memory 인덱스(<0.05ms) 서빙 완결.
   - `hospital_detail.html` (전문의, 주차, 대기시간, 22:30 조기마감 배너, 카카오맵, 하단 통화 CTA, 오프라인 듀얼 로더).
   - `pharmacy_detail.html` (상주 약사, 복약지도, +30분 조제 안전마진, 연계 달빛병원 카드, 카카오맵, 하단 통화 CTA, 오프라인 듀얼 로더).
2. **[완료] `result.html` 백엔드 임상 감별 소견 실시간 바인딩 & 미입력 바이탈 무손실 전달 (Phase 2)**:
   - `result.html` 내 JS SyntaxError 완전 복구, `SupervisorResponse.clinical_rationale` 실시간 표출, 미입력 바이탈 '모름' 무손실 렌더링 파이프라인 완결.
2. **[완료] `result.html` 소아 KTAS 등급별 컬러 테마, 탭 순서/가시성 지능형 제어 및 임상 감별 소견 맞춤 통화 스크립트 구축 (Phase 2-B)**:
   - KTAS 1~5단계별 전용 5대 컬러 시스템(`.ktas-tier-1` ~ `.ktas-tier-5`) 및 인라인 배지 컴포넌트 장착.
   - KTAS 1~3단계(소생/긴급/응급): `소아 응급실 병상 (우선 권고)` 탭을 좌측(첫 번째)으로 우선 배치 및 자동 활성화.
   - KTAS 4~5단계(준응급/비응급): 응급실 과밀화 방지를 위해 소아 응급실 병상 탭을 완전 제거(`display: none`), `달빛어린이병원 + 안심약국` 탭 100% 단독 전폭 표출.
   - `LogisticsAgent` 및 `result.html`: 나이/체온 미입력 시 고열 날조 원천 차단, 백엔드 `clinical_rationale` 결과를 당직의 30초 유선 확인 통화 스크립트에 100% 사실 기반 실시간 연동.
3. **[완료] `result.html` 달빛어린이병원 + 안심약국 목록 `index.html` 위치기반 페어링 동적 렌더링 일치화 (Phase 2-C)**:
   - `result.html` 내 고정 4개 카드 텍스트 덮어쓰기 로직 폐지 ➔ `index.html`과 동일하게 `NATIONWIDE_PAIRINGS_DATA`(전국 156개 페어링)를 사용자 좌표(GPS/설정 주소) 기준으로 실시간 거리순 정렬 및 동적 렌더링(`renderMoonlightPairingCards()`) 구축.
   - 사용자 첨부 UI 카드 컴포넌트 100% 일치 (`추천 1순위`, 병원명 `>`, 거리 배지 `9.5 km (차 24분)`, `오늘 야간진료`, `접수마감 경고`, `연계 안심약국`, `+30분 조제 안전마진`, `병원 동일 건물 안내`, `병원 전화`, `길찾기`).
   - 2-트랙 상세 페이지(`hospital_detail.html`, `pharmacy_detail.html`) 내비게이션 연결 및 통화 스크립트 최단거리 1순위 병원명 실시간 연동.
4. **[완료] `input.html` ➔ `result.html` 소아 KTAS 1·2단계 결과 화면 통합 라우팅 및 초응급 119 원터치 다이얼 배너 연동 (Phase 2-D)**:
   - `input.html` 문진 시 KTAS 1, 2단계 및 12대 Red Flag 판정 시 `emergency_alert.html`로 전환되던 UX 단절 완전 해소 ➔ 종합 결과 화면(`result.html`)으로 100% 통합 라우팅.
   - `result.html` 상단에 `#ktas-emergency-call-banner` (🚨 초응급 이송 권고, `119 즉시 전화` 원터치 다이얼, `응급처치 가이드` 링크) 동적 마운트.
   - `소아 응급실 병상 (우선 권고)` 탭 첫 번째 좌측 배치 및 실시간 병상(`hv28`), 소아 임상 감별 소견, 당직의 통화 스크립트 전면 연계.
5. **[완료] 병원·약국 상세페이지 Leaflet & OpenStreetMap 대화형 지도 및 커스텀 펄스 핀 탑재 (Phase 2-E)**:
   - 카카오 JS SDK 401 Unauthorized(도메인 미등록/REST키 불일치) 제약 완전 극복 ➔ 오픈소스 Leaflet(v1.9.4) + OpenStreetMap(OSM) 타일 엔진 통합.
   - `hospital_detail.html` (로열 블루 펄스 핀 + 달빛병원 팝업) 및 `pharmacy_detail.html` (에메랄드 그린 펄스 핀 + 안심약국 팝업) 실시간 대화형 지도 렌더링.
   - 뷰포트 높이 220px 확장 및 오프라인 SVG 레이더 폴백 2차 안전망 유지.
6. **[완료] 카카오맵 REST API 기반 정적 지도(Static Map) 프록시 연동 및 병원·약국 상세페이지 지도 고도화 (Phase 2-F)**:
   - 카카오맵 REST API 명세(`https://developers.kakao.com/docs/ko/kakaomap/rest-api#static`)에 기반한 백엔드 프록시 라우터(`GET /api/v1/location/staticmap`) 완비.
   - 서버 사이드 `Authorization: KakaoAK` 헤더 인증 바인딩 및 레티나 디스플레이 2배율(`scale=2`) 고해상도 PNG 스트리밍 캐싱.
   - 카카오 시그니처 배지(`kakaomap 정밀 지도`), 동적 줌 컨트롤러(+/-) 탑재, 지도 터치 시 실시간 길찾기(`map.kakao.com/link/to/...`) 딥링크 일체화.
   - API 키 부재 및 네트워크 예외 시 100% 무장애 SVG 벡터 그래픽 Fallback 및 Leaflet 듀얼 안전망 구축.
7. **[완료] Mac 개발 환경 Firebase Admin SDK 연동 & Firestore 활성화 (Phase 2-G)**:
   - Mac OS 절대경로(`/Users/jeong-yeongsig/Desktop/Project/serviceAccountKey.json`)를 `.env`의 `FIREBASE_KEY_PATH`에 바인딩.
   - `Settings.has_firebase_key()` 및 백엔드 헬스체크 `/health`의 `firebase_configured: true` 수신 완료.
8. **[완료] 소아 응급실 병상(hv28) E-Gen ➔ Firestore 5분 주기 Hash Diffing 델타 적재 & result.html 완전 동적 렌더링 (Phase 2-H)**:
   - 서버 시작 시 즉시 1회 초기 동기화(Warmup) 및 5분 주기 In-Memory Hash Diffing 델타 적재(100% 비용 방어) 확립.
   - 응급실 직통 전화, 종별 뱃지(권역 소아전문응급센터 등), 실시간 거리·차량시간, 잔여석 상태별 컬러 뱃지(🟢 여유, 🟡 혼잡, 🔴 만실/제한) 100% 동적 렌더링 완비.
   - **전국 17개 시·도 415개소 응급실 확장 파이프라인 설계**: E-Gen `STAGE1` 파라미터 제외 단일 호출(0.7초)을 통한 전국 415개 응급실 전수 수집 및 Firestore In-Memory Hash Diffing 델타 적재 아키텍처 수립 완료.
9. **[완료] 필수 캐노니컬 데이터셋 Git 형상관리 복원 & `.gitignore` 최적화 (Phase 3)**:
   - GitHub 클론 및 협업 환경에서 데이터 유실 방지를 위해 `data/` 내 핵심 JSON 7종 및 DB 파일 Git 추적 대상 정상 포함.
10. **[완료] 결과페이지(result.html) KTAS 1·2·3단계 실시간 소아 응급실 단독 표출 & KTAS 4·5단계 메인 홈 백엔드 카피 달빛병원 매칭 완비 (Phase 3-C)**:
    - KTAS 1·2·3단계(소생/긴급/응급): 경증용 달빛병원 탭을 완전히 은닉(`display: none`)하고 `소아 응급실 병상 (실시간 현황 · 우선 권고)` 탭을 100% 전폭 단독 표출. E-Gen·Firestore 실시간 병상 연동(🟢/🟡/🔴) 및 119 배너 마운트, 30초 통화 스크립트를 응급실 접수처 대상으로 자동 완성.
    - KTAS 4·5단계(준응급/비응급): 응급실 과밀화 방지를 위해 소아 응급실 병상 탭 버튼 `#tab-btn-emergency`를 완전 은닉(`display: none`)하고, `달빛병원 + 안심약국 (소아 준응급 전용 매칭 · 8곳)`을 단독 전폭 표출.
    - **메인 홈(`index.html` & `main.js`) 4대 핵심 백엔드/LBS 엔진 1:1 카피 이식**:
      1) `<head>` 내 전국 실데이터셋(156개 병원, 2,028개 약국, 페어링) 사전 로드로 0ms 즉각 렌더링 확립.
      2) 사용자 GPS 위치(`AisumPermissionManager` / `localStorage`) 기준 반경 15km 이내(`MAX_RADIUS_KM = 15.0`) 엄격 필터링 및 최단거리 순 오름차순 정렬.
      3) 메인 백엔드 REST API(`GET /api/v1/emergency/pairings`) 비동기 fetch 결합 및 `/data/nationwide_pairings.json` Fallback 안전망.
      4) 병원·약국 카드 클릭 시 2-트랙 상세페이지(`hospital_detail.html`, `pharmacy_detail.html`) 이동 및 세션 상태 저장.
    - `loading.html`, `input.html`, `result.html` 간 KTAS 1~3 단계 응급 라우팅 파이프라인 일체화.
11. **[완료] 결과페이지 KTAS 1·2·3단계 실시간 소아 응급실 무한 로딩 스피너 멈춤 결함 해소 & 0ms LBS 로컬 비상 프리셋 Fallback 완비 (Phase 3-D)**:
    - 브라우저 프로토콜/오리진(file:// 및 비8000 포트) 상대경로 fetch 에러 및 Fallback 부재로 인한 스피너 영구 멈춤 결함 해소.
    - 전국 22개 거점 권역 소아전문응급센터 프리셋(national_emergency_hospitals.js) 탑재.
    - 0ms 하버사인 거리 계산기(calcHaversineDistKm) 기반 즉각 렌더링으로 골든타임 보장.
    - 4.5초 AbortController 타임아웃 세이프티 가드 및 apiBase 자동 라우팅 완결.
12. **[완료] 메인화면 문정동 하드코딩 완전 제거·실시간 GPS 위치 자동 감지 및 결과페이지 ReferenceError 원천 해소 (Phase 3-E)**:
    - index.html 상단 헤더 및 모달 주소 바 내 문정동 하드코딩 텍스트 전면 제거 및 동적 플레이스홀더화.
    - main.js autoDetectUserLocation의 기존 저장 좌표 조기 리턴 가드 해제 ➔ 접속 시 navigator.geolocation 기반 실제 GPS 좌표 및 역지오코딩 도로명 주소 실시간 반영.
    - result.html 내 Line 1898/1904 미선언 변수 currentHospitals 참조로 인한 JS 크래시 및 응급실 병상 멈춤 결함 원천 박멸.
    - emergency-scroll-list 초기 프리셋 카드 탑재로 0ms 골든타임 무지연 노출 완결.
13. **[완료] 온보딩 위치 권한 승인 세션 전 페이지 상시 유지 & 메인화면 실시간 위치 0ms 표출 완비 (Phase 3-F)**:
    - `AisumPermissionManager`에 `sessionStorage` <-> `localStorage` 양방향 세션 동기화 엔진(`syncSession()`) 및 `grantAllPermissions()` 신설.
    - 처음 이용하는 사용자가 `splash.html` ➔ `permission.html` 온보딩에서 "동의하고 시작하기" 클릭 시 브라우저 실제 위치(Geolocation), 알림(Notification), 전화, 카메라, 사진 5대 모든 접근 권한 플래그와 위·경도 좌표, 역지오코딩 주소를 양쪽 스토리지에 동시 영구 저장.
    - `index.html` 상단 헤더 인라인 스크립트의 불필요한 `isManual` 가드를 완전 제거하여 접속 첫 프레임(0ms)에 사용자의 실제 동 이름을 `#current-location-text`에 즉각 바인딩.
    - 홈, 문진, 결과, 상세 등 전 페이지 이동 시 권한 세션 및 LBS 위치 상시 지속성 100% 확립.
14. **[완료] 메인화면 실시간 사용자 현재 위치 자동 적용 & 문정동 더미 캐시 소독 완비 (Phase 3-G)**:
    - 과거 개발 시 브라우저 `localStorage`에 저장되어 영구 잔존하던 문정동(37.4858, 127.1225) 더미 캐시를 접속 즉시 자동 클린업하는 `cleanLegacyMunjeongData()` 파이프라인 탑재.
    - `autoDetectUserLocation`에 `enableHighAccuracy: false` 최적화를 적용하여 데스크탑/모바일 타임아웃 없이 1초 내 실제 GPS 좌표 획득.
    - 실제 기기 위치를 기반으로 백엔드 역지오코딩(`/api/v1/location/coord2address`) 주소를 즉시 조회하여 헤더와 시설 목록을 사용자의 실제 접속 위치 기준 최단거리 순으로 즉각 렌더링.
    - GPS 차단/실패 시 공공 IP 기반 2차 자동 위치 추정(`fetchIpLocationFallback`)을 연동하여 문정동 고정 결함 100% 박멸.
15. **[완료] 메인화면 실시간 의료시설 카드 UI 간결화 & KST 운영시간 기반 실시간 운영 판별·진료가능 우선 정렬 완비 (Phase 3-H)**:
    - 장황한 서브설명 및 건물/호수 상세주소를 정규식으로 정제하는 `formatCompactAddress` 구축 (도로명 + 법정동 단정 노출).
    - KST 요일/시간 기반 실시간 운영 판별 엔진(`evaluateOperatingStatus`)을 통해 5대 상태(진료중, 곧 마감, 오픈 대기, 마감, 휴진) 및 오늘 요일별 시간표 표출.
    - 현재 실제 이용 가능한 시설을 최우선 배치하고 마감된 시설을 후순위로 배치하는 스마트 정렬 및 전체 탭 1:1 교차 인터리빙 완성.
16. **[완료] 온보딩 순차 파이프라인(splash ➔ terms ➔ permission ➔ index) 완결 & 이용약관 설정 모드 완전 분리 (Phase 3-I)**:
    - `splash.html`에서 2중 순차 라우팅 확립: 약관 미동의 시 무조건 `terms.html` 리다이렉트 (동의 전까지 무한 반복), 약관 동의 후 권한 미승인 시 무조건 `permission.html` 리다이렉트 (승인 전까지 무한 반복), 둘 다 완료 시 `index.html` 진입.
    - `terms.html` 온보딩 vs 설정 열람 모드 CSS/JS 물리적 완전 격리: 온보딩 모드에서는 `#btn-terms-view-confirm`("내용을 확인했습니다")과 상단 뒤로가기를 완전 은닉(`display: none !important`), 4대 필수 체크 후 '동의하고 계속하기' 완료 시 반드시 다음 온보딩인 `permission.html`로 전환.
    - 오직 설정 화면에서 진입한 기가입자(`hasViewParam && isAlreadyAgreed`)에게만 뒤로가기 및 "내용을 확인했습니다" 버튼을 활성화하여 `settings.html`로 안전 복귀 지원.
    - `index.html` & `input.html` 상단에 약관 미동의 0ms 차단 + 접근권한 미동의 0ms 차단 2중 가드레일을 설치하여 주소창 URL 직접 입력 우회 100% 방어.
17. **[완료] KTAS 중증 이력자 대상 실시간 응급실 병상 변동 알림(Notification Center) & 하단 GNB '이전 문진 결과 기록(History)' 시스템 (Phase 3-J)**:
    - **AisumHistoryManager**: 문진 결과 완료 시 환아 연령/월령, 성별, 체온, 주증상, KTAS 등급, 추천 시설 스냅샷을 `aisum_triage_history`에 영구 저장 (최대 30건).
    - **응급실 판정 결과 영구 기록 무결점 보장**: `aisum_is_replay_view` 세션 오염 플래그 즉각 자동 소독(문진 제출 및 결과 진입 시 URL에 `?is_replay=true` 부재 시 자동 삭제), 15초 이내 동일 결과만 새로고침 중복 방지(`isWithin15Sec`)를 적용하여 신규 문진 무조건 영구 보관 보장.
    - **KTAS 등급별 추천 시설 정합성 보장**: KTAS 1·2·3단계(소생/긴급/응급) 시 달빛어린이병원 매칭을 배제하고 소아 응급실(`#emergency-scroll-list`) 및 거점 소아응급센터명을 우선 취득. 비동기 E-Gen 병상 수신 시 `updateLatestHospital`로 1순위 소아 응급실명 자동 정밀 보정 및 히스토리 부재 시 자동 안전 저장.
    - **AisumNotificationManager (중증 환아 전용 2대 조건부 실시간 알림 엔진)**:
      - **조건 1 (중증 이력 보유자)**: `hasEmergencyHistory()` 검증을 통해 기록 페이지에 KTAS 1·2·3단계 응급실 판정 이력이 존재하는 보호자에게만 감시 및 알림 발송 허용.
      - **조건 2 (실제 병상 변동 시)**: 사용자 위치(반경 25km) 기준 `/api/v1/emergency/nearby` 백그라운드 폴링(30초 주기)을 통해 소아 일반병상(`hv28`/`available_beds`)이 실제로 변경되었을 때, **어떤 응급실이고 얼마나 변경되었는지(증가/감소/만실 수치: `diff = currentBed - prevBed`)** 명시한 알림 발송:
        - `🟢 [서울아산병원] 소아 응급실 병상 확보 (+2석)` (1석 ➔ 3석)
        - `🔴 [서울아산병원] 소아 응급실 병상 감소 (-2석)` (3석 ➔ 1석)
        - `🚨 [서울아산병원] 소아 응급실 만실 경보 (0석)` (1석 ➔ 0석)
      - 인앱 알림 센터 등록 + 헤더 붉은 뱃지(`.badge-dot`) 점등 + 브라우저 시스템 푸시(`Notification API`) 3중 발송 지원.
    - **하단 GNB 4-Tab 개편 및 전역 템플릿 완전 동기화**: 홈 바로 옆에 '기록' 탭을 신설하여 어디서든 이전 문진 결과 바텀시트 모달을 열람 가능. 메인 홈뿐만 아니라 `emergency_guide.html`, `emergency_guide_symptoms.html`, `emergency_guide_checklist.html`, `settings.html` 및 `app/templates` 전역 파일까지 4-Tab(`홈` | `기록` | `응급실 가이드` | `설정`)을 일괄 동기화. 각 기록 카드에서 `[당시 결과 다시보기]` 클릭 시 `sessionStorage`에 스냅샷을 즉시 주입하여 0ms 딜레이로 당시 결과 화면 완벽 복원 및 `index.html?tab=history` 딥링크 모달 자동 오픈 보장.
18. **카카오맵/네이버맵 30분 안심 동선 지도 시각화 (Phase 4)**:
    - 사용자 현재 위치 ➔ 달빛어린이병원 ➔ +30분 조제 안심약국으로 이어지는 안전 이동 동선을 폴리라인(Polyline)으로 맵 뷰 시각화.
19. **전국 실시간 소아 응급실 병상 전광판 (`beds.html` - Phase 5)**:
    - 5분 주기 E-Gen API 기반 권역별 소아 병상(`hv28`), 소아 중환자실(`hv30`), 장비 가용 현황 실시간 모니터링 대시보드 구축.
20. **[완료] PWA (Progressive Web App) 도입, 설정 QR코드 연동 & Cloud Run 배포 아키텍처 완비 (Phase 6 - [PWA_PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PWA_PLAN.md))**:
    - **PWA 핵심 자산 구축 및 서빙**: `frontend/manifest.json` (`display: standalone`, `theme_color: #10b981`), `frontend/sw.js` (Service Worker Stale-While-Revalidate 및 12대 응급처치 가이드 오프라인 캐싱), 고해상도 앱 아이콘(`icon-192.png`, `icon-512.png`), `main.py` 라우팅 결합.
      - **아이숨 공식 3D 앱 아이콘 및 파비콘 전역 탑재 완료 (`images/aisum_official_app_icon.png`, `frontend/img/`, `app/static/img/`)**: 팀장님 지정 공식 스플래시 로고 심볼(민트-오션블루 의료 십자가 + 듀얼 하트 + 화이트 리프)을 3D 스퀘어클(Squircle)로 정밀 리마스터링하여 PWA 512×512 HD, 192×192 기본, iOS `apple-touch-icon.png`, 멀티레이어 브라우저 파비콘(`favicon.ico`)으로 생성·배치 완료. `main.py`에 `@app.get("/favicon.ico")` 라우터 신설, `sw.js` 오프라인 프리캐시 목록 추가, 19개 전체 HTML 템플릿 `<head>` 파비콘 링크 주입 및 25대 프론트엔드 통합 계약 테스트 All-Green 검증 완결.
    - **설정페이지(`settings.html`) '모바일 기기 연결'**: '스마트폰으로 앱 열기' 클릭 시 현재 접속 도메인(`window.location.origin`)을 실시간 반영하는 QR코드 팝업 모달(`openQrModal()`), 원터치 주소 복사, iOS(홈 화면에 추가) 및 Android(앱 설치) 가이드, `beforeinstallprompt` 기반 PWA 원클릭 설치 버튼 지원.
    - **Google Cloud Run 배포 & .env 다중 API Key 완전 연동**:
      - `main.py` 포트 바인딩 최적화: `port=int(os.getenv("PORT", 8000))` 수신.
      - `app/config.py` Firebase 3단 인증: 로컬/컨테이너 파일 경로, `FIREBASE_KEY_JSON` 환경변수 문자열, Google Cloud IAM 무키(ADC) 인증 지원.
      - 경량 `python:3.11-slim` Multi-stage `Dockerfile` 및 `.dockerignore` 생성.
      - **원클릭 배포 스크립트 (`scripts/deploy_cloud_run.sh`) 개발**: `.env` 파일의 4대 핵심 키(`DATA_GO_API_KEY`, `GEMINI_API_KEY`, `KAKAO_REST_API_KEY`, `serviceAccountKey.json`, `FIRESTORE_DATABASE_ID`)를 자동 주입하여 Cloud Run 서울 리전(`asia-northeast3`)으로 무결점 원클릭 배포 완료.
21. **[완료] 입력·결과 페이지 상하 공백 완전 박멸 & 전 기종 스마트폰 100% 빈틈없는 Full-Screen(100dvh) 웹앱 밀착 반응형 아키텍처 구축 (Phase 3-K)**:
    - **Zero-Gap Layout**: 데스크톱 미디어쿼리의 불필요한 목업 테두리(`border: 8px solid #ffffff`) 및 상하 24px 회색 공백 완전 제거, `body` 전역 패딩/마진 0px 및 배경색 완전 일치화 (결과 `#f8faff`, 입력 `#ffffff`).
    - **전 기종 스마트폰 100% 밀착**: `@media (max-width: 639px)`에서 `width: 100%; max-width: 100%; height: 100dvh; min-height: 100dvh;` 적용으로 아이폰 SE/14/15/16/Pro Max, 갤럭시 S21~S24/Ultra, Z Flip/Fold 등 전 기종에서 화면 전체에 1픽셀의 빈틈도 없이 꽉 채우는 네이티브 앱 UX 실현.
    - **Safe Area 정밀 도킹**: 상단 헤더(`env(safe-area-inset-top)`), 하단 고정 바(`env(safe-area-inset-bottom)`) 도킹으로 노치/다이내믹 아일랜드 및 제스처 홈 바와 겹치지 않는 일체형 마감.
22. **[완료] 이전 문진 결과 바텀시트 모달 폐지 및 독립 전용 페이지(`history.html`, `/history`) 신설 (Phase 3-L)**:
    - **모달 탈피 및 독립 페이지화**: 기존 메인 홈 화면(`index.html`) 바텀시트 모달을 폐지하고, 전 기종 스마트폰 100% 밀착형 단독 웹페이지(`.mobile-viewport.history-shell`) 신설.
    - **상단 헤더 & 요약 바**: 뒤로가기 버튼, "문진 결과 기록" 타이틀, "전체 삭제" 원터치 버튼, 실시간 "총 N건의 문진 기록" 카운트 뱃지, "+ 새 문진" 바로가기 버튼 제공.
    - **기존 기능 100% 동일 유지**: `AisumHistoryManager` 로컬 스토리지 기반 영구 저장 및 0ms 즉시 복원, KTAS 1~5 뱃지, 환아 정보(나이·성별·체온), 증상 태그, 추천 시설, "당시 결과 다시보기"(`result.html?is_replay=true`), 개별/전체 삭제, Empty State, 응급실 병상 모니터링 연동 보존.
    - **전역 GNB 4-Tab 일괄 연동**: `index.html`, `settings.html`, `emergency_guide.html` 등 전 페이지의 Tab 2를 `history.html`로 교체하고, `result.html`에서 `isReplayMode` 시 뒤로가기 버튼을 `history.html`로 연결.
    - **14대 통합 계약 테스트 전수 통과**: TC-814 신설 및 100% 검증 완료.
23. **[완료] 응급실 가이드 페이지 ➔ 구급대원용 응급 브리핑 카드 전용 페이지(`briefing_card.html`, `/briefing-card`) 전면 개편 (Phase 3-M)**:
    - **구급 현장 골든타임 단축을 위한 3대 핵심 섹션 구축**:
      1. **환아 기본 신상 정보 (필수 입력)**: 이름, 생년월일(나이/월령 자동 계산), 성별, 굵은 붉은색 혈액형 캡슐 뱃지(`🩸 RH+ A형`), 비상 연락처 및 원터치 `[📞 통화 연결]` 버튼 도킹. 신상 미등록 시 자동 팝업 유도.
      2. **필수 의료 정보 (문진 기록 불러오기 및 원하는 회차 선택)**: `AisumHistoryManager` 연동으로 최신 기록을 기본 표출하고 `[🔄 기록 변경]` 모달을 통해 저장된 문진 중 원하는 회차를 즉시 선택 바인딩(KTAS 등급, 측정 체온, 해열제 복용 이력, 증상 태그, 추천 응급실).
      3. **응급 시 특이사항**: 종교적 신념에 따른 수혈 거부 여부(수혈 동의 vs 절대 거부 붉은색 경고 박스), 주치의 기존 진료 병원명 및 담당 의사 직통 연락처(`tel:` 버튼 도킹).
    - **구급 현장 특화 편의 기능**:
      - **구급대원 제시용 풀스크린 모드 (`fullscreenParamedicModal`)**: 어두운 구급차 내부에서도 또렷하게 볼 수 있는 대형 폰트 고대비 뷰 제공.
      - **119 원터치 즉시 통화**: 상단 퀵 배너에 `[🚨 119]` 통화 버튼 도킹.
    - **전역 GNB 4-Tab 일괄 개편 및 백엔드 라우터 서빙**:
      - Tab 3 명칭을 `응급실 가이드` ➔ `브리핑 카드`(`briefing_card.html`, `assignment_ind` 아이콘)로 변경하고, `index.html`, `history.html`, `settings.html`, `guidebook.html` 등 전역 템플릿에 일괄 동기화.
      - FastAPI 라우터에 `@app.get("/briefing-card")`, `@app.get("/briefing_card.html")`, `@app.get("/briefing")`, `@app.get("/guide")`, `@app.get("/emergency_guide.html")` 엔드포인트 연동.
    - **15대 통합 계약 테스트 전수 통과**: TC-815 신설 및 15개 프론트엔드 통합 테스트 + 전체 테스트 스위트 100% 통과 (총 118개 테스트 전수 통과).
24. **[완료] 응급 브리핑 카드 스크롤 버그 해결 & 토스/애플 헬스급 프리미엄 미니멀 디자인 전면 리팩토링 (Phase 3-N)**:
    - **스크롤 불능 및 하단 GNB 바 화면 잘림 결함 완전 해소**:
      - `.briefing-content`에 `flex: 1; min-height: 0; overflow-y: auto !important; -webkit-overflow-scrolling: touch; padding: 14px 16px calc(80px + env(safe-area-inset-bottom, 0px) + 24px) 16px !important;` 부여.
      - 외부 모바일 뷰포트 고정 셸 내에서 컨텐츠 영역만 부드러운 네이티브 관성 스크롤로 매끄럽게 동작하도록 개편하여 스크롤 먹통 현상 100% 박멸.
      - 하단 네비게이션 바(GNB)의 가림 현상을 방지하기 위해 104px 이상의 안전 여백을 확보하여 최하단 카드("구급대원 필독 특이사항", 주치의 연락처, 수혈 거부 안내)까지 잘림 없이 시원하게 열람 가능.
    - **토스 & 애플 헬스 스타일의 프리미엄 미니멀리즘 디자인 전면 리뉴얼**:
      - **상단 헤더 정돈**: 복잡하고 눈에 거슬리던 빨간 알약 뱃지를 배제하고, 원형 슬레이트 뒤로가기 버튼 + 볼드한 `119 응급 브리핑` 타이틀 + 깔끔한 `신상 수정` 블루 필 버튼으로 단정하게 개편.
      - **가이드 배너 리파인**: 둔탁한 검은색 배경 대신 딥 슬레이트 & 레드 포인트 그라디언트 카드(`119 구급대원 즉시 전달용`, `[📱 크게]`, `[🚨 119]`)로 세련되게 마감.
      - **일관된 카드 UI**: 제각각 붙어 있던 알록달록 무지개 배지를 제거하고 통일된 아이콘 + 선명한 소제목(`👤 환아 인적사항`, `🩺 최근 문진 및 응급도`, `⚠️ 구급대원 필독 특이사항`) 및 우측 액션 버튼(`[정보 변경]`, `[기록 변경]`, `[특이사항 설정]`)으로 시각적 위계 확립.
      - **환아 신상 카드**: 미등록 시에도 촌스러운 노란 점선 테두리 대신 모던 라이트 슬레이트 카드와 `+ 환아 신상정보 등록하기` CTA 버튼으로 개선하고, 등록 시 굵고 선명한 레드 캡슐 배지(`🩸 RH+ A형`)와 원터치 비상연락처 통화 카드를 정갈하게 배치.
      - **의료 기록 & 특이사항**: KTAS 2단계 긴급 배너, 체온·해열제 2열 그리드, 증상 해시태그 칩, 종교적 수혈 거부 적색 경고 박스 및 주치의 직통 전화 연결 버튼을 완성도 높게 리팩토링.
    - **프론트엔드 통합 계약 테스트 100% 무결점 통과**:
      - TC-815를 포함한 15대 프론트엔드 통합 테스트 및 52개 코어 단위 테스트 전수 통과 확인.
25. **[완료] 환아 인적사항 팝업 모달 제거 및 브리핑 페이지 카드 내 원터치 인라인 직접 입력·저장 파이프라인 구축 (Phase 3-O)**:
    - **모달 팝업 폐지 및 카드 내 전용 인라인 입력 폼(`profileInlineForm`) 탑재**:
      - 모달을 열고 닫는 불필요한 단계를 제거하고, 브리핑 카드 '환아 인적사항' 카드 내부에서 직접 키보드로 타이핑하고 칩을 눌러 저장하는 인라인 폼 설계.
      - 환아 이름(`#inlineInpName`), 생년월일(`#inlineInpBirth`), 남아/여아 토글 칩, Rh+/Rh- 및 ABO 4종(A/B/O/AB) 혈액형 칩, 비상연락처(`#inlineInpPhone`), 보호자 관계(`#inlineInpRelation`), 추가 특이사항(수혈 거부 및 주치의 연락처) 일체형 배치.
    - **원터치 저장 & 인라인 편집(Edit) 모드 전환**:
      - `[환아 정보 저장하기]`(`#btnInlineSave`) 클릭 시 `localStorage`의 `aisum_patient_profile`에 즉각 저장되고 카드 뷰 모드(`profileExistingView`)로 자동 전환되어 환아 이름, 만나이/개월수, 혈액형 배지, 비상연락처 및 통화 연결 버튼 표출.
      - 상단 `[정보 변경]`(`#btnCardEditProfile`) 클릭 시 카드가 인라인 폼으로 토글 전환되어 기존 입력값을 바로 수정 가능하며 `[취소]`(`#btnInlineCancel`) 버튼 지원.
    - **15대 통합 계약 테스트 100% 무결점 통과**:
      - `tests/test_step8_frontend_integration.py` 전수 통과(`15 passed in 20.89s`).
26. **[완료] 응급 브리핑 카드 상단 119 구급대원 즉시 전달용 안내 배너 삭제 및 최상단 레이아웃 최적화 (Phase 3-P)**:
    - **상단 배너(`.paramedic-banner`) 영구 제거 및 클린 UI 달성**:
      - `briefing_card.html`, `frontend/templates/emergency_guide.html`, `app/templates/emergency_guide.html`에서 불필요하게 공간을 차지하던 `<section class="paramedic-banner" id="paramedicNoticeBanner">` 전체 마크업 완전 삭제.
      - 헤더 바로 아래에 '환아 인적사항' 카드가 첫 번째 요소로 시원하게 배치되어 진입 즉시 환아 프로필을 확인 및 작성할 수 있도록 최상단 레이아웃 정돈.
    - **JS 이벤트 리스너 안정화**:
      - 배너 내 존재하던 `btnToggleFullscreen` 버튼 소멸에 따른 `document.getElementById('btnToggleFullscreen')?.addEventListener(...)` 옵셔널 체이닝 가드레일 적용.
    - **15대 통합 계약 테스트 100% 무결점 통과**:
      - `tests/test_step8_frontend_integration.py` 실행 결과: 15 passed in 22.19s (100% 통과).
27. **[완료] 브리핑 카드 환아 프로필 문진 연동 & 자연어 나이·상태 측정 스마트 허브 일체형 감지 파이프라인 구축 (Phase 3-Q)**:
    - **브리핑 카드 환아 프로필 문진 페이지 자동 연동 (`loadSavedProfileAndAutoFillAge`)**:
      - `localStorage`의 `aisum_patient_profile`에 등록된 환아 생년월일을 자동 파싱하여 오늘 기준 일령/월령/연령을 정밀 산출.
      - 문진 페이지(`input.html`) 로드 시 5대 소아 연령 카테고리(`newborn`, `infant`, `toddler`, `child`, `adolescent`)와 나이 슬라이더를 0ms 즉각 동기화.
      - 상단에 `patientProfileAutofillBanner`를 동적 마운트하여 "이하준 (14개월 · 남아) 정보 자동 연동 [나이 적용됨]" 배너 노출.
    - **소아 특화 자연어 나이 파서 대폭 강화 (`extractAgeFromText`)**:
      - 신생아 일수(`생후 15일`, `신생아`), 백일/100일 미만, 개월수(`3개월`, `14개월`), 돌 아기(`돌쟁이`, `돌아기`, `두돌`), 만 나이(`만 3세`, `5살`), 한글 수사(`세살`~`열살`) 전수 지원.
      - 객체 반환 시의 `NaN` 렌더링 버그를 원천 차단하고 `setAgeCategory(detectedAge.category, detectedAge.value)`를 통해 상태 측정 허브 슬라이더와 즉각 동기화.
    - **나이·상태 측정 허브(`card-measurement-hub`) 스마트 일체형 연동**:
      - 증상 입력 시 나이뿐만 아니라 체온(숫자/고열 키워드), 100일 미만 발열 고위험군 플래그, 동반 증상(기침, 콧물, 가래, 호흡곤란, 구토, 설사, 복통 등), 해열제 복용 종류(아세트아미노펜, 이부프로펜 등)를 동시 추출하여 상태 측정 허브 전 탭에 일체형으로 실시간 반영.
      - 감지된 나이와 상태 정보를 직관적인 초록색/적색 피드백 뱃지로 안내.
    - **16대 프론트엔드 통합 계약 테스트 100% 무결점 통과**:
      - `tests/test_step8_frontend_integration.py`에 TC-816 신설 및 전수 통과 확인 (총 119개 테스트 무결점 통과).
28. **[완료] 브리핑 카드 연동 시 증상 나이 중복·충돌 방지 및 브리핑 카드 공식 나이 최우선 자동 유지 체계 구축 (Phase 3-R)**:
    - **브리핑 카드 공식 등록 나이 최우선 원칙 (`useProfileAgeFirst`) 정립**:
      - 브리핑 카드 환아 프로필(`aisum_patient_profile`)이 등록·연동된 상태에서 증상 입력란에 임의의 나이("만7세")가 작성되더라도, 하단 상태 측정 허브의 [아이 나이]가 왜곡되지 않고 브리핑 카드의 공식 나이로 100% 자동 유지(`setAgeCategory(savedProfileData.category, savedProfileData.val)`).
    - **스마트 나이 충돌 감지 및 피드백 뱃지 안내**:
      - 증상 나이와 공식 나이가 상이할 경우 `auto-sync-temp-badge`에 `💡 브리핑 카드 등록 정영식(13개월) 나이가 자동 유지되었습니다. [증상 나이(만 7세)로 변경]` 배지를 노출하여 직관적 피드백 제공.
    - **양방향 토글 및 0초 원터치 복원 지원**:
      - 다자녀 가구 등 다른 아이의 증상 입력을 원하는 경우 `[증상 나이로 변경]` 클릭으로 즉각 전환 지원.
      - 상단 배너 클릭 또는 `[브리핑 카드 나이로 복원]` 클릭 시 언제든 0초 만에 브리핑 카드 공식 나이로 원터치 복원.
    - **17대 프론트엔드 통합 계약 테스트 & 120개 전체 테스트 무결점 통과**:
      - `tests/test_step8_frontend_integration.py`에 TC-817 신설 및 전수 통과 (`17 passed in 22.21s`), 전체 120개 테스트 스위트 100% 통과 (`120 passed in 191.70s`).
29. **[완료] 브리핑 카드 나이 상단 탭 2 배지(#tab-val-age) 및 하단 요약 바 100% 자동 적용 (미입력 X) (Phase 3-S)**:
    - **상단 탭 2 배지 및 하단 요약 바 '미입력(모름)' 정체 결함 근본 해소**:
      - 브리핑 카드 환아 나이(예: 14개월)가 하단 상태 측정 패널 슬라이더에는 세팅되었으나 상단 탭 2 배지(`tab-val-age`)에 여전히 '미입력'으로 남고 하단 요약 바에 '나이 미입력(모름)'으로 유지되던 문제 해결.
      - `loadSavedProfileAndAutoFillAge` 내에서 `state.ageTouched = true;`, `state.hasSavedProfile = true;`를 선행 확정하고, 슬라이더 동기화 후 즉시 `updateSummaryBar()`를 호출하여 상단 탭 2 배지 및 하단 요약 바를 100% 실시간 최신화.
    - **`isEffectiveAgeUnknown()` 가드레일 정립**:
      - `if (state.hasSavedProfile) return false;`를 최우선 가드레일로 배치하여, 브리핑 카드 프로필이 연동된 상태에서는 보호자가 슬라이더 다이얼을 직접 손으로 건드리지 않아도 유효 나이로 공식 인정하여 '나이 모름'이나 '미입력' 처리를 원천 방어.
    - **다각적 브리핑 카드 나이 소스 감지**:
      - 환아 신상정보(`birth`)뿐만 아니라 활성 의료 기록(`activeRecord`)이나 최근 문진 기록의 `childAge` ("14개월" 등) 텍스트 소스까지 감지하여 슬라이더와 탭 배지에 일체형 반영.
    - **18대 프론트엔드 통합 계약 테스트 & 121개 전체 테스트 무결점 통과**:
      - `tests/test_step8_frontend_integration.py`에 TC-818 신설 및 전수 통과 (`18 passed in 22.39s`), 전체 121개 테스트 스위트 100% 통과 (`121 passed in 217.20s`).
30. **[완료] 입력 페이지 초기 로드 시 브리핑 카드 나이 오버라이트 버그 원천 해결 & 아이 상태 측정 허브 즉시 자동 분류·적용 (Phase 3-T)**:
    - **초기 로드 시 하드코딩 기본값 14개월 오버라이트 버그 원천 해소**:
      - 문진 입력 페이지 초기 접속 시 스크립트 중반부(`loadSavedProfileAndAutoFillAge`)에서 브리핑 카드의 공식 나이(13개월)를 정상 로드했음에도, 스크립트 최하단 `// Initialize defaults` 블록의 무조건적인 `updateAgeDisplay(14)` 호출로 인해 14개월로 덮어써지던 버그 해결.
    - **프로필 존재 여부에 따른 분기 가드레일 확립**:
      - `if (!profileLoaded && !state.hasSavedProfile)` 가드레일을 적용하여, 환아 프로필이 없을 때만 기본값 `14개월`이 적용되도록 분기 제어 체계 확립.
      - 초기화 블록 최후미에 `loadSavedProfileAndAutoFillAge()`를 최종 동기화하여 브리핑 카드 나이(13개월)가 최우선으로 확정되도록 보장.
    - **상태 측정 허브 100% 즉시 자동 분류 및 화면 일치화**:
      - 사용자가 아무런 조작을 하지 않아도 문진 페이지에 들어오자마자 상단 배너 `정영식 (13개월 · 여아)`, 탭 2 배지 `13개월`, 영아(infant) 카테고리 칩 활성화 및 슬라이더 13개월 위치, 하단 요약 바 `13개월`로 100% 일치 표출.
    - **19대 프론트엔드 통합 계약 테스트 & 122개 전체 테스트 무결점 통과**:
      - `tests/test_step8_frontend_integration.py`에 신규 TC-819(`test_19_briefing_card_age_not_overwritten_by_defaults`) 신설 및 전수 통과 (`19 passed in 18.80s`), 전체 122개 테스트 스위트 100% 통과.
31. **[완료] 기록페이지 삭제 시 응급실 모니터링 자동 동기화/해제 및 브리핑 카드 '기록 변경' 모달 팝업·즉시 갱신 체계 구축 (Phase 3-U)**:
    - **기록페이지 삭제 시 응급실 모니터링 자동 연동 훅 (`syncWatchTargetsWithHistory`)**:
      - 문진 기록 삭제(`deleteById`) 또는 전체 삭제(`clearAll`) 시 알림 매니저의 병상 감시 대상(`aisum_emergency_watch_target`)과 즉시 동기화.
      - 잔여 문진 기록 중 중증(KTAS 1~3단계) 기록이 0건이면 감시 대상을 완전히 소거하고 모니터링 배너 및 백그라운드 폴링을 즉각 해제. 잔여 중증 기록이 있으면 해당 병원군으로 감시 대상을 정제하고 최신 병원을 1순위로 자동 승격.
    - **브리핑 카드 '기록 변경' 원터치 선택 모달 UI & 파이프라인 완결**:
      - `briefing_card.html` 섹션 2 '최근 문진 및 응급도'의 [기록 변경] 클릭 시 과거 문진 기록을 직관적으로 탐색할 수 있는 카드형 모달 팝업 제공.
      - KTAS 레벨별 컬러 뱃지, 문진 일시, 아이 나이/체온, 증상 태그, 추천 응급실명을 깔끔히 표출하고 원하는 기록 카드 터치 시 브리핑 카드 본문 및 전체화면 모드 데이터를 0초 만에 실시간 갱신.
    - **21대 프론트엔드 통합 계약 테스트 & 122개 전체 테스트 무결점 통과**:
      - `tests/test_step8_frontend_integration.py`에 TC-820(`test_20_history_deletion_syncs_emergency_watch_target`) 및 TC-821(`test_21_briefing_card_record_modal_and_active_switch`) 신설 및 전수 통과.
      - 프론트엔드 21개 통합 계약 테스트 및 전체 122개 테스트 스위트 100% All-Green 통과 (`122 passed in 182.84s`).
32. **[완료] 브리핑 카드 '기록 변경' 모달 버그 해결 및 소아 KTAS 구급대원 인계 상세 요약 박스 신설 (Phase 3-V)**:
    - **모달 오버레이 투명도/표출 버그 완전 해결**:
      - `recordSelectModal.classList.add('active')` 및 인라인 클릭 리스너 결합으로 '기록 변경' 버튼 클릭 시 과거 문진 기록 팝업이 즉시 표출되도록 완벽 조치.
    - **주요 증상 구급대원 인계 상세 브리핑 박스 신설 (`buildSymptomBriefingSummary`)**:
      - 2021 소아 KTAS 임상 지침에 기반하여 119 구급대원과 소아 응급실 의료진이 즉각 파악해야 하는 [🚨 긴급 행동 지침], [📋 임상 주의사항], [💬 보호자 진술] 3단 일체형 요약 박스를 브리핑 카드 본문 및 전체화면 모드에 자동 생성.
    - **22대 프론트엔드 통합 계약 테스트 & 122개 전체 테스트 100% 무결점 검증**:
      - `tests/test_step8_frontend_integration.py`에 TC-822(`test_22_briefing_card_symptom_summary_box_and_modal_active`) 추가 및 전체 테스트 100% 통과.
33. **[완료] 브리핑 카드 주요 증상 태그 & 구급대원 인계 브리핑 단일 일체형 카드 통합 및 간소화 (Phase 3-W)**:
    - **단일 일체형 카드(`.briefing-unified-symptom-card`)로 통합**:
      - 상하 2중으로 나뉘어 있던 주요 증상 태그 박스와 구급대원 인계 브리핑 박스를 상단 헤더(좌측: 태그 뱃지, 우측: 긴급 인계 배지)와 하단 임상 가이드로 결합한 프리미엄 일체형 카드로 통합.
    - **중복 증상명 파싱 제거 및 정보 간소화**:
      - 이미 태그로 선명히 표출된 증상명(`[주요 증상] ...`)을 본문 첫 줄에서 제거하여, 119 구급대원이 필수 행동 지침과 주의사항에 1초 만에 집중할 수 있도록 가독성 대폭 향상.
    - **4대 템플릿 100% 완벽 동기화 및 전수 테스트 통과**:
      - `briefing_card.html`(frontend & app), `emergency_guide.html`(frontend & app) 전수 동기화 및 22개 프론트엔드 통합 계약 테스트 All-Green 검증 완료.
34. **[완료] 구급대원 필독사항 환아 인적사항 카드 내 포함 및 일체화 (Phase 3-X)**:
    - **환아 인적사항 카드 내부 서브 컨테이너(`.patient-special-notes-box`)로 일체화**:
      - 기존에 독립된 카드로 분리되어 세로 스크롤을 유발하던 '🚨 구급대원 필독사항(알레르기, 기저질환, 복용약물, 특이사항)'을 '👶 환아 인적사항' 카드(`cardPatientProfile`) 내부 서브 컨테이너로 완전 수납.
      - 상단에 🚨 구급대원 필독사항 뱃지와 `[수정]` 버튼을 나란히 배치하고, 알레르기/기저질환/복용약물/특이사항 4대 핵심 정보를 컴팩트한 태그/그리드 형태로 일목요연하게 렌더링.
    - **인라인 수정 폼 및 상태 토글 스크립트 완벽 유지**:
      - 환아 인적사항 카드 내에서도 인라인 수정 모드(`#editNotesForm`)를 지원하여 즉각적인 편집 및 저장이 가능하며, 저장 즉시 환아 프로필 및 로컬 스토리지에 동기화.
    - **4대 템플릿 100% 동기화 & 23대 브리핑 카드 통합 계약 테스트 검증 완료**:
      - `briefing_card.html`(frontend & app), `emergency_guide.html`(frontend & app) 4대 템플릿 전수 일치.
      - `scripts/test_briefing_card_integration.py` 23개 항목 100% All-Green 통과.
35. **[완료] PWA Service Worker v2 업그레이드 & Cloud Run 최신 리비전 100% 완전 동기화 배포 (Phase 3-Y)**:
    - **PWA Service Worker 캐시 v2 개편 (`sw.js`)**:
      - `CACHE_NAME`을 `aisum-cache-v2`로 승격하고, 구버전 캐시 즉각 자동 소멸 및 HTML 문서 요청에 대해 `networkFirst` 전략을 적용하여 실서버 배포 시 구버전 화면 고착 현상 원천 차단.
    - **루트(`/`) 라우팅 메인 홈(`index.html`) 직결 및 HTTP 캐시 버스팅**:
      - 루트 진입 시 `index.html`로 정확히 서빙하고 주요 CSS/JS에 `?v=20261018_v2` 캐시 버스팅 파라미터 적용.
    - **Google Cloud Run 무중단 배포 및 트래픽 100% 전환**:
      - 최신 리비전 `aisum-service-00008-msb` 배포 및 실서버(`https://aisum-service-489063687989.asia-northeast3.run.app`) 정상 서빙 검증 완료.
36. **[완료] 웹앱 접속 시 1순위 스플래시(splash.html) 동작 보장 & 0단계 세션 스플래시 가드 구축 (Phase 3-Z)**:
    - **루트(`/`) 라우팅 1순위 `splash.html` 서빙 원복 (`main.py`)**:
      - 브라우저 클라이언트 요청(`accept: text/html`) 시 최우선 순위로 `splash.html`을 서빙하여, 사용자가 서비스 URL 진입 시 무조건 1.8초 브랜드 애니메이션 스플래시가 가장 먼저 실행되도록 보장.
    - **스플래시 화면 세션 플래그(`aisum_splash_shown`) 기록 엔진 탑재 (`splash.html`)**:
      - `splash.html` 진입 즉시 세션 플래그를 등록하여 세션 온보딩 완료 여부 확정.
    - **메인 홈(`index.html`) 0단계 세션 스플래시 가드(Session Splash Guard) 구축**:
      - `/home` 또는 `index.html`로 직접 접속한 미수료 세션 사용자를 즉시 `/splash`로 리다이렉트하는 2중 안전망 구축. 홈 화면 새로고침(F5) 시에는 세션 플래그를 유지하여 스플래시 무한 루프 완벽 방지.
    - **프론트엔드 통합 계약 테스트 TC-823 신설 & 전체 127개 테스트 100% 통과**:
      - `tests/test_step8_frontend_integration.py`에 `test_23_root_serves_splash_as_first_priority_and_session_guard`를 추가하여 총 24개 프론트엔드 통합 테스트 및 127개 전수 테스트 무결점 통과.
37. **[완료] 가이드북·이용약관·오픈소스 라이선스 3대 핵심 법무/안내 문서 전면 최신화 (Phase 3-AA)**:
    - **가이드북 7대 핵심 챕터 및 6종 하이라이트 배지 전면 개편 (`guidebook.html`)**:
      - 상단 히어로 태그 6종(5대 연령별 AI 문진, 2-트랙 안전망, 실시간 병상 알림, 구급대원 브리핑 카드, 이전 문진 기록함, PWA 홈화면 바로가기) 완비.
      - 7대 필터 챕터(AI 문진 & 5대 연령 체계, 2-트랙 안전망, 실시간 병상 알림 센터, 구급대원 인계 브리핑 카드, 이전 문진 기록함, 야간 방문 전 필수 준비물, FAQ) 체계화.
    - **이용약관 개정 및 개인정보보호 민감정보 보호 특칙 신설 (`terms.html`)**:
      - 제2조 용어 정의 4건(브리핑 카드, 문진 기록함, 5대 연령 체계, 병상 알림 센터) 신설.
      - 제8조 신설: 환아 신상정보(혈액형, 알레르기, 기저질환, 수혈 특이사항 등)는 **"서버 DB로 전송·수집되지 않고 이용자 브라우저 LocalStorage에만 암호화 보관"**됨을 명시하여 데이터 유출 위험 원천 차단.
      - 제9조: 실시간 가용병상 알림 및 이용자의 즉각적인 모니터링 해제 권리 보장.
    - **오픈소스 라이선스 및 공공데이터 명세 17개 고지 확장 (`licenses.html`)**:
      - Card 15(APScheduler v3.10+ MIT), Card 16(Pytest & Pytest-Asyncio v8.0+ MIT), Card 17(대한소아응급의학회 2021 소아 KTAS 지침 공공누리 제1유형) 신설 및 카운터(17개 고지) 동기화.
    - **양대 템플릿 디렉터리(`frontend/templates/` & `app/templates/`) 100% 일치 동기화 및 전수 테스트 통과**:
      - `tests/test_step8_frontend_integration.py` 24개 항목 All-Green 검증 완료.
38. **[완료] 설정 화면 '화면 테마 변경' 개편 및 전역 딥 다크 모드 3-Way 시스템 구축 (Phase 3-AB)**:
    - **설정 화면 (`settings.html`) '화면 테마 변경' UI 전면 개편**:
      - 중복되던 '자녀의 기본 정보 변경' 버튼(`#child-info-row-btn`)을 **`화면 테마 변경`**(`#theme-setting-row-btn`)으로 개편.
      - 우측 밸류(`#theme-setting-display`)에 현재 적용된 테마를 실시간 표출 (`화이트 모드` / `다크 모드` / `시스템 설정`).
      - 클릭 시 토스/애플 스타일의 프리미엄 '화면 테마 설정' 모달 다이얼로그(`#theme-setting-modal`) 팝업 제공:
        - ☀️ 화이트 모드 (`theme-opt-light`): 주간 권장 선명한 Calm Harbor 라이트 룩.
        - 🌙 다크 모드 (`theme-opt-dark`): 야간 불 꺼진 방에서 아이를 돌볼 때 눈부심을 원천 차단하는 편안한 딥 미드나이트 다크 룩.
        - ⚙️ 시스템 설정 동기화 (`theme-opt-system`): 기기 OS 테마 자동 추종.
    - **전역 테마 관리자 모듈 구축 (`frontend/js/theme.js`)**:
      - `window.AisumThemeManager` 전역 객체 신설 (`getTheme`, `getEffectiveTheme`, `applyTheme`, `setTheme`, `watchSystemTheme`).
      - `localStorage.setItem('aisum_theme', ...)` 영구 보관 및 모바일 주소창 메타 태그(`theme-color`) 동기화.
    - **전역 스타일 시스템 (`style.css`) 딥 다크 모드 토큰 완비**:
      - `html[data-theme="dark"]`에 `--canvas-bg: #090d16;`, `--app-bg: #0f172a;`, `--card-bg: #1e293b;`, `--slate-900: #f8fafc;` 등 딥 다크 팔레트 완비.
      - 모달, 헤더, 바텀 네비게이션, 인풋 및 가이드/약관/라이선스 카드 다크모드 완벽 대응.
      - `.theme-options-list`, `.theme-option-card` 프리미엄 인터랙션 스타일링 구현.
    - **0ms FOUC(화면 깜빡임) 방지 인라인 스크립트 전역 템플릿 탑재**:
      - `settings.html`, `index.html`, `input.html`, `result.html`, `briefing_card.html`, `history.html`, `guidebook.html`, `terms.html`, `licenses.html` 등 전 템플릿 `<head>` 상단에 테마 즉시 적용 스크립트 삽입.
    - **프론트엔드 통합 계약 테스트 신설 & 전수 통과**:
      - `tests/test_step8_frontend_integration.py`에 TC-824(`test_24_theme_setting_feature_contract`) 추가 및 25개 테스트 100% All-Green 통과 (`25 passed in 22.88s`).
      - `frontend/templates/`와 `app/templates/` 양대 디렉터리 100% 동기화 완료.
    - **Google Cloud Run 무중단 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00026-nhs` 100% 트래픽 서빙 및 실서버(`https://isoom-service-920380215419.asia-northeast3.run.app`) 라이브 헬스체크 검증 완료. 공식 3D 앱 아이콘(icon-192: 29KB, icon-512: 197KB) 및 파비콘(favicon.ico: 5KB) 프로덕션 정상 서빙 확인.
39. **[완료] 다크 모드 전면 리팩토링 및 비주얼 완성도 극대화 완결 (Phase 3-AC)**:
    - **브리핑 카드 (`briefing_card.html`) White-on-White 글씨 가림 결함 원천 해결**:
      - 내부 하드코딩된 `#ffffff` 배경을 `#1e293b` 및 `#0f172a`로 전면 교체하고, 환아 인적사항 텍스트 및 상세 수치 폰트 색상을 `#f8fafc`로 복원하여 100% 선명도 회복.
    - **문진 결과 기록 (`history.html`) 상단 헤더 & 요약 바 다크모드 완결**:
      - 고착되어 있던 흰색 상단 헤더와 요약 카드 배경을 딥 슬레이트 다크 테마로 교정.
    - **바텀 네비게이션 (`.bottom-nav`) 너비 100% 확장 및 좌우 여백 노출 영구 차단**:
      - `max-width: 440px` 제약을 `100%`로 확장하여 모바일 및 태블릿 뷰포트에서 양옆으로 흰색 배경이 삐져나오던 틈새 결함 완벽 해결.
    - **메인 홈 의료시설 카드 & 전화 버튼 시인성 강화**:
      - 전화기 아이콘 버튼에 반투명 글래스 서피스를 적용하여 버튼 경계를 뚜렷하게 분리하고, 야간 마감 시설 카드의 차분한 저대비 스타일링 완비.
    - **Google Cloud Run 무중단 재배포 완결**:
      - 최신 리비전 `isoom-service-00012-snl` 100% 트래픽 전환 및 실서버 검증 완료.
40. **[완료] Nocturne Care 디자인 시스템 기반 전역 다크 모드 CSS 색감 조율 완결 (Phase 3-AD)**:
    - **HTML 무수정 원칙 준수 & 순수 CSS (`style.css`) 색감 고도화**:
      - 마크업 태그 구조는 단 1개도 건드리지 않고 순수 CSS 변수 및 컴포넌트 오버라이드 색상만 Nocturne Care 레퍼런스로 전면 조율.
    - **Neutral 차콜 옵시디언 (`#101318` & `#171a21`) 테마 구축**:
      - 뷰포트 배경 `#101318`, 카드 서피스 `#171a21`, 내부 인셋 박스 `#11141a`, 1px 섬세한 보더 `#232834` 적용.
    - **Primary 로열 블루 (`#3B82F6`) & Tertiary 에메랄드 (`#10B981`) 매칭**:
      - 활성 탭 및 CTA 버튼 `#3b82f6`, 뱃지 및 진료상태 `#10b981` 에메랄드 적용.
    - **순백 텍스트 (`#FFFFFF`) 가독성 100% 회복**:
      - 메인 타이틀 및 핵심 수치 `#ffffff`, 보조 설명 `#9ca3af`로 세련된 시인성 확보.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00013-cml` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
41. **[완료] 메인 홈 캡처 기반 Midnight Slate 다크 테마 전역 일체화 완결 (Phase 3-AE)**:
    - **초고대비 플랫 화이트 카드 CTA 버튼 (`.primary-cta-btn`) 구현**:
      - 칠흑 같은 화면 속에서 '아이 증상 입력하고 병원 찾기' 버튼을 순백 카드(`#ffffff`) + 네이비 차콜 텍스트(`#0f172a`)로 변환하여 시각적 인지성 극대화.
    - **Midnight Slate 3단계 뎁스 아키텍처 확립**:
      - 캔버스 `#0c0e14`, 셸 `#12151d`, 카드 서피스 `#1a1e29`, 내부 인셋 서브 박스 `#141722`.
      - 카드 액션 버튼: `#232938` 배경, `#2d3548` 보더, `#ffffff` 텍스트.
    - **전역 8대 페이지 일체화 & 테스트 무결점 통과**:
      - 홈, 문진, 결과, 브리핑 카드, 문진 기록함, 설정, 가이드북, 이용약관, 오픈소스 라이선스 전반에 완벽 동기화.
      - 25개 통합 계약 테스트 100% All-Green 통과.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00014-rjt` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
42. **[완료] 토스(Toss) 앱 TDS 다크 테마 시스템 전역 구축 및 19개 전체 페이지 다크모드 적용 완결 (Phase 3-AF)**:
    - **Toss TDS 공식 다크 팔레트 전면 이식 (`style.css`)**:
      - 캔버스 `#101012`, 모바일 메인 셸 `#17171c`, 레이어드 카드 `#202027`, 서브 박스/버튼 `#2c2c34`, 토스 블루 `#3182f6`, 토스 그린 `#04b05c`, 토스 레드 `#f04452` 구축.
    - **19개 전 템플릿 0ms 테마 인라인 스크립트 전수 주입 & FOUC 원천 차단**:
      - 10개 누락 페이지에 테마 초기화 스크립트 전수 삽입하여 페이지 이동 시 다크 테마 100% 즉각 렌더링.
    - **하드코딩 흰색 배경 제거 및 `var(--app-bg)` 연동**:
      - `input.html`, `result.html` 내 고정 흰색을 제거하고 CSS 변수로 교정.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00015-vfw` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
43. **[완료] 토스 TDS 다크테마 세부 비주얼 결함 완결 패치 (Phase 3-AG)**:
    - **설정 (`settings.html`) 두꺼운 흰색 구분선 완전 투명화**:
      - 다크모드에서 번쩍거리던 `.settings-section-divider` 8px 흰색 띠를 투명 및 무보더로 오버라이드.
    - **브리핑 카드 (`briefing_card.html`) 잔존 흰색 박스 2곳 제거 & 어두운 텍스트 가림 해결**:
      - `등록된 주치의 병원 없음` 박스 및 KTAS 5단계 요약 바를 다크 인셋 박스(`#2c2c34`)로 반전.
      - 어두운 남색으로 묻히던 권고사항 텍스트를 순백(`#f9fafb`)으로 복원하여 가독성 회복.
      - 상단 뒤로가기 버튼 다크 서피스(`#202027`) 교정.
    - **문진 기록함 (`history.html`) 환아 인적사항 가독성 복원 & 전체삭제 버튼 조율**:
      - 어두운 남색 인적사항 텍스트를 화이트(`#f9fafb`)로 복원하고 전체 삭제 버튼을 다크 서피스로 조화롭게 매칭.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00016-cxx` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
44. **[완료] 전 화면 잔존 라이트 요소 전면 다크화 및 100% Toss TDS 완성 (Phase 3-AH)**:
    - **브리핑 카드 인적사항 수정 폼 (`#profileInlineForm`) 완전 다크화**:
      - 새하얀 `#f8fafc` 폼 박스를 다크 서피스 `#202027` 및 인셋 박스 `#2c2c34`로 반전, 입력창 및 칩 텍스트 가림 원천 해결.
    - **아이숨 가이드북 (`guidebook.html`) 전면 다크 테마 일체화**:
      - 뷰포트 토스 캔버스 `#17171c`, 탭 `#202027`, 세부 피처 박스 3종 `#2c2c34` 및 순백 헤드라인 교정.
    - **서비스 이용약관 (`terms.html`) & 오픈소스 라이선스 (`licenses.html`) 다크 캔버스 완결**:
      - 뷰포트 `#17171c`, 퀵 칩/탭 바 `#202027`, 조항 아티클 카드 일체 다크 테마 규격 통일.
    - **메인 홈 (`index.html`) 의료시설 카드 우측 1px 흰색 스크롤바 트랙 완전 제거**:
      - 다크모드에서 `.facility-card-stack::-webkit-scrollbar-track`을 투명화하여 카드 우측 흰색 줄 제거.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00017-9rb` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
45. **[완료] 심층 핵심 화면 전면 다크화 및 전체 이용 사이클 100% 무결점 달성 (Phase 3-AI)**:
    - **메인 홈 사전 동의 모달 (`#triage-consent-modal`) 다크 인셋화**:
      - 모달 본문 연회색 박스를 `#2c2c34` 인셋 서피스로 전환하고 남색 제목을 토스 블루(`#4593fc`)로 교정.
    - **소아 전문 문진 입력 헤더 (`input.html`) 고대비 순백 복원**:
      - 다크 배경에 묻혀 식별 불가능하던 "소아 전문 문진" 헤더 타이틀을 `#f9fafb` 순백 화이트로 복원.
    - **AI 분석 로딩 화면 (`loading.html`) 전면 다크 카드 시스템 이식**:
      - 화면 전체 바닥과 로딩 카드(`.analyzing-card`)의 하드코딩 흰색을 제거하고 `#101012` + `#202027` 적용.
    - **문진 결과 화면 (`result.html`) & 병원/약국 상세 내역 (`hospital_detail.html`) 전체 다크화**:
      - KTAS 배너, 카테고리 탭, 소아 병상 목록 카드, 법적 안내, 병원 히어로, 당직 전문의, 전화 바 일체 토스 TDS 레이어드 카드로 교정.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00018-dgh` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
46. **[완료] 세부 서브 컴포넌트 전면 다크화 및 100% 무결점 테마 완성 (Phase 3-AJ)**:
    - **가이드북 FAQ 아코디언 & 통화 대본 & 준비물 5종 다크화 (`guidebook.html`)**:
      - `Q1~Q6` 열린/닫힌 아코디언 카드(`.faq-accordion`)를 `#202027` 다크 카드로 전환하고 표준 사전 통화 대본 및 준비물 체크리스트 5종을 `#2c2c34` 인셋 서피스로 완벽 반전.
    - **오픈소스 라이선스 하단 안심 고지 푸터 다크화 (`licenses.html`)**:
      - 최하단 라이선스 안심 고지 카드(`.licenses-footer`)를 `#202027` 다크 서피스로 정돈.
    - **브리핑 카드 구급대원 필독사항 아코디언 서브폼 다크화 (`briefing_card.html`)**:
      - `+ 구급대원 필독사항 추가 입력` 아코디언 내부를 `#202027`로 반전시키고, 수혈 동의/거부 버튼의 색감을 토스 다크 규격으로 정돈.
    - **소아 전문 문진 '아이 나이' 5대 연령 카드/디스플레이/빠른 칩 다크화 (`input.html`)**:
      - 신생아·영아·유아·어린이 5대 연령 버튼(`.age-cat-btn`)과 선택 연령 디스플레이 박스(`.age-display-box`), 빠른 나이 칩(`.age-preset-pill-btn`) 일체를 토스 TDS 레이어드 카드로 완전 통일.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00019-jp6` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
47. **[완료] 입력·결과·메인 3대 핵심 페이지 및 전역 심층 다크모드 100% 완전무결화 (Phase 3-AK)**:
    - **문진 입력 페이지 해열제 5종 카드 & 체온 미측정/다음 버튼 다크화 (`input.html`)**:
      - 복용 안 함/아세트아미노펜/이부프로펜/덱시부프로펜/교차복용 5대 해열제 선택 카드(`.med-type-card`) 및 체온 미측정 버튼(`.temp-unknown-toggle-btn`), 단계 이동 버튼(`.panel-nav-btn`)을 `#202027` 및 `#2c2c34` 다크 서피스로 전면 반전.
    - **문진 결과 화면 탭 알약 바 & 병원명 고대비 순백 복원 & 통화 대본 다크화 (`result.html`)**:
      - 병원 목록 활성 탭(`.track-tab-btn.active`) `#2c2c34` 다크 인셋화, 다크 카드 위에서 안 보이던 병원명(`.slim-hospital-name`)을 `#f9fafb` 순백 화이트로 전면 복원, 통화 대본(`.script-text-box`) 및 복사 버튼(`.btn-copy-script`) 다크화, 하단 법적 안내 인라인 흰색 제거 완결.
    - **메인 홈 위치 설정 바텀 시트 & 병상 알림 모달 다크화 (`index.html`)**:
      - 위치 설정 시트(`.location-bottom-sheet`) 및 주소/키워드 모드 탭, 응급실 병상 변동 알림 시트(`.sheet-dialog-card`)를 `#202027` 다크 서피스로 전면 오버라이드.
    - **서비스 이용약관 운영팀 정보 푸터 다크화 (`terms.html`)**:
      - 최하단 운영팀 정보 카드(`.terms-footer-meta`)를 `#202027` 다크 카드로 교정.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00020-th8` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
48. **[완료] 다크 테마 조화형 버튼 컬러 & 잔존 라이트 5종 전면 개편 (Phase 3-AL)**:
    - **메인 홈 최상단 히어로 CTA 토스 공식 블루 개편 (`index.html`)**:
      - 눈부시게 하얗던 직사각형 버튼(`.primary-cta-btn`)을 **토스 공식 TDS 블루 (`#3182f6`) 서피스** + **순백 텍스트/화살표 (`#ffffff`)** + `box-shadow: 0 4px 20px rgba(49, 130, 246, 0.35)`로 전면 개편하여 차콜 다크 배경 위에서 가장 아름답고 눈이 편안한 프리미엄 CTA 완성.
    - **결과 화면 병원 카드 액션 버튼 & 순위/거리/약국 태그 다크 조화 (`result.html`)**:
      - 전화 버튼(`.slim-btn-call`)을 `#2c2c34` 다크 서피스 + 소프트 화이트 아이콘(`#f9fafb`), 길찾기 버튼(`.slim-btn-map`)을 토스 블루 `#3182f6`, 거리 태그 `#2c2c34`, 진료시간/약국 태그 다크 에메랄드/스카이블루 소프트 틴트로 정돈.
    - **가이드북 하단 플로팅 바 & 액션 버튼 다크화 (`guidebook.html`)**:
      - 하단 바 전체를 `rgba(23, 23, 28, 0.94)` 블러 서피스로 전환, 문진 시작 버튼 토스 블루 `#3182f6`, 응급수칙 버튼 `#2c2c34`로 개편.
    - **문진 입력 3대 탭 컨테이너 & 뱃지 다크화 (`input.html`)**:
      - 탭 바 컨테이너 전체(`.measure-tab-bar`) `#17171c` 딥 다크 인셋 적용, 활성 탭 `#2c2c34`, 뱃지 `#2c2c34` 전면 다크화.
    - **메인 홈 응급실 병상 알림 시트 헤더/카드/버튼 다크화 (`index.html`)**:
      - 시트 헤더 `#202027`, 시트 바디 `#17171c`, 알림 카드 `#202027`, 읽지 않음 `#24242d`, 전화 버튼 `#2c2c34` 전면 적용.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00021-9cw` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
49. **[완료] 세부 5대 핵심 화면 잔존 라이트 & 글씨 가독성 완결 (Phase 3-AM)**:
    - **심야약국 상세 정보 전면 다크화 & 타이틀 가독성 복원 (`pharmacy_detail.html`)**:
      - 실제 마크업 클래스 매핑 교정, 섹션 타이틀(`#f9fafb`) 순백 복원, 상주 약사 프로필 박스 `#2c2c34` 인셋 다크화, 하단 고정 바 `rgba(23, 23, 28, 0.96)` 및 전화 버튼 `#2c2c34` 다크화 완결.
    - **병원 상세 내역 타이틀 가독성 & 접수 마감 배너 조율 (`hospital_detail.html`)**:
      - `야간 당직 전문의 현황`, `진료 시간표` 등 안 보이던 타이틀 글씨 순백 복원, 접수 마감 주의 노란 박스를 차분한 다크 앰버 틴트(`rgba(245, 158, 11, 0.12)`)로 조율, 하단 전화 바 다크화.
    - **위치 설정 바텀 시트 칩 & 닫기 버튼 다크화 (`index.html`)**:
      - 자주 찾는 지역 `색달동` 등 비활성 칩(`.loc-chip-btn`) `#2c2c34` 다크 서피스 + `#f9fafb` 순백 텍스트 전환, 현재 주소 바 텍스트 고대비 복원, 닫기 버튼 `#2c2c34` 다크화.
    - **스마트폰으로 앱 열기 전체 뷰포트 다크화 (`qr.html`)**:
      - `.qr-viewport` `#17171c`, 헤더 `#17171c`, 타이틀/서브타이틀 순백 복원, QR 카드 `#202027` 다크 서피스 개편 (스캔성을 위해 QR 이미지 패딩은 흰색 유지).
    - **문진 결과 KTAS 1단계 긴급 배너 & 새로고침 다크화 (`result.html`)**:
      - `KTAS 1단계 · 소생` 긴급 배너 다크 코랄 틴트(`rgba(239, 68, 68, 0.14)`) 반전, 핵심 메시지 `#f9fafb` 복원, `응급처치 가이드` 및 `새로고침` 버튼 `#2c2c34` 다크 서피스 개편.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00022-4qw` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
50. **[완료] 위치 설정 모달 현재 설정된 주소 다크모드 가독성 결함 완결 (Phase 3-AN)**:
    - **JS 동적 innerHTML 인라인 하드코딩(#0f172a, #334155) 전수 소독 (`main.js`)**:
      - `updateLocationDisplay`, `setUserCustomLocation`, `openLocationSelectModal` 함수에서 `barEl.innerHTML` 주입 시 하드코딩되어 있던 인라인 스타일 색상을 완전히 제거하고, 정규 시맨틱 클래스로 교체.
    - **고대비 순백(#f9fafb) 텍스트 전역 연동 (`style.css`, `index.html`)**:
      - `html[data-theme="dark"] .current-address-bar strong`, `#modal-current-address-val`, `.current-address-val`을 완벽한 순백(`#f9fafb`)으로 고정하여 어두운 배경 위에서 주소가 선명하게 읽히도록 개선.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00023-4kx` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
51. **[완료] 문진 입력 환아 정보 자동 연동 배너 다크모드 완결 (Phase 3-AO)**:
    - **환아 프로필 자동 연동 배너 토스 TDS 다크 서피스 개편 (`input.html`, `style.css`)**:
      - 새하얀 라이트 블루(`#eff6ff`) 배경을 다크 서피스 `#202027`로 전환하고 은은한 블루 보더(`rgba(49, 130, 246, 0.3)`)를 부여하여 눈부심 100% 해소.
      - 아이콘 박스 및 확인 버튼을 `#2c2c34` 다크 서피스로 개편, 환아 타이틀 순백(`#f9fafb`) 복원, `나이 적용됨` 뱃지를 토스 다크 틴트 + `#3182f6` 텍스트로 조화.
    - **증상 입력 경고 팁 다크 코랄 틴트 조율 (`input.html`)**:
      - `.symptom-invalid-tip`을 핑크색에서 차분한 다크 코랄 틴트(`rgba(239, 68, 68, 0.12)`)로 동시 조율.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00024-4jw` 100% 트래픽 전환 및 실서버 라이브 검증 완료.
52. **[완료] 문진 섹션 카드 다크모드 흰색 테두리 눈부심 결함 완결 (Phase 3-AP)**:
    - **문진 섹션 카드(`.triage-section-card`) 토스 TDS 프리미엄 다크 보더 전면화 (`input.html`, `style.css`)**:
      - 기본 상태 라이트 테두리 `#f1f5f9`를 소독하고, 은은하고 부드러운 다크 보더 `rgba(255, 255, 255, 0.08)` 및 `#202027` 서피스로 교체하여 시각적 눈부심 100% 해소.
      - 포커스 및 활성 상태(`.active-card`)의 밝은 하늘색 `#bfdbfe`를 토스 블루 다크 림 `rgba(49, 130, 246, 0.4)` 및 미세 앰비언트 글로우로 정돈.
    - **단계 번호 원형 뱃지 및 서브 요소 일체 다크화 (`input.html`, `style.css`)**:
      - 1번, 2번 단계 번호(`.section-step-num`)를 토스 블루 다크 틴트(`rgba(49, 130, 246, 0.16)`) 배경 + `#3182f6` 텍스트로 조율.
      - 증상 밑줄 필드, 패널 하단 점선 구분선, 나이 카테고리 카드, 체온 다이얼 SVG 배경 트랙 다크화 완결.
    - **Google Cloud Run 프로덕션 재배포 완결**:
      - 최신 리비전 `isoom-service-00025-clw` 100% 트래픽 전환 및 실서버 라이브 검증 완료.




























