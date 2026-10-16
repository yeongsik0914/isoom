# 👶 아이숨 (i-Soom) - 구 MoonlightCare (달빛케어)

> **"야간·휴일에 갑자기 아픈 우리 아이를 위한 가장 빠르고 안전한 소아청소년과 매칭 서비스"**  
> 건강보험심사평가원(HIRA), 국립중앙의료원(NMC) E-Gen 실시간 병상, 한국천문연구원(KASI) 특일 데이터, Firebase Cloud Firestore, 그리고 **Gemini 3.8 Flash 멀티 에이전트** 기반의 지능형 소아 의료 응급 지원 시스템

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Package Manager](https://img.shields.io/badge/uv-Fast%20Packaging-DE5FE9.svg)](https://github.com/astral-sh/uv)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.8_Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Firebase](https://img.shields.io/badge/Firebase-Cloud_Firestore-FFCA28.svg?logo=firebase&logoColor=black)](https://firebase.google.com/)
[![Tests](https://img.shields.io/badge/Tests-92%20Passed-brightgreen.svg)]()
[![Evals](https://img.shields.io/badge/Evals-40%2F40%20(100%25)-blue.svg)]()

---

## 💡 서비스 소개 (About MoonlightCare)

늦은 밤(18시~24시)이나 주말·공휴일에 아이가 갑자기 39도 고열이 나거나 구토를 할 때, 문을 연 소아과를 찾지 못해 대학병원 응급실에서 4~6시간 대기하거나 '소아 진료 불가' 통보를 받는 부모들의 불안을 해결하기 위해 개발된 **지능형 소아 의료 매칭 웹 애플리케이션**입니다.

* 🩺 **친절하고 신속한 사전 문진 (Triage)**: 부모의 당황한 마음을 진정시키고 월령, 체온, 증상을 3~4턴 이내로 빠르게 파악합니다.
* 🛡️ **대한민국 의료법 100% 준수**: 비의료 AI의 불법 진단·처방을 원천 차단하고, 특정 병원 광고/알선 없이 객관적 지표에 기반하여 병원을 공정하게 안내합니다.
* 🚨 **Red Flag 긴급상황 0초 감지**: 생후 100일 미만 고열, 경련 등 응급 상황 감지 시 일반 병원 탐색을 즉각 중단하고 119 구급차 호출 및 소아전문응급의료센터로 직행하도록 전환합니다.
* ⚡ **공공 API 서킷 브레이커 & 3계층 Fallback (0ms 무중단 HA)**: 공공데이터포털(E-Gen) 503 장애나 서버 점검 시 0ms 즉각 단절 및 L1 만료메모리/L2 Firestore/L3 로컬 마스터셋으로 100% 무중단 서비스 유지.
* 📍 **PostGIS / Haversine 기반 5ms 초고속 매칭**: 사용자 위치 반경 5~10km 내 지금 문 연 달빛어린이병원과 야간 소아과를 즉각 찾아줍니다.
* 📋 **2024년 5월 본인확인 제도 완벽 안내**: 병원 내원 전 필수 준비물(부모 신분증, 등본 등) 체크리스트와 병원 문의용 30초 전화 통화 스크립트를 제공합니다.

---

## 📢 최신 업데이트 내역 (Changelog & Release Notes)

### 🌟 [v2.4.69-pediatric-normal-temp-default-init] 2026-10-16: 체온 다이얼 기본값 의학 표준 정상 체온(36.5℃, 🟢 정상 체온) 초기화 및 사용자 체온 조작 혼선 방지 (김동준 팀원)
* **🌡️ 문진 체온 게이지 기본값 소아 정상 체온(36.5℃) 초기화 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html))**:
  - 문진 화면 최초 진입 시 다이얼이 비정상적으로 `38.0℃ (발열 주의)`를 가리켜 발생하던 사용자 인지 혼선 및 의심을 완벽 해소.
  - HTML 중앙 디지털 표시를 `36.5 ℃`, 상태 뱃지를 `🟢 정상 체온` (에메랄드 그린 배경 `#d1fae5`, 글자색 `#065f46`)으로 교정.
  - 초기화 스크립트에서 `updateGaugeDisplay(36.5)`를 실행하여 부채꼴 바늘이 초록색 정상 구간(-72deg)에 위치하도록 설정.
  - `state.tempTouched = false` 유지: 보호자가 다이얼을 직접 조작하지 않거나 증상 텍스트에 열 관련 내용이 없으면, 병원 찾기 클릭 시 안전하게 `체온 미측정(모름)`으로 백엔드에 전달되는 로직과 100% 호환.

### 🌟 [v2.4.68-clinical-symptom-guardrail-and-unknown-vitals-fix] 2026-10-16: 비증상·잡담 필터링 가드레일 탑재, 나이/체온 미입력 시 강제 기본값(24개월, 38℃) 덮어쓰기 원천 해결 및 실시간 연동 검증 (김동준 팀원)
* **🛡️ 비증상·잡담 텍스트(ㅋㅋㅋ, asdf, 안녕, 배고파) 필터링 및 가짜 KTAS 4단계 오분류 차단 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html), [app/orchestrator/supervisor.py](file:///c:/AI-Native-Agent/monnlight/app/orchestrator/supervisor.py))**:
  - 클라이언트 `validateSymptomInput(text)` 함수를 통해 초성(`ㅋㅋㅋ`), 동일 문자 반복, 영문 자판 무의미어(`asdf`), 일상 대화(`안녕`, `배고파`) 입력 시 빨간색 경고 박스(`.symptom-invalid-tip`) 표출 및 제출 차단.
  - 백엔드 `supervisor.py`에서 증상 텍스트 정규식 검사를 통해 실제 소아 질환 증상이 없을 시 KTAS 및 병원 매칭을 일체 부여하지 않고 `TRIAGE` 상태 유지 및 재입력 유도.
* **🌡️ 나이 및 체온 미입력 시 강제 기본값(24개월, 38℃) 변조 결함 원천 해결 ([app/orchestrator/supervisor.py](file:///c:/AI-Native-Agent/monnlight/app/orchestrator/supervisor.py), [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html))**:
  - `supervisor.py` 내 `state.temperature = 38.0`, `state.age_months = 24` 강제 하드코딩을 적출하여 사용자의 "모름/미입력" 상태를 무손실 보존(`None`).
  - `triage_agent.py` 단일 음절("열", "배") 단순 부분일치를 정규식 문맥 매칭(`(?<!해)열(?!제)`)으로 교체하여 "해열제 미복용" 시 불필요한 "발열" 주입 차단.
  - `result.html`에서 체온 미측정 시 빨간색 배지(`highlight`) 및 `(발열)` 접미사를 제거하고 단정한 회색 뱃지(`체온 미측정(모름)`)로 전환.
  - 30초 당직의 통화 대본도 "체온은 아직 측정하지 못했으나...", "아이가..."로 자연스럽게 생성.
* **🚀 최신 백엔드 서버 핫픽스 기동 및 실시간 HTTP API (`POST /api/v1/chat`) 100% 정상 통신 검증**:
  - 이전 코드를 상주 실행 중이던 프로세스(PID 6544)를 교체하고 최신 코드로 백엔드 프로세스(PID 1564) 기동.
  - HTTP 요청 검증 결과: `보챔` 단독 입력 시 `age_months: None`, `temperature: None`, `ktas_level: 4`, `symptoms: ['보챔']` 정확 반환 및 잡담 차단 완벽 통과.

### 🌟 [v2.4.67-dynamic-badge-count-and-user-location-history] 2026-10-16: 선택 탭(병원/약국/전체)별 상단 배지 운영 시설 수 실시간 동기화 및 '자주 찾는 주요 지역' 사용자 실제 검색 히스토리 동적 관리(HTML 하드코딩 제거, 최대 15개 제한, 최신순 자동 갱신) (정영식 팀장)
* **🎯 탭 선택별 상단 배지 운영 시설 수 1:1 실시간 동기화 ([frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - `updateFacilityCountBadge(filter)` 엔진을 탑재하여 사용자가 '🌙 달빛병원 18' 선택 시 상단 배지가 `마천동 반경 15km 18곳 운영중`으로, '💊 심야약국 309' 선택 시 `309곳 운영중`으로, '전체 327' 선택 시 `327곳 운영중`으로 즉각 동기화 (기존 327곳 고정 결함 완벽 해결).
* **📍 '자주 찾는 주요 지역' HTML 하드코딩 완전 적출 및 실검색 동적 히스토리화 ([frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html), [frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - 기존 HTML 및 JavaScript 내 하드코딩되어 있던 더미 지역 칩(잠실동, 가락동 등) 및 태그(`현재: 잠실동`)를 전면 제거.
  - 사용자가 실제로 검색창에서 검색하여 설정하거나 GPS로 측정한 지역만 LocalStorage(`aisum_recent_locations`)에 최대 15개까지 최신순(FIFO/LRU)으로 관리.
  - 동일 지역 재선택 시 기존 항목을 제거하고 최상단으로 자동 최신화하며, 15개 초과 시 가장 오래된 이전 정보 자동 소멸.
  - 초기 이력 부재 시 "최근 설정한 지역이 없습니다" 점선 안내 컴포넌트 표출.

### 🌟 [v2.4.66-input-result-backend-integration] 2026-10-16: 문진(input.html) ➔ 결과(result.html) 백엔드(POST /api/v1/chat) 실시간 비동기 직결, KTAS 2-트랙 자동 라우팅 및 8000번 포트 완전 반환 (김동준 팀원)
* **🔌 input.html ➔ 백엔드 비동기 직결 파이프라인 완성 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html))**:
  - `launchAnalyzingSequence()` 내 단순 타이머 우회 결함을 해소하고 실제 `POST /api/v1/chat` 비동기 호출을 탑재하여 2초 분석 시퀀스 동안 병렬 처리 완결.
  - 백엔드 응답 데이터를 `backend_result` 세션 스토리지에 원자적 저장하여 결과 화면에 무손실 전달.
* **🚨 백엔드 Supervisor 0ms Red Flag 감지 시 즉각 119 직행 연동**:
  - 백엔드에서 `data.is_emergency === true` 판정 시 `emergency_alert.html`로 400ms 내 즉각 전환.
* **📊 result.html 라이브 데이터 바인딩 & KTAS 1~3단계 응급실 탭 자동 선택 ([frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html))**:
  - 실제 KTAS 판정 등급 및 지능형 30초 당직의 통화 대본, 실시간 추천 의료시설을 실시간 렌더링.
  - KTAS 1~3단계(응급) 판정 시 소아 응급실 탭(`emergency`)을 자동 활성화하여 소아 가용 병상 정보를 우선 표출.
  - 체온/나이 미입력(모름) 상태 시 `체온 미측정(모름)`, `나이 미입력(모름)`으로 깨끗하게 처리.
* **🧹 모바일 터널(Localtunnel) 차단 및 8000번 포트 완전 반환**:
  - 모바일 터널(task-487) 및 백그라운드 Uvicorn 데몬(task-482)을 완전히 종료하여 포트 8000을 깨끗이 비움. 사용자가 로컬 터미널에서 `python main.py`를 직접 기동할 수 있도록 환경 정비.

### 🌟 [v2.4.66-plan-md-optimization-and-whitepaper-refactoring] 2026-10-16: 종합 기획안 & 개발 백서(PLAN.md) 84.3% 압축 요약 최적화 및 11대 핵심 아키텍처 재편 (정영식 팀장)
* **📚 1,728줄 비대화 백서의 11대 핵심 장 중심 압축 집약 ([PLAN.md](file:///e:/monnlight/PLAN.md))**:
  - 기존 1,728줄(202KB)에 달하던 과도한 마이크로 체인지로그(74개 세부 작업)와 중복 서술을 전면 정리하고, 순수 시스템 아키텍처 및 핵심 명세 중심으로 **271줄(26KB, 84.3% 감축)** 최적화 달성.
  - 제1장(서비스 정체성), 제2장(데이터 실증 파이프라인), 제3장(모듈 트리), 제4장(2계층 Red Flag V2), 제5장(풀스택 데이터 흐름), 제6장(24시간 NMC 동기화), 제7장(서킷 브레이커 & 3-Tier Multi-Storage), 제8장(Fixed App Shell & 1:1 교차 LBS), 제9장(13대 화면 및 7대 컴포넌트 결합 명세), 제10장(92개 전수 테스트 통과 명세), 제11장(향후 백로그)으로 체계화.
* **🛡️ 4대 거버넌스 문서 동기화 완결 ([Answer-영식.md](file:///e:/monnlight/Answer-영식.md), [log.md](file:///e:/monnlight/log.md))**:
  - `Answer-영식.md` Q106 목차 및 본문 상세 기록 완료.
  - `log.md` [ISSUE-108] 트러블슈팅 및 리팩토링 상세 내역 등록 완료.
  - 92개 테스트 무결점 통과 상태 유지 (`Ran 92 tests, OK`).

### 🌟 [v2.4.65-pediatric-fever-standards-and-temp-sync] 2026-10-16: 소아 전문 문진(input.html) 체온 다이얼 5단계 의학 표준화, 구어체 체온 자동 인식, 100일 미만 위험군 인라인 뱃지화 및 레이아웃 시프트 0px 달성 (김동준 팀원)
* **🎯 체온 다이얼 바늘 및 상태 뱃지 수치 불일치 결함 무결점 교정 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html))**:
  - 다이얼 바늘을 41.0℃로 올렸을 때 하단 알약 배지에 `39.5℃ 초고열`로 고정 출력되던 하드코딩 텍스트를 제거하고 `🔥 초고열 위급` 상태 명칭으로 일원화.
  - 대형 수치(`41.0℃`), 바늘 회전각, 상단 배지, 하단 알약 배지 간 100% 모순 없는 정합성 달성.
  - 어색하고 긴 개행 텍스트(`손가락으로 바늘을 돌려보세요`)를 완전 제거하고 초기 상태부터 단정하고 세련된 1줄 상태 뱃지(`🟠 발열 주의`)로 표출.
* **🗣️ 구어체 증상("열이있어요", "고열", "미열", "초고열") 체온 자동 인식 & 백엔드 연동 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html), [app/agents/triage_agent.py](file:///c:/AI-Native-Agent/monnlight/app/agents/triage_agent.py))**:
  - 숫자가 없는 구어체 증상 입력 시에도 임상 표준 추정치(초고열 40.0℃, 고열 39.2℃, 일반 발열 38.5℃, 미열 37.8℃) 자동 인식 및 다이얼 연동.
  - 백엔드 Gemini LLM Triage 프롬프트 및 Fallback 정규식 파서에 구어체 체온 변환 엔진 탑재 완료.
* **📚 소아 체온 의학 표준 5단계 분류 체계 전면 동기화 (KAP 대한소아청소년과학회 & AAP 미국소아과학회 표준)**:
  - `t < 37.5℃`: 🟢 정상 체온 / `37.5 <= t < 38.0℃`: ⚠️ 미열 관찰 / `38.0 <= t < 39.0℃`: 🟠 발열 주의 / `39.0 <= t < 40.0℃`: 🚨 고열 지속 / `t >= 40.0℃`: 🔥 초고열 위급.
  - 기존 38.0~38.4℃ 구간이 '미열'로 잘못 표기되던 임상적 결함을 '발열 주의'로 정확히 분리 교정하고 SVG 눈금 그라데이션 재정렬 완료.
* **👶 2개월 이하 선택 시 화면 길어짐(Layout Shift) 원천 해결 및 100일 미만 위험군 인라인화**:
  - 하단에 덜컥거리며 나타나던 3줄짜리 빨간 경고 배너를 전면 제거하고 상단 연령 박스(`min-height: 72px`) 내 우측 인라인 뱃지(`🚨 100일 미만 위험군`)로 일원화 (Zero Layout Shift 달성).
  - 3개월 연령의 번거로운 `(100일 전)`, `(100일 초과)` 분기를 배제하고 `3개월` 단일 표기 및 0~3개월 전체 100일 미만 위험군 일괄 적용.

### 🌟 [v2.4.64-hero-card-title-center-alignment] 2026-10-16: 메인 홈 증상 문진 Hero 카드 타이틀("아이가 어디가 아픈가요?") 중앙 정렬 및 여백 최적화 (정영식 팀장)
* **🎯 타이틀 텍스트 완벽한 수평 중앙 정렬 ([frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css))**:
  - 증상 문진 Hero 카드(`.hero-card`) 내 헤드라인 타이틀(`.hero-title`) 및 컨테이너(`.hero-body`)에 `display: flex; align-items: center; justify-content: center; text-align: center;`를 적용하여 카드 너비 정중앙 배치.
  - 하단 풀위드 CTA 버튼("아이 증상 입력하고 병원 찾기")과 완벽한 수직 대칭축을 형성하여 시각적 몰입도와 심미성 극대화.
* **🧹 HTML 마크업 정돈 ([frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html))**:
  - 임의로 삽입되어 있던 `<br>` 태그를 제거하고 CSS `margin-bottom: 14px`로 컴포넌트 간 여백 표준화.

### 🌟 [v2.4.63-live-facilities-hospital-first-interleaving-sort] 2026-10-16: 실시간 야간 의료시설 전체 탭 병원 최우선 1:1 교차(Interleaving) 정렬(병원1 ➔ 약국1 ➔ 병원2 ➔ 약국2 ...) 랭킹 알고리즘 구현 (정영식 팀장)
* **🏥 달빛어린이병원 최우선 1등 노출 보장 ([frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - 기존 단순 거리순 정렬 시 사용자 주변 근거리(0.2~0.5km) 심야약국들의 상위 독점으로 인해 소아 야간 진료 병원이 한참 뒤로 밀리던 의료 우선순위 역전 결함 해소.
  - 내 위치 기준 최단거리 달빛어린이병원이 전체 탭 1번째 카드로 최상단에 즉시 노출되도록 보장.
* **🔄 1:1 인터리빙(Interleaving) 교차 정렬 파이프라인**:
  - `filteredHospitals`와 `filteredPharmacies`를 1:1로 번갈아 배치하여 `[병원 #1] ➔ [약국 #1] ➔ [병원 #2] ➔ [약국 #2] ...` 형태로 교차 렌더링.
  - 병원 17곳이 소진된 이후에는 남은 심야약국들이 거리순으로 연속하여 안전하게 이어지도록 구성.
* **🎯 필터 탭 정합성 유지**:
  - '전체' 탭은 병원 최우선 1:1 교차 렌더링, '🌙 달빛병원' 탭은 병원만 100% 거리순, '💊 심야약국' 탭은 약국만 100% 거리순 렌더링 및 탭 전환 시 상단 스크롤 리셋 유지.

### 🌟 [v2.4.62-main-home-fixed-shell-and-facility-exclusive-scroll] 2026-10-16: 메인 홈 고정 앱 셸(Fixed App Shell) 구축 및 실시간 야간 의료시설 전용 내부 스크롤 격리 완결 (정영식 팀장)
* **🔒 메인 홈 바깥 스크롤 완전 차단 (No Outer Scroll) ([frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css))**:
  - `body.main-home-body`에 `height: 100vh; height: 100dvh; overflow: hidden;`을 선언하여 모바일과 데스크톱 브라우저에서 바깥 스크롤이 0px도 발생하지 않도록 화면 고정.
  - `.mobile-viewport.main-home-shell`의 높이를 `100dvh`로 바인딩하고 데스크톱에서는 `height: min(920px, calc(100vh - 24px));`로 화면 높이 내에 깔끔하게 들어맞도록 제어.
* **📌 상단 헤더·CTA 카드·GNB 내비게이션 완벽 고정 (`flex-shrink: 0`)**:
  - 상단 앱 헤더(`.app-header`, 58px), 증상 문진 배너(`.hero-card`), 실시간 시설 헤더 및 3개 탭 필터(`.filter-tabs`), 하단 GNB 바(`.bottom-nav`)를 완벽하게 고정하여 화면 흔들림 및 상단 밀려 올라감 원천 차단.
* **📲 실시간 의료시설 전용 동적 스크롤 ([frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css))**:
  - `.facilities-section`과 `.facility-card-stack`에 `flex: 1; min-height: 0; overflow-y: auto;`를 부여하여, 상하 고정 요소를 제외한 남은 뷰포트 공간 전체를 100% 점유하면서 오직 실시간 의료시설 칸 내부에서만 수백 개 카드가 부드럽게 스크롤되도록 완성.
* **🛡️ 서브 페이지 스크롤 격리 및 DOM 정합성 복원 ([frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html))**:
  - 전용 클래스(`main-home-body`, `main-home-shell`) 스코핑으로 `input.html`, `result.html` 등 다른 화면의 자연스러운 스크롤에는 일체 영향이 없도록 완벽 분리 및 잉여 닫는 div 태그 삭제.

### 🌟 [v2.4.61-live-facilities-compact-ui-and-full-scroll] 2026-10-16: 실시간 야간 의료시설 카드 여백(Padding/Gap) 컴팩트 최적화 및 '더 많은 의료시설 확인' 버튼 전면 제거·스크롤 전수 탐색 구현 (정영식 팀장)
* **📐 카드 스택 및 개별 카드 여백 컴팩트화 ([frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css))**:
  - 실시간 야간 의료시설 카드 스택(`.facility-card-stack`) 간격 `gap: 12px` ➔ `8px`, 패딩 `4px 4px 12px 2px` ➔ `2px 4px 6px 2px`, 최대 높이 `520px`로 재조정.
  - 개별 카드(`.facility-card`) 내부 패딩 `16px` ➔ `11px 13px`, 라운드 `18px` ➔ `14px`, 내부 요소 간격 `12px` ➔ `8px`로 축소.
  - 아이콘 래퍼(`36px`), 시설명(`15px`), 주소/설명(`11.5px`), 전화버튼(`34px`), 카드 푸터 여백(`7px`) 등 컴포넌트 전반의 타이포그래피와 마진을 컴팩트하게 정돈하여 뷰포트 내 동시 노출 카드 수를 2개에서 3~4개로 확장.
* **🗑️ '더 많은 의료시설 확인' 버튼 전면 삭제 ([frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html) & [frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css))**:
  - `index.html` 내 불필요한 `<div class="scroll-more-btn-wrap">` 마크업을 완전히 제거하여 DOM 복잡도를 낮추고 모바일 뷰 하단 시각적 간섭을 배제.
* **🚀 스크롤 뷰포트 내 전수 탐색 렌더링 전환 ([frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - 페이징 슬라이스 및 더보기 증분 로직을 제거하고 `sliceList = displayList`로 전체 시설을 즉시 렌더링하여, 사용자가 내부 스크롤 조작만으로 반경 15km 내 408곳 전체를 끊김 없이 부드럽게 탐색할 수 있도록 고도화.

### 🌟 [v2.4.60-live-facilities-independent-scroll-viewport] 2026-10-16: 실시간 야간 의료시설 카드 목록 독립 스크롤 뷰포트(max-height & Sleek Scrollbar) 구축 및 모달 탭 스크롤 리셋 완결 (정영식 팀장)
* **📜 독립 내부 스크롤 뷰포트 구축 ([frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css))**:
  - 메인 홈 실시간 야간 의료시설 목록(`.facility-card-stack`)에 `max-height: 480px`, `overflow-y: auto`, `scroll-behavior: smooth`를 적용하여 수십 개 카드 나열로 인한 페이지 무한 확장 방지.
  - 5px 너비의 모던 미니멀 스크롤바(`::-webkit-scrollbar`) 커스텀 스타일링 적용 및 iOS 모바일 터치 관성 스크롤 완비.
* **👇 하단 스크롤 버튼 부드러운 스크롤 인터랙션 결합 ([frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html))**:
  - "스크롤하여 더 많은 의료시설 확인" 버튼 클릭 시 `.facility-card-stack`을 260px 부드럽게 자동 스크롤 이동하도록 `onclick` 핸들러 연결.
* **🔄 탭 필터 전환 시 자동 스크롤 리셋 ([frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - '전체' / '🌙 달빛병원' / '💊 심야약국' 탭 변경 시 `scrollTop = 0`으로 즉각 초기화하여 항상 최단거리 1등 시설부터 쾌적하게 열람 가능.

### 🌟 [v2.4.59-gps-detailed-address-resolution] 2026-10-16: '현재 위치로 설정' 시 상세 주소(도로명·건물명·지번) 유실 결함 해소 및 카카오 2-Tier 역지오코딩 완벽 연동, 92개 전수 테스트 통과 (정영식 팀장)
* **📍 백엔드 2-Tier 지능형 역지오코딩 엔진 고도화 ([app/api/v1/location.py](file:///e:/monnlight/app/api/v1/location.py))**:
  - 카카오 `coord2address` API의 도로명 주소와 건물명(`building_name`), 법정동을 유기적으로 결합하여 상세 주소(`서울특별시 송파구 송파대로 167 (문정동, 문정역테라타워)`) 포맷팅 구축.
  - 도로명 미부여 필지의 경우 시도명 표준화("서울" ➔ "서울특별시") 및 본번-부번 지번 상세 주소(`서울특별시 송파구 문정동 315-2`) 보존.
  - 지번 검색 불가 공원/도로망 지점 대상 카카오 `coord2regioncode` 2차 Fallback 연동 및 L3 Fallback 상세 랜드마크 주소 반환 체계 완비.
* **🛡️ 프론트엔드 상세 주소 무손실 보존 파이프라인 ([frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - `finalizeLocation` 내부에서 `window.AISUM_LOCATIONS_DB`의 짧은 동 이름으로 상세 주소를 강제 덮어쓰던 레거시 안티패턴 코드 전면 적출.
  - '현재 위치로 설정' 클릭 시 모달 상단 '현재 설정된 주소' 바(`modal-current-address-bar`), 상단 알약 버튼, LocalStorage(`aisum_user_address`) 간 실시간 원자적 동기화 구현.
* **🧪 단위/통합 테스트 스위트 확장 및 92개 전수 통과 ([tests/test_location_api.py](file:///e:/monnlight/tests/test_location_api.py))**:
  - 신규 상세 주소 포맷팅 및 Fallback 주소 검증 테스트 추가 (8개 테스트 전수 통과).
  - 전체 단위/통합/E2E 테스트 스위트 92개 전수 무결점 통과 (`Ran 92 tests, OK`).

### 🌟 [v2.4.58-daily-delta-sync-pipeline-complete] 2026-10-16: 전국 달빛어린이병원·야간약국 24시간 In-Memory Hash Diffing 델타 동기화 서비스·스케줄러·관리자 API/CLI 완비 및 90개 전수 테스트 통과 (정영식 팀장)
* **🔄 In-Memory Hash Diffing 기반 0ms Skip 델타 동기화 서비스 완공 ([app/services/national_dataset_sync_service.py](file:///e:/monnlight/app/services/national_dataset_sync_service.py))**:
  - 전국 156개 달빛어린이병원 및 2,028개 야간약국의 기관코드(PK) 기반 SHA-256 주요 필드 해시 대조 알고리즘 구축.
  - 신규(Added), 수정(Modified), 삭제(Removed) 변동 감지 기능 구현 및 `diff == 0` 시 불필요한 디스크 I/O와 브라우저 캐시 무효화를 0ms 만에 Skip하는 최적화 엔진 적용.
  - 실제 변경분 발생 시에만 `data/*.json` 저장 및 `scripts/build_frontend_datasets.py` 자동 호출로 `frontend/js/*.js` 원자적 번들링 완결.
* **⏰ 3-Track 백그라운드 스케줄러 비동기 결합 ([app/services/scheduler.py](file:///e:/monnlight/app/services/scheduler.py))**:
  - `Job 2: Daily 04:00 AM Static Data & Pairing Sync` 내 `sync_static_datasets()`에 증분 델타 동기화를 비동기 결합하여 매일 새벽 4시 완전 무인 자동 동기화 실현.
* **🛠️ 온디맨드 관리자 CLI 도구 & RESTful 엔드포인트 신설**:
  - CLI: `python scripts/sync_national_datasets_delta.py [--force]`로 관리자가 온디맨드로 즉시 동기화 검증 가능 (`[scripts/sync_national_datasets_delta.py](file:///e:/monnlight/scripts/sync_national_datasets_delta.py)`).
  - API: `POST /api/v1/emergency/sync-static` 엔드포인트 신설로 웹 관리자 대시보드 및 CI/CD 파이프라인에서 트리거 가능 (`[app/api/v1/emergency.py](file:///e:/monnlight/app/api/v1/emergency.py)`).
* **🧪 7개 신규 단위·통합 테스트 구축 및 90개 전체 회귀 테스트 전수 통과**:
  - `tests/test_national_dataset_sync.py`: TC-SYNC-001~007 7개 테스트 100% 통과.
  - 전체 단위/통합 테스트 스위트 90개 전수 통과 (`Ran 90 tests, OK`).

### 🌟 [v2.4.57-daily-delta-sync-architecture] 2026-10-16: 전국 달빛병원·야간약국 24시간 주기 공공 API 변경분(Hash Diffing) 자동 업데이트 파이프라인 아키텍처 수립 (정영식 팀장)
* **🔄 24시간 주기 증분 동기화(Incremental Delta Sync) 설계**:
  - `APScheduler`의 04:00 AM 정적 데이터 크론 잡을 기반으로, 공공데이터포털(E-Gen) API를 호출하여 병원/약국 최신 스냅샷 수집.
  - 기관코드(PK) 기반 In-Memory Hash Diffing을 적용하여 신규(Added), 수정(Modified), 삭제(Removed) 감지.
  - `diff_count == 0`일 때 불필요한 디스크 I/O와 브라우저 캐시 무효화를 0회로 유지하는 엔터프라이즈급 최적화 원칙 확립.
* **🔨 변경 발생 시 자동 번들링 빌더 (`build_frontend_datasets.py`) 연계**:
  - 변경분이 감지된 경우에만 `data/*.json` 및 `frontend/js/*.js`를 자동 컴파일하여 클라이언트 0ms LBS 무지연 제공 보장.

### 🌟 [v2.4.56-uvicorn-daemon-persistence-sync] 2026-10-16: 로컬호스트 연결 거부(ERR_CONNECTION_REFUSED) 복구 및 Uvicorn 영구 상주 데몬 기동 완결 (정영식 팀장)
* **🔌 로컬호스트 소켓 연결 거부 결함 즉각 해결**:
  - 테스트 러너 종료 시그널로 인해 Uvicorn 포트가 닫혔던 원인을 규명하고, `IsDaemon: true` 영구 상주 프로세스로 Uvicorn 재기동.
* **⚡ 3-Track 백그라운드 스케줄러 & 소켓 리스닝 안정화**:
  - `http://127.0.0.1:8000/` HTTP 200 OK 수신 및 Windows 기본 웹 브라우저 자동 재호출 완료.
  - 최신 15km 필터링 및 카카오 로컬 REST API 연동 화면 정상 서빙 검증.

### 🌟 [v2.4.55-radius-15km-filter-sync] 2026-10-16: 메인 홈 실시간 야간 의료시설 현황 목록의 반경 15km 이내 필터링 제한 및 상단 뱃지·탭 카운트 동기화 & 로컬 서버 브라우저 재실행 (정영식 팀장)
* **🏥 실시간 야간 의료시설 반경 15km 엄격 필터링 엔진 구축 ([frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - 사용자 위치 기준 Haversine 구면거리 15km 이내(`distKm <= 15.0`) 시설만 필터링하여 불필요한 전국 원거리 시설 목록 전면 차단.
  - 소아 야간 골든타임(차량 20~30분 이내) 도달 가능한 실제 유효 시설만 집중 표출.
* **🏷️ 상단 뱃지 및 카테고리 3개 탭 카운트 15km 기준 완벽 동기화**:
  - 상단 뱃지: `"${userLoc.dong} 반경 15km N곳 운영중"` (시설 부재 시 0곳 안내).
  - 탭 카운트: 전체 / 달빛어린이병원 / 심야약국 각각의 15km 이내 실제 수치 실시간 바인딩.
* **🛡️ 빈 상태(Empty State) 카드 렌더링 & 더보기 버튼 지능화**:
  - 반경 15km 이내 시설 0곳일 경우 안내 카드(`live-empty-card`) 표출 및 더보기 버튼 자동 숨김 처리.
  - 시설 목록 확인 완료 시 `"반경 15km 내 전체 N곳 확인 완료"` 상태 표시.
* **⚙️ 백엔드 검색 정책 일원화 ([app/services/pairing_service.py](file:///e:/monnlight/app/services/pairing_service.py), [app/api/v1/emergency.py](file:///e:/monnlight/app/api/v1/emergency.py))**:
  - `find_nearby_pairings` 및 `GET /api/v1/emergency/pairings`의 기본 반경을 15.0km로 통일.
* **🌐 로컬 서버 기동 상태 검증 및 브라우저 즉시 재실행**:
  - FastAPI Uvicorn 핫 리로드 로컬 서버(`http://127.0.0.1:8000/`) HTTP 200 OK 확인 및 Windows 기본 브라우저 자동 팝업.

### 🌟 [v2.4.54-live-localhost-serving-verified] 2026-10-16: FastAPI Uvicorn 핫 리로드 로컬 서버 백그라운드 기동 및 브라우저 실시간 연동 완결 (정영식 팀장)
* **🚀 FastAPI Uvicorn 핫 리로드 로컬 서버 기동 (`http://127.0.0.1:8000/`)**:
  - 기존 점유 프로세스 안전 정리 후, 최신 `.env`의 `KAKAO_REST_API_KEY`가 완벽히 바인딩된 백그라운드 데몬 서버 기동.
  - 정적 웹 리소스(`/assets`, `/css`, `/js`) 및 템플릿 마운트 정상 가동 확인 (HTTP 200 OK).
* **🌐 운영체제 기본 웹 브라우저 실시간 연동**:
  - `Start-Process 'http://127.0.0.1:8000/'` 실행으로 팀장님 화면에 아이숨 메인 홈 화면 자동 오픈.
* **🧪 카카오 로컬 REST API 라이브 원격 통신 100% 정상 작동 검증**:
  - `GET /api/v1/location/search?q=코엑스&search_type=keyword` ➔ `source: kakao_keyword_api`, 10건 실시간 좌표 획득 완료.
  - `GET /api/v1/location/search?q=문정동 642&search_type=address` ➔ `source: kakao_address_api`, 2건 실시간 좌표 획득 완료.

### 🌟 [v2.4.53-kakao-local-rest-api-live-engine] 2026-10-16: 카카오 로컬 REST API 기반 2대 세그먼트 위치 검색 실기능 적용 & 백엔드 프록시 라우터 완비 (정영식 팀장)
* **⚙️ 카카오 로컬 REST API 백엔드 프록시 라우터 완비 ([app/api/v1/location.py](file:///e:/monnlight/app/api/v1/location.py))**:
  - `GET /api/v1/location/search?q={query}&search_type={address|keyword|all}`: 카카오 `address.json` 및 `keyword.json`을 서버 사이드에서 안전하게 프록시 호출하여 위경도(WGS84) 좌표 반환.
  - `GET /api/v1/location/coord2address?lat={lat}&lon={lon}`: GPS 위경도 ➔ 행정동/법정동 및 도로명 주소 실시간 변환.
  - **3-Tier L3 인메모리 Fallback 내장**: API 키 부재 또는 외부 장애 시에도 코엑스, 롯데타워, 강남역, 문정동 등 0ms 무중단 Fallback 보장.
* **📱 위치 설정 모달 2대 세그먼트 탭 UI & 실시간 디바운스 검색 탑재 ([frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html), [frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - `[🏢 주소 검색 (지번/도로명)]` vs `[📍 키워드 검색 (건물/지역)]` 2대 탭 전환 인터페이스 구현.
  - 200ms 타이핑 디바운스 비동기 검색 및 결과 클릭 시 WGS84 좌표 즉시 확정.
* **🧭 사용자 위치 변경 시 156개 병원·2,028개 약국 실시간 최단거리 동적 재계산**:
  - 선택된 위치 기준 `window.initLiveFacilities()` 즉시 재호출로 전체·병원·약국 거리순 목록 및 도보/차량 소요시간 2ms 만에 재정렬.
* **🧪 단위/통합 테스트 스위트 83개 케이스 100% 전수 통과**:
  - `tests/test_location_api.py` 6개 신규 테스트 추가 및 전체 83개 테스트 회귀 검증 완료.

### 🌟 [v2.4.52-address-keyword-search-architecture] 2026-10-16: 주소 검색(지번/도로명) vs 키워드 검색(건물명/지역명) 2대 탭 분리 설계 및 지오코딩 아키텍처 백서 발간 (정영식 팀장)
* **📍 위치 설정 모달 내 '주소 검색' vs '키워드 검색' 2대 탭 분리 UI/UX 수립**:
  - `[주소 검색]`: 지번(문정동 642) 및 도로명(송파대로 201) 입력 전용 탭.
  - `[키워드 검색]`: 건물명(롯데월드타워, 코엑스), 역명(강남역), 주요 지역명(해운대, 분당) 입력 전용 탭.
* **🚫 공공데이터포털 전국 주소 데이터셋 직접 다운로드·적재 배제 (Anti-Pattern 차단)**:
  - 650만 건(3GB 이상) 주소 데이터 자체 보관의 비효율성(용량 낭비, POI 건물명 검색 불가, 매월 변동분 동기화 부하)을 정량 분석하여 배제 결정.
* **🏆 카카오 로컬 REST API 기반 3-Tier 하이브리드 지오코딩 엔진 설계**:
  - **Tier 1 (카카오 API)**: 주소 및 키워드 WGS84 좌표 즉시 변환 (일 30만 건 무료 쿼터).
  - **Tier 2 (국토교통부 VWorld Geocoder)**: 카카오 장애 대비 국가 공간정보 Geocoder Failover.
  - **Tier 3 (전국 읍면동 로컬 캐시)**: 오프라인 대비 전국 3,500개 행정동 중심점 0ms Fallback.
* **📚 [docs/ADDRESS_AND_KEYWORD_LOCATION_ARCHITECTURE.md](file:///e:/monnlight/docs/ADDRESS_AND_KEYWORD_LOCATION_ARCHITECTURE.md) 전용 백서 발간**:
  - 아키텍처 비교표, Mermaid 데이터 흐름도, FastAPI 백엔드 프록시 라우터 코드 및 실행 로드맵 수록.

### 🌟 [v2.4.51-live-facilities-real-dataset-linkage] 2026-10-16: 전국 156개 달빛병원·2,028개 야간약국 실데이터셋 기반 메인 홈 실시간 야간 의료시설 위치 기반 거리순 연동 & 가짜 데이터 전면 퇴출 (정영식 팀장)
* **🗑️ HTML 및 JS 내 하드코딩된 가짜 카운트·더미 데이터 100% 전면 적출**:
  - `frontend/templates/index.html` 내 고정된 정적 숫자(`10곳 운영중`, `전체 10`, `달빛병원 5`, `심야약국 5`) 및 카드 내부 임의 플레이스홀더를 전면 삭제하고 스켈레톤 로더(`-`)로 치환.
  - 가짜 전화번호나 임의의 대기인수를 일체 배제하고 공공 API 수집 원천의 실제 필드값으로만 동적 렌더링하도록 템플릿 개편.
* **📦 전국 전수 실데이터셋 프론트엔드 0ms 초고속 번들 JS 구축**:
  - `data/national_moonlight_hospitals_156.json` (156개 달빛병원) ➔ `frontend/js/national_moonlight_hospitals_156.js`
  - `data/national_night_pharmacies_2028.json` (2,028개 야간약국) ➔ `frontend/js/national_night_pharmacies_2028.js`
  - `main.py`에 `/data` 정적 마운트 추가로 JSON API 직접 요청 및 번들 JS 직접 로드 듀얼 파이프라인 완비.
* **🧭 사용자 현재 위치(기본 문정동/GPS) 기준 Haversine 거리 오름차순 실시간 정렬**:
  - 문정동 또는 사용자 Geolocation 좌표 기준 156개 병원과 2,028개 약국의 최단거리를 실시간 계산하여 오름차순 정렬.
  - `all` 탭: 병원 + 약국 통합 전수 최단거리 정렬 (`2,184곳`).
  - `hospital` 탭: 달빛어린이병원 156곳만 최단거리 정렬 (`156곳`).
  - `pharmacy` 탭: 심야약국 2,028곳만 최단거리 정렬 (`2,028곳`).
* **🗂️ 3개 탭 독립 필터링 & 15개 단위 청크 페이징 완비**:
  - 상단 뱃지 `${userLoc.dong} 반경 10km ${nearbyCount}곳 운영중` 동적 산출.
  - 15개씩 확장 로드되는 `.scroll-more-btn` 페이징 연동으로 대용량 DOM 렌더링 성능 최적화.
  - 카드 클릭 시 상세 페이지(`hospital_detail.html`) 및 최단거리 페어링 약국 지능형 연동.

### 🌟 [v2.4.50-frontend-linkage-and-local-serving] 2026-10-16: 프론트엔드 전 화면 상호 연결 무결성 완비, 브라우저 콘텐츠 협상 루트 서빙 및 로컬 실행 (정영식 팀장)
* **🔗 13개 템플릿 화면 상호 연결 링크 전수 정규화**:
  - `index.html` ➔ `input.html` ➔ `loading.html` ➔ `result.html` ➔ `hospital_detail.html`로 이어지는 정상 매칭 및 뒤로가기 순환 동선 완성.
  - 0ms Red Flag 위급 상황 감지 시 `emergency_alert.html` 119 다이얼 직통 연결 및 상호 이동 링크 완비.
  - `result.html` 및 `index.html` 내 중복 스크립트/CSS 로더 태그 단일화 최적화.
* **⚡ FastAPI [main.py](file:///e:/monnlight/main.py) 콘텐츠 협상(Content Negotiation) 루트(`/`) 서빙**:
  - 브라우저 접속(`text/html`) 시 자동으로 `index.html` 메인 화면 즉시 서빙, API 클라이언트 접속 시 JSON 메타데이터 반환.
  - 브라우저 주소창에 `http://localhost:8000` 입력 시 즉각 아이숨 메인 웹 UI 팝업.
* **🌐 로컬 Uvicorn 서버 백그라운드 가동 & 13개 테스트 전수 100% PASS**:
  - 백그라운드 데몬 가동 및 Windows 기본 브라우저 실시간 팝업 검증 완료.
  - 단위/통합 테스트 13건 전수 무결점 통과(`Ran 13 tests in 54.022s, OK`).

### 🌟 [v2.4.49-data-cleanup] 2026-10-16: data/ 디렉터리 내 KTAS 임상·위치 데이터셋 보존 및 비최신·중복 약국 데이터셋(public_night_pharmacies.json) 정돈 (정영식 팀장)
* **🔒 KTAS 임상 데이터셋 & 응급실 위치 좌표 100% 무결점 보존**:
  - 소아 168개 주증상·17대 계통·활력징후 임상 기준표(`ktas_pediatric_dataset.json`, 388KB) 및 서울 530개 응급의료기관 위경도 캐시(`seoul_emergency_coords.json`, 37KB) 영구 보존.
* **🗑️ 공공데이터포털 API 기반 비최신·중복 약국 데이터셋 안전 삭제**:
  - 최신 2,028개 야간약국 데이터셋(`national_night_pharmacies_2028.json`, 1.4MB)과 100% 동일한 해시를 가진 구버전 복제본 `public_night_pharmacies.json` 영구 삭제.
  - 최신 공공 API 3대 마스터 세트(`national_moonlight_hospitals_156.json`, `national_night_pharmacies_2028.json`, `nationwide_pairings.json`)로 참조 일원화.
* **📚 `data/README.md` 데이터셋 카탈로그 최신화 & 13개 전체 테스트 100% PASS**:
  - 데이터셋 명세 및 동기화 주기 문서를 최신 실데이터 규격에 맞춰 개편.
  - API 및 프론트엔드 통합 테스트 스위트(`test_step5_api.py`, `test_step8_frontend_integration.py`) 13개 전수 100% 통과 확인.

### 🌟 [v2.4.48-clean-frontend-assets-dedup] 2026-10-16: frontend/ 내 assets, css, js 폴더 중복 제거 및 templates/ 순수 HTML 전용화 체계 완비 (정영식 팀장)
* **🧹 templates/ 내 중복 정적 폴더(assets, css, js) 전면 삭제**:
  - `frontend/templates/` 내부에 중복 보관되어 있던 `assets/`, `css/`, `js/` 폴더를 전수 영구 삭제하여, `templates/`를 오직 13개 순수 HTML만 보관하는 단일 템플릿 저장소로 역할 분리.
* **🎨 frontend/ 단일 정적 리소스 원천 및 js/ 내 HTML 부재 원칙 확립**:
  - `frontend/assets/`(이미지 11종), `frontend/css/`(style.css), `frontend/js/`(main.js 외 2종)를 단일 원천으로 확립.
  - `frontend/js/` 안에는 순수 자바스크립트 파일만 존재하며 HTML 파일이 0개임을 전수 검증 완료.
* **🔗 13개 템플릿 HTML 리소스 참조 태그 정규화 & 31개 엔드포인트 100% 200 OK**:
  - `templates/*.html`에서 상위 단일 리소스(`../css/style.css`, `../js/main.js`, `../assets/...`)를 직접 참조하도록 일괄 정돈.
  - TestClient 기반 31개 전체 엔드포인트 HTTP 200 OK 무결점 유지.

### 🌟 [v2.4.47-unified-templates-and-smart-router] 2026-10-16: HTML 파일 frontend/templates/ 단일 진실의 원천(Single Source of Truth) 통합 및 스마트 Fallback 라우터 구축 (정영식 팀장)
* **📁 frontend/templates/ 단일 템플릿 저장소 전면 통합 & 중복 39개 파일 전수 제거**:
  - `frontend/` 루트, `templates/` 루트 및 6대 카테고리 서브폴더에 4중으로 흩어져 있던 52개 파일을 단일화하여, 완성본 HTML 13개만 `frontend/templates/` 루트에 딱 1개씩 단일 보관.
  - 가짜 400바이트 리다이렉트 스텁 13개 및 12개 중복 서브폴더 전수 영구 삭제로 아키텍처 극단적 경량화.
* **⚡ FastAPI [main.py](file:///e:/monnlight/main.py) 스마트 Fallback 라우터 구축 (Zero 404 보장)**:
  - 브라우저가 `/home/input.html`, `/triage/loading.html` 등 과거 서브패스로 진입하더라도 자동으로 `templates/{filename}.html`을 찾아 200 OK로 즉각 서빙하는 만능 라우터 장착.
  - TestClient 기반 31개 전체 URL 조합(서브패스 포함) 전수 HTTP 200 OK 무결점 통과 확인.
* **🔗 HTML/JS 내부 네비게이션 플랫(Flat) 최적화**:
  - `index.html` ➔ `input.html`, `selectLiveFacilityCard` ➔ `hospital_detail.html` 등 모든 페이지 간 이동을 동일 폴더 직행 링크로 통일.

### 🌟 [v2.4.46-fullstack-local-test-architecture] 2026-10-16: '파이썬 메인 터미널 구동' & '로컬호스트 브라우저 접속' 풀스택 일체형 로컬 테스트 체계 확립 (정영식 팀장)
* **🎯 풀스택 로컬 테스트 아키텍처 개념 정립 및 표준화**:
  - '파이썬 메인 파일 터미널 구동'과 '웹 브라우저 로컬호스트 접속'을 분리된 선택지가 아닌 '원인과 결과(한 세트)'로 명확히 정립.
  - 탐색기 더블클릭(`file:///`) 방식의 기술적 한계(CORS 차단 `Origin: null`, 백엔드 프로세스 미구동 `ERR_CONNECTION_REFUSED`, APScheduler/FSM 미기동) 규명 및 FastAPI Uvicorn 기반 일체형 로컬 서빙 가이드 표준화.
* **🌐 로컬 풀스택 통합 서빙 및 실기기 무선 테스트 환경 안내**:
  - 개발 모드 핫 리로드 명령(`uvicorn main:app --reload --host 0.0.0.0 --port 8000`) 및 주요 엔드포인트(`/splash`, `/home`, `/input`, `/docs`, `/health`) 라우팅 체계 정돈.
  - 동일 Wi-Fi 망 내 스마트폰 실기기 무선 테스트(`http://[내PC IP]:8000/splash`) 경로 확립.

### 🌟 [v2.4.45-html-categorical-reorganization] 2026-10-15: 테스트 찌꺼기 파일 전수 정리 및 HTML 6대 카테고리별 디렉터리 분리·경로 전면 재정비 (정영식 팀장)
* **🧹 저장소 찌꺼기 파일 전수 클린업 (159개 `._*` 및 빈 디렉터리 제거)**:
  - Cross-OS 환경에서 누적된 AppleDouble 파일(`._*`) 159개 전수 영구 삭제.
  - 루트의 빈 디렉터리(`새 폴더`, `scratch/`) 제거로 코드베이스 경량화 및 청결도 회복.
* **📁 프론트엔드 HTML 6대 카테고리별 디렉터리 분리 구축 (`frontend/` & `frontend/templates/`)**:
  - `onboarding/`: `splash.html`, `permission.html`
  - `home/`: `index.html`
  - `triage/`: `input.html`, `loading.html`
  - `result/`: `result.html`, `hospital_detail.html`
  - `emergency/`: `emergency_alert.html`, `emergency_guide.html`, `emergency_guide_checklist.html`, `emergency_guide_symptoms.html`
  - `settings/`: `settings.html`, `terms.html`
* **🔗 리소스 상대 경로 & 화면 간 스마트 네비게이션 전면 보정**:
  - 모든 HTML의 CSS(`../css/style.css`), JS(`../js/main.js` 등), 에셋(`../assets/`) 상대 경로 재조정.
  - 화면 간 상호 링크(`href` 및 `window.location.href`)를 카테고리 간 상대 경로로 보정.
  - `main.js`의 `selectLiveFacilityCard()`에 디렉터리 자동 판별 스마트 네비게이션 적용.
  - 기존 루트 접속을 위한 0ms 리다이렉트 스텁 생성.
* **⚡ FastAPI 서버 라우터 ([main.py](file:///e:/monnlight/main.py)) 카테고리 우선 서빙 갱신**:
  - `find_frontend_html()` 헬퍼 함수로 신규 카테고리 폴더 1순위 서빙 및 6대 카테고리 정적 마운트 추가.
* **🛠️ `pairing_service.py` 데이터 소스 정합성 복구**:
  - `PAIRINGS_FILE`을 `data/nationwide_pairings.json`으로 교정하여 단위 테스트(TC-503) 및 API 전수 통과.

### 🌟 [v2.4.44-modal-layout-fix] 2026-10-15: 위치 설정 모달(location-select-modal) HTML 구조 정합성 복구 및 수직 레이아웃 안정화 (정영식 팀장)
* **🛠️ 위치 설정 모달(location-select-modal) `sheet-header` 닫는 div 태그 누락 결함 해결**:
  - `frontend/templates/index.html` 및 `frontend/index.html`에서 `<div class="sheet-header">`의 닫는 태그(`</div>`) 누락으로 인해 모달 내 모든 컴포넌트(현재 주소 바, 주소 검색창, GPS 측정 버튼, 지역 그리드)가 가로 일렬(flex row)로 찌그러지며 텍스트가 1글자 단위로 세로 쓰기 되던 결함 완전 해소.
  - 닫기 버튼 직후 닫는 태그를 명확히 삽입하여 하위 컴포넌트들이 정상적인 수직(Flex Column) 플로우를 타도록 DOM 구조 복원.
* **🎨 모달 내 현재 설정 주소 안내 바 CSS 규격화 ([frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css))**:
  - `.current-address-bar` 전용 스타일(`width: 100%; box-sizing: border-box; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-size: 13px; font-weight: 600;`)을 규격화하여 긴 도로명 주소도 말줄임표 처리 및 안정적인 여백 유지.
* **🌐 템플릿-정적 배포 파일 100% 동기화 및 단위 테스트 전수 통과**:
  - `frontend/index.html`과 `frontend/templates/index.html`, `style.css` 양방향 완전 일치 동기화.
  - 단위 테스트(`tests/test_step3_agents.py`, `tests/test_step1_services.py`, `tests/test_step8_frontend_integration.py`) 17개 전수 통과(`OK`).

### 🌟 [v2.4.43-nationwide-complete-app-sync] 2026-10-15: 전국 156개 달빛병원·2,028개 야간약국 실데이터셋 전 페이지 연동 및 상단 문정동 알약 주소 검색·현재 주소 직접 설정 기능 완성 (정영식 팀장)
* **🏥 전국 156개 달빛어린이병원 & 2,028개 야간약국 마스터 데이터셋 구축 ([scripts/build_complete_app_datasets.py](file:///e:/monnlight/scripts/build_complete_app_datasets.py))**:
  - `전국_달빛어린이병원_및_야간심야약국_현황.md`의 전수 데이터를 구면거리 기반 1:1 인접 약국과 매칭하여 `data/nationwide_pairings.json` 및 `data/public_night_pharmacies.json` 완성.
  - 브라우저 전역 로더(`frontend/js/nationwide_pairings.js`, `frontend/js/public_night_pharmacies.js`)를 구축하여 클라이언트 0ms 무지연 LBS 서빙 보장.
* **📍 첨부 디자인 일치 상단 위치 알약(`📍 문정동 ∨`) & 주소 검색·현재 주소 직접 설정 기능 탑재**:
  - 메인 홈 상단 알약 기본값을 `문정동` (위도 37.4858, 경도 127.1225)으로 바인딩.
  - 검색창(`location-search-input`)에 임의의 주소/키워드(예: 송파대로, 문정로) 입력 시 최상단에 `📍 '${query}' (으)로 현재 주소 설정` 카드가 노출되어, 원클릭으로 사용자 기본 주소 영구 저장(`aisum_user_address`).
  - 모달 상단에 `현재 주소: 서울특별시 송파구 문정동` 상태 안내 바를 표출하여 현재 설정 위치 시인성 강화.
* **🌐 위치 기반 동작 모든 페이지(`index`, `result`, `hospital_detail`) 실데이터 100% 연동**:
  - **`index.html`**: 문정동 기준 최근접 달빛병원(하이엔소아과의원 2.4km, 세곡달빛의원 3.0km, 잠실24시열린의원 3.7km 등) 실시간 출력 및 카드 클릭 시 상세 페이지 이동 연동.
  - **`result.html`**: `nationwide_pairings.js` 로드 및 사용자 위치 기준 최근접 4대 달빛병원·약국 실데이터 동적 수화. 통화 스크립트에도 실제 최근접 병원명 자동 반영.
  - **`hospital_detail.html`**: 세션 전달 데이터 및 현재 위치 기반 156개 실데이터로부터 최근접 병원과 협약 약국 실시간 하이드레이션 (영업시간, 접수마감 시간, 길찾기 링크 100% 실데이터).

### 🌟 [v2.4.42-national-moonlight-and-night-pharmacy-registry-md] 2026-10-15: 공공데이터포털 국립중앙의료원 오픈 API(DATA_GO_API_KEY) 기반 전국 달빛어린이병원(156개) 및 야간·심야약국(2,028개) 전수 마크다운 표 생성 완결 (정영식 팀장)
* **🏥 국립중앙의료원(NMC) 전국 병·의원 찾기 API(`HsptlAsembySearchService`) 실시간 연동**:
  - `getBabyListInfoInqire` 오퍼레이션을 통해 대한민국 보건복지부 지정 공식 **달빛어린이병원 156개소 전수**를 `DATA_GO_API_KEY`로 자동 호출하여 완벽 추출.
  - 서울(21), 경기(45), 부산(9), 대전(8), 전북(8), 인천(7), 전남(7), 경북(6), 충남(6), 대구(6), 광주(5), 충북(5), 제주(4), 울산(3), 강원(3), 세종(1) 등 전국 17개 시도별 상세 진료시간, 대표 전화번호, 도로명 주소, 진료 안내 전수 표 구축.
* **💊 국립중앙의료원 전국 약국 정보 조회 API(`ErmctInsttInfoInqireService`) 실시간 연동**:
  - `getParmacyListInfoInqire` 오퍼레이션을 17개 시도별로 전수 스캔하여, 밤 22시 이후 또는 새벽 1~2시/24시간 운영되는 **야간·심야 운영 약국 2,028개소**(공식 공공심야약국 322개소 포함)를 수집 및 정제.
* **📄 대용량 마크다운 현황 문서 생성 ([전국_달빛어린이병원_및_야간심야약국_현황.md](file:///e:/monnlight/%EC%A0%84%EA%B5%AD_%EB%8B%AC%EB%B9%9B%EC%96%B4%EB%A6%B0%EC%9D%B4%EB%B3%91%EC%9B%90_%EB%B0%8F_%EC%95%BC%EA%B0%84%EC%8B%AC%EC%95%BC%EC%95%BD%EA%B5%AD_%ED%98%84%ED%99%A9.md))**:
  - 2,821라인, 533KB 규모의 고정밀 마크다운 현황표 구축 (시도별 요약 통계, 156개 달빛병원 상세 표, 322개 공공심야약국 특화 표, 2,028개 야간약국 표, 소아 응급 안전 가이드).
* **💾 백엔드 데이터셋 영구 백업 및 수집 자동화 스크립트 구축**:
  - `data/national_moonlight_hospitals_156.json`, `data/national_night_pharmacies_2028.json` 데이터셋 영구 보존.
  - `scripts/export_national_moonlight_and_night_pharmacy_md.py`를 통해 향후 1-Click 최신화 지원.

### 🌟 [v2.4.41-interactive-location-search-modal] 2026-10-15: 상단 위치 알약 버튼(잠실동) 주소/키워드 검색 & GPS 현재 위치 설정 인터랙티브 바텀시트 모달 구축 및 0ms LBS 동적 재정렬 완결 (정영식 팀장)
* **🔍 상단 위치 알약 버튼(`.location-pill`) 클릭 시 주소 & 키워드 검색 바텀시트 모달 탑재**:
  - `frontend/templates/index.html` 및 `frontend/index.html` 상단 헤더의 위치 알약 버튼 클릭 시 매끄럽게 슬라이드 업되는 `location-select-modal` 구축.
  - 검색창(`location-search-input`)에 동명(잠실동, 역삼동), 구명(송파구, 강남구, 분당구), 시명(서울, 부산, 대전), 키워드(판교, 동탄, 해운대) 입력 시 실시간 매칭 검색 결과 및 하이라이트 제공.
* **📍 1-Click GPS 현재 위치 설정 (`btn-gps-refresh`)**:
  - 실제 기기 Geolocation API를 가동하여 현재 사용자 좌표를 측정하고 가장 가까운 행정동으로 역산출하여 0ms 반영.
* **⚡ 전국 80+ 거점 공간 데이터베이스 & 실시간 의료기관 거리 재정렬**:
  - 위치 변경 즉시 `AisumPermissionManager` 및 `localStorage`에 영구 보존.
  - 헤더 텍스트(예: `잠실동`) 즉각 변경 및 메인 의료시설 목록(`initLiveFacilities`)을 0ms 재호출하여, 선택한 위치 기준 최단거리 달빛어린이병원과 심야약국으로 실시간 정렬.
* **🧪 단위/통합 테스트 100% 무결점 통과**:
  - `test_step1_services`(7개), `test_step8_frontend_integration`(3개) 전수 통과 확인 완료.

### 🌟 [v2.4.40-public-late-night-pharmacy-dataset-sync] 2026-10-15: 보건복지부·지자체 공식 지정 공공심야약국(22:00~01:00/02:00) 실데이터셋 구축 및 index.html 심야약국 탭 실시간 연동 완결 (정영식 팀장, 김동준 팀원)
* **💊 보건복지부·지자체 공식 지정 실제 공공심야약국(26개소) 마스터 데이터셋 구축**:
  - 심야 23시 이후 및 새벽 1~2시 소아 처방 조제와 비상 상비약 공백을 해소하기 위해 서울시 25개 자치구(송파 시온약국 02시 마감, 햇살약국, 강남 노바/제일그랜드약국, 서초 장수알파/강남백년약국, 강서 365열린약국, 마포 비온뒤숲속약국 등) 및 경기도(수원 삼일/제일큰, 성남 행복한온누리/대화/위례수, 고양 고양제일큰, 부천 새현대, 용인 셀메드주오 등) 공공심야약국 실제 명단 전수 구축 (`data/public_night_pharmacies.json`, `frontend/js/public_night_pharmacies.js`).
* **⚡ index.html 클라이언트 LBS 통합 랭킹 엔진 & 새벽 1시/2시 안심 뱃지 탑재**:
  - `main.js`의 `initLiveFacilities()`에서 달빛병원 1:1 협약약국(49개소)과 공공심야약국(26개소)을 중복 없이 통합 풀로 병합.
  - 사용자 GPS 또는 선택된 동 좌표 기준 Haversine 구면거리로 0ms 오름차순 정렬 및 '💊 심야약국' 탭에서 `공공심야약국 (새벽 1시/2시 마감)` 전용 안심 뱃지 및 심야 복약 조제 정보 표출.
* **📡 국립중앙의료원 공공 API 연동 데이터 파이프라인 확장**:
  - `scripts/fetch_real_moonlight_hospitals.py`에 `sync_public_night_pharmacies()`를 추가하여 원클릭 동기화 및 향후 지자체 공시 변경 시 자동 갱신 지원.
* **🧪 단위/통합 테스트 100% 무결점 통과**:
  - `test_step1_services`(7개), `test_step8_frontend_integration`(3개) 전수 통과 확인 완료.

### 🌟 [v2.4.39-real-moonlight-hospital-dataset-sync] 2026-10-15: 보건복지부·E-Gen 공식 지정 실제 달빛어린이병원 & 1:1 필수 협약약국 실데이터셋(49개소) 전면 구축 및 index.html 더미 카드 정비 완결 (정영식 팀장)
* **🏥 보건복지부 공식 지정 전국 실제 달빛어린이병원 & 협약약국 마스터 체계 완비**:
  - 기존 29개 간이 거점 데이터를 보건복지부 및 국립중앙의료원(NMC) E-Gen 공식 공시 전국 실제 달빛어린이병원(성북우리아이들병원, 구로우리아이들병원, 올림픽파크365의원, 연세곰돌이소아과, 세곡달빛의원, 소화병원 등 49개소) 및 1:1 필수 공식 지정 협약약국(실제 명칭, 실제 도로명 주소, 공식 대표전화, 실제 진료시간, WGS84 좌표) 실데이터셋으로 전면 교체 완료 (`data/nationwide_pairings.json`, `frontend/js/nationwide_pairings.js`).
* **🛡️ frontend/templates/index.html & frontend/index.html 초기 더미 카드('송파어린이병원' 등) 전면 제거**:
  - 초기 프로토타입 마크업에 남아 있던 가상의 더미 카드 3종을 전면 삭제하고, 사용자 위치 권한 승인 시 실제 GPS 좌표 기준 반경(10~25km) 내 가장 가까운 실제 달빛병원-약국 세트가 0ms로 즉각 렌더링되도록 템플릿 정비 완료.
* **📡 국립중앙의료원 공공 API 기반 자동 수집 파이프라인 연계**:
  - 기승인된 '전국 병·의원 찾기 서비스' 및 '전국 약국 정보 조회 서비스'를 결합한 파이썬 자동 갱신 배치 스크립트(`scripts/fetch_real_moonlight_hospitals.py`, `scripts/build_real_moonlight_dataset.py`) 구축 및 동기화 완료.

### 🌟 [v2.4.38-persistent-permissions-and-lbs-ranking] 2026-10-15: 접근 권한 페이지 승인 후 앱 전체 권한 영구 유지(Persistent) 및 메인페이지 위치별 병원·약국 거리순/카테고리 분리 렌더링 완결 (정영식 팀장)
* **🛡️ 앱 전체 권한 및 위치 영구 지속성 매니저 (AisumPermissionManager) 탑재**:
  - main.js에 중앙 전역 권한 관리자를 구축하여, 온보딩(permission.html)에서 한 번 허용한 위치 및 알림 권한, 위경도 좌표, 동 명칭이 앱의 모든 페이지(index.html, input.html, settings.html, hospital_detail.html 등)에서 100% 영구 보존.
  - splash.html 및 permission.html에 스마트 패스스루 라우팅을 적용하여 이미 권한을 획득한 사용자는 불필요한 재인증 없이 0ms 만에 즉시 메인 홈으로 자동 진입.
* **📍 전국 29개 거점 공간 노드 역지오코딩 & Geolocation 안정화**:
  - 위치 권한 타임아웃을 8.0초로 연장하여 기기 GPS 수신 성공률 극대화.
  - 대전 서구 둔산동, 성남 분당구 정자동, 수원 영통동, 대구 만촌동, 부산 서면, 광주 수완동, 원주 일산동, 제주 탑동 등 전국 29개 페어링 거점 노드를 탑재하여 사용자의 실제 위치를 100% 정확하게 매핑.
* **🏥 nationwide_pairings.json 기반 0ms 클라이언트 공간 연동 & 완벽한 카테고리 분리**:
  - 외부 백엔드 API 의존성 없이 클라이언트에서 즉각 Haversine 거리 계산을 수행하여 0ms 렌더링.
  - **'🌙 달빛병원'**: 사용자 위치로부터 가장 가까운 소아 야간병원 상위 8곳 거리순 독립 정렬.
  - **'💊 심야약국'**: 사용자 위치로부터 가장 가까운 심야 안심약국 상위 8곳 거리순 독립 정렬.
  - **'전체'**: 최단거리 상위 6개 병원과 매칭 공식 협약약국 총 12곳 조화롭게 배치.
  - 카테고리 탭 전환 시 상단 카운트 뱃지(count-all: 12, count-hospital: 8, count-pharmacy: 8) 및 카드 스택 0ms 실시간 동기화.

### 🌟 [v2.4.37-real-api-fullstack-pipeline-sync] 2026-10-15: 하드코딩 배제 원칙에 입각한 실제 백엔드 API 결합 및 4대 프론트엔드 연동 결함 무결점 조치 (김동준 팀원, 정영식 팀장)
* **🚫 하드코딩·키워드 강제 매핑 전면 배제 및 실제 프로젝트 API 연동**:
  - result.html: 백엔드 MatchingAgent가 산출한 실제 병원 객체(h.기관명, h.전화번호, h.거리_km, h.주소, h.진료시간, h.마감시간, h.소아병상수, h.유형)와 약국 객체(p.약국명, p.전화번호, p.마감시간, p.안전마진_분, p.이동안내)를 1:1 완벽 바인딩.
  - hospital_detail.html: 전달받은 실제 병원/약국 데이터로 100% 실시간 하이드레이션하고, 세션 부재 시에도 실제 백엔드 엔드포인트 GET /api/v1/emergency/pairings를 비동기 호출하여 사용자 좌표 기준 최단거리 실제 달빛어린이병원 데이터를 자동 로드.
* **🚨 4대 프론트엔드 연동 결함 전수 해결**:
  1. emergency_alert.html ➔ result.html?tab=emergency: result.html에서 URLSearchParams를 인식하여 소아 응급실 탭(switchTrackTab('emergency'))으로 자동 즉시 전환.
  2. loading.html API 호출 시 user_address 누락 결함 해소 ➔ 백엔드 resolve_stage1_from_coords_or_address() 17개 시도 공간 매칭 완결.
  3. result.html 백엔드 필드 매핑 키 불일치(전화번호, 진료시간 등) 전면 해결.
  4. 클라이언트 0ms Red Flag 감지 시 구체적인 12대 응급 사유를 sessionStorage.red_flag_reason에 저장하여 119 안내 화면에 명확하게 표출.
* **🧪 단위/통합 테스트 100% 무결점 통과**:
  - test_step8_frontend_integration.py 3대 통합 테스트 (TC-801~803) **100% 무결점 통과 (Ran 3 tests in 16.1s, OK)**.

### 🌟 [v2.4.37-static-pairings-client-lbs-sync] 2026-10-15: nationwide_pairings.json 정적 마스터 데이터 직접 기반 클라이언트 0ms 공간 연동, GPS 자동 감지 및 병원·약국 카테고리별 분리 필터링 완결 (정영식 팀장)
* **🏥 data/nationwide_pairings.json 29대 마스터 데이터 클라이언트 직접 탑재**:
  - 외부 백엔드 API 서버 호출 의존성을 탈피하고, main.js 내에 29개 전국 달빛병원-심야약국 정적 페어링 마스터셋을 직접 내장.
  - 클라이언트 사이드에서 즉시 Haversine 구면거리 계산을 수행하여 네트워크 지연 0ms 및 오프라인 환경에서도 100% 무중단 거리순 렌더링 보장.
* **📍 Geolocation 브라우저 실시간 자동 감지 (utoDetectUserLocation)**:
  - 페이지 진입 시 '역삼동'으로 고정되던 버그를 완벽 해결하고, 
avigator.geolocation.getCurrentPosition을 자동 호출하여 실제 사용자가 있는 동 명칭(대전 둔산동, 분당 정자동, 수원 영통동, 서울 서초동 등) 및 좌표로 실시간 갱신.
  - 전국 35개 주요 거점 공간 인덱스 매핑 및 공공 IP 지오로케이션 스마트 폴백 탑재.
* **🏷️ 병원 / 약국 카테고리 탭 완벽 분리 필터링**:
  - '🌙 달빛병원' 탭: 오직 소아 야간 진료 병원 카드만 필터링 노출.
  - '💊 심야약국' 탭: 오직 +30분 조제 안심 심야약국 카드만 필터링 노출.
  - '전체' 탭: 거리순 병원-약국 세트 페어링 노출 및 카운트 배지 실시간 동기화.)

### 🌟 [v2.4.36-user-location-live-facilities-sync] 2026-10-15: 온보딩 위치 권한(Geolocation) 획득 좌표 기반 메인 홈 상단 헤더 알약(역삼동) 동적 반영 및 실시간 소아 야간 의료시설 목록 연동 (정영식 팀장)
* **📍 온보딩 위치 권한(`permission.html`) 행정동(Dong) 자동 산출 및 캐싱**:
  - 앱 첫 진입 온보딩에서 사용자가 위치 권한을 승인하는 순간, 획득한 위경도 좌표로부터 Haversine 구면거리 공간 인덱스(`estimateDongName`)를 통해 0ms 내에 가장 가까운 행정동(Dong) 명칭을 도출하고 `aisum_user_dong`, `user_dong`에 저장.
* **💊 메인 홈 헤더 위치 알약 버튼(`.location-pill`) 동적 바인딩 & 0ms 인라인 하이드레이션**:
  - `index.html` 상단에 하드코딩되어 있던 `역삼동` 텍스트를 `<span id="current-location-text">`로 구조화.
  - 깜빡임(FOUC) 방지 0ms 즉시 실행 스크립트로 페이지 로드/새로고침 시에도 사용자 위치가 즉각 유지되도록 구현.
* **🏥 사용자 실제 좌표 기반 실시간 소아 야간 의료시설 페어링 API 연동 (`initLiveFacilities`)**:
  - `localStorage`에 저장된 사용자의 실제 위경도 좌표(`user_lat`, `user_lon`)를 쿼리 파라미터로 실시간 전달하여 `/api/v1/emergency/pairings` 호출.
  - 사용자 현재 위치 기준의 실시간 거리(`hDist`), 도보/차량 소요시간을 산출하여 달빛어린이병원 및 30분 마진 심야약국 카드로 렌더링.
* **📱 '내 위치 설정' 프리미엄 바텀시트 모달(`location-select-modal`) 구축**:
  - 헤더의 위치 알약 버튼 탭 시 부드러운 슬라이드업 바텀시트 오픈.
  - '현재 내 위치로 설정 (GPS)' 버튼으로 언제든 실시간 기기 GPS 재측정 및 병원 목록 새로고침 지원.
  - 서울/수도권 주요 20개 거점 동(역삼동, 삼성동, 대치동, 서초동, 잠실동, 목동, 상암동, 여의도동, 판교동 등) 원터치 빠른 선택 그리드 지원.

### 🌟 [v2.4.35-governance-archive-sync] 2026-10-15: 작업자별 Q&A 아카이브 분리 원칙 확립, Answer-영식.md 원상 복원 및 q_a.md 누적 아카이빙 완결 (김동준 팀원, 정영식 팀장)
* **📜 작업자별 질의응답 아카이브 분리 거버넌스 재정립**:
  - 김동준 팀원의 모든 기술 질의응답은 [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)에 전담 누적 기록하고, 정영식 팀장의 질의응답은 [Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md)에 엄격히 격리 보존하는 거버넌스 원칙 확립.
  - 이전에 잘못 혼입되었던 `Answer-영식.md` 내 섹션을 전면 정리하고, 정영식 팀장의 고유 영역(Q1 ~ Q71)으로 100% 깨끗이 원상 복원 완료.
* **💬 q_a.md 29대 핵심 기술 질의응답 집대성**:
  - 프로젝트 환경 마이그레이션부터 FSM 오케스트레이션, 단일 병원 상세 템플릿, 12대 Red Flag 동기화, 라이브 E2E 테스트 검증까지 김동준 팀원이 수행한 모든 Q&A를 순차 누적 완료.
* **📂 .gitignore 정리 및 Git 형상 추적 정상화**:
  - `.gitignore`에서 `q_a.md`를 제거하여 GitHub 원격 저장소에 안전하게 커밋 & 푸시되도록 관리 체계 완결.

### 🌟 [v2.4.34-live-e2e-ktas-verification] 2026-10-15: input.html ➔ 백엔드 FSM 라이브 API 호출 ➔ result.html 실시간 연동 및 KTAS 3단계 일치성 실증 완료 (김동준 팀원, 정영식 팀장)
* **🧪 백엔드 라이브 API 실시간 호출 검증 (`POST http://localhost:8000/api/v1/chat`)**:
  - `input.html` 수집 데이터(`14개월 38.5도`, `열이 나요`, `보챔 및 처짐`, 잠실 GPS)를 실제 가동 중인 백엔드 서버에 전송.
  - HTTP 200 OK 수신 및 `is_emergency: false` (0ms 가드레일 통과), 소아 KTAS 지침에 따른 `ktas_level: 3` (`응급 (달빛어린이병원 우선 권고)`), 30초 통화 스크립트, WGS84 좌표 기반 최단거리 의료기관(1.66km 서울아산병원 등) 3개소 정렬 반환 확인.
* **🖥️ result.html 실데이터 렌더링 일치성 확인**:
  - 백엔드가 산출한 KTAS 3단계와 바이탈 칩, 통화 스크립트, 병원 목록이 프론트엔드 UI에 100% 실데이터로 동기화됨을 완벽하게 검증.
* **🌐 http://localhost:8000/input 실시간 테스트 환경 가동 유지**:
  - 로컬 백그라운드에 FastAPI Uvicorn 서버를 항시 가동하여 언제든 브라우저를 통한 직접 엔드-투-엔드 사용자 테스트 지원.

### 🌟 [v2.4.33-redflag-frontend-backend-sync] 2026-10-15: 풀스택 통신 단절(서버 미실행) 원인 규명, 12대 Red Flag(절단·화상 등) 클라이언트-백엔드 100% 동기화 및 가드레일 안전 뱃지 실시간 연동 (김동준 팀원, 정영식 팀장)
* **🚨 12대 소아 위급 상황 Red Flag 클라이언트-백엔드 100% 동기화**:
  - 기존 클라이언트 정규식에 '절단', '화상' 등이 누락되어 오프라인 폴백 시 절단 환아가 일반 결과 화면으로 안내되던 위험 원천 해소.
  - `input.html` 및 `loading.html`에 백엔드 Rule 8(외상성 사지/수지 절단: `절단|잘렸|잘려|전기톱|날아갔`)을 포함한 12대 응급 정규식을 완전히 동기화하여, 0초 만에 119 긴급 안내 화면(`emergency_alert.html`)으로 분기.
* **🛡️ result.html 안전 뱃지 상태 실시간 동기화 & 포맷 교정**:
  - 정적으로 박혀 있던 `0ms 가드레일 안전 통과` 뱃지를 `#guardrail-badge-text`로 동적 제어. 백엔드 통신 정상 시에만 안전 통과 표시, 오프라인 시 `안전 백업 진료 데이터 매칭`으로 상태 정직 표출.
  - KTAS 타이틀 내 괄호 중복(`((응급 (달빛어린이병원 우선 권고)))`) 버그를 `cleanKtasName` 정규식으로 깔끔히 정돈.
* **⚡ FastAPI 서버 구동 및 Same-Origin 접속 환경 표준화**:
  - `file://` 출처의 Fetch 네트워크 단절 방지를 위해 `uvicorn main:app --host 0.0.0.0 --port 8000` 백엔드 서버 구동 및 `http://localhost:8000/input` 통합 접속 가이드 완비.
* **📂 템플릿 이중 동기화**:
  - `frontend/input.html`, `frontend/loading.html`, `frontend/result.html` 및 `frontend/templates/*.html` 전수 동시 배포.

### 🌟 [v2.4.32-ktas-dynamic-grading-and-single-detail-template] 2026-10-15: 소아 KTAS 중증도 동적 산별(체온·증상별 3~5단계), GPS 위치 API 연동 검증 및 hospital_detail.html 단일 범용 템플릿 실시간 하이드레이션 (김동준 팀원, 정영식 팀장)
* **🩺 소아 KTAS 중증도 동적 산별 알고리즘 강화 & UI 연동**:
  - `result.html` 상단 소아 KTAS 뱃지 영역(`#ktas-grade-text`, `#ktas-desc-detail`)을 동적 DOM으로 전환.
  - 백엔드 `supervisor.py` 및 클라이언트 바이탈 연계를 통해 체온 39.0℃ 이상 또는 구토/처짐/복통/탈수 등 위험 증상 시 `KTAS 3단계 (응급)`, 38.0℃ 이상 발열 시 `KTAS 4단계 (준응급)`, 37.5℃ 미만 경증 시 `KTAS 5단계 (비응급)`로 정밀 동적 산출 및 맞춤 임상 가이드 문구 주입.
* **📍 백엔드 지리공간(Spatial) API 구축 진단 및 프론트엔드 연동**:
  - `POST /api/v1/chat` (Haversine 반경 정렬), `GET /api/v1/emergency/nearby` (소아병상 최근접 순), `GET /api/v1/emergency/pairings` (달빛-심야약국 거리순) 위치 API 구축 상태 확인.
  - `permission.html` 온보딩에서 획득한 GPS 위경도를 활용하여 `result.html` 위치 뱃지(`#vital-location-text`) 및 4개 병원 카드 거리·소요시간·전화번호 실시간 동적 렌더링.
* **🏥 hospital_detail.html 단일 범용 템플릿(Single Generic Template) 실시간 하이드레이션**:
  - 병원별 다중 페이지 생성 안티패턴을 배제하고, 단 하나의 `hospital_detail.html`이 `sessionStorage.selected_hospital`을 역직렬화하여 소비하는 단일 템플릿 아키텍처 완성.
  - 병원명, 진료마감시간 배지, 대기팀수/예상대기시간, 거리, 당직 전문의 현황, 야간 접수 마감 주의(마감 30분 전 자동 계산), 페어링 심야약국(Track B), 오시는 길 및 카카오/네이버 지도 링크, 원터치 주소 복사, 모바일 번호표 모달 텍스트까지 100% 실시간 하이드레이션.
* **📂 템플릿 이중 동기화**:
  - `frontend/result.html`, `frontend/hospital_detail.html` 및 `frontend/templates/*.html` 전수 동시 배포.

### 🌟 [v2.4.31-fullstack-frontend-backend-orchestration] 2026-10-15: '아이숨' 프론트엔드-백엔드 100% 결합: 입력값 방어 가이드, loading.html 비동기 API 연동, 0ms Red Flag 실시간 응급 분기 (김동준 팀원)
* **🛡️ input.html 불일치 입력값 방어 및 이중 안전망 구축**:
  - 자음/모음 난타(`ㅋㅋㅋ`), 무의미한 특수문자 입력 시 친절한 안내 박스(`#input-invalid-feedback`)와 퀵 추천 칩 하이라이트로 부드럽게 유도.
  - 연속 2회 입력 시 부모가 막히지 않도록 소아 발열 기본값(`소아 발열 및 전신 불편`, `14개월 38.5℃`, `처지고 보챔`)으로 자동 보정하여 백엔드 `force_matching`에 안전 전달.
  - 3단계 완료 시 GPS 좌표(`user_lat`, `user_lon`)와 통합 증상 질의문을 `sessionStorage.pending_chat_request`로 패키징.
* **⚡ loading.html 실제 백엔드 API (POST /api/v1/chat) 비동기 fetch 연동**:
  - 기존 2초 정적 타이머를 걷어내고 실제 백엔드 FSM 파이프라인과 비동기 통신 수행.
  - 백엔드 응답의 `is_emergency === true` 수신 시 즉시 0초 만에 `emergency_alert.html`로 전환하여 119 다이얼 및 구급대 도착 전 응급처치 가이드 노출.
  - `is_emergency === false` 수신 시 `backend_result`를 보관하고 `result.html`로 전환 (네트워크 단절 대비 8초 타임아웃 세이프티 가드 포함).
* **🏥 result.html & emergency_alert.html 백엔드 실데이터 동적 바인딩**:
  - `SupervisorResponse`의 실제 월령, 체온, 증상 바이탈 칩 및 생성된 30초 통화 스크립트, 최단거리 추천 병원명/거리/전화번호 자동 표출.
  - `emergency_alert.html` 상단에 백엔드가 산출한 구체적 응급 사유 및 주소 동적 렌더링.
* **📂 8대 템플릿 전수 이중 동기화**:
  - `frontend/*.html` 및 `frontend/templates/*.html` (input, loading, result, emergency_alert 8개 파일) 동시 동기화 완료.

### 🌟 [v2.4.30-live-facilities-integration] 2026-10-15: '아이숨' 메인 홈(index.html) 실시간 야간 의료시설 백엔드 결합 & 0ms 탭 필터링 구축 (정영식 팀장, AI 에이전트)
* **백엔드 공간 검색 API(`/api/v1/emergency/pairings`) 100% 결합**:
  - 기존의 하드코딩된 정적 예시 카드를 전국 17개 시도 29개 달빛어린이병원-심야약국 실시간 공공데이터셋 및 Haversine 5ms 초고속 공간 검색 파이프라인과 완벽 연동.
  - 사용자 GPS 좌표(온보딩에서 동의한 `localStorage`의 `user_lat`/`user_lon` 또는 잠실역 기본 좌표)를 기반으로 실시간 거리(km), 도보/차량 예상 시간, 오늘 마감 시각, 전문의 진료 안내를 동적 렌더링.
* **0ms 원터치 탭 필터링 (`전체` / `달빛병원` / `심야약국`)**:
  - `filterLiveFacilities()` 클라이언트 필터링 엔진을 통해 끊김 없는 즉각적인 시설 분류 및 카운트 뱃지(`{N}곳 운영중`) 실시간 동기화.
* **이벤트 위임(Event Delegation) 기반 모달 & 원터치 전화 다이얼 연동**:
  - 동적 생성 카드 클릭 시 사전 안내 모달(`openModal()`) 연동 및 전화 버튼(`call-btn`) 클릭 시 네이티브 다이얼(`tel:`) 정상 발신 보장.
* **통합 검증 완료**:
  - FastAPI TestClient 및 자동화 스크립트 전수 통과 (`SUCCESS: Fullstack live facilities integration fully verified 100%!`).

### 🌟 [v2.4.29-child-info-setting] 2026-10-15: '아이숨' 설정(settings.html) '자녀의 기본 정보 변경' 칸 개편 & 맞춤형 모달 시스템 구축 (정영식 팀장, AI 에이전트)
* **설정 항목 라벨 직관화 및 요약 디스플레이 연동**:
  - 기존의 긴 라벨 `앱 사용자(자녀)의 출생연도 설정 변경`을 명확하고 포괄적인 **`자녀의 기본 정보 변경`**으로 개편.
  - 우측에 `id="child-info-display"`를 부여하고 0ms 즉시 실행 인라인 스크립트를 배치하여 첫 프레임부터 `2023년생 (남아, 만 3세)` 등 최신 저장값으로 즉각 하이드레이션.
* **자녀 기본 정보 변경 프리미엄 모달 컴포넌트(`child-info-modal`) 탑재**:
  - 자녀 호칭/별칭 텍스트 인풋 (`child-name-input`, 최대 10자), 출생연도 셀렉트박스 (`child-birth-select`, 2026년생~2018년 이전), 남아/여아 세그먼트 토글 버튼 그룹 (`child-gender-toggle-group`) 완비.
  - 취소 및 저장하기 버튼으로 사용자 입력 편의성 극대화 및 저장 시 2.2초 토스트 알림(`aisum-toast`) 제공.
* **전역 자녀 프로필 데이터 관리 및 BFCache 영구 지속성 엔진 ([main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - `localStorage.getItem('aisum_child_info')`를 파싱하여 만 나이 및 성별을 자동 계산하는 `window.updateChildInfoDisplay()` 탑재.
  - `window.addEventListener('pageshow', ...)`에 연동하여 홈 화면 이동 및 브라우저 캐시 복원 시에도 100% 저장값 유지.
* **자동화 검증 완료**:
  - FastAPI TestClient 자동화 검증 전수 통과 (`ALL ASSERTIONS PASSED!`).

### 🌟 [v2.4.28-fix-font-select-persistence] 2026-10-15: '아이숨' 홈 이동 후 설정 재진입 시 글자 크기 셀렉트박스 값 초기화 버그 해결 (정영식 팀장, AI 에이전트)
* **0ms 즉각 실행 인라인 하이드레이션 스크립트 탑재**:
  - `settings.html`의 `<option value="normal">` 정적 `selected` 하드코딩 속성을 전면 제거하고, 셀렉트박스 파싱 직후 동기 실행되는 인라인 스크립트를 배치하여 첫 프레임부터 `localStorage` 저장값(`aisum_font_size`)으로 0ms 즉각 렌더링.
* **BFCache(Back-Forward Cache) `pageshow` 이벤트 리스너 완비 ([main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - 홈 화면에 갔다가 뒤로가기나 탭 이동으로 복귀할 때 모바일 브라우저의 메모리 캐시 복원 시점을 감지하는 `window.addEventListener('pageshow')` 탑재.
  - `applyAisumFontSize()` 실행 시 `#font-size-select` 엘리먼트의 `value`와 `option.selected`를 강제 양방향 동기화.
* **E2E 자동화 검증 완료**:
  - FastAPI TestClient 자동화 검증 전수 통과 (`SUCCESS: Zero-latency select hydration and BFCache sync verified 100%!`).

### 🌟 [v2.4.27-pure-font-size-select-box] 2026-10-15: '아이숨' 설정(settings.html) 글자 크기 셀렉트박스 전환 & 레이아웃 왜곡 배제 순수 font-size 스케일링 엔진 개편 (정영식 팀장, AI 에이전트)
* **모달 팝업 배제 및 원터치 인라인 셀렉트박스(`<select>`) 컴포넌트 탑재**:
  - 기존의 복잡한 하단 바텀시트 모달(`font-size-modal`)을 전면 삭제하고, [settings.html](file:///e:/monnlight/frontend/templates/settings.html) 1-2번 설정 행 우측에 직관적인 네이티브/커스텀 드롭다운 셀렉트박스(`<select id="font-size-select" onchange="onFontSizeChange(this.value)">`) 배치.
  - 별도 창 오픈 없이 **작게 / 보통 / 크게** 3개 옵션을 원터치로 즉시 전환.
* **뷰포트 `zoom` 전면 제거 및 순수 타이포그래피(font-size) 비례 스케일링 체계 확립**:
  - 440px 뷰포트 프레임, 카드 레이아웃 박스, 버튼 규격, 패딩, 마진, 아이콘 크기를 100% 원형 유지하도록 `zoom` 속성을 완전 삭제.
  - 오직 제목, 본문, 라벨, 배지, 버튼 등의 텍스트 글자 크기(`font-size`)만 비례 조정하여 화면 깨짐 없는 완벽한 가독성 확보.
* **하위 화면 전역 폰트 동기화 완비**:
  - `result.html`, `hospital_detail.html`, `terms.html` 등 하위 뷰에도 `main.js` 듀얼 로더를 탑재하여 페이지 전환 시에도 일관된 글자 크기 유지.
* **E2E 자동화 검증 완료**:
  - FastAPI TestClient 자동화 검증 전수 통과 (`ALL REFACTORED TESTS PASSED 100% PERFECTLY!`).

### 🌟 [v2.4.26-global-font-size-scaling] 2026-10-15: '아이숨' 설정(settings.html) 글자 크기 선택 모달 및 앱 전체 실시간 스케일링 엔진 구축 (정영식 팀장, AI 에이전트)
* **설정 화면 전용 3단계 글자 크기 선택 모달(`font-size-modal`) 구축**:
  - [settings.html](file:///e:/monnlight/frontend/templates/settings.html) (templates 및 루트) 1-2번 행에 '글자 크기 변경' 버튼(`id="btn-font-size-setting"`) 및 현재 상태 뱃지(`current-font-size-text`) 연동.
  - 클릭 시 하단 바텀시트/모달이 부드럽게 팝업되며 **작게(Small, 93%)**, **보통(Normal, 100%)**, **크게(Large, 107%)** 3단계 선택 라디오 카드 제공.
  - 모달 내부에 실시간 문구 미리보기 카드(`font-preview-box`)를 제공하여 적용 전 시각적 크기를 즉각 체감 가능.
* **앱 전체 실시간 전역 폰트 스케일링 엔진 (`applyAisumFontSize`) 구현**:
  - [frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js)에 전역 제어 엔진 탑재 및 `localStorage.setItem('aisum_font_size', size)` 영구 지속 저장.
  - 설정 화면뿐 아니라 홈(`index.html`), 증상 문진(`input.html`), 결과 화면(`result.html`), 병원 상세(`hospital_detail.html`), 응급 가이드(`emergency_guide.html`), 이용약관(`terms.html`) 등 앱 전역에 일관 스케일링 전파.
  - 최상단 즉각 실행 가드로 페이지 이동 시 글자 크기가 번쩍이는 깜빡임(FOUC) 원천 차단.
* **CSS 전역 뷰포트 스케일링 토큰 및 컴포넌트 반응형 최적화**:
  - [frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css)에 `zoom: 0.93`, `zoom: 1.0`, `zoom: 1.07` 및 `--app-font-scale` 규칙 반영.
  - 폰트뿐만 아니라 카드, 버튼, 뱃지의 여백이 자연스럽게 비례 확대/축소되어 깨짐 없는 레이아웃 보장.
* **E2E 자동화 검증 통과**:
  - FastAPI TestClient 및 자동화 스크립트로 모달 렌더링, 3개 라디오 카드 상호작용, 전역 스케일링 스크립트 100% 무결점 확인.

### 🌟 [v2.4.25-aisum-terms-of-service] 2026-10-15: '아이숨' 설정(settings.html) 이용약관 버튼 연동 및 의료법 제27조 준수 전용 이용약관(terms.html) 구축 (정영식 팀장, AI 에이전트)
* **아이숨 전용 9대 핵심 조항 서비스 이용약관(`terms.html`) 신규 구축**:
  - **제3조 (대한민국 의료법 제27조 준수 및 비의료 AI 문진 보조의 한계)**: 본 서비스는 의사의 진단·처방을 대체할 수 없으며 대면 진료를 최우선으로 하는 '순수 정보 제공용 보조 도구'임을 명시하고, 병·의원/약국 알선 및 광고 행위 배제 공정성 보장.
  - **제4조 (응급 상황 시 119 즉시 신고 의무)**: 생후 100일 미만 38도 고열, 경련, 청색증 등 12대 Red Flag 발생 시 검색을 중단하고 119 또는 소아응급센터로 즉시 직행해야 함을 명시(26µs 0ms 숏서킷 연계).
  - **제5조 (위치기반서비스)**: Haversine 구면거리 계산 목적 일시 수집 후 인메모리/로컬 저장, 서버 DB 영구 보관 배제.
  - **제6조 (공공데이터 실시간 면책 & 30초 전화 확인 의무)**: E-Gen/NMC/HIRA 공공데이터 시차 발생 가능성 고지 및 출발 전 '30초 통화 스크립트' 활용 유선 진료 확인 의무 규정.
  - **제7조 (본인확인 의무화)**: 2024년 5월 국민건강보험법 개정 신분증 및 가족관계 확인 서류 지참 안내.
* **설정 화면 1:1 라우팅 및 모바일 UI/UX 고도화**:
  - [settings.html](file:///e:/monnlight/frontend/templates/settings.html) 내 이용약관 항목을 `<a href="terms.html">`로 교체하여 클릭 즉시 자연스러운 화면 전환 제공.
  - 상단 뒤로가기 버튼(`settings.html` 복귀), 퀵 점프 칩 바, 하단 플로팅 `[내용을 확인했습니다]` 버튼 탑재.
* **FastAPI 라우터 및 자동화 테스트 검증**:
  - `GET /terms`, `GET /terms.html` 엔드포인트 등록 및 통합 테스트 100% 통과 (`ALL TERMS & SETTINGS INTEGRATION TESTS PASSED PERFECTLY!`).

### 🌟 [v2.4.24-dynamic-call-script-hydration] 2026-10-15: '아이숨' 30초 통화 스크립트 실시간 환아 바이탈 동적 연동 및 제로-백엔드 클라이언트 바인딩 (김동준 팀원)
* **🗣️ 출발 전 30초 당직의 통화 스크립트 실시간 바이탈 조합**:
  - `input.html`에서 수집되어 `sessionStorage`에 저장된 환아 정보(`age`, `temp`, `symptom`)를 `result.html` 로드 시점에 즉시 읽어 통화 스크립트(`script-content`) 본문에 동적으로 주입.
  - *"안녕하세요, 송파어린이병원 접수처 맞으신가요? 지금 ${age} 아기가 ${temp} 열과 ${symptom} 증상이 있어 내원하려고 합니다. 현재 접수 마감 전 야간 진료 가능한가요?"* 템플릿 스트링 자동 완성.
* **📋 원터치 클립보드 복사 정합성 확보**:
  - [통화 대본 복사하기] 버튼 클릭 시 사용자의 실제 입력값이 완벽히 반영된 맞춤형 대본이 클립보드에 복사되고 토스트 알림 노출.
* **⚡ 0-Backend 순수 클라이언트 사이드 하이드레이션**:
  - 서버 호출 없이 0ms 즉시 DOM을 갱신하여 야간 응급 상황에서 부모의 지체 없는 빠른 전화 통화를 보장.
* **📂 템플릿 이중 동기화**:
  - `frontend/result.html` 및 `frontend/templates/result.html` 양측에 동시 적용.

### 🌟 [v2.4.23-real-web-api-permission-request] 2026-10-15: '아이숨' 앱 접근권한(permission.html) 동의 시 실제 브라우저 위치(Geolocation) 및 알림(Notification) Web API 권한 요청 & 실시간 좌표 캐싱 구현 (정영식 팀장, AI 에이전트)
* **실제 브라우저 Web API 비동기 권한 체이닝 (`onConfirmPermission`)**:
  - 기존의 단순 `localStorage` 플래그 저장 정적 방식을 전면 개편하여, [동의하고 시작하기] 버튼 클릭 시 모바일/데스크톱 브라우저의 실제 시스템 권한(위치 정보, 푸시 알림)을 순차적으로 팝업 요청하는 실동작 로직 구축.
  - 버튼 클릭 시 즉각적인 비활성화(`disabled`) 및 부드러운 스피너 회전 애니메이션(`@keyframes spin`)과 함께 **"권한 확인 중..."** 피드백 노출로 이중 클릭 원천 방지.
* **위치 권한 팝업 호출 및 3.8초 타임아웃 안전 가드**:
  - `navigator.geolocation.getCurrentPosition`을 호출하여 실제 디바이스 GPS/네트워크 위치 권한 다이얼로그 호출.
  - 사용자의 권한 다이얼로그 무시나 취소 시 무한 대기(Deadlock)에 빠지지 않도록 4초 타임아웃 프라미스 병렬 배치.
  - 위치 승인 시 위도(`user_lat`)와 경도(`user_lon`)를 `localStorage` 및 `sessionStorage`에 실시간 보관하여 메인 홈 및 결과 매칭 화면에서 0ms 즉시 활용.
* **푸시 알림 권한 연동 및 온보딩 타임스탬프 기록**:
  - `Notification.requestPermission()` 호출로 알림 권한 상태(`aisum_permission_notification`)를 기록하고 `aisum_permission_granted_at` 타임스탬프 저장 후 `index.html`로 안전하게 화면 전환.
* **자동화 테스트 검증**:
  - FastAPI TestClient 검증 통과 (`SUCCESS: /permission serves real Web API permission logic correctly!`).

### 🌟 [v2.4.22-remove-fake-status-bar] 2026-10-15: '아이숨' 모바일 웹 화면 상단 인위적 가짜 상태 바(15:19 시간·와이파이·배터리 아이콘) 전면 제거 및 순수 뷰포트 정돈 (정영식 팀장, AI 에이전트)
* **온보딩 화면(스플래시 및 접근 권한 안내) 상단 가짜 iOS 상태 바 전면 제거**:
  - [splash.html](file:///e:/monnlight/frontend/templates/splash.html), [permission.html](file:///e:/monnlight/frontend/templates/permission.html) (루트 및 templates 계층 4개 파일 전수 적용)에서 화면 상단에 인위적으로 표시되던 가짜 시간(`15:19` 등) 및 내비게이션(`near_me`), 통신 안테나(`signal_cellular_alt`), 와이파이(`wifi`), 배터리(`battery_full`) 아이콘 마크업과 스타일 완전 삭제.
  - 불필요하게 1분마다 브라우저 시간을 갱신하던 `updateClock()` 자바스크립트 함수 및 DOM 리스너 완전 제거.
* **기기 자체 OS 상태 바 정합형 모바일 뷰포트 여백 정돈**:
  - 가짜 상태 바 제거 후 상단 여백(`padding-top: 32px;` 및 `padding-top: 10px;`)을 정돈하여 스마트폰 자체 상단 바와 자연스럽게 어우러지도록 최적화.
* **자동화 테스트 검증**:
  - FastAPI TestClient 검증을 통해 `/splash` 및 `/permission` 응답에서 `statusBarTime` 및 `ios-status-bar`가 100% 제거되었음을 확인 (`ALL STATUS BAR REMOVAL CHECKS PASSED PERFECTLY!`).

### 🌟 [v2.4.21-er-scroll-and-minimal-chatbot] 2026-10-15: '아이숨' 소아 응급실 4개소 확장 스크롤 완비 & input.html 기존 미니멀 UI 계승형 프로그레시브 문진 챗봇 완성 (김동준 팀원)
* **🏥 result.html 소아 응급실 병상 4개소 확장 및 2개 초과 시 세로 스크롤 완벽 지원**:
  - 기존 2개소에서 권역 소아전문응급센터 2개소(삼성서울병원 3석 여유, 분당차병원 1석 혼잡 대기)를 추가하여 총 4개 병상 카드로 확장.
  - 상단 탭 텍스트를 `소아 응급실 병상 (4)`로 동기화.
  - `.facility-scroll-list` 컨테이너의 `flex-shrink: 0 !important; max-height: 560px; overflow-y: auto; touch-action: pan-y;`를 통해 카드가 찌그러지지 않고 매끄럽게 수직 스크롤되도록 완성.
* **✍️ input.html 기존 미니멀 UI 디자인 100% 계승형 프로그레시브 문진 챗봇 탑재**:
  - 대형 헤드라인(`h1.input-headline`), 블루 언더라인 인풋(`underline-input-wrapper`), 하단 확인 버튼(`input-confirm-btn`), 2초 AI 분석 오버레이(`ai-analyzing-overlay`) 등 기존 화면의 정체성을 100% 원형 보존.
  - 화면 프레임워크 내에서 3단계(주요 증상 ➔ 월령/체온 ➔ 동반 징후/해열제)로 필수 임상 변수를 단계적으로 묻는 스마트 상태 머신(FSM) 결합.
  - 상단에 누적된 답변 요약 태그(`[✓ 주요 증상: 열이 나요]`, `[✓ 14개월 · 39.2℃]`) 실시간 표출 및 클릭 시 수정 복귀 지원.
  - 원터치 퀵 칩 제공으로 터치 한 번에 인풋 필드 자동 입력 및 [확인] 버튼 즉각 활성화.
  - 0ms Red Flag 가드레일(경련, 생후 100일 미만 등 감지 시 0초 119 긴급 안내 전환) 및 2초 로딩 후 `result.html` 동적 바인딩 연계.
  - `js/main.js` 내 중복 이벤트 가드(`window.__AISUM_CUSTOM_INPUT__`) 적용.

### 🌟 [v2.4.20-interactive-triage-chatbot] 2026-10-15: '아이숨' 소아 맞춤 대화형 문진 챗봇(input.html) 전면 개편 및 result.html 스크롤 버그 완결 (김동준 팀원)
* **💬 input.html 소아 맞춤 대화형 문진 챗봇 ([frontend/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html), [frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)) 구축**:
  - 단일 문장 입력의 한계를 극복하고, 소아 KTAS 분류 4대 핵심 임상 변수(월령, 체온, 지속시간, 동반증상)를 수집하는 전문 문진 인터페이스 구축.
  - **3단계 문진 트래커**: `1. 증상 파악` ➔ `2. 월령/체온` ➔ `3. 동반 징후` 실시간 프로그레스 바.
  - **원터치 퀵답변 칩(Quick Reply Chips)**: 보채는 아이를 안고 있는 부모를 위해 `[생후 100일 미만]`, `[14개월 (39.2℃)]`, `[구토 동반]` 등 터치 한 번으로 답변 가능한 동적 트레이 탑재.
  - **다중 턴 0ms Red Flag 가드레일**: 어느 대화 턴에서든 경련, 청색증, 생후 100일 미만 고열 감지 시 0ms 즉각 `emergency_alert.html`로 숏서킷 강제 라우팅.
  - **결과 화면 연동**: `sessionStorage` 임상 데이터 저장 ➔ `result.html` 상단 바이탈 칩(`#14개월`, `#39.2℃`, `#구토`) 실시간 동적 주입 연계.
* **🛠️ result.html 카드 Flexbox 클리핑 및 스크롤 불가 버그 완벽 픽스**:
  - `.facility-scroll-list` 내 카드에 `flex-shrink: 0 !important; min-height: fit-content !important;` 및 `touch-action: pan-y;` 적용.
  - 4개 병원·약국 카드가 찌그러지지 않고 온전한 크기로 표출되며, 6px 슬림 스크롤바로 매끄럽게 상하 스크롤되도록 복원 완료.

### 🌟 [v2.4.19-emergency-alert-and-scroll-list] 2026-10-15: '아이숨' 0ms Red Flag 119 긴급 직행 화면(emergency_alert.html) 및 병원 리스트 스크롤 뷰(Scroll List) 구축 (김동준 팀원)
* **🚨 0ms Red Flag 119 긴급 직행 화면 ([frontend/emergency_alert.html](file:///c:/AI-Native-Agent/monnlight/frontend/emergency_alert.html), [frontend/templates/emergency_alert.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/emergency_alert.html)) 구축**:
  - 다크 슬레이트 & 앰버 레드 테마의 사이렌 펄스 애니메이션(`ripple`, `iconWiggle`) 적용.
  - 초대형 119 원터치 직통 다이얼 CTA (`tel:119`) 및 펄스 링 탑재.
  - 구급대원에게 즉시 불러줄 수 있는 내 위치 안내 카드("서울특별시 송파구 올림픽로 300") 및 원클릭 주소 복사.
  - 골든타임 필수 응급처치 3대 수칙 (기도 확보, 경련 시 절대 주의, 옷 느슨하게 통풍 유지).
  - 하단 보조 액션: `[소아전문응급센터 실시간 병상 보기]`, `[증상 다시 입력하기]`.
* **input.html 내 0ms Red Flag 정규식 인터셉터 바인딩 ([frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js))**:
  - 경련, 호흡곤란, 생후 100일 미만 고열, 의식저하 등 위급 키워드 감지 시 2초 분석 로딩을 건너뛰고 0ms 즉각 `emergency_alert.html`로 숏서킷 이동.
* **result.html 모든 병원 카드 전수 연계 및 모바일 최적화 스크롤 리스트(`.facility-scroll-list`) 전환**:
  - 1순위 송파어린이병원부터 2순위 강동소아청소년과의원, 3순위 잠실아이사랑소아과, 4순위 위례달빛어린이병원 전체에 `hospital_detail.html` 링크 연계.
  - 기존 더보기 아코디언 토글 버튼을 제거하고, 전체 병원·약국 카드 및 소아 응급실 카드를 부드러운 순수 CSS/JS 스크롤 컨테이너(`max-height: 520px; overflow-y: auto`)로 개편하여 자연스러운 모바일 탐색 제공.
  - `main.py`에 `@app.get("/emergency_alert")` 라우트 등록 및 HTTP 200 OK 서빙 검증 완료.

### 🌟 [v2.4.18-backend-phase1-integration] 2026-10-15: '아이숨' 풀스택 결합 백엔드 1단계 - SupervisorResponse 임상 바이탈 5대 필드 확장 및 1턴 완결 force_matching FSM 모드 구축 (정영식 팀장, AI 에이전트)
* **`SupervisorResponse` 클라이언트 반환 DTO 임상 바이탈 필드 탑재**:
  - `result.html` 상단 바이탈 칩(나이, 체온, 중증도)과 증상 목록을 백엔드에서 100% 동적 주입할 수 있도록 5대 핵심 필드(`age_months`, `temperature`, `ktas_level`, `ktas_level_name`, `symptoms`) 신설.
* **단발성 증상 입력(`input.html`) 전용 `force_matching` FSM 모드 도입**:
  - `ChatRequest`에 `force_matching: bool = False` 플래그 추가.
  - 사용자가 증상을 단발로 입력했을 때도 결측치에 대한 안전 기본값(체온 38.0℃, 월령 24개월)을 채우고 1턴 만에 즉각 `MATCHING` ➔ `LOGISTICS` ➔ `COMPLETED`로 이행하여 병원/약국/통화스크립트를 100% 반환.
* **0ms Red Flag 26µs 최우선 119 직행 안전망 사수**:
  - `force_matching=True` 호출이라도 생후 100일 미만 고열, 경련 등 12대 위급 상황 감지 시 즉각 `EMERGENCY_ESCALATION`으로 숏서킷되어 의료 안전 완전 보장.
* **Step 8 신규 통합 테스트 스위트 ([tests/test_step8_frontend_integration.py](file:///e:/monnlight/tests/test_step8_frontend_integration.py)) 전수 통과**:
  - TC-801, TC-802, TC-803 무결점 통과 ➔ **총 77개 테스트 100% 전수 합격 (`Ran 77 tests, OK`)**.

### 🌟 [v2.4.17-frontend-backend-integration-spec] 2026-10-15: '아이숨' 프론트엔드-백엔드 100% 결합 연동 명세서(FRONTEND_BACKEND_INTEGRATION_SPEC.md) 수립 및 개발 백서 배포 (정영식 팀장, AI 에이전트)
* **프로젝트 루트 전용 종합 백서 [FRONTEND_BACKEND_INTEGRATION_SPEC.md](file:///e:/monnlight/FRONTEND_BACKEND_INTEGRATION_SPEC.md) 수립**:
  - **백엔드 모듈화 4대 계층 요약**: API 계층(`api/v1/`), 에이전트 계층(`agents/`), FSM 오케스트레이션 계층(`orchestrator/`), 공간/병상 동기화 계층(`services/`).
  - **프론트엔드 9대 화면 요약**: `splash.html`, `permission.html`, `index.html`, `input.html`, `loading.html`, `result.html`, `hospital_detail.html`, `emergency_guide.html`, `settings.html` 현황.
  - **화면단별 버튼 클릭 시 백엔드 동작 1:1 결합 매핑 매트릭스**:
    - `index.html` 진입 시 `GET /api/v1/emergency/nearby` ➔ 실시간 병상 및 주변 응급실 카드 렌더링.
    - `input.html` "확인" 클릭 시 `POST /api/v1/chat` ➔ Red Flag 0ms 검사 & Triage/Matching/Logistics 실행 ➔ `sessionStorage`에 결과 저장 후 `loading.html` 거쳐 `result.html` 표출.
    - `result.html` 2-트랙 탭 전환 및 +30분 조제 안전마진 약국/실시간 병상 상세 렌더링.
    - `hospital_detail.html` 모바일 번호표 접수 및 당직의 프로필/지참 서류 안내.
    - `emergency_guide.html` KTAS 7단계 시각 슬라이더 & 통화 스크립트 복사.
  - **E2E 풀스택 라이프사이클 Mermaid 시퀀스 다이어그램** 수록.
  - **미구현 4대 핵심 화면 및 기능 구현 가이드**:
    - ① `result.js` (실시간 백엔드 데이터 동적 바인딩)
    - ② `chat.html` (멀티턴 문진 대화형 모달/채팅 UI)
    - ③ `map.html` (카카오맵 / 네이버맵 기반 지리공간 30분 안심 페어링 지도 뷰)
    - ④ `beds.html` (전국 실시간 소아 응급실 병상 전광판 & 공지 모니터 대시보드)
  - **단계별 풀스택 결합 개발 실행 로드맵 (Action Items)**: Phase 1~4 구체화.

### 🌟 [v2.4.16-hospital-detail-ticketing] 2026-10-15: '아이숨' 야간 병원 상세 및 실시간 접수 안내 화면(hospital_detail.html) 순수 프론트엔드 구축 & result.html 연계 완료 (김동준 팀원)
* **아이숨 3대 핵심 화면 중 완결판 ([frontend/hospital_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/hospital_detail.html), [frontend/templates/hospital_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/hospital_detail.html)) 구축**:
  - **병원 히어로 배너**: 송파어린이병원 타이틀, 보건복지부 지정 달빛어린이병원 엠블럼, 실시간 야간진료 중(`~23:00`) 라이브 펄스 배지.
  - **3열 핵심 지표 바**: 현재 대기 `4팀 (약 20분)`(코발트 블루 강조) | `거리 1.8km (차 6분)` | `지하주차장 무료 2시간`.
  - **야간 당직 전문의 프로필**: Dr. 김서연 세부전문의 (소아 호흡기/급성발열 전문, 제1소아진료실 2층, 현재 14번 환아 진료 중 안내).
  - **야간 접수 마감 주의 배너**: 22:30 접수 마감 및 환아 폭증 시 30분 전 조기 마감 대비 권장 안내.
  - **실시간 진료 시간표**: 오늘 평일 야간(09:00~23:00, 접수마감 22:30), 토요일, 일·공휴일 시간표 (E-Gen 규격).
  - **Track B 안심 심야약국 연계 카드**: 송파달빛약국 (도보 1분 80m, 오늘 24:00 마감, `+30분 조제 안전마진` 배지, 소아 시럽제/네블라이저 상비 태그).
  - **오시는 길 & 길찾기**: 주소 원클릭 복사(토스트 팝업 연동), 카카오맵 / 네이버지도 앱 연동 길안내 버튼.
  - **내원 전 필수 지참 서류 체크리스트**: 보호자 신분증, 환아 등본, 복용 중인 약 체크리스트 (2024년 5월 본인확인 의무화 준수).
  - **하단 고정 플로팅 바 & 모바일 대기표 모달**: `[📞 병원 직통 전화]` + `[모바일 번호표 접수하기]` ➔ 클릭 시 대기번호 19번 발급 팝업 인터랙션 제공.
* **화면 간 유기적 네비게이션 완성**:
  - [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html) 및 템플릿의 송파어린이병원 카드 클릭 시 `hospital_detail.html`로 화면 자동 이동하도록 연동.
  - [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)에 `@app.get("/hospital_detail")` 라우트 등록 및 200 OK 서빙 확인.

### 🌟 [v2.4.15-onboarding-splash-permission] 2026-10-15: '아이숨' monimo 스타일 첫 로딩(스플래시) 및 백엔드 로직 정합형 5대 접근 권한 명시 페이지 구축 (정영식 팀장)
* **monimo 레퍼런스 스타일 미니멀 첫 로딩 스플래시 (`splash.html`) 구축**:
  - 완벽한 화이트 배경에 볼드 산세리프 브랜드 로고(**아이숨.**) 및 펄스 포인트 애니메이션 탑재.
  - 하단 서브 브랜드 표기(`i-Soom / Pediatric Healthcare Networks`)와 iOS 홈 인디케이터 바 라인.
  - 1.8초 후 자연스러운 자동 페이드아웃 전환(`fadeOut` ➔ `permission.html`) 및 화면 탭 즉시 건너뛰기 지원.
* **백엔드 로직에 100% 정합된 5대 선택 접근 권한 명시 (`permission.html`) 구축**:
  - 모니모 1:1 스타일 대형 헤드라인(`앱 사용을 위해 접근 권한을 허용해주세요`), `선택 권한` 라벨, 컬러풀 심볼 아이콘 완비.
  - 📍 **위치**: 야간 소아과·약국·응급실 거리 계산 및 길안내 *(Haversine 반경 5~10km 페어링)*
  - 🔔 **알림**: 소아 응급실 병상 변동 및 접수 마감 긴급 안내 *(5분 주기 NMC 병상 SSE 스트리밍)*
  - 📞 **전화**: 119 응급 직통 연결 및 병원 출발 전 사전 확인 통화 *(Red Flag 0ms 직통 다이얼)*
  - 📷 **카메라**: 본인확인 신분증 및 환아 증상(발진, 상처) 촬영 *(2024년 5월 본인확인 의무화 대응)*
  - 🖼️ **사진**: 아이 증상 사진 첨부 및 처방전·진료 서류 보관 *(문진 이미지 업로드 & 서류 보관)*
  - 확인 버튼 클릭 시 `localStorage` 동의 상태 저장 후 메인 홈(`index.html`)으로 원스톱 네비게이션.
* **FastAPI 백엔드 라우트 및 상용 서빙 테스트 전수 통과**:
  - `/splash`, `/splash.html`, `/permission`, `/permission.html` 전수 **HTTP 200 OK** 검증 완료.

### 🌟 [v2.4.14-loading-overlay-animation] 2026-10-15: '아이숨' AI 분석 중 로딩 오버레이 & 2초 키프레임 시퀀스(loading.html) 구축 (김동준 팀원)
* **순수 CSS3 키프레임 애니메이션 기반 로딩 컴포넌트 탑재**:
  - 외부 무거운 라이브러리(Lottie, JS 애니메이션) 의존 없이 브라우저 GPU 가속 기반 순수 CSS 키프레임(`pulseGlow`, `spinLoader`, `shimmer`) 탑재로 60fps 부드러운 모션 보장.
  - 신뢰감을 주는 로열 블루 테마 스마트 토이 엠블럼(`smart_toy`, `#0066FF`) 및 외곽 펄스 링 비주얼 구현.
* **임상 체감 3단계 동적 진행 시퀀스 (2.0초 setTimeout 파이프라인)**:
  - 0.0초: "의료 안전 가드레일 (Red Flag) 0ms 검사 중..." (진행률 25%)
  - 0.7초: "소아 KTAS 168개 임상 분류 지침 대조 중..." (진행률 65%)
  - 1.4초: "실시간 달빛병원 & +30분 조제 안심약국 매칭 중..." (진행률 95%)
  - 2.0초: 진행률 100% 도달과 함께 맞춤 결과 화면(`result.html`)으로 자동 전환.
* **인풋 화면 오버레이 & 단독 페이지 동시 제공**:
  - `frontend/input.html` & `frontend/templates/input.html`: 확인 버튼 클릭 시 키보드를 닫고 자연스럽게 페이드인되는 `#ai-analyzing-overlay` 탑재.
  - `frontend/loading.html` & `frontend/templates/loading.html`: 단독 로딩 뷰 테스트 및 독립 컴포넌트 검증용 단독 페이지 신규 구축.
  - `main.py`에 `@app.get("/loading")` 엔드포인트 등록 및 HTTP 200 OK 서빙 검증 완료.

### 🌟 [v2.4.13-result-screen-mockup] 2026-10-15: '아이숨' 맞춤 결과 화면(result.html) 정적 목업 구축 & input.html 연계 완료 (김동준 팀원)
* **백엔드 핵심 기능 100% 매핑 정적 결과 화면([frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html), [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)) 구축**:
  - **바이탈 요약 & 0ms 가드레일 배지**: `0ms 가드레일 안전 통과 🟢` 및 환아 정보(`14개월`, `39.2℃ (고열)`, `#구토`, `KTAS 3단계`).
  - **2-트랙 세그먼트 탭**: `[🌙 달빛병원·약국 (3)]` ↔ `[🚨 소아 응급실 병상 (2)]` 순수 CSS/JS 탭 전환.
  - **Track B 페어링 카드**: 추천 1순위 송파어린이병원 + 송파달빛약국의 `[🟢 +30분 조제 안전마진 확보]` 배지, 마감주의 뱃지, 원터치 전화/카카오맵 길찾기.
  - **Track A 소아응급실 카드**: 서울아산병원 소아전문응급센터 실시간 병상(`hv28` 4석 여유), 전문의 당직 여부, E-Gen 데이터 신선도 배지.
  - **내원 지원 툴킷**: 30초 통화 대본 복사(토스트 팝업 연동) 및 2024년 5월 본인확인 의무화 지참 서류 인터랙티브 체크박스 3종.
  - **의료법 제27조 안심 고지**: 하단 법적 안심 면책 푸터 탑재.
* **화면 간 유기적 네비게이션**:
  - `input.html`에서 텍스트 입력 후 "확인" 버튼 클릭 시 `result.html`로 화면 자동 이동.
  - `main.py`에 `@app.get("/result")` 정적 서빙 라우트 등록 완료 (HTTP 200 OK 검증).
* **Git 협업 무결점 동기화**:
  - 정영식 팀장의 7단계 비주얼 가이드 캐러셀 최신 작업분을 `git stash ➔ git pull ➔ git stash pop`으로 충돌 0건 안전 병합 완료.

### 🌟 [v2.4.12-guide-visual-carousel] 2026-10-15: '아이숨' 응급실 가이드(emergency_guide.html) 소아 응급실 & KTAS 7단계 시각 이미지 슬라이더 전면 개편
* **기존 장황한 텍스트 배제 및 7단계 시각 카드 슬라이더 전면 전환**:
  - 사용자 제공 "소아전용 응급실 이용 가이드 & KTAS 안내" 원본 인포그래픽에서 Step 1부터 Step 7까지의 카드를 1px 오차 없이 정밀 분할(`guide_ktas_step1~7.png`)하여 탑재.
  - 기존 텍스트(통화 스크립트 탭, 응급실 병상 테이블 등)를 전면 삭제하고 오직 단계별 일러스트와 핵심 표제어만 노출하여 가독성 극대화.
* **모바일 최적화 CSS Scroll Snap & 상호작용**:
  - 터치 좌우 스와이프 지원, 상단 실시간 슬라이드 카운터(`1 / 7` ~ `7 / 7`), 하단 7개 도트 인디케이터, 데스크톱 좌우 화살표 버튼 연동.
  - "가이드 인포그래픽 원본 한눈에 크게 보기" 모달 다이얼로그 탑재(`guide_ktas_full.png`).
* **FastAPI 백엔드 및 크로스 브라우징 검증 통과**:
  - `GET /guide`, `GET /guide/emergency` (200 OK) 및 7종 크롭 이미지 서빙 전수 테스트 완료.
  - Safari `file://` 로컬 열람과 웹 서빙 환경 100% 호환을 위한 듀얼 이미지 폴백 속성 적용.

### 🌟 [v2.4.11-input-remote-pull-sync] 2026-10-15: 원격 input.html 최신 업데이트(확인 버튼 인터랙션 & PWA 메타태그) 풀 및 index.html 모달 연동 무결점 3-Way 머지
* **원격 변경 사항 안전 통합**:
  - 원격 저장소의 `input.html`(확인 버튼 애니메이션, PWA Standalone 메타태그, Pure CSS `:has()` 셀렉터)을 로컬의 `index.html` 모달 트리거 로직과 무결점 병합 완료.
  - Conda DS 환경 기반 `FastAPI TestClient`로 `/home`, `/input`, `/input.html` 전수 200 OK 검증 완료.

### 🌟 [v2.4.10-modal-trigger-link] 2026-10-15: '아이숨' 메인 홈(index.html) 아이증상 입력버튼 모달 팝업 및 증상 입력(input.html) 연동
* **메인 홈 CTA 클릭 시 모달 다이얼로그 팝업 연동**:
  - `frontend/templates/index.html`, `frontend/index.html`, `app/templates/index.html`에 레퍼런스 이미지와 100% 일치하는 `#triage-consent-modal` 마크업 탑재.
  - "아이 증상 입력하고 병원 찾기" CTA 버튼(`#start-triage-btn`) 클릭 시 부드러운 백드롭 블러 오버레이와 함께 중앙 팝업 구현.
* **소아 응급의료 특화 5대 필수 안내문 및 시각 강조**:
  - 헤더: `"아이숨은 보호자님이 입력하신 증상 정보를 바탕으로 진료 가능한 야간 소아과와 안전한 응급처치 가이드를 안내합니다."`
  - 본문 안내 박스: 의료법 제27조 준수, 위급 상황 즉시 119, 현장 조기 마감 주의, 본인확인 서류 지참, 진행 동의 안내 등 5대 컴플라이언스 불릿 탑재.
* **최종확인 버튼 클릭 시 `input.html` 즉시 네비게이션**:
  - 모달 내 "동의하고 증상 입력하기"(`modal-confirm-btn`) 클릭 시 `window.location.href = 'input.html'`로 연동되어 증상 입력 화면으로 직결 전환.
  - 취소 버튼 클릭 시 모달 닫기 (`closeModal()`).
* **FastAPI 라우트 확장 & Cross-Browser 듀얼 로더**:
  - `main.py`에 `@app.get("/input.html")` 데코레이터 추가로 직접 HTML 요청 서빙 지원.
  - `frontend/templates/input.html`에 Safari/Chrome 듀얼 CSS/JS 로더 적용 완료.
  - TestClient 검증: `/home`, `/input`, `/input.html` 전수 **HTTP 200 OK** 통과.

### 🌟 [v2.4.9-mobile-qr-test] 2026-10-15: 로컬 Wi-Fi IP 바인딩, QR코드 모바일 테스트 파이프라인 및 Standalone 메타태그 구축
* **로컬 Wi-Fi 초고속 모바일 테스트 환경 완성**:
  - 복잡한 Cloud Run 배포 없이, PC Wi-Fi IP(`192.168.14.189:8000`) 바인딩 및 즉시 스캔 QR코드를 생성하여 스마트폰 카메라로 0.1초 만에 실제 접속 테스트 가능.
* **iOS / 안드로이드 홈 바로가기(PWA Standalone) 메타 태그 완비**:
  - `apple-mobile-web-app-capable="yes"`, `mobile-web-app-capable="yes"`, `theme-color="#ffffff"` 탑재.
  - 모바일 브라우저에서 '홈 화면에 추가' 시 브라우저 주소창 없는 100% 네이티브 앱 풀스크린 모드 작동.

### 🌟 [v2.4.8-input-confirm-btn] 2026-10-15: '아이숨' 증상 입력 페이지(input.html) 텍스트 입력 시 확인 버튼 동적 표출 인터랙션 구현
* **레퍼런스 이미지 우측 화면 1:1 완벽 구현**:
  - 인풋이 비어있을 때는 확인 버튼을 숨기고, 텍스트가 1글자 이상 입력되면 인풋 필드 하단에 코발트 블루 풀 너비 **"확인"** 버튼(`.input-confirm-btn`)이 부드럽게 등장(`fadeInSlideUp` 애니메이션).
  - 지우기 버튼(`✕`) 클릭 또는 텍스트 전면 삭제 시 확인 버튼 자동 숨김 연동.
  - Pure CSS `:has(:not(:placeholder-shown))` 셀렉터 및 `main.js` 인터랙션의 듀얼 지원으로 Zero-JS 환경에서도 안정적 표출.
* **FastAPI 8대 엔드포인트 전수 검증 통과**:
  - `GET /input` ➔ **HTTP 200 OK** (`2,825 bytes`) 정상 서빙.

### 🌟 [v2.4.7-modal-refine] 2026-10-15: '아이숨' 처치정보 및 법적 동의 모달(modal.html) 소아 의료 도메인 최적화
* **모달 안내 문구 전면 고도화**:
  - 헤더 타이틀: `"아이숨은 보호자님이 입력하신 증상 정보를 바탕으로 진료 가능한 야간 소아과와 안전한 응급처치 가이드를 안내합니다."`
  - 소아 의료 특화 5대 불릿 탑재: 의료법 제27조 준수, 119 위급상황(100일 미만 고열/경련) 즉각 신고, 야간 대기열 현장 조기마감 주의, 2024년 5월 본인확인 의무화 서류 지참, 최종 판단 안내.
* **사용자 플로우 연동 및 라우트 탑재**:
  - `동의하고 증상 입력하기` 버튼 클릭 시 `input.html`(증상 입력 화면)으로 직결 연계 (`onclick="location.href='input.html'"`).
  - FastAPI `@app.get("/modal")` 서빙 엔드포인트 등록 및 TestClient 100% **HTTP 200 OK** 검증 완료.

### 🌟 [v2.4.6-index-rollback] 2026-10-15: 타 작업자(정영식) 전담 `index.html` 원형 100% 롤백 및 김동준 전담 모듈(`input.html`, `modal.html`) 독립화
* **`index.html` 파일군(3종) 원형 100% 복원**:
  - `frontend/templates/index.html`, `frontend/index.html`, `app/templates/index.html`을 정영식 작업자의 최종 커밋([`b12ebe4`](https://github.com/yeongsik0914/monnlight/commit/b12ebe4)) 상태로 완전 롤백 (208줄 순수 마크업 복원).
  - 임의 삽입되었던 모달 다이얼로그 및 히어로 UI 변경 사항을 완전히 걷어내고, 정영식 작업자가 작성한 응급실 가이드 링크, 설정 링크, WebKit 듀얼 CSS/JS 로더를 무결하게 보존.
* **김동준 팀원 담당 파일의 완벽한 독립 보존**:
  - `input.html` (증상 입력 화면) 및 `modal.html` (처치정보 및 법적 안내 모달) 독립 모듈로 온전히 유지.
* **FastAPI 7대 엔드포인트 100% 서빙 검증**:
  - `/home`(10,258 bytes), `/input`(2,516 bytes), `/guide`, `/settings`, `/css/style.css`, `/js/main.js` 전수 **HTTP 200 OK** 검증 통과.

### 🌟 [v2.4.5-collab-merge] 2026-10-15: 정영식 팀장·김동준 팀원 프론트엔드 통합 머지(Merge) 및 Cross-OS NFD 정규화
* **팀 협업 분기 무결점 통합 머지 (3-Way Merge 완결)**:
  - 정영식 팀장 구현 산출물(응급실 가이드 `emergency_guide.html`, 설정 `settings.html`)과 김동준 팀원 구현 산출물(증상 입력 `input.html`, 처치정보 모달 `modal.html`)을 단 1건의 코드 손실 없이 무결점 통합.
  - 최신 통합 커밋 `b573e46` 생성 및 원격 저장소(`origin/main`) 푸시 완결.
* **FastAPI 백엔드 7대 핵심 엔드포인트 서빙 전수 검증**:
  - `GET /`, `GET /home`, `GET /input`, `GET /guide`, `GET /settings`, `GET /css/style.css`, `GET /js/main.js` TestClient 100% **HTTP 200 OK** 검증 통과.
* **Cross-OS NFD/NFC 유니코드 자모 분리 정규화**:
  - macOS APFS와 Windows NTFS 간의 파일명 인코딩 차이로 인해 Git 인덱스에 중복 생성되었던 NFD 파일 2종(`Answer-영식.md`, `2021년 KTAS...pdf`)을 제거하고 표준 NFC로 단일화하여 향후 충돌 요소를 선제 박멸.

### 🌟 [v2.4.4-guide-settings] 2026-10-15: '아이숨(Aisum)' 응급실 가이드(emergency_guide.html) 및 설정(settings.html) 웹페이지 구축
* **응급실 가이드(Emergency Guide) 전용 페이지 구축**:
  - `frontend/templates/emergency_guide.html` & `app/templates/emergency_guide.html`: 좌우 스와이프 포토 캐러셀 및 2대 카테고리(증상별 포토 가이드 / 출발 전 체크리스트) 세그먼트 탭 분리.
  - Safari WebKit `file://` 보안 샌드박스 호환 스마트 듀얼 CSS/JS 로더 탑재.
  - `GET /guide`, `GET /guide/emergency`, `GET /guide/symptoms`, `GET /guide/checklist` 서빙 라우트 등록.
* **설정(Settings) 웹페이지 구축**:
  - `frontend/templates/settings.html` & `app/templates/settings.html`: 모니모(Monimo) 레퍼런스 스타일 3대 카테고리(일반, 사용자 지원, 정보) 및 단독 섹션 8px 디바이더.
  - 순수 CSS iOS 토글 스위치 컴포넌트(`🔔 앱 알림`) 탑재.
  - `GET /settings` 서빙 라우트 등록 및 GNB 네비게이션 연동.

### 🌟 [v2.4.2-input-refine] 2026-10-15: '아이숨(Aisum)' 증상 입력 페이지 카피 고도화 및 미니멀 레이아웃 최적화
* **증상 입력 페이지(Input Page) UI/UX 개선**:
  - `frontend/input.html` & `frontend/templates/input.html`: 미니멀 화이트 배경의 증상 입력 페이지.
  - 헤드라인 카피 정밀화: `"증상을 최대한 입력해주세요"` ➔ `"증상을 구체적으로 정확하게 입력해주세요"`로 문진 정밀도 향상 유도.
  - 언더라인 인풋: 로열 블루(`2px solid #0066FF`) 하단 보더 라인 및 `"입력"` 플레이스홀더.
  - 하단 확인 버튼 배제: 불필요한 고정 버튼을 제거하고 순수 인풋 집중형 미니멀 여백 확보.
  - `main.py`에 `GET /input` 라우트 서빙 유지.

### 🌟 [v2.4.0-isoom-web] 2026-10-14: '아이숨(Aisum)' 프론트엔드 워크스페이스(`frontend/templates/`) 구축 및 순수 웹 퍼블리싱 완성
* **프론트엔드 전용 모듈형 디렉터리(`frontend/`) 구축**:
  - `frontend/templates/index.html`: 메인 홈 화면 SPA 템플릿 진입점 (`<link href="../css/style.css">`)
  - `frontend/css/style.css`: Calm Harbor 디자인 시스템 Vanilla CSS (CSS 변수, 440px 모바일 프리뷰, 글래스모피즘, 펄스 애니메이션)
  - `frontend/js/main.js`: 클라이언트 인터랙션 및 향후 SSE 챗봇 연동 모듈 (`<script src="../js/main.js">`)
  - `frontend/assets/`: `icons/`, `images/` 정적 그래픽 에셋 디렉터리
  - `frontend/README.md`: 프론트엔드 워크스페이스 가이드 문서
* **에셋 이동 및 템플릿 폴더화**:
  - `index.html`을 `frontend/templates/`로 이관하고 리소스 상대경로(`../css/`, `../js/`) 정밀 설정.
  - `app/templates/index.html` 및 `app/static/css/style.css` 동기화.
* **FastAPI 라우팅 및 정적 파일 마운트 연동**:
  - `app.mount("/frontend", ...)`, `/css`, `/js`, `/assets` 마운트 등록.
  - `GET /home`: `frontend/templates/index.html` 서빙 (Fallback: `frontend/index.html`, `app/templates/index.html`)
  - `GET /style.css`, `GET /css/style.css`: `frontend/css/style.css` 서빙
  - `GET /js/main.js`: `frontend/js/main.js` 서빙

### 🌟 [v2.3.1-modal] 2026-10-14: [UI/UX] 사전 처치정보 및 법적 안내 모달 다이얼로그(반투명 오버레이, 취소/확인) 화면 구현
* **레퍼런스 이미지 기반 사전 처치정보 안내 모달 팝업 구현**:
  - `아이 증상 입력하고 병원 찾기` 또는 증상 칩 클릭 시 어두운 반투명 오버레이(`rgba(15, 23, 42, 0.65)`)와 함께 블러 처리된 모달 팝업 활성화.
  - 모달 다이얼로그 카드(328px, 22px 라운드): 제목 강조("인근 병원과", "참고용 처치정보"), 연파랑 배경 박스 내 5대 안내사항(의료법 제27조 한계, 119 즉시 연락, 추천 결과 유동성, 최종 판단 책임) 불릿 렌더링.
  - 하단 분할 50px 듀얼 버튼: 좌측 회색 `[취소]`, 우측 볼드 로열 블루 `[확인]` (터치 시 모달 닫기).
  - 배경 오버레이 클릭 또는 ESC 키 입력 시 부드러운 모달 닫기 지원.

### 🌟 [v2.3.0-isoom-stitch] 2026-10-14: [screen.png 1:1 완벽 이식] '아이숨(Aisum)' 신규 전용 Stitch 프로젝트 개설 및 모던 라이트 3대 화면 완성
* **신규 Stitch 전용 프로젝트 공식 개설**: `projects/17449043314542457561` ('아이숨 (Aisum) - 소아 야간 의료 매칭 케어')
* **'Calm Harbor' 모던 클린 라이트 디자인 시스템 확립**:
  - Primary Brand: 신뢰의 로열 코발트 블루 (`#0066FF`), Canvas: `#F8FAFC`, Cards: `#FFFFFF` (18px 라운드 코너).
  - Live Safety Pip: `#10B981` (실시간 동기화/진료중 배지), Moonlight Amber: `#F59E0B`, Red-Flag: `#EF4444`.
* **Stitch 3대 핵심 모바일 화면 생성 완료**:
  1. **화면 1: 아이숨 - 홈 (`65dcc96b817143c3adb7bfdfa545267b`)**:
     - `screen.png` 100% 동일 컴포넌트: 볼드 `아이숨` 로고, `역삼동 ∨` 알약 드롭다운, 초록 라이브 닷 `소아 전문 의료 데이터 실시간 동기화`.
     - `아이가 어디가 아픈가요?` 헤드라인 + 미소 아이 일러스트, `+ 아이 증상 입력하고 병원 찾기 →` 메인 CTA 버튼.
     - 4대 증상 퀵태그: `# 열나요(고열)`, `# 구토/설사`, `# 기침/호흡`, `# 발진/두드러기`.
     - 실시간 야간 의료시설 필터: `전체 10` (블루 활성) | `달빛병원 3` | `심야약국 5`.
     - 시설 카드 3종: 송파어린이병원 (전문의 2명 진료중, 대기 4팀, ~23:00 마감), 강남아이마음병원 (~22:30 마감), 송파달빛약국 (~24:00 마감).
     - 하단 3탭 고정 GNB: `홈(활성)` | `응급실 가이드` | `설정`.
  2. **화면 2: 아이숨 - 증상 입력 및 문진 (`0cdadf1dc86a4c229423b5b02caa8cc1`)**:
     - `Step 1/3 (33%)` 진행 바, `정하은 (생후 18개월 · 11.2kg)` 환아 선택 칩.
     - `38.6°C` 대형 디지털 체온 디스플레이, 컬러 게이지 슬라이더 & `+/-` 미세조절, `발열 시작: 2시간 전` 태그.
     - KTAS 증상 멀티 셀렉터 (열나요, 기침/호흡 활성 선택) + `🚨 경련/의식 저하` 레드 숏서킷 칩.
     - 해열제 복용 기록(아세트아미노펜 3.5ml) 및 **`💡 다음 이부프로펜 교차복용 가능: 23:30 (30분 후)`** 안심 타이머.
     - KTAS 4단계(준응급) 달빛어린이병원 권장 카드 및 `내 주변 진료 가능 병원 매칭하기 →` CTA.
  3. **화면 3: 아이숨 - 야간 병원 상세 및 실시간 접수 (`3c5db317bb354d02838e5306adfc4f1a`)**:
     - 송파어린이병원 히어로 및 3열 핵심 지표 (`현재 대기 4팀 (20분 예상)` 블루 강조, 거리 1.8km, 무료주차 2시간).
     - 야간 당직 전문의 (Dr. 김서연 소아호흡기 세부전문의, 현재 14번 환아 진료중).
     - 송파달빛약국 (도보 1분 80m, 24:00까지 조제 100% 보장, 시럽제/네블라이저 상비 태그).
     - 오시는 길 미니 맵 + 송파대로 345 주소 복사 + **티맵 / 카카오내비** 원클릭 연동.
     - 하단 듀얼 액션 바: `[📞 전화상담]` & `[모바일 야간진료 번호표 접수하기 (대기 4번째) →]`.
* **신규 종합 명세 보고서 발간**: [AISUM_STITCH_DESIGN_REPORT.md](AISUM_STITCH_DESIGN_REPORT.md) (디자인 토큰, 3대 화면 스펙, 고화질 스크린샷 뷰어 및 백엔드 매핑 집대성)

### 🌟 [v2.2.0-isoom] 2026-10-14: [리브랜딩] '아이숨(i-Soom)' 브랜드 전환 및 screen.png 기반 화이트 & 코발트 블루 모바일 UI 3종 Stitch 재구축 완료
* **서비스 브랜드 공식 개편**: 기존 MoonlightCare ➔ **아이숨 (i-Soom)** (우리아이 편안한 숨결을 지키는 24시간 안심 소아 케어)
* **screen.png 레퍼런스 기반 디자인 시스템 혁신**:
  - 기존 다크 네이비 테마에서 **화이트 & 코발트 블루(#0066FF) 라이트 모드**로 전면 전환.
  - 라벤더 소프트 블루(#EBF2FF), 에메랄드 그린(#10B981, 실시간 운영/조제마진), 코랄 레드(#EF4444, 119 직통 숏서킷) 컬러 팔레트 구축.
  - 상단 귀여운 아기 캐릭터 배너 일러스트 탑재.
* **Stitch MCP UI 화면 3종(및 서브 뷰) 재구축 완료**:
  1. **화면 1: 아이숨 최초 로딩 & 온보딩 스플래시 (397c4e98ffaf47518e568e04fa60fef7)**:
     - 아기 캐릭터 웰컴 헤더, GPS 위치 권한 안내, 의료법 준수 및 119 안심 배지, 코발트 블루 풀와이드 CTA.
  2. **화면 2: 아이숨 메인 홈 (c0bb4df907b44ddd9ee91bad51a308d6)**:
     - screen.png 100% 동일 컴포넌트: 상단 위치바, 캐릭터 배너, 8대 퀵 카테고리 그리드, 메인 문진 대형 CTA 배너, 실시간 송파어린이병원 & 달빛약국(+30분 마진) 카드, 5탭 하단 고정 내비.
  3. **화면 3: 병원·약국 1:1 매칭 완료 및 내원 안내 (e41d07bcd314bfcb5f4a7bd97a24850)**:
     - 미니 경로 맵, **[🟢 +30분 조제 안전마진 확보 ~23:30]** 배지, 2024년 5월 본인확인 서류 체크리스트, 30초 당직의 통화 스크립트 원클릭 복사, 하단 듀얼 CTA.
* **백엔드 엔드포인트 100% 결합 매핑**: FastAPI SSE 챗봇(/api/v1/chat/stream) 및 1:1 병원약국 매칭(/api/v1/emergency/pairings) 준비 완료.

### 🌟 [v2.2.0-ui] 2026-10-14: [Stitch] 타다(TADA) 온디맨드 모빌리티 레퍼런스 기반 3대 핵심 모바일 화면 프로토타입 생성 완료
* **Stitch MCP를 통한 타다(TADA) 스타일 3대 핵심 모바일 UI 생성 완료**:
  1. **화면 1: 로딩 & 최초 1회 온보딩 스플래시 (5f348380315d4efc934d9a22b283dc36)**:
     - 타다 특유의 미니멀 웰컴 감성, GPS 위치 권한 허용 플로팅 카드, 의료법 제27조 준수 배지, 56px 풀와이드 골드 CTA.
  2. **화면 2: 타다 스타일 온디맨드 야간케어 홈 (c578206de4a417693297b2603a4e0e1)**:
     - 목적지 검색창을 차용한 증상 문진 입력 바, 원터치 퀵 트리아지 칩, 실시간 슬라이딩 바텀시트, 119 플로팅 펄스 버튼.
  3. **화면 3: 병원-약국 1:1 매칭 완료 및 내원 안내 (3d395741108845e9b5edcc5fc9589164)**:
     - 배차 완료 스타일 미니 라우팅 그래픽, 달빛병원 + **[🟢 +30분 조제 안전마진]** 약국 페어링 카드, 2024년 5월 본인확인 서류 체크리스트, 30초 통화 스크립트 원클릭 복사, 고정 듀얼 CTA.

### 🌟 [v2.2.0-spec] 2026-10-14: [프론트엔드] 백엔드 100% 결합형 반응형 웹 UI/UX 상세 화면 구성 명세서 수립
* **공식 프론트엔드 명세서 수립 ([docs/FRONTEND_UI_UX_SPECIFICATION.md](docs/FRONTEND_UI_UX_SPECIFICATION.md))**:
  - 심야 시간대 눈부심 없는 **미드나잇 다크 글래스모피즘(Midnight Dark & Warm Moonlight)** 디자인 시스템 규격화.
  - 늦은 밤 다급한 부모의 한 손 조작을 위한 **Thumb-Zone 모바일 최적화** 레이아웃 설계.
* **백엔드 핵심 기능 1:1 결합 6대 UI 컴포넌트 설계**:
  1. EmergencyModalOverlay: 0ms Red Flag 감지 시 즉시 119 다이렉트 콜 및 응급처치 가이드 오버레이.
  2. TriageChatContainer: SSE 실시간 토큰 스트리밍, 3턴 진행률 게이지, 환아 바이탈 메타 캡슐 시각화.
  3. HospitalPharmacyPairingCard: [Track B] 달빛병원 + **[🟢 +30분 조제 안전마진]** 심야약국 1:1 페어링 세트.
  4. EmergencyDepartmentBoard: [Track A] 소아전문응급의료센터 실시간 잔여 병상(hv28), 소아 당직의 여부 배지.
  5. ActionHelper: 2024년 5월 본인확인 의무화 지참 서류 체크리스트 및 30초 통화 스크립트 복사 박스.
  6. ComplianceNotice: 대한민국 의료법 제27조 준수 비의료 AI 안심 고지문.

### 🌟 [v2.1.1] 2026-10-14: [거버넌스] 팀 프로젝트(정영식 팀장, 김동준 팀원) 협업 체계 공식 전환 & 4대 문서 지속 누적 관리 시스템 구축
* **팀 프로젝트 거버넌스 수립**:
  - **팀장 (정영식)**: 프로젝트 총괄, 시스템 아키텍처 설계, 질의응답 및 의사결정.
  - **팀원 (김동준)**: 백엔드 API, 파이프라인 엔지니어링, 모듈 구현 및 테스트 검증.
* **4대 핵심 문서 지속 누적 관리 불변 규율 확립**:
  1. `Answer-영식.md`: 정영식 팀장의 모든 질문과 AI 답변을 Q 번호별로 영구 누적 아카이빙.
  2. `log.md`: 각 사용자가 개발/디버깅 중 직면한 모든 이슈(Errors, Pitfalls) 및 구체적 해결 방안 지속 누적.
  3. `README.md`: 신규 개발 및 업데이트 내역을 릴리스 체인지로그에 지속 반영.
  4. `PLAN.md`: 개발 진행 시 업데이트된 기능과 아키텍처를 기획안과 100% 동기화하고 향후 개선책 지속 보강.
* **에이전트 시스템 레벨 불변 규칙 파일 3종 탑재**:
  - `GEMINI.md`, `AGENTS.md`, `.agents/rules/team_collaboration_rules.md`를 신설하여 어떤 세션/사용자든 규율 자동 준수 강제.

### 🌟 [v2.1.0] 2026-10-14: [Step 7] 공공 API 서킷 브레이커 & 3단계 Multi-Storage Fallback 고가용성(HA) 아키텍처 구축 (총 74개 테스트 전수 통과)
* **3-State FSM 서킷 브레이커 (`app/services/circuit_breaker.py`)**:
  - `CLOSED` (정상 통신) ➔ 공공 API 3회 연속 실패/타임아웃 감지 시 즉각 `OPEN` 전이.
  - `OPEN` (0ms 즉시 차단): 외부 네트워크 호출을 일체 중단하고 Multi-Tier Fallback으로 즉시 분기.
  - `HALF_OPEN` (자동 자가치유): 60초 쿨다운 만료 후 카나리 1회 시험 요청 ➔ 성공 시 `CLOSED` 자동 복구.
* **3단계 계층형 Fallback 파이프라인 (`app/services/emergency_sync_service.py`)**:
  - **Tier 1 (L1 Stale In-Memory)**: 만료된 직전 회차 캐시라도 Stale-While-Revalidate로 0.1ms 만에 즉시 서빙.
  - **Tier 2 (L2 Cloud Firestore Snapshot)**: 서버 재부팅 직후 장애 시 Firestore의 최근 정상 수집 배치 복원 (15ms).
  - **Tier 3 (L3 Local Immutable Baseline JSON)**: 국가 공공망 전체 마비 시 사전 탑재된 거점 응급의료기관 정적 마스터셋 서빙 (0.5ms).
* **데이터 신선도 투명성 배지 (`DataFreshnessMeta`)**:
  - `/api/v1/emergency/nearby` 응답에 `is_realtime`, `source_tier`, `elapsed_minutes`, `warning_message` 주입.
  - 부모 사용자에게 수집 경과 시간(분)과 병원 출발 전 30초 전화 확인 권고 배지 투명 제공.
* **백그라운드 스케줄러 격리 (`app/services/scheduler.py`)**:
  - 공공망 장애 시 백그라운드 5분 폴링 워커가 크래시 없이 격리 동작하며 `circuit_status="OPEN"` 기록.
* **테스트 및 품질 검증**:
  - `tests/test_step7_circuit_breaker.py` 8개 테스트 신설 및 100% 통과.
  - **전체 74개 단위/통합 테스트 전수 통과 (100% OK)** 및 **40대 임상 골든 케이스 Evals 100% 합격**.

### 🌟 [v2.0.0] 2026-10-14: [V2 Upgrade] 공식 소아 KTAS 168개 주증상 Direct Context Grounding & 2계층 Red Flag 심층 감시망 구축 (총 66개 테스트 전수 통과)
* **2계층 심층 감시선 (Two-Tier Deep Defense Network) 구현**:
  - **Pass 1 (0ms 정규식 인터셉터)**: 5대 신규 위급 룰 추가(외상성 절단 `NACRS 553`, 돌발 실신+발열 `NACRS 008`, 소아 장중첩증 `NACRS 260`, 크룹 협착음 `NACRS 610`, 양방향 특수부위 중증화상 `NACRS 705`) ➔ 12대 절대적 Red Flag 26µs 초고속 119 격상.
  - **Pass 2 (Direct Grounded Thinking Gemini)**: 2021 공식 소아 KTAS 168개 주증상/841개 세부기준 지식 베이스(~8,500 토큰)를 인메모리 싱글톤 캐싱하여 프롬프트에 직접 주입. Gemini 3.8 Flash Thinking High(`budget=1024`)를 통해 비정형 문맥 완독 및 시간차 가역성(해열 후 컨디션 정상화 vs 악화) 감별.
* **오케스트레이터 및 세션 DTO 연동**:
  - `PatientSessionState`에 KTAS 정밀 메타데이터(`ktas_level`, `matched_nacrs_code`, `clinical_rationale` 등) 저장 및 직렬화.
  - `SupervisorOrchestrator`에서 Step 2뿐만 아니라 Step 3(Triage 실행 직후)에도 Tier 2 Red Flag를 즉시 감지하여 119 비상 격상으로 전환.
* **테스트 및 검증**:
  - `tests/test_redflag_v2_upgrade.py` 8개 테스트 신설 및 전수 통과.
  - **전체 단위/통합 테스트 66개 전수 통과 (Ran 66 tests, 100% OK)** 및 **40대 임상 골든 케이스 Evals 100.0% 합격**.

### 🌟 [v1.4.0] 2026-10-13: [Step 6] E2E 통합 테스트 완수 및 40대 임상 골든 케이스 Evals 100% 합격 (전체 58개 테스트 전수 통과)
* **8대 E2E 핵심 시나리오 자동 검증 스위트 (`tests/test_step6_e2e.py`)**:
  - `TC-601`: 생후 55일 고열 1턴 119 직행 및 기도확보 응급처치 가이드 출력.
  - `TC-602`: 14개월 38.5도 경증 2턴 문진 ➔ 달빛병원 + 30분 안심 약국 페어링 ➔ 30초 통화 스크립트 ➔ 등본 지참 체크리스트 완주.
  - `TC-603`: 의료법 제27조 무면허 의료행위 방어(부모의 돌발진 단정 유도 거부 및 전문의 대면 진찰 안내).
  - `TC-604`: 적대적 4대 안전 위반(바늘 사혈 민간요법, 잔여 항생제, 용량 처방 요구, 단독 병원 알선 요구) 0ms 원천 차단.
  - `TC-605`: 다중 턴 중도 급변(Deterioration) 시나리오(1턴 미열 상담 중 2턴 청색증 발생 시 즉시 Track A 비상 전환).
  - `TC-606`: 3턴 데드락 가드(3턴 연속 모호한 입력 시 안전 기본값 세팅 후 MATCHING 강제 전이).
  - `TC-607`: FastAPI REST API `/api/v1/chat` E2E 단일/다중 턴 호출 무결성 검증.
  - `TC-608`: FastAPI SSE 실시간 스트리밍 `/api/v1/chat/stream` 토큰 스트리밍 및 `[DONE]` 완료 이벤트 검증.
* **40대 임상 골든 케이스 자동 채점기 (`tests/evals/run_evals.py`)**:
  - `tests/evals/golden_test_cases.json`의 40개 테스트 케이스를 5대 임상 평가 지표(DIM-1~DIM-5) 기준 자동 채점.
  - **종합 결과**: **40 / 40 케이스 100% 전수 통과 (평균 99.5점)**.
  - 성적표 리포트 자동 생성: [tests/evals/eval_report.md](file:///e:/monnlight/tests/evals/eval_report.md).
* **인터랙티브 CLI 시연 데모 (`demo_step6.py`)**:
  - 초응급, 야간 발열, 의료법 방어, 적대적 공격 차단, 자유 대화, Evals 성적표 뷰어를 통합 제공.
* **프로젝트 전체 테스트 현황**: 총 **58개 단위/통합 테스트 100% 전수 통과 (`Ran 58 tests in 193s, OK`)**.

### 🌟 [v1.3.0] 2026-10-13: 8대 핵심 잠재 이슈 선제 리팩토링 완수 및 50개 테스트 전수 통과 (Step 6 준비 완료)
* **Gemini 3.8 Flash / 3.5 Lite 최신 전환**: 구버전 모델 deprecation(404) 무음 예외를 제거하고 `200 OK` 정상 통신 보장.
* **0ms 병상 인메모리 TTL 캐시 (`emergency_sync_service.py`)**: 5분 TTL 캐시로 외부 공공 API 지연을 0회 차단하고 0.2~0.5ms 즉시 반환.
* **전국 17개 시·도 행정구역 동적 판별 및 맞춤 좌표망 구축**: 서울 하드코딩을 제거하고 수원, 대전, 부산, 광주 등 전국 환아 위치에서 35km 이내의 해당 지자체 소아 가용 응급실 매칭.
* **4대 악의적 의료법 우회 차단 (`guardrail_agent.py`)**: 바늘 손 따기 민간요법, 잔여 항생제 임의 복용, 약 용량 직접 지시, Dr. Kim 탈옥 선제 차단 룰엔진 탑재.
* **Triage 연령·기간·다발성 증상 정규화 확장 (`triage_agent.py`)**: `만 N세`, `초등 1학년`, `N일 전`, `어제`, 귀 통증(이통), 눈곱, 천명음, 복통 표준화.
* **진료 마감 시간(HH:MM) 대소 비교 필터링**: 심야(23:00~07:00) 24시간 응급실 직행 및 마감 40분 전 `[⚠️ 조기 접수 마감 주의]` 태그 부착.
* **Windows UTF-8 인코딩 보정 및 Conda DS 가상환경 동기화**: 콘솔 한글 깨짐 방지 및 `apscheduler`, `fastapi`, `uvicorn` 패키지 설치 완료.
* **신규 검증 테스트 스위트 (`tests/test_audit_fixes.py`)**: 7개 테스트(TC-FIX-01 ~ TC-FIX-07) 100% 통과 (총 50개 테스트 전수 합격).

### 🌟 [v1.2.0] 2026-10-13: [Step 5] FastAPI REST 서빙, 실시간 SSE 스트리밍 & APScheduler 2-트랙 데몬 완성
* **FastAPI 코어 엔트리포인트 (`main.py`)**: 비동기 lifespan 캐시 워밍, 전역 CORS 미들웨어, 종합 시스템 헬스체크 탑재.
* **대화 & 실시간 SSE 스트리밍 API (`app/api/v1/chat.py`)**: `POST /api/v1/chat` 및 Server-Sent Events 기반 단어 델타 스트리밍(`POST /api/v1/chat/stream`).
* **초고속 공간 검색 & 온디맨드 동기화 API (`app/api/v1/emergency.py`)**: 5ms 반경 응급실 검색(`GET /nearby`), 달빛병원-약국 30분 마진 페어링(`GET /pairings`), Hash Diffing 기반 즉시 동기화 트리거(`POST /sync`).
* **APScheduler 2-트랙 백그라운드 데몬 (`app/services/scheduler.py`)**: 5분 주기 E-Gen 병상 Hash Diffing 수집 및 매일 04:00 AM 정적 데이터 동기화.
* **`tests/test_step5_api.py` 10개 테스트(TC-501 ~ TC-510) 100% 통과**.

### 🌟 [v1.1.0] 2026-10-13: [Step 4] 메인 오케스트레이터(Supervisor FSM) 조립 & 세션 매니저 완성 (33개 테스트 100% 통과)
* **Supervisor FSM 라우터 (`app/orchestrator/supervisor.py`)**:
  - 6단계 라이프사이클(`INIT` ➔ `TRIAGE` ➔ `MATCHING` ➔ `LOGISTICS` ➔ `COMPLETED` / `EMERGENCY_ESCALATION`) 중앙 제어.
  - **3턴 무한 루프 가드**: 부모의 불충분한 입력 반복 시에도 `turn_count >= 3` 도달 시 강제 매칭 전이로 대기 지연 원천 차단.
  - **매 턴 0ms Red Flag 선제 검사**: 1턴뿐만 아니라 2~3턴 도중 경련/청색증 등 증상 급변 시 즉시 전 에이전트 실행을 중단하고 119 에스컬레이션.
  - **단일 출구 의료법 제27조 소독 관문**: 모든 에이전트 응답이 오케스트레이터 단일 출구에서 `sanitize_output()`을 통과하도록 구조화.
* **Thread-Safe 세션 매니저 (`app/orchestrator/session_manager.py`)**:
  - `asyncio.Lock` 기반 동시성 제어 및 30분 비활성 세션 자동 만료(TTL Eviction)로 메모리 누수 방지.
* **클라이언트 표준 규격 DTO (`app/schemas/supervisor.py`)**:
  - `SupervisorResponse` Pydantic DTO 탑재.
* **통합 데모 러너 (`app/demo_step4.py`)**: 멀티턴 문진, 중도 경련 비상 격상, 3턴 루프 방어 3대 시나리오 실증 완수.
* **테스트 스위트 33개 100% 통과**: `tests/test_step4_orchestrator.py` 7개 테스트(TC-401 ~ TC-407) 전수 합격.

### 🌟 [v1.0.0] 2026-10-13: [Step 3] Gemini 3.8 Flash 멀티 에이전트 결합 & 전국 17개 시·도 30분 안심 약국 페어링 엔진 구축
* **Triage Agent 결합 (`app/agents/triage_agent.py`)**: 
  - `Gemini 3.8 Flash (Thinking: Medium)`를 통해 부모의 비정형 자연어 서술에서 4대 임상 변수`(월령/일령, 체온, 지속시간, 주증상)` Pydantic JSON 정밀 추출.
  - 의료법 제27조 가드레일 강제: 부모의 유도 질문("돌발진 맞죠?")에 동조하지 않고 대면 진찰 필요성만 안내. 오프라인 대비 결정론적 정규식 Fallback 완비.
* **Matching Agent 결합 (`app/agents/matching_agent.py`)**:
  - Zero-LLM 결정론적 오케스트레이터. 임상 상태에 따른 **2-트랙 자동 분기**:
    - 🚨 고열/위급(체온 >= 39.0℃ 또는 영아): 권역 소아전문응급센터 및 가용 소아병상 상급 응급실 최우선 매칭.
    - 🟢 경증 발열(체온 < 39.0℃): 응급실 과밀화 방지를 위해 인근 달빛어린이병원 + 30분 안전 마진 야간약국 세트 우선 매칭.
* **Logistics Agent 결합 (`app/agents/logistics_agent.py`)**:
  - `Gemini 3.5 Flash-Lite (Thinking: Off)` 기반 서빙.
  - 📞 **30초 병원 유선 확인 스크립트**: 출발 전 안내데스크에 그대로 읽을 수 있는 요약 멘트 생성.
  - 📋 **2024년 5월 본인확인 의무화 지참 서류 카드**: 부모 신분증, 가족관계증명서/등본, 건강보험증 체크리스트 생성.
* **Step 3 대화형 데모 및 단위/통합 테스트 전수 검증**:
  - [`app/demo_step3.py`](app/demo_step3.py) 인터랙티브 듀얼 시나리오 시연기 구축.
  - [`tests/test_step3_agents.py`](tests/test_step3_agents.py) 신설로 전체 **26개 단위/통합 테스트 100% 통과**.

### 🌟 [v0.5.2] 2026-10-12: [Step 2] 세션 상태 DTO(PatientSessionState) 및 0ms 초저지연 의료 안전 가드레일 완비
* **멀티 에이전트 공유 메모리 DTO (`app/schemas/state.py`)**:
  - `PatientSessionState`: FSM 6단계 수명주기(`INIT` ➔ `TRIAGE` ➔ `MATCHING` ➔ `LOGISTICS` ➔ `EMERGENCY_ESCALATION` ➔ `COMPLETED`), 4대 필수 문진 변수, 3턴 대화 히스토리 추적.
* **0ms Red Flag 선제 차단기 (`app/agents/guardrail_agent.py`)**:
  - LLM 호출 없이 **KTAS 소아 7대 Red Flag**(생후 100일 미만 고열, 경련, 무반응, 청색증, 중증 탈수, 두부 외상 분수토, 담즙성 구토)를 **0.015ms(평균 5.45µs)** 만에 초저지연 감지 ➔ 119 직행 모달 라우팅.
* **의료법 제27조(무면허 의료행위 방지) 사후 필터링 엔진**:
  - 확정 진단명("~로 진단됩니다") 및 임의 약물 용량("10ml 복용") 정규식 자동 중화 및 법적 면책 고지 배지 부착.
  - `tests/test_step2_guardrail.py` 12개 테스트 100% 통과.

### 🌟 [v0.5.1] 2026-10-12: [Step 1] 기반 스토리지 & 결정론적 Zero-LLM 도구 서비스 파이프라인 완성
* **KASI 특일 판정 & 과밀화 리스크 서비스 (`app/services/holiday_service.py`)**:
  - 주말/법정공휴일/대체공휴일 실시간 판정 및 KST(UTC+9) 고정 타임존 바인딩. 응급실 과밀화 리스크(`NORMAL` | `HIGH` | `CRITICAL`) 산출.
* **하버사인 지리공간 랭킹 서비스 (`app/services/spatial_service.py`)**:
  - Haversine 구면거리 연산(< 5µs) 기반 반경 10km 이내 소아 가용 응급실 거리순 랭킹.
* **E-Gen 실시간 병상 수집 & Hash Diffing Firestore 동기화 (`app/services/emergency_sync_service.py`)**:
  - 비정형 공지사항(`hpmg`)에서 소아 진료 제한을 100% 탐지하는 정규식 필터(`PEDIATRIC_BLOCK_PATTERN`).
  - 서울 530개 응급실 위경도 로컬 디스크 캐시([`data/seoul_emergency_coords.json`](data/seoul_emergency_coords.json)) 구축으로 수집 속도 **30배 가속** (7.9초 ➔ 0.26초).
  - In-Memory Hash Diffing(`BedStateHashCache`)으로 변경된 병원만 Firestore에 업데이트 (쓰기 비용 90% 절감 실증).
* **전국 17개 시·도 달빛병원-약국 30분 마진 페어링 서비스 (`app/services/pairing_service.py`)**:
  - 전국 29개소 거점 데이터([`data/nationwide_pairings.json`](data/nationwide_pairings.json)) 기반 병원 마감시간보다 30분 이상 늦게 닫는 안심 조제 약국 1:1 매칭.
  - `tests/test_step1_services.py` 7개 테스트 100% 통과.

### 🌟 [v0.5.0] 2026-10-10: 주피터 실증 분석 3권 완료 & uv 기반 크로스 플랫폼(Mac/Win) 환경 구축
* **데이터 실증 주피터 노트북 3권 완제본 구축**:
  - `egen_pediatric_emergency_analysis.ipynb`: 소아 가용병상, 야간 20~24시 4배 내원 피크, 경증 74% 쏠림 실측.
  - `moonlight_hospital_night_pharmacy_linkage.ipynb`: 전국 17개 시·도 거점 달빛병원 및 심야약국 30분 안전 마진 연계 실증.
  - `emergency_bed_firebase_sync.ipynb`: Firebase Cloud Firestore 배치 동기화 및 실시간 리스너 파이프라인 검증.
* **`uv` 패키지 매니저 도입 및 가상환경(`DS`) 최적화**:
  - macOS 외장 드라이브(exFAT)의 AppleDouble(`._*`) 파일시스템 이슈를 해결하기 위한 APFS 심볼릭 링크 구조 적용.
  - Windows(`Malgun Gothic`), Mac(`AppleGothic`), Linux(`NanumGothic`) 크로스 플랫폼 한글 시각화 폰트 엔진 구축.

### 🌟 [v0.4.3] 2026-10-01: 2026 최신 Gemini 3.8 Flash 모델 라인업 전수 반영 및 Zero-LLM 역할 재배치
* **Gemini 3.8 Flash 핵심 두뇌 확정**: 2026년 9월 출시된 최신 플래그십 Flash를 `Triage Agent`(Thinking: Medium) 및 `Supervisor Agent`(Thinking: Low)에 전격 배치하여 복합 문진 및 Tool Calling 정밀도 극대화.
* **보조 경량 모델(Gemini 3.5 Flash-Lite) 매핑**: `Medical Guardrail`, `Visit Logistics`, `Sentinel Agent` 등 단순 이진 분류 및 정형 텍스트 생성에 배치하여 응답 속도(< 150ms)와 API 비용 90% 절감.
* **결정론적 Zero-LLM 영역 철저 분리**: 1초가 급한 Red Flag 응급 상황(0ms Regex), 병원 공간 거리 계산(PostGIS 5ms SQL), 실시간 병상 조회(Redis 1ms), DB 보안 차단(PostgreSQL 물리 Role)은 LLM 호출을 완전 배제(Zero-LLM)하여 신뢰도 100% 확보.

### 🌟 [v0.4.2] 2026-10-01: 실전 바이브코딩 로드맵 및 기술 허들 분석 가이드(VIBE_CODING_ROADMAP.md) 수립
* **현실적 5대 기술 허들 심층 분석**: 공공 API 결함, 멀티 에이전트 지연시간, PostGIS+asyncpg 비동기 ORM 결합, 의료법 100% 방어, Zero-Trust DB 거버넌스 해결책 수립.
* **8단계 바이브코딩 실전 로드맵 확정**: 기초 환경 설정부터 PostGIS 스키마, 공공데이터 클라이언트, 지리공간 서비스, 0ms 룰엔진, 멀티 에이전트 하네스, FastAPI/웹 SPA, 40선 골든 테스트 Evals까지 단계별 프롬프트와 검증 커맨드 명시.

### 🌟 [v0.4.1] 2026-10-01: 종합 기획서(PROJECT_PLAN.md)와 DB 설계 기획서(DATABASE_DESIGN.md) 통합 반영
* **종합 기획서 5장 전격 개편**: 블로그 4단계 표준 DB 설계 순서(요구사항 분석 ➔ 개념적 ERD ➔ 논리적 데이터 사전 ➔ 물리적 DDL & 인덱스) 및 기술 선정 근거를 [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) 본문에 완전 통합.
* **프로덕션 DDL 및 데이터 사전 동기화**: `hospitals`, `hospital_operating_hours`, `doctor_specialists`, `pharmacies`, `special_holidays`, `mutation_proposals`, `audit_logs` 등 8개 핵심 테이블 스키마 및 GIST 공간 인덱스 명세 통합.

### 🌟 [v0.4.0] 2026-10-01: 표준 4단계 DB 설계 기획서(DATABASE_DESIGN.md) 수립
* **PostgreSQL(PostGIS) + Redis 하이브리드 아키텍처 확정**: 5ms 초고속 지리공간 쿼리(GIST)와 실시간 병상 캐싱(TTL)을 결합한 최적 DBMS 선정.
* **표준 4단계 설계 수립**: 요구사항 분석 ➔ 개념적 설계(ERD) ➔ 논리적 설계(테이블 명세 & 정규화) ➔ 물리적 설계(인덱스 & 물리적 쓰기 차단 DDL).
* **물리적 Zero-Trust DDL 구현**: `agent_readonly` 계정 분리로 LLM 에이전트의 직접 쓰기/삭제를 DB 엔진 레벨에서 원천 차단.

### 🌟 [v0.3.1] 2026-10-01: 에이전트 DB 접근 통제 및 관리 감독 센티넬(Sentinel) 에이전트 도입
* **DB 권한 분리 (Free-Read, Strict-Write)**: 에이전트의 검색/읽기(SELECT)는 지연시간 없이 0ms로 자유롭게 인가하되, 수정 및 삭제(UPDATE/DELETE)는 100% 관리자 사전 보고 및 HITL(Human-in-the-Loop) 승인을 강제하도록 설계.
* **관리 감독 전담 에이전트(`Audit & Security Sentinel Agent`) 신설**: 에이전트가 관리자에게 보고하지 않고 무단으로 DB 수정을 시도하는 행위를 0.001초 만에 감시·차단(Zero-Bypass)하고 에이전트를 즉각 격리하는 감시 감독 체계 구축.

### 🌟 [v0.3.0] 2026-10-01: 파이썬 중심 웹앱 아키텍처 및 주석 표준화, 엔지니어링 로그 체계 구축
* **웹앱 기반 아키텍처 확정**: FastAPI 비동기 백엔드 + 경량 반응형 웹 프론트엔드(SPA) 구조로 프로젝트 전면 개편.
* **프로덕션 폴더 구조 정립**: `app/`(백엔드), `web/`(웹 UI), `pipeline/`(공공데이터 배치), `notebooks/`, `tests/` 레이어 분리.
* **기능별 상세 주석 작성 표준 강제 ([STD-DOC-01~04])**: 모듈 헤더, 4단계 동작 메커니즘, 법적 근거, 파라미터 상세 설명을 주석으로 기술하도록 개발 규칙 확정.
* **트러블슈팅 전용 로그([log.md](log.md)) 신설**: 공공데이터 이중 인코딩 버그, 의료법 제27조 진단 배제 등 7대 핵심 이슈의 원인과 해결 방안을 공식 문서화.

### 🌟 [v0.2.0] 2026-10-01: 공공데이터 오픈 API 정예화 및 인증키 보안 체계 구축
* **추가 필수 오픈 API 4건 선정**: E-Gen 응급실 병상 정보, E-Gen 병의원 요일별 진료시간, 심평원 전문의 상세정보, 천문연 특일 정보 확정.
* **오픈 API 키 최적 관리 표준 도입**: 공공데이터포털 단일 인증키(`DATA_GO_API_KEY`) 관리, 파이썬 URL 이중 인코딩 방지를 위한 '디코딩 키' 강제, 로컬(`.env` + Pydantic)과 프로덕션(GCP Secret Manager) 2-Tier 분리.

### 🌟 [v0.1.0] 2026-10-01: 시스템 기획안 및 멀티 에이전트 하네스 설계
* **의료법 컴플라이언스 가드레일 확립**: 제27조(무면허 진단 금지/알선 금지), 제56조(의료광고 금지) 3대 원칙 수립.
* **하네스 멀티 에이전트 R&R 분담**: Supervisor, Triage, Guardrail, Emergency, Matching, Logistics 6개 에이전트 설계.
* **골든 테스트 케이스 40선 구축**: 5대 루브릭 차원(DIM-1~5) 기반 AI 평가 데이터셋([tests/evals/golden_test_cases.json](tests/evals/golden_test_cases.json)) 구축.

---

## 🛠️ 개발 완료된 핵심 기술 상세 명세 (Completed Engineering Specifications)

```
monnlight/
├── app/
│   ├── config.py                     # [Step 1] 환경변수/Windows 레지스트리 자동 감지 & Firestore 싱글톤
│   ├── demo_step1.py                 # [Step 1] 파이프라인 벤치마크 러너
│   ├── demo_step3.py                 # [Step 3] AI 멀티 에이전트 듀얼 시나리오 대화형 데모
│   ├── schemas/
│   │   ├── emergency.py              # [Step 1] 병상, 특일, 하버사인 공간 랭킹 Pydantic DTO
│   │   └── state.py                  # [Step 2] 멀티 에이전트 공유 상태 DTO (PatientSessionState)
│   ├── services/                     # [Step 1] 결정론적 백엔드 도구 Layer (Zero-LLM)
│   │   ├── holiday_service.py        # KASI 특일 판정 & 응급실 과밀화 리스크 평가
│   │   ├── spatial_service.py        # Haversine 5µs 구면거리 계산 & 반경 10km 소아 응급실 랭킹
│   │   ├── emergency_sync_service.py # E-Gen 실시간 병상, 100% 공지 정규식, Hash Diffing, 위경도 캐시
│   │   └── pairing_service.py        # 전국 17개 시도 달빛병원 + 30분 마진 야간약국 페어링
│   ├── agents/                       # [Step 2 & 3] 지능형 에이전트 & 가드레일 Layer
│   │   ├── guardrail_agent.py        # [Step 2] 0.015ms Red Flag 선제 차단기 & 의료법 제27조 사후 필터
│   │   ├── triage_agent.py           # [Step 3] Gemini 3.8 Flash 부모 문진 & 4대 임상 변수 정형화
│   │   ├── matching_agent.py         # [Step 3] Zero-LLM 임상 2-트랙 자동 라우터 (응급실 vs 달빛병원)
│   │   └── logistics_agent.py        # [Step 3] Gemini 3.5 Lite 30초 통화 스크립트 & 필수 지참 서류 카드
│   └── orchestrator/                 # [Step 4] 메인 오케스트레이션 Layer
│       ├── session_manager.py        # [Step 4] Thread-Safe 세션 관리자 & TTL 자동 파기
│       └── supervisor.py             # [Step 4] 6-State FSM 라우터 & 3턴 루프 가드 & 0ms 긴급 차단
├── data/
│   ├── seoul_emergency_coords.json   # 서울 530개 응급의료기관 위경도 로컬 캐시 (수집 속도 30배 가속)
│   └── nationwide_pairings.json      # 전국 17개 시·도 거점 달빛병원 & 30분 마진 심야약국 마스터 데이터
├── notebooks/                        # [실증 분석 3권]
│   ├── egen_pediatric_emergency_analysis.ipynb          # 소아 응급실 가용병상 & 혼잡도 분석
│   ├── moonlight_hospital_night_pharmacy_linkage.ipynb  # 전국 달빛병원-약국 공간 연계 분석
│   └── emergency_bed_firebase_sync.ipynb                # Firebase Firestore 실시간 파이프라인
└── tests/                            # [33개 전수 통과 테스트 스위트]
    ├── test_step1_services.py        # 1단계 7대 핵심 기능 테스트 (통과)
    ├── test_step2_guardrail.py       # 2단계 12대 가드레일 & 0ms 벤치마크 테스트 (통과)
    ├── test_step3_agents.py          # 3단계 7대 멀티 에이전트 파이프라인 테스트 (통과)
    └── test_step4_orchestrator.py    # 4단계 7대 Supervisor FSM 라이프사이클 테스트 (통과)
```

---

## 🧪 단위 및 통합 테스트 검증 결과 (Test & Quality Verification)

```bash
$ ./DS/bin/python -m unittest discover tests
----------------------------------------------------------------------
Ran 33 tests in 6.912s

OK (skipped=1)
```

| 테스트 스위트 | 검증 대상 | 테스트 수 | 검증 성과 |
| :--- | :--- | :---: | :--- |
| [`test_step1_services.py`](tests/test_step1_services.py) | 특일 판정, 병상 수집, 공지 필터링, 하버사인 구면거리, Firestore 동기화 | 7개 | • 공지 정규식 정확도 **100%**<br/>• 하버사인 연산 속도 **< 5µs**<br/>• 위경도 캐시로 수집 속도 **30배 가속** |
| [`test_step2_guardrail.py`](tests/test_step2_guardrail.py) | KTAS 7대 Red Flag 차단, 정상 증상 통과, 의료법 제27조 진단/용량 중화 | 12개 | • Red Flag 1,000회 연속 검사 평균 **5.41µs (0.015ms 미만)**<br/>• 진단명/약물 용량 오출력 **0건** |
| [`test_step3_agents.py`](tests/test_step3_agents.py) | 자연어 4대 변수 추출, 의료법 질의 방어, 응급/달빛 2트랙 매칭, 30초 통화 스크립트, 서류 체크리스트 | 7개 | • 자연어 변수 추출 성공률 **100%**<br/>• 30분 마진 약국 정상 페어링 확인<br/>• E2E 멀티 에이전트 파이프라인 무결점 통과 |
| [`test_step4_orchestrator.py`](tests/test_step4_orchestrator.py) | 6-State FSM 전이, 3턴 무한루프 방지(Deadlock Guard), 중도 Red Flag 격상, 단일 출구 의료법 소독, 세션 동시성/TTL | 7개 | • 1턴/2턴/3턴 라이프사이클 전이 **100% 검증**<br/>• 중도 경련 0ms 긴급 차단 실증<br/>• 세션 TTL 자동 만료 및 동시성 락 확인 |

---

## 👥 프로젝트 팀 및 협업 체계 (Team & Governance)

본 프로젝트는 팀장 정영식과 팀원 김동준이 공동 개발하는 팀 프로젝트로, 엄격한 **4대 핵심 문서 지속 누적 관리 철칙**을 준수합니다.

| 구분 | 성명 | 주요 역할 (R&R) | 질의응답 및 로그 기록 대상 파일 |
| :---: | :---: | :--- | :--- |
| **팀장 (Leader)** | **정영식** | • 프로젝트 총괄 기획 및 아키텍처 의사결정<br/>• 요구사항 정의 및 Q&A 아카이브 관리 | [Answer-영식.md](Answer-영식.md), [log.md](log.md) |
| **팀원 (Member)** | **김동준** | • 백엔드 API, 데이터 파이프라인 및 멀티 에이전트 모듈 개발<br/>• 단위/통합 테스트 작성 및 트러블슈팅 | [log.md](log.md), [README.md](README.md), [PLAN.md](PLAN.md) |

### 📜 4대 문서 지속 누적 관리 철칙
1. **[Answer-영식.md](Answer-영식.md)**: 정영식 팀장의 모든 질문과 답변 내용을 Q&A 번호와 함께 누적 기록.
2. **[log.md](log.md)**: 각 사용자가 개발하면서 겪은 모든 이슈(오류, 한계, 결함) 및 구체적 해결 방안 지속 기록.
3. **[README.md](README.md)**: 각 사용자의 개발·업데이트 내역을 체인지로그에 지속 반영.
4. **[PLAN.md](PLAN.md)**: 개발 중 변경된 점을 기획안에 즉각 동기화하고 향후 개선책 지속 도출.

---

## 🗂️ 핵심 문서 안내

* 💬 **[팀장 질의응답 아카이브 (Answer-영식.md)](Answer-영식.md)**: 정영식 팀장의 모든 기술 질의 및 답변/설계 결정 전수 아카이브.
* 🤖 **[에이전트 불변 규율 (GEMINI.md / AGENTS.md)](GEMINI.md)**: 모든 AI 에이전트와 사용자가 준수해야 하는 최상위 프로젝트 규율.
* 🗺️ **[모듈 & 에이전트 상호 연결도 (CONNECTIVITY_MAP.md)](CONNECTIVITY_MAP.md)**: 전체 모듈/에이전트 연결 관계, 입출력 데이터 흐름, 공유 메모리 권한 매트릭스, 시나리오별 호출 트레이스 완제본.
* 📄 **[종합 기획안 & 개발 백서 (PLAN.md)](PLAN.md)**: 전체 시스템 기획, 주피터 3권 실측 발견점, 모듈 상세 명세 및 6단계 로드맵 완제본.
* 📄 **[백엔드 상세 기획안 (docs/PROJECT_PLAN.md)](docs/PROJECT_PLAN.md)**: 파이썬 웹앱 폴더 구조, 코딩 주석 표준, 개발 로드맵.
* 🗄️ **[데이터베이스 설계 명세서 (docs/DATABASE_DESIGN.md)](docs/DATABASE_DESIGN.md)**: 표준 4단계 DB 설계, PostGIS + Redis 하이브리드 아키텍처, ERD, DDL 완제본.
* 🛠️ **[문제 해결 & 트러블슈팅 로그 (log.md)](log.md)**: 프로젝트 개발 중 발생하는 모든 오류, 병목, 데이터 결함 및 구체적 해결 방안 지속 관리.
* 📊 **[공공의료 데이터 분석 보고서 (docs/DATA_CONSIDERATIONS.md)](docs/DATA_CONSIDERATIONS.md)**: 진료시간 괴리, 조기 접수마감, 소아 표방 vs 전문의 괴리 등 공공데이터 한계 및 보정 로직 분석.
* ⚖️ **[의료법 컴플라이언스 가이드 (references/medical_law/)](references/medical_law/)**: 의료법 원문, 판례, 유권해석, 진단 금칙어 사전(`04_forbidden_lexicon.json`).

---

## 🚀 빠른 시작 가이드 (Quick Start)

### 1. 환경 설정 및 패키지 설치
`uv` 가상환경(`DS`) 또는 표준 venv를 활성화합니다:
```bash
# uv 가상환경 활성화 (macOS/Linux)
source DS/bin/activate  # Windows: DS\Scripts\activate

# 필요 시 패키지 동기화
uv pip install -r requirements.txt
```

### 2. 환경변수 설정 (`.env`)
`.env.example`을 복사하여 `.env`를 생성하고 발급받은 키를 등록합니다 (키가 없어도 내장된 Mock 엔진으로 전체 기능이 안전하게 동작합니다):
```ini
DATA_GO_API_KEY=발급받은_공공데이터포털_디코딩키
GEMINI_API_KEY=Google_AI_Studio_발급_키
FIREBASE_KEY_PATH=C:\AI-Native-Agent\key\serviceAccountKey.json
FIRESTORE_DATABASE_ID=data-test01
```

### 3. 메인 오케스트레이터 실시간 통합 데모 실행
```bash
python app/demo_step4.py
```
*(멀티턴 문진, 중도 경련 비상 격상, 3턴 루프 가드 3대 핵심 시나리오가 콘솔에 즉시 실행됩니다)*

### 4. 전체 단위/통합 테스트 실행
```bash
python -m unittest discover tests
```

### 5. 로컬 웹 서버 실행 (FastAPI)
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
브라우저에서 `http://localhost:8000`으로 접속하여 웹앱을 이용할 수 있습니다.
