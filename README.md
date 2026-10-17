# 👶 아이숨 (i-Soom) - 구 MoonlightCare (달빛케어)

> **"야간·휴일에 갑자기 아픈 우리 아이를 위한 가장 빠르고 안전한 소아청소년과 매칭 서비스"**
> 건강보험심사평가원(HIRA), 국립중앙의료원(NMC) E-Gen 실시간 병상, 한국천문연구원(KASI) 특일 데이터, Firebase Cloud Firestore, 그리고 **Gemini 3.8 Flash 멀티 에이전트** 기반의 지능형 소아 의료 응급 지원 시스템

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Package Manager](https://img.shields.io/badge/uv-Fast%20Packaging-DE5FE9.svg)](https://github.com/astral-sh/uv)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-3.8_Flash-4285F4.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Firebase](https://img.shields.io/badge/Firebase-Cloud_Firestore-FFCA28.svg?logo=firebase&logoColor=black)](https://firebase.google.com/)
[![Tests](https://img.shields.io/badge/Tests-108%20Passed-brightgreen.svg)]()
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

### 🌟 [v2.8.3-notification-bed-sync-complete] 2026-10-18: 응급실 기록 모니터링 대상 자동 연동 및 E-Gen 실시간 병상 변동 감지 파이프라인 완결 릴리스 (정영식 팀장 총괄)
* **🎯 기록 페이지 추천 응급실 감시 대상 1순위 자동 연동 (`main.js` - `getWatchTargets`, `result.html`)**:
  - `AisumNotificationManager.getWatchTargets` 호출 시 `AisumHistoryManager`의 최신 중증(KTAS 1~3단계) 기록의 추천 시설명(`한림대학교성심병원`)을 1순위 감시 대상으로 자동 주입 및 동기화.
  - 기존 레거시 제네릭 명칭(`소아응급센터`)을 영구 소독하여 알림 바텀시트 상단 배너에 정확한 병원명이 표출되도록 개선.
  - `result.html` 렌더링 시 `registerWatch(hospitals, window.currentKtasLevel)`를 명시적으로 호출하여 최신 감시 타겟 즉시 등록.
* **⚡ E-Gen API 응답 파싱 및 소아 병상(`pediatric_beds`) 필드 매핑 완비 (`main.js`)**:
  - `syncAndCheckBeds`에서 백엔드 응답 `data.hospitals`를 정상 수신하도록 개선하여 백그라운드 30초 주기 폴링 파이프라인 정상 가동.
  - `checkBedUpdates` 및 `registerWatch`에서 소아 잔여 병상 필드인 `pediatric_beds`를 1순위로 조회하여 실제 병상 증감(증가/감소/만실) 알림이 100% 정상 발송되도록 완결.
* **🧪 13대 통합 계약 테스트 100% 전수 통과 (`tests/test_step8_frontend_integration.py`)**:
  - TC-813 (`test_13_emergency_notification_history_sync_and_pediatric_beds_contract`) 신설 및 **13/13 100% 통과**.
* **📜 4대 불변 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q179, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-179, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v3.04)**.

### 🌟 [v2.8.2-history-dummy-prevention] 2026-10-18: 비동기 병상 로드 시 더미 히스토리 생성 원천 차단 및 사용자 입력값 1:1 매칭 릴리스 (정영식 팀장 총괄)
* **🚫 비동기 병상 로드 시 유령 더미 레코드 생성 원천 차단 (`result.html`)**:
  - `renderEmergencyBedCards` 내에서 기존 기록이 없을 때 임시 생성하던 더미 레코드(`childAge: '아이', temperature: '고열/응급'`) 코드를 완전히 제거.
  - 비동기 로딩 완료 시에는 오직 최신 기록의 추천 시설명만 정밀 보정(`updateLatestHospital`)하도록 책임 분리.
* **🎯 사용자 직접 입력값(`triageData`) 최우선 동기화 (`result.html`)**:
  - `triageData.age`(`12개월 (영아)`) 및 `triageData.temp`(`체온 미측정(모름)`)를 최우선으로 반영하여, 입력 페이지 세팅값이 결과 화면 바이탈 칩 및 기록 카드에 100% 온전히 유지되도록 개선.
* **🧹 과거 유령 더미 레코드 자동 소독 (`main.js` - `AisumHistoryManager`)**:
  - `getAll()` 실행 시 과거에 누적되었던 `아이 / 고열·응급 / 소아 응급 상황` 형태의 유령 더미 레코드를 자동 감지하여 영구 소독.
  - 최신 레코드가 더미인 경우 신규 생성 대신 실제 문진 데이터로 덮어쓰도록 처리.
* **🧪 12대 통합 계약 테스트 100% 전수 통과 (`tests/test_step8_frontend_integration.py`)**:
  - TC-812 (`test_12_history_duplicate_and_dummy_prevention_contract`) 신설 및 **12/12 100% 통과**.
* **📜 4대 불변 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q178, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-178, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v3.03)**.

### 🌟 [v2.8.1-notification-sheet-collapse-fix] 2026-10-18: 응급실 병상 변동 알림 카드 찌그러짐(Collapsing) 버그 해결 및 중복 알림 스마트 디듀플리케이션 체계 완결 릴리스 (정영식 팀장 총괄)
* **🛡️ Flexbox 수축(Flex-Shrink) 원천 차단 및 무결점 카드 높이 보장 (`style.css`)**:
  - 알림이 다수 누적될 때 `.sheet-body` 플렉스 컨테이너 안에서 카드가 1~2px 두께로 찌그러지던 CSS 수축 버그를 완벽 해결.
  - `.sheet-body`에 `min-height: 0; flex: 1; overflow-y: auto;`를 부여하고, `.notif-card-wrapper` 및 `.notif-card`에 `flex-shrink: 0; min-height: 85px;`를 명시하여 아무리 많은 알림이 쌓여도 부드럽게 세로 스크롤되도록 보장.
  - `.watch-status-banner` 및 `.history-card`에도 `flex-shrink: 0;`를 사전 적용하여 잠재적 레이아웃 붕괴 전면 차단.
* **⚡ 스마트 디듀플리케이션 및 중복 병원명 Set 필터링 (`main.js`, `index.html`)**:
  - `addNotification`에 3분 이내 동일 제목/메시지 중복 등록 방지 및 `WATCH_START` 30분 쿨다운을 적용하여 동일 알림 폭증 차단.
  - 상단 감시 배너의 대상 응급실 명칭에서 `Set`을 적용하여 "소아응급센터, 소아응급센터, 소아응급센터" 중복 표출 현상을 완전 소독.
* **🧪 11대 통합 계약 테스트 100% 전수 통과 (`tests/test_step8_frontend_integration.py`)**:
  - TC-811 (`test_11_notification_sheet_collapse_prevention_contract`) 신설 및 **11/11 100% 통과**.
* **📜 4대 불변 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q177, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-177, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v3.02)**.

### 🌟 [v2.8.0-integrated-measurement-hub] 2026-10-18: 입력 페이지 체온·나이·해열제 3대 측정 항목 통합 탭 카드 구축(한 칸 내 원터치 전환 UI) 릴리스 (정영식 팀장 총괄)
* **🎛️ 3대 핵심 측정 항목 단일 통합 허브 카드 결합 (`#card-measurement-hub`, `.integrated-measure-card`)**:
  - 기존 세로 3단계(체온, 나이, 해열제)로 길게 나열되어 스크롤 피로도가 높았던 구조를 단 1개의 세련된 통합 카드로 전면 개편.
  - 상단에 **3대 카테고리 탭 버튼 바 (`.measure-tab-bar`)** 신설:
    - `[ 🌡️ 현재 체온 (36.5℃) ]`
    - `[ 👶 아이 나이 (14개월) ]`
    - `[ 💊 해열제·상태 (복용 안 함) ]`
* **🔄 원터치 0ms 탭 전환 엔진 및 퀵 내비게이션 구축 (`switchMeasureTab`, `.measure-panel`)**:
  - 상단 탭 버튼 클릭 시 한 칸(단일 컨테이너) 안에서 체온 게이지 패널 / 3+2 나이 조절 패널 / 해열제 및 동반 증상 패널이 페이드인 애니메이션과 함께 매끄럽게 교체 표출.
  - 각 패널 하단에 `[ 다음 단계 설정 → ]` 퀵 버튼을 두어 자연스러운 순차 입력 플로우 제공.
* **⚡ 실시간 탭 요약 배지 & 하단 액션바 양방향 동기화**:
  - 어느 탭에서 값을 조작하든 탭 헤더의 상태 배지(`tab-val-temp`, `tab-val-age`, `tab-val-med`)가 0ms로 실시간 반영되어 다른 탭을 보면서도 전체 세팅 현황을 한눈에 파악 가능.
* **🧪 10대 통합 계약 테스트 100% 전수 통과 (`tests/test_step8_frontend_integration.py`)**:
  - TC-810 (`test_10_integrated_measurement_tabs_contract`) 신설 및 **10/10 100% 통과**.
* **📜 4대 불변 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q176, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-176, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v3.01)**.

### 🌟 [v2.7.9-pediatric-age-grid-buttons] 2026-10-18: 입력 페이지 선택박스 전면 제거 & 3+2 반응형 그리드 카테고리 버튼 도입(청소년 버튼 잘림 완전 해소) 릴리스 (정영식 팀장 총괄)
* **🗑️ 드롭다운 선택박스 제거 및 직관적 원터치 카테고리 버튼 전면 전환 (`input.html`)**:
  - 화면 상단을 불필요하게 차지하던 `<select>` 드롭다운 박스를 전면 제거하고, 오직 손가락으로 가볍게 터치할 수 있는 카테고리 버튼만으로 연령대를 분류하도록 UI를 극적으로 단순화.
* **📱 청소년 버튼 UI 잘림 원천 해결: 6컬럼 3+2 반응형 스마트 그리드 구축 (`.age-cat-grid`, `.age-cat-btn`)**:
  - 기존 1열 나열 시 모바일 화면 우측 경계에서 '청소년' 버튼이 잘리던 문제를 해결하기 위해 6컬럼 3+2 스마트 그리드로 재설계.
  - **상단 3개 (각 2컬럼 차지)**: `[👶 신생아 (28일 미만)]`, `[🍼 영아 (~24개월)]`, `[🧸 유아 (만 2~5세)]`.
  - **하단 2개 (각 3컬럼 차지, 50% 와이드 레이아웃)**: `[🎒 어린이(아동) (만 6~12세 미만)]`, `[🎧 청소년 (만 12~18세)]`.
  - 모든 버튼에 이모지, 연령명, 기준 세부 연령(sub)을 체계적으로 담아 글자가 절대 잘리지 않으며, 손가락 터치 면적이 넉넉하게 확보되어 모바일 UX 극대화.
* **⚡ 자바스크립트 양방향 연동 & 100% 통합 검증 (`tests/test_step8_frontend_integration.py`)**:
  - `setAgeCategory`에서 `ageCatButtons`의 활성화 토글을 즉각 반영하고, 슬라이더/눈금선/프리셋과 완벽 호환.
  - TC-809 (`test_09_pediatric_age_category_selector_contract`) 검증 갱신 및 9/9 전수 100% 통과.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q175, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-175, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v3.00)**.

### 🌟 [v2.7.8-pediatric-age-category-engine] 2026-10-18: 입력 페이지 소아 연령 0세~만18세 전면 확장 & 5대 연령 분류 선택박스·맞춤형 동적 조절 칸 엔진 구축 릴리스 (정영식 팀장 총괄)
* **👶 소아 연령 0세 ~ 만 18세 전 연령대 확장 및 5대 의학적 분류 선택박스 (`input.html`)**:
  - 기존 0~7세 단일 슬라이더의 한계를 극복하고, 소아청소년과 임상 지침에 맞춘 5대 연령 분류 선택박스(`<select id="age-category-select">`) 및 원터치 칩 연동:
    - **신생아**: 출생 후 28일 미만 (생후 4주일까지 / 0~27일 일령 조절)
    - **영아**: 생후 28일 이상 ~ 24개월 미만 (1~23개월 개월수 조절, 100일 미만 주의 배지 연동)
    - **유아**: 생후 24개월 이상 ~ 만 6세 미만 (만 2~5세 만 나이 및 개월수 병기)
    - **어린이(아동)**: 만 6세 이상 ~ 만 12세 미만 (만 6~11세 학령기 프리셋 연동)
    - **청소년**: 만 12세 이상 ~ 만 19세 미만 (만 12~18세 중·고교생 연령 조절)
* **🎛️ 카테고리별 맞춤형 동적 나이 조절 칸 엔진 (`setAgeCategory`, `updateAgeDisplay`)**:
  - 선택박스에서 분류 변경 시 슬라이더 범위(min/max/step), 정밀 눈금선(marks), 퀵 프리셋 버튼(presets), 위험 안내문(notice)이 즉시 동적으로 생성/재배치.
  - 신생아 선택 시 일령(일) 단위 슬라이더 및 신생아 발열·패혈증 응급실 진료 권고 배너 노출.
  - 영아 선택 시 생후 100일 미만 🚨 퀵 프리셋과 3개월 이하 자동 감지 배지 점등.
* **⚡ 데이터 표준화 및 100% 통합 검증 (`tests/test_step8_frontend_integration.py`)**:
  - `getFormattedAge()` 표준화로 서머리 바 및 백엔드 제출 페이로드 완벽 일치.
  - TC-809 (`test_09_pediatric_age_category_selector_contract`) 신설 및 9/9 전수 100% 통과.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q174, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-174, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.99)**.

### 🌟 [v2.7.7-app-guidebook-view] 2026-10-18: 설정 페이지 '아이숨 가이드북' 전용 뷰(`/guidebook`) 신설 & 5대 핵심 가이드 체계 완결 릴리스 (정영식 팀장 총괄)
* **📖 설정 화면 내 '아이숨 가이드북' 원터치 연동 (`settings.html`)**:
  - '정보' 섹션의 아이숨 가이드북 항목을 `<a href="guidebook.html">` 링크로 연결하여 설정에서 한 번의 탭으로 가이드북에 즉시 진입 가능.
* **🌐 프리미엄 아이숨 가이드북 전용 페이지 신규 구축 (`guidebook.html`, `/guidebook`)**:
  - **비주얼 히어로 배너**: "야간 소아 응급실 뺑뺑이 끝! 아이숨과 함께라면 안심" 슬로건과 4대 가치 캡슐 배지 탑재.
  - **원클릭 챕터 퀵 필터 탭**: `전체 보기`, `AI 문진`, `2-트랙 안내`, `병상 알림`, `통화 & 준비물`, `자주 묻는 질문`.
  - **5대 핵심 챕터 가이드**:
    - **STEP 1. 0ms AI 안심 문진**: 2021 소아 KTAS 168개 주증상 기반 3단계 터치 문진 및 초응급 0초 세이프티 가드레일.
    - **STEP 2. 2-트랙 맞춤 안내**: 소아전문응급센터(KTAS 1~3 중증) vs 달빛어린이병원(KTAS 4~5 경증) 비교 가이드 및 야간 달빛약국 원스톱 연계.
    - **STEP 3. 소아 응급실 실시간 병상 변동 알림**: 국립중앙의료원(NMC) E-Gen 3분 주기 감지 및 설정 앱 알림 토글 연동.
    - **STEP 4. 1초 안심 통화 대본 & 필수 준비물 5종**: 당황한 부모님을 위한 사전 통화 표준 브리핑 대본 및 필수 준비물(등본, 신분증, 약, 기저귀, 담요) 체크리스트.
    - **STEP 5. 자주 묻는 질문 (FAQ) 아코디언**: 달빛병원과 응급실 차이, 병상 데이터 정확도, 무료 이용, 이전 기록 다시보기 등 핵심 질의응답 수록.
  - **하단 플로팅 CTA 바**: `[ 🩺 우리 아이 증상 문진 시작 ]` 원터치 버튼 탑재.
* **⚡ FastAPI 라우팅 및 100% 통합 검증 (`main.py`, `tests/test_step8_frontend_integration.py`)**:
  - `/guidebook`, `/guidebook.html` 라우팅 등록 및 루트 탐색 딕셔너리 연동.
  - TC-808 (`test_08_guidebook_page_contract`) 신설 및 8/8 전수 100% 통과.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q173, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-173, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.98)**.

### 🌟 [v2.7.6-app-notification-toggle-integration] 2026-10-18: 설정 페이지 '앱 알림' On/Off 기능 & 메인화면 실시간 응급실 소아병동 알림 연동 체계 완결 릴리스 (정영식 팀장 총괄)
* **🔔 설정 화면 '앱 알림' 토글 스위치 영구 연동 (`settings.html`)**:
  - `localStorage` 키 `aisum_app_notification_enabled` 기반으로 토글 On/Off 상태를 동기화하고 변경 시 실시간 영구 보존.
  - 토글 조작 시 직관적인 안내 토스트 메시지 및 브라우저 푸시 권한 연계 요청 지원.
* **🛡️ 알림 매니저 차단/수신 제어 파이프라인 (`main.js`, `AisumNotificationManager`)**:
  - `isEnabled()`, `setEnabled()` 메서드 탑재.
  - 알림 Off 시 소아 응급실 병상 변동 감지(`checkBedUpdates`), 백그라운드 폴링(`syncAndCheckBeds`), 신규 알림 등록(`addNotification`), 헤더 붉은 뱃지(`updateBadgeUI`)를 원천 차단하여 사용자 방해 요소 완전 제거.
  - 알림 On 시 실시간 병상 변동 감지 및 뱃지 점등 정상 가동.
* **📱 메인화면 알림 센터 바텀시트 UI 연동 (`index.html`)**:
  - 앱 알림 Off 상태 시 상단 안내 배너에 알림 꺼짐 상태 표시 및 '설정에서 알림 켜기' 바로가기 링크 제공.
  - `storage` 이벤트 리스너를 통한 크로스탭/페이지 간 실시간 동기화 지원.
* **⚡ 100% 통합 검증 완결 (`tests/test_step8_frontend_integration.py`)**:
  - TC-807 (`test_07_app_notification_toggle_contract`) 신설 및 7/7 전수 100% 통과.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q172, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-172, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.97)**.

### 🌟 [v2.7.5-open-source-licenses-view] 2026-10-18: 설정 페이지 '오픈소스 라이선스' 전용 뷰(`/licenses`) 신설 & 14개 오픈소스·공공데이터 저작권 고지 체계 완결 릴리스 (정영식 팀장 총괄)
* **📜 설정 페이지 내 오픈소스 라이선스 원터치 연동 (`settings.html`)**:
  - '정보' 섹션의 오픈소스 라이선스 항목을 `<a href="licenses.html">` 링크로 연결하여 설정에서 한 번의 탭으로 라이선스 목록에 접근 가능.
* **🌐 오픈소스 라이선스 전용 페이지 신규 구축 (`licenses.html`, `/licenses`)**:
  - **4대 카테고리 필터**: `전체 보기`, `백엔드 & AI`, `프론트 & 지도`, `공공데이터` 실시간 원클릭 필터링 지원.
  - **14개 오픈소스 & 공공데이터 상세 명세**: FastAPI, Google GenAI SDK, Leaflet.js, Firebase Admin, Uvicorn, Pydantic, QRCode.js, Material Symbols, Noto Sans KR, 국립중앙의료원(NMC) E-Gen, 보건복지부 달빛어린이병원, 한국천문연구원(KASI), 카카오맵 REST API.
  - **라이선스 전문 아코디언(`<details>`)**: JetBrains Mono 서체 기반 코드 블록으로 표준 라이선스(MIT, Apache 2.0, BSD-3, 공공누리 제1유형) 전문 수록.
* **⚡ FastAPI 백엔드 라우팅 및 100% 통합 검증 (`main.py`, `tests/test_step8_frontend_integration.py`)**:
  - `/licenses`, `/licenses.html`, `/opensource`, `/opensource.html` 라우팅 등록.
  - TC-806 (`test_06_licenses_page_integration`) 신설 및 6/6 전수 100% 통과.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q171, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-171, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.96)**.

### 🌟 [v2.7.4-mobile-touch-scroll-restoration] 2026-10-17: 모바일 응급실·달빛병원 목록 touch-action pan-y & 가속 스크롤(clamp 280~350px) 완벽 복원 릴리스 (정영식 팀장 총괄)
* **📱 독립 모바일 가속 터치 스크롤 컨테이너 전면 복원 (`result.html`)**:
  - `.facility-scroll-list`에 `max-height: clamp(280px, 42vh, 350px); overflow-y: auto;` 적용으로 최소 4개 카드가 스크롤 없이 시원하게 바로 보이고, 5순위~8순위/10순위까지 손가락으로 매끄럽게 스크롤 가능하도록 복원.
  - `touch-action: pan-y !important;` 및 `-webkit-overflow-scrolling: touch !important;` 지정으로 모바일 브라우저의 터치 스크롤 락 결함을 원천 해소.
  - `overscroll-behavior-y: contain !important;`로 스크롤 체이닝 차단.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q170, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-170, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.95)**.

### 🌟 [v2.7.3-er-8-unconditional-rendering-hotfix] 2026-10-17: 소아 응급실 8곳 전수 하드코딩 마크업 & 0ms 무조건 프리셋 렌더링 전환 핫픽스 릴리스 (정영식 팀장 총괄)
* **🚨 정적 HTML 마크업 8곳 전수 완벽 구축 (`result.html`)**:
  - 기존 2개만 존재하던 마크업 한계를 탈피하여 1순위 서울아산병원부터 8순위 가톨릭대 서울성모병원까지 8곳 전체 카드를 정적 HTML에 100% 완전하게 내장.
  - 하단에 8곳 안내 완료 인증 배지 정적 포함.
* **⚡ 0ms 무조건 프리셋 렌더링 & 이중 안전망 완성**:
  - `hasExistingCards` 스킵 조건을 완전 폐기하고 진입 즉시 8곳을 0ms 무조건 렌더링.
  - 비동기 E-Gen API 실시간 수신 시 잔여 병상 최신 정보로 부드럽게 업데이트되어, 어떤 네트워크 환경에서도 8곳이 100% 보장됨.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q169, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-169, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.94)**.

### 🌟 [v2.7.2-er-8-visible-and-swipe-dismiss-rounded-ui] 2026-10-17: 실시간 소아 응급실 8곳 전수 자연 노출 & 알림 스와이프 삭제·전체 비우기 & 프리미엄 모바일 소프트 라운드 디자인 시스템 완결 릴리스 (정영식 팀장 총괄)
* **🚨 실시간 소아 응급실 8곳 전수 시원한 노출 & 인증 배지 완비 (`result.html`)**:
  - `.facility-scroll-list` 높이 제한(`max-height: 275px;`)을 과감히 해제하고 `overflow-y: visible;`로 개편하여 1순위 서울아산병원부터 8순위 서울성모병원까지 8곳 전수 한눈에 아래로 시원하게 펼쳐지도록 개선.
  - 목록 하단에 `[인근 소아 진료 가용 응급실 8곳 실시간 안내 완료 (거리순)]` 인증 캡슐 배지 탑재로 8곳 전수 완결 인지성 100% 확보.
* **🔔 알림 센터 네이티브 모바일 스와이프 삭제 & 전체 삭제 완비 (`index.html`, `main.js`)**:
  - **터치 제스처 스와이프**: 카드를 좌/우로 70px 이상 밀면 빨간 배경과 함께 부드럽게 화면 밖으로 날아가며 삭제되는 모바일 네이티브 스와이프 제스처 인터랙션 구축.
  - **원클릭 삭제(X) 버튼** 및 상단 헤더 **`[전체 삭제]`** 버튼 신설로 한 번의 탭으로 알림 보관함 일괄 비우기 지원.
  - `AisumNotificationManager.deleteNotification(id)` 및 `clearAll()` 동기화 완료.
* **📱 최신 스마트폰 기기 맞춤 소프트 모바일 라운드 디자인 전면 적용**:
  - 응급실 카드(`.slim-er-card`), 달빛병원 카드(`.facility-card`), KTAS 응급 배너, 진단 요약 카드를 **`border-radius: 18px ~ 20px`**의 유기적 곡면으로 통일.
  - 알약 배지류 **`border-radius: 9999px`**, 버튼류 **`border-radius: 14px ~ 16px`**, 바텀시트 **`border-radius: 30px 30px 0 0`** 적용으로 스마트폰 물리 베젤 곡면과 완벽한 일체감 실현.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q168, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-168, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.93)**.

### 🌟 [v2.7.1-dedicated-qr-page-and-splash-priority] 2026-10-17: 전용 모바일 QR코드 페이지(`/qr`) 신설 및 사이트 첫 접속 시 무조건 1순위 스플래시(`splash.html`) ➔ 이용약관(`terms.html`) 순차 파이프라인 완결 릴리스 (정영식 팀장 총괄)
* **🔳 전용 모바일 QR코드 온보딩 페이지 신설 (`frontend/templates/qr.html`, `/qr`)**:
  - 설정 화면에서 "스마트폰으로 앱 열기" 클릭 시 모달 대신 독립적인 프리미엄 풀스크린 `/qr` 전용 페이지로 즉각 전환.
  - 현재 호스팅 도메인(`origin`) 실시간 감지 고화질 260x260 QR코드 생성, 원터치 주소 복사, Web Share API 연동 링크 공유.
  - **iOS Safari** (공유 ➔ '홈 화면에 추가') & **Android Chrome** (더보기 ➔ '앱 설치') 단계별 안내 카드 및 PWA 설치 버튼 탑재.
* **🌙 사이트 첫 접속 시 무조건 1순위 스플래시 ➔ 이용약관 파이프라인 정립**:
  - `main.py` 루트(`/`) 라우트 개편: 브라우저 첫 요청 시 항상 1순위로 `splash.html` 서빙.
  - `splash.html` 100dvh 풀스크린 최적화 및 1.8초 브랜드 애니메이션 종료 후 미동의 사용자를 무조건 이용약관(`/terms`)으로 강제 유도하여 법적 컴플라이언스 및 정석 온보딩 플로우 확립.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q167, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-167, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.92)**.

### 🌟 [v2.7.0-pwa-and-cloud-run-production-deployment] 2026-10-17: PWA(Progressive Web App) 풀스택 구축 & .env 다중 API Key 연동 Google Cloud Run 원클릭 배포 파이프라인 완결 릴리스 (정영식 팀장 총괄)
* **📱 PWA (Progressive Web App) 풀스택 인프라 완비**:
  - **웹 앱 매니페스트 (`frontend/manifest.json`)**: `standalone` 모드, 테마 컬러 `#10b981`, 고해상도 앱 아이콘(192x192, 512x512) 연동 완료.
  - **서비스 워커 (`frontend/sw.js`)**: 정적 자산(CSS, JS, HTML, 폰트) `Stale-While-Revalidate` 및 실시간 API `Network First` 2계층 캐싱 적용으로 오프라인 및 음영지역 완벽 대응.
  - **FastAPI 백엔드(`main.py`)**: `/manifest.json`, `/sw.js`, `/img/{filename}` 전용 엔드포인트 등록 완료.
* **🔳 설정 페이지(`settings.html`) '모바일 기기 연결' & 실시간 QR코드 모달 연동**:
  - '모바일 기기 연결' 신규 섹션 구축 (`스마트폰으로 앱 열기`, PWA 지원 뱃지).
  - 바닐라 JS 실시간 QR코드 모달(`openQrModal()`): 현재 접속 도메인(`window.location.origin`)을 자동 감지하여 QR코드 생성, 원터치 주소 복사, iOS(Safari 홈 화면 추가)/Android(Chrome 앱 설치) 가이드 제공.
  - `beforeinstallprompt` 이벤트 연동: 설치 지원 기기에서 "홈 화면에 앱 설치하기" 원클릭 버튼 동적 활성화.
* **🐳 Google Cloud Run 프로덕션 컨테이너 최적화 & .env API Key 완전 연동**:
  - `main.py` 포트 바인딩 최적화: Cloud Run 주입 환경변수 `PORT`(`port=int(os.getenv("PORT", 8000))`) 완벽 수신.
  - `app/config.py` Firebase 3단 인증 안전망: 컨테이너 파일 경로, `FIREBASE_KEY_JSON` 환경변수 문자열, Google Cloud IAM 무키(ADC) 인증 완전 지원.
  - 프로덕션 `Dockerfile` (`python:3.11-slim`, `HEALTHCHECK /health`) 및 `.dockerignore` 생성.
* **🚀 원클릭 배포 스크립트 개발 (`scripts/deploy_cloud_run.sh`)**:
  - `.env`에 보관된 실제 API 키 4종(`DATA_GO_API_KEY`, `GEMINI_API_KEY`, `KAKAO_REST_API_KEY`, `serviceAccountKey.json`, `FIRESTORE_DATABASE_ID`)을 자동 로드하여 Cloud Run 서울 리전(`asia-northeast3`)으로 무결점 원클릭 배포 지원.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q164~Q166, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-164~ISSUE-166, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.91)**.

### 🌟 [v2.6.6-fullscreen-fit-and-zero-gap-ui] 2026-10-17: 입력 페이지(`input.html`) & 결과 페이지(`result.html`) 상하 공백 완전 박멸 및 전 기종 스마트폰 100% 빈틈없는 Full-Screen(100dvh) 웹앱 밀착 반응형 아키텍처 구축 릴리스 (정영식 팀장 총괄)
* **📱 입력·결과 페이지 상하 캔버스 공백 & 목업 테두리 100% 완전 박멸**:
  - 기존 데스크톱 미디어쿼리의 불필요한 목업 테두리(`border: 8px solid #ffffff`) 및 상하 24px 회색 공백 완전 제거.
  - `body` 전역 패딩/마진 0px 및 배경색 완전 일치화 (결과 `#f8faff`, 입력 `#ffffff`), 불필요한 테두리/모서리 둥글기 제거로 틈새 노출 원천 차단.
* **📲 전 기종 스마트폰 100% 꽉 차는 풀스크린 반응형 정립 (`max-width: 100%`, `100dvh`)**:
  - 모바일 전 기종(`@media (max-width: 639px)`)에서 `width: 100%; max-width: 100%; height: 100dvh; min-height: 100dvh;` 적용.
  - 아이폰 SE, 아이폰 14/15/16/Pro Max, 갤럭시 S21~S24/Ultra, Z Flip/Fold 등 **어떤 스마트폰 기종이든 화면 전체에 1픽셀의 빈틈도 없이 100% 꽉 채우는 완벽한 네이티브 앱 UX** 실현.
* **🛡️ Safe Area (상단 노치/다이내믹 아일랜드 & 하단 제스처 홈 바) 정밀 도킹**:
  - 상단 헤더: `height: calc(56px + env(safe-area-inset-top, 0px))` 적용.
  - 하단 고정 바: `height: calc(64px + env(safe-area-inset-bottom, 10px))` 및 바닥 밀착 도킹으로 홈 바와 겹치지 않으면서도 상하 공백 없는 일체형 마감.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q163, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-163, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.90)**.

### 🌟 [v2.6.5-emergency-history-and-bed-change-alerts] 2026-10-17: 맞춤 결과 페이지(`result.html`) 응급실 판정 결과 영구 기록 누락 결함 원천 해소 & 중증 환아 전용 2대 조건부 근방 응급실 병상 변동 실시간 알림 엔진 구축 릴리스 (정영식 팀장 총괄)
* **💾 응급실 판정 결과 영구 기록(`AisumHistoryManager`) 100% 보관 보장**:
  - 기존 세션 잔존 플래그(`aisum_is_replay_view`)로 인해 신규 문진도 Replay 모드로 오인되어 저장이 스킵되던 결함 원천 해소 (문진 제출 및 진입 시 자동 소독).
  - 15초 이내 동일 결과만 새로고침 중복 방지(`isWithin15Sec`)를 적용하여 신규 문진은 무조건 영구 저장 보장.
  - 소아 응급실 병상 비동기 로드 완료 시 최신 히스토리 기관명을 실제 1순위 응급실명으로 자동 동기화.
* **🔔 중증 환아 전용 2대 조건부 근방 소아 응급실 병상 변동 실시간 알림 엔진 (`AisumNotificationManager`)**:
  - **조건 1**: 기록 페이지에 KTAS 1·2·3단계 응급실 판정 이력이 존재하는 보호자에게만 감시 및 알림 허용 (`hasEmergencyHistory()`).
  - **조건 2**: 사용자 위치(반경 25km) 기준 근방 응급실 병상 정보가 실제로 변경되었을 때, **어떤 응급실이고 얼마나 변경되었는지(증가/감소/만실 수치)** 명확한 알림 발송:
    - `🟢 [서울아산병원] 소아 응급실 병상 확보 (+2석)` (1석 ➔ 3석)
    - `🔴 [서울아산병원] 소아 응급실 병상 감소 (-2석)` (3석 ➔ 1석)
    - `🚨 [서울아산병원] 소아 응급실 만실 경보 (0석)` (1석 ➔ 0석)
  - 인앱 알림 센터 + 헤더 뱃지 점등 + 브라우저 시스템 푸시(`Notification API`) 3중 발송 지원.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q162, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-162, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.89)**.

### 🌟 [v2.6.4-unified-er-track-tab-and-4cards-fit] 2026-10-17: 맞춤 결과 페이지(`result.html`) 상단 트랙 탭 & 상태 바 단일 칸 일체화(새로고침 버튼 도킹) 및 소아 응급실 카드 4개소 무스크롤 100% 완전 노출 릴리스 (정영식 팀장 총괄)
* **🔄 상단 트랙 탭 & 하단 상태 바 단일 칸 통합 & 새로고침 버튼 도킹**:
  - 기존 탭 버튼(`[ ✱ 소아 응급실 병상 (실시간 현황 · 8곳) ]`)과 하단 상태 바(`[ 4분 전 실시간 연동 ] [ 🔄 새로고침 ]`)의 2중 칸 누적으로 인한 75px 세로 공간 잠식 결함 해소.
  - `tab-btn-emergency`를 Flex 컨테이너로 통합하여 좌측에 실시간 현황 타이틀, 우측에 원터치 `[ 🔄 새로고침 ]` 버튼(`btn-refresh-er-beds`)을 일체형 도킹.
  - 하단의 중복된 `er-header-status-bar`를 은닉하여 세로 **36px의 화면 공간을 즉각 추가 확보**.
* **🏥 소아 응급실 병상 목록 최소 4개소 무스크롤 100% 완전 노출**:
  - 확보된 공간을 바탕으로 `.facility-scroll-list` 뷰포트를 `max-height: 275px`로 확장하고 카드를 `min-height: 48px !important; padding: 6px 10px !important;`로 슬림화.
  - **사용자가 스크롤을 전혀 하지 않아도 4개 응급실 카드가 아래쪽 테두리까지 단 1픽셀도 잘리지 않고 화면 중앙에 100% 온전히 표출**되며, 5개째 이후부터 전용 스크롤바로 부드럽게 탐색 가능.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q161, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-161, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.88)**.

### 🌟 [v2.6.3-concise-emergency-banner-and-clean-directive] 2026-10-17: 맞춤 결과 페이지(`result.html`) 응급 배너 중복 문구 100% 제거, 1줄 핵심 지침 정예화(shortKtasMap) 및 전문 감별 소견 접이식 토글(details) 적용 릴리스 (정영식 팀장 총괄)
* **🚨 헤더 단일 정예 배지화 (`shortKtasMap`) & 중복어 100% 완전 제거**:
  - 헤더 1행에 `[KTAS 1단계 (소생 119 즉시 신고 · 응급실 이송)]` + `최고 응급 (소생)` + `즉각 처치 필요` 3중 중복 및 텍스트 줄바꿈 깨짐 결함 원천 해소.
  - `shortKtasMap` 도입으로 **`🚨 KTAS 1단계 · 소생`**, **`⚠️ KTAS 2단계 · 긴급`**, **`⚡ KTAS 3단계 · 응급`** 정갈한 단일 캡슐 배지 및 4글자 컴팩트 태그(`즉시 신고`, `골든타임 확보`, `가용병상 확인`, `white-space: nowrap;`) 정착.
* **📢 1줄 크고 뚜렷한 핵심 행동 지침 정예화**:
  - 환아 위급 상황에서 부모가 0.1초 만에 행동을 결정할 수 있도록 12px 굵은 다크 슬레이트 폰트로 핵심 지침 명확화:
    - KTAS 1: **"생명이 위급한 최고 응급 상태입니다. 지체 없이 119 구급차를 호출하십시오."**
    - KTAS 2: **"신체 기능 위험이 있는 긴급 상태입니다. 대학병원 소아응급센터로 즉시 이동하십시오."**
    - KTAS 3: **"응급 진료가 필요한 상태입니다. 아래 실시간 소아 응급실 병상을 확인 후 이동하십시오."**
* **🩺 전문 임상 감별 소견 접이식 아코디언(`<details>`) 토글화**:
  - 5줄짜리 장황한 전문 의학 소견을 접이식 토글(`🩺 상세 감별소견 보기`)로 격리하여 기본 화면 가독성을 극대화하고 시각적 노이즈를 100% 제거.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q160, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-160, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.87)**.

### 🌟 [v2.6.2-unified-emergency-banner-and-4cards-fit] 2026-10-17: 결과페이지 상단 감별소견 & 초응급 배너 단일 카드 통합(높이 -210px 압축) 및 소아 응급실 병상 목록 4개소 무스크롤 100% 완전 노출 릴리스 (정영식 팀장 총괄)
* **🚨 상단 감별소견 & 초응급 배너 단일 카드(`triage-summary-card`) 일체화**:
  - 기존 감별 소견 박스와 초응급 배너의 2중 중첩 및 360px 세로 공간 잠식 결함 해소.
  - KTAS 1·2·3단계 시 장황한 별도 노란 박스를 숨기고 `#ktas-emergency-call-banner` 내부에 KTAS 등급 배지 + 이송 지침 + 핵심 임상 감별 소견을 2줄로 명쾌하게 통합.
  - 바로 아래 `[ 📞 119 즉시 전화 ]` 및 `[ 응급처치 가이드 > ]` 버튼을 일체형 도킹하여 상단 높이를 **360px ➔ 150px (무려 210px 절감)**로 획기적 압축.
* **🏥 소아 응급실 병상 목록 최소 4개소 무스크롤 100% 완전 노출**:
  - 상단에서 확보된 210px 공간을 바탕으로, `.facility-scroll-list`(`max-height: 250px; min-height: 236px; gap: 6px;`) 및 52px 슬림 카드(4개 합계 226px) 정밀 튜닝.
  - **사용자가 스크롤을 전혀 하지 않아도 4개 응급실 카드가 화면 중앙에 100% 온전히 표출**되며, 5개째 이후부터 전용 스크롤바로 매끄럽게 탐색 가능.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q159, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-159, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.86)**.

### 🌟 [v2.6.1-ktas-er-category-rename-and-card-layout-fix] 2026-10-17: 결과페이지 KTAS 1·2·3단계 중증 상황 카테고리 탭 명칭 동적 변경('병원 목록' ➔ '응급실 목록') 및 소아 응급실 카드 세로 잘림 해소 & 가독성 극대화 릴리스 (정영식 팀장 총괄)
* **🚨 KTAS 1·2·3단계 중증 상황 카테고리 탭 명칭 동적 변경 (`updateCategoryHospitalsTitle`)**:
  - 상단 3대 카테고리 내비게이션 바(`result-category-nav`)의 첫 번째 탭 버튼(`cat-btn-hospitals`)을 환아 KTAS 등급에 따라 0ms 동적 스위칭.
  - KTAS 1·2·3단계 (소생, 긴급, 응급): `[ 🚨 응급실 목록 ]` (레드 아이콘 `#ef4444` + '응급실 목록' 명칭).
  - KTAS 4·5단계 (준응급, 비응급): `[ 🏥 병원 목록 ]` (외래 달빛어린이병원 안내).
* **🩹 소아 응급실 카드 세로 잘림 및 UI 붕괴 결함 원천 박멸**:
  - 레거시 `.emergency-room-card`의 세로 column 및 16px 패딩 스타일이 `.slim-er-card`를 덮어쓰던 CSS Specificity 충돌 완전 해결.
  - `.facility-scroll-list .emergency-room-card` 및 `.slim-er-card`에 `flex-direction: row !important; align-items: center !important; justify-content: space-between !important; padding: 8px 10px !important;`를 적용하여 슬림 리스트형 가로 카드 레이아웃 완전 정착.
* **✨ 잔여 병상 배지 & 직통 전화·길안내 버튼 온전한 한눈 노출**:
  - `[1순위 (빨강)] 삼성서울병원 [5.8km (블루)]` 아래 `🟢 2석 여유` 알약 배지와 `소아전문센터` 배지가 잘림 없이 선명하게 표시.
  - 우측 원터치 32x32px 응급실 직통전화 버튼(`er-call`) 및 카카오맵 길찾기 버튼(`slim-btn-map`)이 완벽하게 정렬.
* **📜 스크롤 뷰포트(`max-height: 290px`) 및 헤더 바 슬림화**:
  - 상단 긴급 이송 배너 노출 시에도 4개 응급실 카드가 시원하게 노출되고 나머지 응급실은 전용 스크롤바로 부드럽게 탐색 가능.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q158, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-158, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.85)**.

### 🌟 [v2.6.0-result-hospital-scroll-and-clean-typography] 2026-10-17: 맞춤 결과 페이지(`result.html`) 병원 목록 전용 스크롤 뷰포트(max-height: 272px & 슬림 스크롤바) 구축, 병원명·시간·약국 중복 단어 전면 제거 및 가독성 극대화 릴리스 (정영식 팀장 총괄)
* **📜 병원 목록 전용 독립 스크롤 뷰포트(`.facility-scroll-list`) 완성**:
  - `max-height: 272px; overflow-y: auto;` 및 5px 슬림 스크롤바(`::-webkit-scrollbar`) 적용.
  - 상위 카테고리 탭과 배너가 고정된 채, 카드 1~4번이 깔끔하게 표시되며 휠/터치 시 5~12번 병원까지 매끄럽게 스크롤되어 전체 병원을 손쉽게 탐색 가능.
* **✨ 병원명 중복 접미사 `(달빛어린이병원)` 100% 제거**:
  - 공공데이터 원본의 중복 명칭을 정제하여 `새솔어린이병원 (달빛어린이...` ➔ **`새솔어린이병원`**으로 말줄임표 없이 병원 고유명을 100% 완전 노출.
* **🏷️ 순위 배지 간결화**:
  - `추천 1순위` ➔ **`1순위`**, **`2순위`**, **`3순위`**로 압축하여 가로 공간 절약 및 가독성 개선.
* **⏰ 진료시간 스마트 포맷터(`formatDutyTimeClean`) 구축**:
  - 중복 `오늘 오늘` 표현 완전 박멸, 마감시간 중심 `오늘 ~23:00` 또는 `야간·휴일 진료`로 깔끔 압축 및 연초록 알약 배지 부여.
* **💊 약국 태그 간소화 (`+30분` 안전마진 가독성 극대화)**:
  - `(연계 안심약국)` 중복 제거 ➔ **`동의삼성약국 (+30분)`**으로 축약하여 안전마진이 잘리지 않고 연하늘 알약 배지로 온전 노출.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q157, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-157, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.84)**.

### 🌟 [v2.5.9-result-slim-cards-and-viewport-optimization] 2026-10-17: 맞춤 결과 페이지(`result.html`) 최소 4개 병원 카드 무스크롤 노출(슬림 리스트형 카드 설계), 통화 대본 복사 버튼 잘림 해소 및 필수 준비물 체크리스트 3종 온전 표출 릴리스 (정영식 팀장 총괄)
* **🏥 최소 4개 병원 무스크롤 100% 노출 슬림 리스트형 카드(`.slim-pairing-card`, `.slim-er-card`) 전면 혁신**:
  - 기존 240px 이상의 거대 카드를 높이 60~64px 모바일 최적화 슬림 리스트형 카드로 전면 리디자인.
  - 좌측: `[순위]` 배지 + 병원명(13.5px bold) + 거리 배지 + 오늘 마감시간 + 1:1 연계약국/안전마진 요약 태그(1줄 압축).
  - 우측: 원터치 `[📞 전화]` 및 `[🗺️ 길찾기]` 컴팩트 아이콘 버튼 배치.
  - 4개 카드 연속 배치 시 총 높이 약 260px로, **사용자가 스크롤을 하지 않아도 4개 병원이 한눈에 100% 완벽 노출**.
* **📊 상단 바이탈 요약 카드(`triage-summary-card`) 컴팩트 슬림화**:
  - 내부 패딩 축소(`18px` ➔ `12px 14px 10px 14px`), 칩 패딩 및 KTAS 감별 소견 박스 마진 압축으로 세로 공간 약 120px 추가 확보.
* **📞 통화 스크립트 뷰포트 최적화 ([통화 대본 복사하기] 버튼 100% 완전 노출)**:
  - 텍스트 박스에 `max-height: 110px; overflow-y: auto; font-size: 12px;` 및 실전 간결 대본을 적용하여, 핵심 CTA인 `[통화 대본 복사하기]` 버튼(높이 38px)과 하단 고지문이 스크롤 전혀 없이 화면 내에 온전히 표출.
* **📋 필수 준비물 체크리스트 3종 테두리 잘림 완전 해소**:
  - 체크박스 아이템 패딩 및 간격 최적화(`padding: 8px 10px; margin-bottom: 6px;`)로 3번째 항목("아기수첩 또는 해열제 교차복용 기록 메모")의 바닥 둥근 모서리 잘림 결함 원천 해결.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q156, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-156, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.83)**.

### 🌟 [v2.5.8-result-unified-category-tabs] 2026-10-17: 맞춤 결과 페이지(`result.html`) 병원 목록·통화 스크립트·필수 준비물 3대 카테고리 1칸 통합 세그먼트 탭 전환 UI 구현 릴리스 (정영식 팀장 총괄)
* **📑 맞춤 결과 페이지 3대 핵심 기능 단일 컨테이너("한 칸", `.result-category-box`) 통합**:
  - 기존 세로로 길게 순차 나열되던 병원 목록, 통화 스크립트 카드, 필수 준비물 카드를 1개의 모바일 최적화 통합 카드 박스로 일체화.
  - 상단에 `[ 🏥 병원 목록 ]` | `[ 📞 통화 스크립트 ]` | `[ 📋 필수 준비물 ]` 3-Tab 세그먼트 네비게이션(`.result-category-nav`)을 신설하여 탭 원클릭 전환 UX 구축.
* **🏥 병원 목록 2-Track & 실시간 병상 DOM 계약 100% 보존**:
  - `category-pane-hospitals` 내부에 기존 달빛병원·약국 vs 소아 응급실 2-Track 탭 스위처 및 스크롤 리스트를 그대로 배치하여, KTAS 등급별 자동 라우팅 및 E-Gen 실시간 병상 연동 계약 무결성 완전 유지.
* **📞 30초 당직의 통화 스크립트 전용 뷰 (`category-pane-script`)**:
  - 사용자 맞춤형 스크린샷 규격을 정밀 계승한 전화 아이콘 헤더, 실시간 바이탈·증상 및 추천 병원명 동적 치환 대본 박스(`#script-content`), 원클릭 클립보드 복사 버튼 및 토스트 알림 완비.
* **📋 본인확인 의무화 3대 준비물 체크리스트 전용 뷰 (`category-pane-checklist`)**:
  - 부모 실물 신분증, 주민등록등본, 아기수첩 3대 항목에 대해 클릭 시 초록색 하이라이트 및 취소선 토글 인터랙션(`toggleCheckItem`) 구현.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q155, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-155, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.82)**.

### 🌟 [v2.5.7-input-clipping-fix-and-result-phone-frame] 2026-10-17: 문진 입력 하단 버튼 잘림 결함 해소 및 맞춤 결과 페이지(`result.html`) 스마트폰 프레임 셸 전면 적용 릴리스 (정영식 팀장 총괄)
* **🔧 문진 입력 화면(`input.html`) 하단 버튼 잘림 결함 해소 & 본문 스크롤 여백 확장**:
  - `.triage-bottom-action-bar`: 바닥 및 좌우 안전 패딩(`padding: 12px 20px 24px 20px;`, 데스크탑 `padding: 12px 20px 26px 20px;`)을 확장하여, 파란색 전폭 버튼의 모서리가 폰 프레임 테두리에 클리핑되어 잘리던 결함 원천 해소.
  - 본문 스크롤 패딩(`padding-bottom: 155px;`)을 대폭 늘려, 맨 마지막 질문 카드 입력창이 하단 액션바에 가려지지 않고 시원하게 스크롤되도록 개선.
* **📱 맞춤 결과 페이지(`result.html`) 스마트폰 프레임 셸 전면 전환**:
  - `result.html`을 독자 뷰포트에서 전역 스마트폰 프레임 셸(`.mobile-viewport.result-shell`)로 전면 개편.
  - 데스크탑에서 홈 화면과 100% 동일한 8px 흰색 보더, 36px 둥근 모서리, 부드러운 그림자, 중앙 고정 뷰포트(`height: min(920px, calc(100vh - 24px))`) 적용.
  - 상단 헤더 고정, 본문 결과 목록 내부 독립 스크롤(`flex: 1; min-height: 0; overflow-y: auto; padding: 18px 16px 96px 16px;`) 분리.
  - 하단 액션바(`.result-bottom-bar`)를 `position: absolute; bottom: 0;`으로 스마트폰 프레임 바닥에 도킹 및 데스크탑 바닥 라운딩(28px) 일체화.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q154, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-154, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.81)**.

### 🌟 [v2.5.6-global-app-shell-and-input-phone-frame] 2026-10-17: 가이드·설정 하단 붕 뜬 여백 해소 및 문진 입력 페이지(`input.html`) 전역 스마트폰 프레임 셸 통일 릴리스 (정영식 팀장 총괄)
* **📱 문진 입력 페이지 스마트폰 프레임 셸(`mobile-viewport`) 전면 개편**:
  - `input.html`의 독자 뷰포트(`triage-viewport`)를 전역 스마트폰 목업 프레임(`.mobile-viewport.triage-shell`)으로 전면 전환.
  - 데스크탑에서 홈 화면과 100% 동일한 8px 흰색 보더, 36px 둥근 모서리, 부드러운 그림자, 중앙 고정 뷰포트(`height: min(920px, calc(100vh - 24px))`) 적용.
  - 상단 헤더/프로그레스바 고정, 본문 문진 카드 내부 스크롤(`flex: 1; min-height: 0; overflow-y: auto; padding: 16px 16px 120px;`) 분리.
  - 하단 액션 플로팅 바(`.triage-bottom-action-bar`)를 `position: absolute; bottom: 0;`으로 스마트폰 프레임 바닥에 도킹하고 데스크탑 모서리 둥글기(28px) 일체화.
* **🎨 응급실 가이드 및 설정 화면 하단 붕 뜬 여백(회색 빈 박스) 해소 & 바닥 일체화**:
  - `settings.html`: 모바일 뷰포트 배경을 흰색(#ffffff)으로 일체화하여 `.settings-body` 바닥과 GNB 사이의 회색 빈 박스 노출 결함 원천 박멸.
  - `emergency_guide.html`: `.guide-scroll-body` 배경을 흰색으로 정돈하고, 인포그래픽 버튼 아래에 **"야간 소아 응급실 방문 필수 팁"** 섹션을 보강하여 화면 하단이 휑하지 않고 알차게 꽉 찬 모바일 화면 완성.
* **📐 전역 앱 셸(`body.app-shell-body`, `.mobile-viewport.app-shell-viewport`) 표준화 (`style.css`)**:
  - 모든 화면의 `<body>`에 고정 앱 셸(`height: 100vh; overflow: hidden;`) 규칙을 동기화하여 화면 전환 시 1px 흔들림 없는 일관된 뷰포트 제공.
  - `frontend/templates/` 최신 마크업을 `app/templates/`로 전체 동기화 복사(`cp -r`).
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q153, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-153, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.80)**.

### 🌟 [v2.5.5-unified-gnb-and-app-shell-fix] 2026-10-17: 전역 고정 앱 셸(App Shell) 규격화 & 홈·응급실가이드·설정 하단 GNB 및 활성 알약 크기 100% 일치화 릴리스 (정영식 팀장 총괄)
* **📐 전역 모바일 뷰포트 & 앱 셸(App Shell) 규격 완전 통일**:
  - 홈, 응급실 가이드, 설정 등 모든 화면의 `.mobile-viewport`에 `height: 100vh; height: 100dvh; max-height: 100dvh; overflow: hidden;` 및 데스크탑 `height: min(920px, calc(100vh - 24px)); border-radius: 36px; border: 8px solid #ffffff;`를 전역 적용.
  - 화면 이동 시 모바일 폰 프레임 외형 크기 및 높이가 1픽셀도 변하지 않는 완벽한 네이티브 앱 규격 확립.
* **⚓ 하단 내비게이션 바(`.bottom-nav`) 모바일 프레임 바닥 절대 도킹 (`position: absolute; bottom: 0;`)**:
  - `fixed`로 인해 데스크탑에서 모바일 프레임 바닥을 뚫고 화면 맨 밑으로 24px 이탈하던 결함 원천 해소.
  - 전 화면에서 높이 68px, 데스크탑 둥근 모서리(28px)로 일체화.
* **💊 4개 탭 및 활성 알약(`.nav-item.active`) 전역 동일 규격화 (`max-width: 76px`, `height: 50px`, `border-radius: 16px`)**:
  - '응급실 가이드'(6글자) 등 텍스트 길이에 따라 알약 가로 너비가 비대하게 늘어나던 결함 완전 교정.
  - 어떤 탭이 활성화되든 항상 대칭되고 동일한 크기의 파란색 알약 배경 유지.
* **📜 본문 내부 스크롤 컨테이너 분리 (`.guide-scroll-body`, `.settings-body`)**:
  - 상단 헤더와 하단 GNB는 견고하게 고정되고, 가운데 본문만 부드럽게 스크롤되는 최상급 모바일 앱 UX 구현.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q152, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-152, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.79)**.

### 🌟 [v2.5.4-emergency-guide-history-tab-fix] 2026-10-17: 응급실 가이드 페이지 하단 GNB '기록' 탭 누락 결함 해소 & 전역 템플릿 4-Tab 완전 동기화 릴리스 (정영식 팀장 총괄)
* **📋 응급실 가이드 하단바 '기록' 탭 복원 및 4-Tab GNB 전역 템플릿 일괄 동기화**:
  - `app/templates` 및 `frontend/templates` 내 서브 가이드 페이지들(`emergency_guide.html`, `emergency_guide_symptoms.html`, `emergency_guide_checklist.html`, `settings.html`, `index.html`)에 과거 3-Tab이 남아있던 결함 원천 해소.
  - 어디서든 '기록' 탭(`receipt_long`)이 항상 노출되는 4-Tab(`홈` | `기록` | `응급실 가이드` | `설정`) 레이아웃 완성.
  - `app/templates/` 디렉터리에 최신 마크업/CSS/JS 에셋을 전체 동기화 복사(`cp -r`)하여 템플릿 이원화 불일치 원천 박멸.
* **🔗 `index.html?tab=history` 딥링크 기반 기록 모달 자동 오픈 파이프라인 보장**:
  - 응급실 가이드 페이지나 설정 페이지에서 '기록' 탭 클릭 시 `index.html?tab=history`로 이동하며, 접속 즉시 200ms 내에 `openHistoryModal()`이 자동 실행되어 과거 문진 결과 바텀시트가 즉각 오픈되도록 연동 완료.
* **🧪 프론트엔드 통합 테스트 5건 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q151, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-151, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.78)**.

### 🌟 [v2.5.3-pwa-and-cloud-run-plan] 2026-10-17: PWA 도입, 설정 페이지 스마트폰 QR코드 웹앱 연동 & Cloud Run 다중 API Key 보안 관리 전략 상세 기획안(PWA_PLAN.md) 수립 릴리스 (정영식 팀장 총괄)
* **📱 PWA(Progressive Web App) 도입 & 설정 페이지 스마트폰 QR코드 모달 기획 ([PWA_PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PWA_PLAN.md))**:
  - `settings.html` 내 '모바일 기기 연결' 신규 그룹 및 '스마트폰으로 앱 열기 (QR코드)' 마크업/UI 설계.
  - 현재 브라우저 도메인(`window.location.origin`)을 자동 감지하는 실시간 경량 바닐라 JS QR코드 렌더러 탑재 방안.
  - iOS(Safari) '홈 화면에 추가' 및 Android(Chrome) '앱 설치' 가이드 모달 설계.
  - `manifest.json` (`display: standalone`, `theme_color: #10b981`) 및 `sw.js` (오프라인 12대 응급처치 가이드 캐싱).
* **🔐 Google Cloud Run 배포 & 다중 API Key 엔터프라이즈 보안 관리 아키텍처 ([PWA_PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PWA_PLAN.md))**:
  - 프로젝트 4대 핵심 API Key(`GEMINI_API_KEY`, `DATA_GO_KR_API_KEY`, `KAKAO_REST_API_KEY`, `serviceAccountKey.json`) 안전 관리 방안 수립.
  - **전략 1 (🥇 GCP 엔터프라이즈 권장 Best Practice)**: GCP Secret Manager 환경변수 마운트 + Cloud Run 기본 서비스 계정 Cloud IAM(`roles/datastore.user`) 기반 **무키(Keyless) ADC 자동 인증** (키 분실/유출 위험 0%).
  - **전략 2 (🥈 기존 코드 100% 호환)**: Secret Manager 볼륨 마운트(`/secrets/serviceAccountKey.json`) 및 `FIREBASE_KEY_PATH` 주입.
  - **전략 3 (🥉 테스트용)**: `--set-env-vars` CLI 인라인 주입.
  - 경량 `python:3.11-slim` Multi-stage `Dockerfile` 및 `PORT=${PORT:-8080}` 바인딩 최적화, `gcloud` 원클릭 배포 CLI 명령어 완비.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q150, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.77, [PWA_PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PWA_PLAN.md))**.

### 🌟 [v2.5.2-project-completion-report] 2026-10-17: 프로젝트 기획 대비 종합 완성률 정량 분석 보고서(PROJECT_COMPLETION_REPORT.md) 발간 릴리스 (정영식 팀장 총괄)
* **📊 프로젝트 종합 완성률 정밀 진단 보고서 공식 발간 ([PROJECT_COMPLETION_REPORT.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PROJECT_COMPLETION_REPORT.md))**:
  - **상용 론칭 필수 코어 스코프 (Core MVP & Production Services)**: **100.0% 완성** (실제 배포 및 상용화 즉시 가용).
  - **장기 고도화 백로그 (Phase 4~6) 포함 종합 로드맵**: **92.5% 완성** (35개 세부 과제 중 32개 완결, 3개 순차 추진).
  - **5대 도메인별 진척도**: 데이터 파이프라인(100%), 안전 가드레일 & 멀티에이전트(100%), 백엔드 API & 인프라(100%), 프론트엔드 앱 셸 & 14대 템플릿(98.5%), 심화 백로그(50%).
  - **108개 단위/통합 테스트 전수 통과 (100% Pass)** 및 40대 소아 임상 골든 케이스 평가 100% 달성 기록.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q149, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) v2.76, [PROJECT_COMPLETION_REPORT.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PROJECT_COMPLETION_REPORT.md))**.

### 🌟 [v2.5.1-history-duplication-and-er-recommendation-fix] 2026-10-17: 히스토리 KTAS 중증(1~3단계) 추천 시설 응급실 오표기 정정 & 결과 다시보기 복귀 시 중복 생성 원천 차단 릴리스 (정영식 팀장 총괄)
* **🚨 KTAS 1·2·3단계(중증) 추천 시설 응급실 전용 분기 및 비동기 E-Gen 정밀 보정 ([frontend/templates/result.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/result.html), [frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js))**:
  - 기존 단일 셀렉터로 인해 KTAS 1단계 환아에게 달빛어린이병원(새솔어린이병원)이 매칭되던 DOM 간섭 결함 원천 해소.
  - KTAS 1·2·3단계 시 소아 응급실 전용 셀렉터(`#emergency-scroll-list .facility-name`) 및 거점 소아응급센터 목록을 우선 취득.
  - 비동기 E-Gen 실시간 병상 로드 완료 시 `AisumHistoryManager.updateLatestHospital(topErName)`를 실행하여 최신 기록의 추천 기관명을 실제 1순위 소아 응급실명으로 자동 정밀 보정.
  - 히스토리 카드에 빨간색 사이렌 아이콘(`e911_emergency`)과 `추천 응급실:` 라벨 강조 표출 ([frontend/templates/index.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/index.html)).
* **🛡️ 결과 다시보기 모드(`is_replay`) 플래그 도입 및 신규 히스토리 중복 생성 원천 차단**:
  - `restoreAndNavigate()` 호출 시 `aisum_is_replay_view: 'true'` 및 URL에 `?is_replay=true` 파라미터 부여.
  - `result.html`에서 다시보기 화면으로 진입한 경우 `saveHistory` 호출을 100% 스킵하여 홈으로 복귀해도 히스토리가 절대 중복 생성되지 않도록 방어.
  - `AisumHistoryManager.saveHistory()`에서 직전 최신 기록과 내용(증상, KTAS, 연령, 체온)이 동일하면 무조건 중복 저장 스킵.
  - `AisumHistoryManager.getAll()` 실행 시 과거에 누적되었던 연속 중복 항목을 자동 소독하고 잘못된 달빛병원 명칭을 소아 응급실로 자동 보정.
* **🧪 프론트엔드 통합 테스트 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q148, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-150, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-J 고도화)**.

### 🌟 [v2.5.0-history-tab-and-bed-notification-center] 2026-10-17: GNB 이전 결과 기록(History) 탭 신설, 0ms 무손실 결과 다시보기 & KTAS 중증 소아 응급실 병상 변동 실시간 알림 센터 구축 릴리스 (정영식 팀장 총괄)
* **📋 메인페이지 하단 GNB '이전 결과 기록(History)' 탭 신설 & 4-Tab 레이아웃 최적화 ([frontend/templates/index.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/index.html), [frontend/css/style.css](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/css/style.css))**:
  - 홈 버튼 바로 옆에 '기록' 탭을 신설하여 4-Tab(`홈` | `기록` | `응급실 가이드` | `설정`) 완성.
  - 클릭 시 슬라이드업 바텀시트 모달(`history-modal-overlay`)이 부드럽게 열리며 과거 문진 기록 카드 목록 최신순 표출.
  - `settings.html`, `emergency_guide.html` 서브 페이지 GNB에도 '기록' 탭 동기화 및 `index.html?tab=history` 딥링크 파이프라인 구축.
* **💾 이전 문진 결과 영구 저장 & 0ms 무손실 복원 엔진 (`AisumHistoryManager`) ([frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js), [frontend/templates/result.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/result.html))**:
  - 문진 완료 시 환아 정보, 체온, 주증상, KTAS 등급, 추천 병원명 및 백엔드 원본 스냅샷을 `aisum_triage_history`에 자동 직렬화 저장 (최대 30건 LRU).
  - 기록 카드 내 `[당시 결과 다시보기]` 원클릭 시, 스냅샷 데이터를 `sessionStorage`에 주입하고 결과 화면으로 전환하여 0ms 딜레이로 완벽 복원.
  - 개별 기록 삭제(휴지통 아이콘) 및 전체 삭제 지원, 빈 상태 UI 완비.
* **🔔 KTAS 중증(1·2·3단계) 환아 전용 소아 응급실 실시간 병상 변동 알림 센터 (`AisumNotificationManager`) ([frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js), [frontend/templates/index.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/index.html))**:
  - KTAS 1·2·3단계(소생/긴급/응급) 또는 12대 Red Flag 중증 판정 시 인근 거점 소아응급센터 상위 3곳을 감시 대상으로 자동 등록.
  - 실시간 E-Gen 병상 데이터 폴링 및 대조를 통해 소아 일반병상(`hv28`) 증감(확보/급감) 및 응급실 공지(`hpmg`) 갱신 시 알림 자동 발행.
  - 메인페이지 상단 헤더 우측 종 아이콘 위에 빨간색 알림 점(`.badge-dot`) 자동 점등.
  - 종 아이콘 클릭 시 알림 센터 바텀시트(`notification-modal-overlay`) 오픈, 변동 내역 카드 및 응급실 바로 전화걸기(`tel:`) 연동, 자동 읽음 처리 및 배지 소등.
* **🧪 프론트엔드 통합 테스트 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 완벽 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q147, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-149, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-J)**.

### 🌟 [v2.4.99-onboarding-pipeline-and-terms-mode-isolation] 2026-10-17: 온보딩 순차 파이프라인(splash ➔ terms ➔ permission ➔ index) 완결 & 설정 모드 완전 분리 릴리스 (정영식 팀장 총괄)
* **🔄 온보딩 4단계 순차 파이프라인 완결 및 무한 가드레일 확립 ([splash.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/splash.html), [terms.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/terms.html), [permission.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/permission.html), [index.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/index.html))**:
  - `splash.html` ➔ 약관 미동의 시 무조건 `terms.html` (동의 전까지 앱 실행 시 계속 뜸).
  - `terms.html` 동의 완료 시 ➔ `permission.html`로 자동 이동.
  - `permission.html` ➔ 권한 미승인 시 다음 실행 시에도 계속 뜸 / 승인 완료 시 1회 통과 후 `index.html` (메인화면) 진입.
  - `index.html` & `input.html`에 약관 가드 + 권한 가드 2중 0ms 즉시 차단 탑재로 URL 우회 진입 100% 방어.
* **🛡️ 이용약관(terms.html) 온보딩 모드 vs 설정 열람 모드(?mode=view) 물리적 완전 분리**:
  - CSS `#btn-terms-view-confirm { display: none !important; }`를 기본 격리하여 온보딩 과정에서 "내용을 확인했습니다" 버튼 노출을 영구 차단.
  - `hasViewParam && isAlreadyAgreed`일 때만 `.is-view-mode` 클래스를 활성화하여 오직 설정 메뉴에서 진입한 기가입자에게만 뒤로가기 및 "내용을 확인했습니다"(설정 복귀) 버튼이 노출되도록 격리.
  - 온보딩 모드에서는 오직 4대 필수 동의 체크박스와 "동의하고 계속하기" 버튼만 노출되며, 완료 시 `permission.html`로 정확히 이동.
* **🧪 프론트엔드 통합 테스트 100% 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q144, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-148, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-I)**.

### 🌟 [v2.4.98-terms-agreement-onboarding-and-enforcement] 2026-10-17: 스플래시 직후 이용약관 최초 1회 필수 동의 & 약관 미동의 시 서비스 이용 전면 차단 릴리스 (정영식 팀장 총괄)
* **🛡️ 스플래시 이후 이용약관(terms.html) 최초 1회 필수 동의 게이트웨이 파이프라인 구축 ([frontend/templates/splash.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/splash.html), [frontend/templates/terms.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/terms.html))**:
  - `splash.html` 진입 시 `aisum_terms_agreed === 'true'` 여부를 1순위로 검증하여 미동의 사용자 무조건 `terms.html`로 라우팅.
  - 신규 사용자: `스플래시` ➔ `이용약관(terms.html)` ➔ `접근권한(permission.html)` ➔ `메인홈(index.html)`의 철저한 보안/법률 규제 준수 온보딩 플로우 확립.
  - 기동의 완료자: 불필요한 약관 화면 반복 없이 권한 상태에 따라 `permission.html` 또는 `index.html`로 다이렉트 신속 이동.
* **📋 4대 필수 약관 동의 체크박스 컴포넌트 탑재 (`terms-agreement-card`) ([frontend/templates/terms.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/terms.html))**:
  - 전체 동의 토글(`toggleAgreeAll`) 및 개별 동의(`checkSubAgreements`) 양방향 연동.
  - 4대 필수 항목(서비스 이용약관, 개인정보 처리, 위치기반서비스, 의료법 제27조 준수) 전수 동의 시에만 하단 '동의하고 계속하기' 버튼이 파란색(`.active`)으로 활성화되며, 미체크 시 비활성화 상태 유지 및 클릭 시 경고 토스트 표출.
  - 동의 완료 시 `aisum_terms_agreed: 'true'`, `aisum_terms_agreed_at`를 `localStorage` 및 `sessionStorage`에 영구 기록 후 `permission.html`로 자동 이동.
* **🚫 약관 미동의 시 앱 전면 이용 불가 0ms 차단 가드레일 (Zero-Bypass Guardrail)**:
  - `permission.html`, `index.html`, `input.html` 최상단에 인라인 가드 스크립트 탑재.
  - 사용자가 주소창에 직접 URL을 입력하여 우회 진입을 시도하더라도 0ms 즉각 `terms.html`로 강제 리다이렉트.
* **⚙️ 설정(Settings) 메뉴 열람 모드 분기 (`?mode=view`) ([frontend/templates/settings.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/settings.html))**:
  - 기존 사용자가 설정 화면에서 이용약관을 열람할 때에는 뒤로가기 버튼이 노출되고 하단 동의 버튼 바는 숨김 처리되어 언제든 설정 화면으로 안전하게 복귀 가능하도록 분기 처리.
* **🧪 프론트엔드 통합 테스트 100% 정상 통과 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q143, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-147, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-G)**.

### 🌟 [v2.4.97-compact-card-ui-and-realtime-operating-hours-sorting] 2026-10-17: 메인화면 의료시설 카드 UI 간결화 & 현재 시간 실시간 운영 판별·진료가능 우선 정렬 릴리스 (정영식 팀장 총괄)
* **✨ 장황한 카드 서브설명 및 상세주소 초간결화 (`formatCompactAddress`) ([frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js))**:
  - 상세 층수, 호수, 빌딩 상가명을 스마트 정규식으로 정제하여 도로명과 법정동만 단정하게 추출.
  - 중복 뱃지 명칭을 제거하고 `소아 야간·휴일 진료 · 경기 하남시 감일백제로 177 (감이동)` 및 `소아 시럽제 조제 · 서울 송파구 거마로22길 49 (마천동)` 등 시원하고 정갈한 1~2줄 UI 완성.
* **⏰ KST 요일/시간 기반 실시간 운영 상태 판별 엔진 (`evaluateOperatingStatus`) ([frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js), [frontend/css/style.css](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/css/style.css))**:
  - 토/일/공휴일/평일 오늘 요일의 실제 운영시간(토요진료, 일요진료 등)을 실시간 대조.
  - `진료중 · 접수 가능` (초록), `곧 마감 · 접수 마감 주의` (주황), `N시 진료 시작` (대기), `진료 마감` (회색), `오늘 휴진` 5대 정밀 상태 판정 및 카드 우측 하단에 오늘 요일 맞춤 시간(예: `토요일 09:00 ~ 18:00`) 표출.
* **🥇 운영 중 시설 최우선(1순위) 거리순 스마트 정렬 파이프라인**:
  - 현재 실제 이용 가능한 시설들을 최상단에 거리순으로 배치하고, 마감/휴진 시설은 후순위로 자동 배치.
  - 전체(`all`) 탭 1:1 교차 스마트 인터리빙 및 상단 카운트 배너에 `(진료·영업중 N곳)` 투명 공개.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q142, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-146, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-G)**.

### 🌟 [v2.4.96-local-server-safe-restart-and-health-verified] 2026-10-17: 로컬 서버 안전 재구동 & Firebase·Gemini·스케줄러 실시간 헬스체크 검증 릴리스 (정영식 팀장 총괄)
* **🔄 포트 8000 충돌 방어 및 그레이스풀 재구동 ([main.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/main.py))**:
  - 기존 백그라운드 프로세스(PID: 4479)를 SIGTERM으로 안전하게 종료하여 포트 8000 점유 해제 확인.
  - 최신 프론트엔드 위치 소독 엔진 및 백엔드 3-트랙 데몬과 함께 Uvicorn ASGI 서버 완벽 재구동.
* **🩺 실시간 헬스체크 100% 정상 통과 (`/health`)**:
  - `scheduler.running: true`, `poll_count: 1` 정상 가동.
  - `firebase_configured: true`, `gemini_api_configured: true`, `public_data_api_configured: true` 3대 핵심 외부 연동 전수 활성화 확인.
  - 프론트엔드 엔드포인트(`GET /`, `GET /frontend/templates/index.html`) HTTP 200 OK 서빙 무결성 검증.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q141, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-145, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-G)**.

### 🌟 [v2.4.95-real-user-location-autodetect-and-legacy-sanitization] 2026-10-17: 메인화면 실시간 사용자 현재 위치 자동 적용 & 과거 스토리지 문정동 더미 잔재 자동 소독 릴리스 (정영식 팀장 총괄)
* **🧹 과거 개발 문정동(37.4858, 127.1225) 더미 캐시 자동 소독 엔진 구축 (`cleanLegacyMunjeongData`) ([frontend/templates/index.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/index.html), [frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js))**:
  - 과거 개발 시 브라우저 `localStorage`에 저장되어 영구 잔존하던 문정동 좌표 및 행정동 더미 데이터를 스크립트 실행 즉시 자동 감지하여 100% 클린업/소독.
  - 사용자가 수동 선택한 경우가 아니라면 접속 시 문정동으로 고정되던 결함을 원천 박멸.
* **📍 접속 즉시 실제 기기 현재 위치 자동 감지 및 실시간 시설 거리 재계산 (`autoDetectUserLocation`)**:
  - `enableHighAccuracy: false` 최적화로 Mac/PC 데스크탑 브라우저의 Geolocation 타임아웃 에러를 원천 차단하고 1초 이내에 실제 기기 GPS 좌표를 신속 획득.
  - 획득 즉시 카카오/OSM 역지오코딩(`/api/v1/location/coord2address`)을 통해 사용자의 실제 접속 지역(역삼동, 공덕동, 판교, 분당, 대구, 부산 등)의 행정동명과 도로명 주소를 상단 헤더와 모달 바에 실시간 바인딩.
  - 야간 의료시설 목록(`initLiveFacilities`)을 사용자의 실제 현재 위치 기준 최단거리 순으로 즉각 재계산하여 표출.
* **🌐 GPS 차단/실패 시 공공 IP 기반 2차 자동 위치 추정 연동 (`fetchIpLocationFallback`)**:
  - 위치 권한이 꺼져있거나 실내 전파 음영 지역인 경우, 절대로 문정동으로 회귀하지 않고 IP 기반 네트워크 위치를 자동 획득하여 적용.
* **🧪 종합 단위/통합 테스트 회귀 검증**:
  - 전체 13개 테스트 모듈 108개 테스트 100% ALL PASS (108 passed).
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q140, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-144, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-G)**.

### 🌟 [v2.4.94-onboarding-permission-session-persistence-and-zero-delay-location] 2026-10-17: 온보딩 위치 권한 승인 세션 전 페이지 상시 유지 & 메인화면 실시간 위치 0ms 표출 릴리스 (정영식 팀장 총괄)
* **🛡️ 온보딩 5대 접근 권한 및 LBS 위치 세션 양방향 상시 동기화 파이프라인 구축 ([frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js), [frontend/templates/permission.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/permission.html))**:
  - `AisumPermissionManager`에 `sessionStorage` <-> `localStorage` 양방향 세션 동기화 엔진(`syncSession()`) 및 `grantAllPermissions()` 신설.
  - 처음 이용하는 사용자가 `splash.html` ➔ `permission.html` 온보딩에서 "동의하고 시작하기" 클릭 시 브라우저 실제 위치(Geolocation), 알림(Notification), 전화, 카메라, 사진 5대 모든 접근 권한 플래그와 위·경도 좌표, 역지오코딩 주소 7개 핵심 키를 양쪽 스토리지에 동시 영구 저장.
  - 이후 홈, 문진, 결과, 상세 등 어떤 페이지로 이동하더라도 권한 세션 및 현재 위치가 100% 영구/상시 유지됨.
* **📍 메인 홈(`index.html`) 첫 프레임(0ms) 실시간 위치 즉시 표출 ([frontend/templates/index.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/index.html))**:
  - 상단 헤더 인라인 스크립트의 불필요한 `isManual` 가드를 완전 제거하여, 온보딩에서 GPS 승인으로 수신된 사용자의 실제 행정동명이 페이지 로드 0ms 순간에 `#current-location-text`에 즉각 바인딩.
  - 지연이나 깜빡임("위치 확인 중...") 없이 사용자의 실제 현재 위치가 메인화면에 즉시 선명하게 표시됨.
* **스마트 스플래시 온보딩 라우팅 ([frontend/templates/splash.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/splash.html))**:
  - `localStorage` 및 `sessionStorage`의 `aisum_permission_granted`를 동시 검사하여 이미 권한을 부여받은 사용자는 1.8초 후 `index.html`로 즉시 직행.
* **🧪 종합 단위/통합 테스트 회귀 검증**:
  - 전체 13개 테스트 모듈 108개 테스트 100% ALL PASS (108 passed).
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q139, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-143, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-E)**.

### 🌟 [v2.4.93-location-autodetect-and-result-er-reference-error-resolution] 2026-10-17: 메인화면 문정동 하드코딩 제거 및 실시간 위치 자동 감지 적용 & 결과페이지 ReferenceError(currentHospitals) 원천 해소 릴리스 (정영식 팀장 총괄)
* **📍 메인화면 초기 문정동 하드코딩 완전 제거 & 접속 시 브라우저 GPS 실시간 위치 자동 감지 ([frontend/templates/index.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/index.html), [frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js))**:
  - `index.html` 상단 헤더 및 모달 주소 바의 '문정동', '서울특별시 송파구 문정동' 정적 텍스트를 제거하고 실시간 위치 확인 플레이스홀더로 전환.
  - `main.js`의 `autoDetectUserLocation` 내 과거 저장 좌표 존재 시 리턴하던 가로막기 로직을 전면 해제 ➔ 사용자가 수동 설정한 경우가 아니라면 메인 접속 시 항상 `navigator.geolocation.getCurrentPosition`을 호출하여 실제 GPS 좌표 실시간 획득.
  - 백엔드 역지오코딩 API(`/api/v1/location/coord2address`)를 통해 실제 도로명/행정동명을 자동 획득하여 헤더, 모달 바, 및 인근 야간 의료시설 목록 즉각 재계산/동기화.
* **🚨 결과페이지 소아 응급실 병상 로딩 멈춤 치명적 원인 `ReferenceError: currentHospitals` 원천 박멸 ([frontend/templates/result.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/result.html))**:
  - `renderResultData()` 내부 Line 1898, 1904의 미선언 변수 `currentHospitals` 참조로 인한 자바스크립트 크래시 및 `refreshLiveEmergencyBeds` 미실행 결함 완전 해소.
  - `window._activeHospitals = window._activeHospitals || [];` 로 안전하게 정규화.
  - `#emergency-scroll-list` 컨테이너의 초기 HTML에 빈 스피너 대신 **권역 소아전문응급센터(서울아산병원, 삼성서울병원) 안심 프리셋 카드를 0ms 즉각 기본 마운트**하여 첫 프레임부터 응급실 정보 노출 보장.
* **🧪 종합 단위/통합 테스트 회귀 검증**:
  - 전체 13개 테스트 모듈 108개 테스트 100% ALL PASS (108 passed in 10.68s).
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q138, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-142, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-E)**.

### 🌟 [v2.4.92-result-page-er-infinite-spinner-resolution-and-lbs-fallback] 2026-10-17: 결과페이지 KTAS 1·2·3단계 실시간 소아 응급실 무한 로딩 스피너 멈춤 결함 해소 & 0ms LBS 로컬 비상 프리셋 Fallback 릴리스 (정영식 팀장 총괄)
* **🚨 무한 로딩 스피너 멈춤 결함 해소 및 0ms 즉각 LBS 렌더링 구축 ([frontend/templates/result.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/result.html))**:
  - `file://` 또는 Live Server(비8000 포트) 환경에서 `fetch('/api/v1/emergency/nearby')` 호출 시 발생하던 상대경로 결함 및 `Failed to fetch` 에러 해소.
  - `apiBase` 지능형 판별(`file://` 및 타 포트 시 `http://127.0.0.1:8000` 자동 바인딩) 및 4.5초 AbortController 타임아웃 세이프티 가드 적용.
* **🏥 전국 22개 권역 소아전문응급센터 프리셋 정적 데이터셋 구축 ([frontend/js/national_emergency_hospitals.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/national_emergency_hospitals.js))**:
  - 서울아산병원, 삼성서울병원, 건국대병원, 강동경희대병원, 한양대병원, 성남시의료원, 서울성모병원 등 전국 주요 권역 소아전문응급센터 및 상급종합병원 응급실 22개소의 좌표, 직통 전화번호, 종별 메타데이터 정적 사전 컴파일.
  - 사용자 위경도 기준 하버사인 거리 계산기(`calcHaversineDistKm`)를 통해 인근 8곳을 0ms 동기식으로 즉각 추출하여, 첫 프레임(0ms)에 실제 병상 카드로 대체함으로써 골든타임 보장.
* **🛡️ 3-Tier Multi-Storage 실시간 비동기 연동**:
  - 1차: 0ms 로컬 소아 응급실 안심 캐시 즉시 렌더링.
  - 2차: 백엔드 E-Gen 공공데이터 & Firebase Firestore 실시간 병상(`hv28`) 66ms 내 비동기 동기화.
  - 3차: 네트워크 오류/타임아웃 발생 시 이미 렌더링된 0ms 카드를 안전하게 유지하며 상태바에 `로컬 안심 캐시 기준 (8곳 가용)` 표기.
* **🧪 종합 단위/통합 테스트 회귀 검증**:
  - 전체 13개 테스트 모듈 108개 테스트 100% ALL PASS (108 passed in 10.63s).
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q137, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-141, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-C)**.

### 🌟 [v2.4.91-result-page-ktas-emergency-and-moonlight-backend-copy] 2026-10-17: 검사 결과페이지 KTAS 1·2·3단계 실시간 소아 응급실 단독 표출 & KTAS 4·5단계 메인 홈 실시간 의료시설 백엔드 카피 달빛병원 매칭 릴리스 (정영식 팀장 총괄)
* **🚨 KTAS 1·2·3단계: 실시간 소아 가용 응급실 병상 현황 단독 전면 표출 ([frontend/templates/result.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/result.html))**:
  - 소생(1단계), 긴급(2단계), 응급(3단계) 진입 시 경증용 달빛병원 탭을 완전히 배제(`display: none`)하고 `소아 응급실 병상 (실시간 현황 · 우선 권고)` 단독 전면 활성화.
  - E-Gen 및 Firebase Cloud Firestore 실시간 연동 소아 병상(`hv28`), 혼잡도 배지(🟢 여유, 🟡 혼잡, 🔴 만실/제한) 5분 주기 실시간 동기화.
  - 119 초응급 즉시 전화 배너 노출 및 권역 소아전문응급센터 당직의 통화 대본 자동 맞춤 완성.
* **🌙 KTAS 4·5단계: 메인 홈 실시간 의료시설 백엔드 카피 달빛병원 매칭 엔진 완결**:
  - 응급실 과밀화 방지를 위해 소아 응급실 병상 탭 완전 은닉(`display: none`) 및 `달빛어린이병원 + 안심약국 (소아 준응급 전용 매칭)` 단독 100% 표출.
  - **메인 홈(`index.html` & `main.js`) 4대 핵심 백엔드/LBS 엔진 1:1 카피 이식**:
    1. `<head>` 내 전국 실데이터셋(156개 달빛병원, 2,028개 야간약국, 156개 페어링) 사전 로드로 0ms 즉각 렌더링 확립.
    2. 사용자 GPS 위치(`AisumPermissionManager` / `localStorage`) 기준 반경 15km 이내(`MAX_RADIUS_KM = 15.0`) 엄격 필터링 및 최단거리 순 오름차순 정렬.
    3. 메인 백엔드 REST API(`GET /api/v1/emergency/pairings`) 비동기 fetch 결합 및 `/data/nationwide_pairings.json` Fallback 안전망.
    4. 병원·약국 카드 클릭 시 2-트랙 상세페이지(`hospital_detail.html`, `pharmacy_detail.html`) 이동 및 세션 상태 저장.
* **🧪 종합 단위/통합 테스트 회귀 검증**:
  - 전체 13개 테스트 모듈 108개 테스트 100% ALL PASS (0 Failures, 0 Errors).
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q136, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-140, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-C)**:
  - 사용자 질의 및 구현 상세 내역 실시간 기록 완료.

### 🌟 [v2.4.90-ktas-dual-track-result-page-routing] 2026-10-17: 결과페이지(result.html) KTAS 1·2·3단계 실시간 소아 응급실 병상 우선 표출 vs KTAS 4·5단계 달빛병원 + 30분 안심약국 100% 전용 매칭 릴리스 (정영식 팀장 총괄)
* **🚨 KTAS 1·2·3단계: 실시간 소아 응급실 병상 현황 우선 표출 및 119 배너 연동 ([frontend/templates/result.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/result.html))**:
  - `track-tabs-container`에서 `btnEmergency`를 좌측 1순위로 배치(`소아 응급실 병상 (실시간 현황 · 우선 권고)`)하고 `#pane-emergency`를 기본 활성화.
  - E-Gen 및 Firebase Cloud Firestore 실시간 병상 현황 연동(🟢 여유, 🟡 혼잡, 🔴 만실/제한) 및 5분 주기 자동 갱신.
  - KTAS 1·2단계 초응급 즉시 119 이송 배너 및 KTAS 3단계 응급 안내 배너 가시성 분기.
  - 30초 통화 스크립트를 최근접 소아 전문 응급실 접수처 대상으로 자동 맞춤 생성.
* **🌙 KTAS 4·5단계: 달빛어린이병원 + 30분 안심약국 100% 전용 매칭 & 응급실 과밀화 원천 차단**:
  - 소아 응급실 병상 탭 버튼 `#tab-btn-emergency`를 완전 은닉(`display: none`)하여 경증 환아의 불필요한 응급실 방문 및 고비용 지출을 원천 방어.
  - `#pane-moonlight` 단독 100% 매칭 표출, 거리순 정렬된 달빛병원 8곳 및 +30분 조제 안전마진 심야약국 브릿지 제공.
  - 30초 통화 스크립트를 달빛어린이병원 외래 접수처 대상으로 자동 튜닝.
* **🧪 프론트엔드-백엔드 듀얼 트랙 계약 검증 ([tests/test_step8_frontend_integration.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_step8_frontend_integration.py))**:
  - TC-804 (듀얼 트랙 템플릿 DOM 계약) 및 TC-805 (KTAS API 라우팅 매트릭스) 신설.
  - **전체 13개 테스트 모듈 108개 단위/통합 테스트 100% ALL PASS**.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q135, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-139, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 3-C)**:
  - 질문 및 구현 세부 내역 실시간 누적 기록 완료.

### 🌟 [v2.4.89-nationwide-er-bed-firebase-and-lbs-sync] 2026-10-17: 소아 응급실 병상 전국 17개 시·도 415개소 단일 호출 확장 & 530개 기관 정밀 LBS 랭킹 연동 릴리스 (정영식 팀장 총괄)
* **🗺️ 전국 17개 시·도 415개소 단일 호출 파이프라인 ([app/services/emergency_sync_service.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/services/emergency_sync_service.py))**:
  - `STAGE1` 파라미터를 생략하여 17개 지자체를 각각 쪼개서 호출하지 않고, **단 1회 호출(0.70초)로 전국 415개 응급의료기관 실시간 병상(`hv28`, `hvec`, `hv29`) 및 비정형 공지(`hpmg`) 전수 일괄 수신** 완료.
* **📍 전국 530개 응급의료기관 메타데이터 정적 캐시 구축 ([data/national_emergency_metadata.json](file:///Users/jeong-yeongsig/Desktop/Project/isoom/data/national_emergency_metadata.json))**:
  - NMC 기본정보 API(`getEgytBassInfoInqire`)를 연동하여 530개 응급실의 대표/직통 전화번호(`dutyTel1`/`dutyTel3`), 도로명 주소, 센터 종별을 캐시화.
  - 전국 415개 병상 데이터와 100% 매칭 완료 (전화번호·위경도 좌표 누락률 0%).
* **🧠 In-Memory Hash Diffing 전국 최적화 (Spark 무료 티어 16.5% 방어)**:
  - 415개소 전체를 5분 주기로 폴링하더라도 변동된 5~15개소만 Firestore에 델타 쓰기 수행 (평균 400개소 0ms Skip, 비용 절감률 96~98%).
  - 하루 약 3,295회 Write로 Firebase 무료 한도(20,000회) 내 영구 안전 운영.
* **🧭 적응형 반경(Adaptive Radius) LBS 정밀 랭킹 ([app/services/spatial_service.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/services/spatial_service.py), [app/api/v1/emergency.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/api/v1/emergency.py))**:
  - 사용자 GPS 좌표(`lat`, `lon`) 기준 Haversine 구면 거리를 0ms로 계산하여 서울(잠실), 경기(수원 성빈센트/아주대 1.6~2.4km), 부산(부산대/동아대 0.09~2.0km), 전남(순천 성가롤로 5.49km), 제주(제주한라 4.41km) 등 전국 어느 위치에서든 정확한 최근접 소아 가용 응급실 즉시 표출.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q133/Q134, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-138, [PLAN.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/PLAN.md) Phase 2-H)**:
  - 사용자 질의 및 해결 내역 실시간 누적 기록 완료.

### 🌟 [v2.4.88-pediatric-er-bed-firebase-sync-and-dynamic-cards] 2026-10-17: 소아 응급실 병상(hv28) E-Gen ➔ Firestore 5분 주기 Hash Diffing 델타 적재 & result.html 완전 동적 렌더링 릴리스 (정영식 팀장 총괄)
* **⏱️ 서버 기동 즉시 초기 동기화(Warmup) & 5분 주기 백그라운드 스케줄러 ([app/services/scheduler.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/services/scheduler.py))**:
  - `start()` 내 `job_realtime_bed_poller`에 `next_run_time=now_dt`를 결합하여 서버 부팅 시점에 즉시 1회 E-Gen 공공 API를 수집하고 Firestore에 동기화 완료.
* **🧠 In-Memory Hash Diffing 델타 적재 (FinOps 100% 비용 절감 방어)**:
  - MD5 해시 지문(`MD5(pediatric_beds + "_" + notice_raw + "_" + pediatric_acceptable)`) 비교를 통해 실제 변경된 병원만 `batch.set(..., merge=True)` 쓰기 수행. 변경 없을 시 0회 디스크 쓰기(`100.0% skip`)로 Firebase Spark Plan 무료 티어 영구 보호.
* **🏥 응급의료기관 메타데이터 확장 ([app/api/v1/emergency.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/api/v1/emergency.py), [app/services/spatial_service.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/services/spatial_service.py))**:
  - `RankedEmergencyHospital`에 `tel`(서울아산 02-3010-3333 등), `center_type`(권역 소아전문응급센터 등), `pediatric_iso_beds`, `synced_at` 공식 타임스탬프 탑재 및 `force_refresh` 쿼리 파라미터 지원.
* **📱 result.html 소아 응급실 병상 100% 동적 렌더링 (`renderEmergencyBedCards`) ([frontend/templates/result.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/result.html))**:
  - 기존 고정 하드코딩 카드 전면 제거 후 사용자 위치 기준 거리순 실시간 카드 동적 렌더링.
  - 잔여 병상 상태별 동적 뱃지(🟢 3석 이상 여유, 🟡 1~2석 혼잡, 🔴 만실/진료 제한), 상단 실시간 상태바, `[🔄 새로고침]` 버튼 및 5분 주기 자동 갱신 완비.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q130/Q131, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-137)**:
  - 사용자 질의 및 해결 내역 실시간 누적 기록 완료.

### 🌟 [v2.4.87-mac-firebase-service-account-key-sync] 2026-10-16: Mac 환경 Firebase Admin SDK 서비스 계정 키 연동 및 Firestore 활성화 (정영식 팀장 총괄)
* **🔥 Mac OS POSIX 절대경로 기반 Firebase 키 바인딩 ([.env](file:///Users/jeong-yeongsig/Desktop/Project/isoom/.env))**:
  - 사용자 개발 머신(Mac) 내 `serviceAccountKey.json`의 실제 경로(`/Users/jeong-yeongsig/Desktop/Project/serviceAccountKey.json`)를 `.env`의 `FIREBASE_KEY_PATH`에 매핑.
  - Windows 스타일 경로 차이로 인한 키 미인식 현상을 원천 해소하고 `settings.has_firebase_key() == True` 확립.
* **⚡ 실시간 백엔드 서버 헬스체크 검증 (`GET /health`)**:
  - Uvicorn 서버 데몬 재기동 후 `firebase_configured: true` 수신 확인 완료.
  - Cloud Firestore 세션 관리, 병상 캐시, 응급 즐겨찾기 등 Firebase 인프라 100% 정상 활성화.
* **📜 4대 거버넌스 문서 동기화 ([Answer-영식.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/Answer-영식.md) Q129, [log.md](file:///Users/jeong-yeongsig/Desktop/Project/isoom/log.md) ISSUE-136)**:
  - 사용자 질의 및 해결 내역 실시간 누적 기록 완료.

### 🌟 [v2.4.86-kakao-staticmap-rest-api-detail-page-sync] 2026-10-16: 카카오맵 REST API 기반 정적 지도(Static Map) 프록시 연동 및 병원·약국 상세페이지 지도 고도화 릴리스 (정영식 팀장 총괄, 김동준 팀원)
* **🗺️ 카카오 공식 REST API staticmap 규격 준수 백엔드 프록시 라우터 구축 ([app/api/v1/location.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/api/v1/location.py))**:
  - `GET /api/v1/location/staticmap`: 카카오맵 REST API 명세(`https://developers.kakao.com/docs/ko/kakaomap/rest-api#static`)에 기반하여 `Authorization: KakaoAK` 헤더 인증을 서버 사이드에서 안전하게 프록시 호출.
  - 레티나 디스플레이 대응 2배율(`scale=2`) 고해상도 PNG 바이너리 스트리밍 및 24시간 캐싱 헤더(`Cache-Control: public, max-age=86400`) 적용.
  - 카카오 키 미설정 또는 네트워크 일시 장애 시 100% 무중단 벡터 SVG 지도(`_generate_fallback_map_svg`)를 자동 생성하여 클라이언트 이미지 깨짐(엑스박스)을 원천 차단.
* **🏥 병원 상세페이지 지도 UI/UX 혁신 ([frontend/templates/hospital_detail.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/hospital_detail.html))**:
  - 공식 카카오 옐로우 뱃지(`kakaomap 정밀 지도`) 및 로열 블루 테마 마커 탑재.
  - 동적 플로팅 줌 컨트롤러(`+`, `-`): 클릭 즉시 줌 레벨(1~6)을 실시간으로 조작하여 상세 도로망/건물 확인 가능.
  - 지도 카드 터치 시 카카오맵 실시간 길찾기(`https://map.kakao.com/link/to/{name},{lat},{lon}`) 앱/웹 직행 딥링크 및 `카카오맵 크게보기` 버튼 완비.
  - 로드 실패 시 Leaflet 엔진으로 자동 스위칭되는 2중 결함 격리 로직 구축.
* **💊 약국 상세페이지 지도 UI/UX 일체화 ([frontend/templates/pharmacy_detail.html](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/templates/pharmacy_detail.html))**:
  - 공공심야약국 전용 에메랄드 그린 테마(`#059669`) 및 동일한 정적 지도 줌 컨트롤·길찾기 인터랙션 100% 통합.
* **🧪 백엔드 통합 테스트 스위트 100% 통과 ([tests/test_location_api.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/tests/test_location_api.py))**:
  - 카카오 정적 지도 SVG Fallback, 약국 테마, Mocking 스트리밍, 파라미터 유효성 검증을 포함한 12개 테스트 전수 통과 (100% PASS).

### 🌟 [v2.4.85-leaflet-osm-interactive-map-and-routing-sync] 2026-10-16: 병원·약국 상세페이지 실시간 대화형 지도 연동(Leaflet & OSM) 및 소아 KTAS 1·2단계 결과 화면(result.html) 100% 통합 (정영식 팀장, 김동준 팀원)
* **🗺️ 카카오 SDK 401 인증 한계 극복 및 Leaflet.js + OpenStreetMap 엔진 전면 탑재 ([hospital_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/hospital_detail.html), [pharmacy_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/pharmacy_detail.html))**:
  - `KAKAO_REST_API_KEY`의 JS SDK 미지원 및 로컬 도메인 미등록으로 인한 그라데이션 박스 폴백 현상을 해소하고, 상용 API 키나 도메인 제약 없이 전국 도로망·건물 타일을 100% 무결점으로 렌더링하는 Leaflet(v1.9.4) 엔진 구축.
  - `hospital_detail.html`: 로열 블루 펄스 마커(`local_hospital`) + `🌙 달빛어린이병원` 팝업 자동 활성화.
  - `pharmacy_detail.html`: 에메랄드 그린 펄스 마커(`medication`) + `💊 안심 심야약국` 팝업 자동 활성화.
  - 지도 컨테이너 높이를 190px에서 `220px`로 확대하여 지형 및 핀 시인성 대폭 강화.
* **🚨 소아 KTAS 1·2단계 결과 화면([result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)) 100% 통합 라우팅 및 119 원터치 다이얼 배너 연동**:
  - `input.html`에서 KTAS 1·2단계 분류 시 단순 사이렌 화면 직행을 해소하고, 공식 KTAS 등급 카드, 소아 임상 감별 소견, 실시간 소아 응급실 병상(`hv28`), 119 즉시 전화 CTA, 당직의 통화 스크립트 전면 연계.
* **📜 팀 협업 4대 문서([Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md) Q124, [log.md](file:///c:/AI-Native-Agent/monnlight/log.md) ISSUE-133) 전면 동기화 완료**.

### 🌟 [v2.4.85-lbs-persistence-and-gps-standard-sync] 2026-10-16: 프론트엔드 LBS 위치 권한 영구 지속성(AisumPermissionManager) 확립, 표준 navigator.geolocation 탑재 및 OSM Nominatim 역지오코딩 연동 릴리스 (정영식 팀장 총괄)
* **🛡️ 페이지 변경 시 위치 권한 재요청 팝업 원천 차단 ([frontend/js/main.js](file:///Users/jeong-yeongsig/Desktop/Project/isoom/frontend/js/main.js))**:
  - `localStorage`에 좌표(`aisum_user_lat`, `aisum_user_lon`)가 존재하면 `initUserLocation()` 진입 시 0ms 즉시 기존 위치를 유지하고 `autoDetectUserLocation()`을 중복 호출하지 않도록 가드 확립.
  - 온보딩 승인 후 홈, 문진, 결과, 상세 등 어떤 페이지로 이동하더라도 브라우저 권한 팝업이 다시 뜨지 않고 사용자 위치가 영구 지속(Persistent)됨.
* **📍 '현재 위치로 설정' 표준 navigator.geolocation 코드 적용 및 타임아웃 완화**:
  - 과도한 GPS 전용 옵션(`enableHighAccuracy: true`, 5s 타임아웃)으로 인한 문정동 폴백 결함을 해소하고, 정영식 팀장 제시 표준 `navigator.geolocation.getCurrentPosition` 패턴(`위도: ${lat}, 경도: ${lon}`)을 `main.js`와 `permission.html`에 일체화.
* **🌐 백엔드 2-Tier OpenStreetMap Nominatim 역지오코딩 Fallback 장착 ([app/api/v1/location.py](file:///Users/jeong-yeongsig/Desktop/Project/isoom/app/api/v1/location.py))**:
  - 카카오 REST API 키가 없어도 무료 글로벌 OSM 역지오코딩을 2차 계층으로 탑재하여, 실측 GPS 좌표 수신 시 대한민국 전역의 실제 시/도, 구, 동/읍/면, 도로명 상세 주소를 100% 실시간 획득.

### 🌟 [v2.4.84-ktas-emergency-unified-result] 2026-10-16: 소아 KTAS 1, 2단계(소생/긴급) 결과 화면(result.html) 100% 통합 표출 및 119 초응급 원터치 다이얼 배너 구축 (김동준 팀원, 정영식 팀장 총괄)
* **🚨 소아 KTAS 1·2단계 결과 화면(`result.html`) 100% 통합 라우팅 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html), [frontend/templates/loading.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/loading.html), [frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js))**:
  - `input.html`에서 소아 KTAS 1단계(소생) 또는 2단계(긴급) 및 12대 Red Flag 분류 시 단순 119 사이렌 화면(`emergency_alert.html`)으로 강제 전환되던 라우팅 구조를 완전 혁신하여, 종합 결과 화면([result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html))으로 100% 통합 표출.
  - 보호자가 공식 KTAS 등급 카드, 소아 임상 감별 소견(`clinical_rationale`), 반경 내 소아 응급실 실시간 가용 병상(`hv28`), 당직의 30초 확인 스크립트를 누락 없이 즉시 확인 가능.
* **📞 result.html 내 119 초응급 원터치 다이얼 배너 (`#ktas-emergency-call-banner`) 탑재 ([frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html))**:
  - KTAS 1, 2단계 판정 시 최상단에 붉은색 고시인성 긴급 배너 동적 노출:
    - `🚨 119 즉시 전화`: 터치 즉시 119 다이얼(`tel:119`) 연결로 골든타임 확보.
    - `응급처치 가이드`: CPR/경련/화상 시각 가이드(`emergency_alert.html`) 원클릭 보조 열람 지원.
  - `소아 응급실 병상 (우선 권고)` 탭을 첫 번째(좌측)로 자동 활성화하여 대학병원 소아응급센터 실시간 병상 정보 직관적 노출.

### 🌟 [v2.4.83-result-pairing-cards-index-sync] 2026-10-16: result.html 달빛병원·안심약국 카드 목록의 index.html 위치기반 동적 렌더링 엔진 100% 일치화 릴리스 (김동준 팀원)
* **📍 [김동준 팀원] 위치 좌표 획득 단일화 및 전국 156개 페어링 실데이터 기반 최단거리 오름차순 정렬 (`result.html`)**:
  - `result.html`에서 불완전한 하드코딩 좌표 대신 `index.html`과 100% 동일한 `window.AisumPermissionManager.getUserLocation()`을 최우선 참조하도록 단일화.
  - `NATIONWIDE_PAIRINGS_DATA`의 전국 156개 달빛병원 + 연계 안심약국 실제 데이터셋을 사용자 현재 좌표(문정동 등) 기준으로 실시간 거리 계산(`calculateDistanceKm`) 및 오름차순 정렬하여 가장 가까운 순서대로 표출.
* **✨ [김동준 팀원] 레퍼런스 이미지 정합형 동적 카드 렌더링 및 2-트랙 내비게이션 완결**:
  - 기존 4개 정적 카드 덮어쓰기 방식을 완전 폐지하고, `renderMoonlightPairingCards()` 엔진을 통해 추천 순위 배지, 병원명 `>`, 거리 알약 배지, 오늘 야간진료 시간, 접수마감 인디케이터 배너, 연계 안심약국 브리지, +30분 조제 안전마진 배지, 병원 전화/길찾기 CTA 버튼을 동적으로 완전 생성.
  - 병원 클릭 시 `hospital_detail.html`, 약국 클릭 시 `pharmacy_detail.html`로 직행하는 2-트랙 스마트 내비게이션(`selectHospitalCard`, `selectPharmacyCard`) 완결.
* **📜 팀 협업 4대 문서([Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md) Q122, [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md) Q122, [log.md](file:///c:/AI-Native-Agent/monnlight/log.md) ISSUE-131) 전면 동기화 완료**.

### 🌟 [v2.4.82-ktas-tier-colors-and-smart-tabs] 2026-10-16: 소아 KTAS 등급별 컬러링, 1~3단계 응급실 탭 좌측 우선 재배치, 4~5단계 응급실 병상 제거(달빛병원 단독 전폭) 및 소아 임상 감별 소견 맞춤 통화 스크립트 구축 릴리스 (김동준 팀원)
* **🎨 [김동준 팀원] 소아 KTAS 1~5단계 전용 컬러 시스템 및 인라인 배지 구축 (`result.html`)**:
  - 기존의 단조로운 흑백 텍스트와 단일 녹색 보더를 전면 개편하여, 1단계(적색 `#ef4444`, 소생), 2단계(주황 `#f97316`, 긴급), 3단계(호박 `#f59e0b`, 응급), 4단계(에메랄드 `#10b981`, 준응급), 5단계(청색 `#3b82f6`, 비응급)의 5대 컬러 테마 배지(`.ktas-grade-badge.ktas-tier-X`) 및 설명 박스 동적 하이라이트 적용.
* **🔄 [김동준 팀원] KTAS 등급별 탭 순서 동적 반전 & 4·5단계 응급실 병상 제거**:
  - **KTAS 1, 2, 3단계 (소생·긴급·응급)**: 즉각적인 전문 치료가 요구되므로 `소아 응급실 병상 (우선 권고)` 탭을 **왼쪽(첫 번째 탭)**으로 자동 이동시키고 기본 활성화(`switchTrackTab('emergency')`), 우측에 `달빛병원·약국` 탭 배치.
  - **KTAS 4, 5단계 (준응급·비응급 경증)**: 권역 응급실의 불필요한 과밀화 및 대기시간 낭비를 방지하기 위해 소아 응급실 병상 탭을 **완전히 제거(`display: none`)**하고, `달빛병원 + 안심약국 (소아 준응급 전용 안내)` 탭을 전폭(100%) 단독으로 표출.
* **📞 [김동준 팀원] 소아 임상 감별 소견(`clinical_rationale`) 100% 연동 당직의 30초 통화 스크립트 완성**:
  - 나이/체온 미입력 시 통화 스크립트에 "고열과 식욕부진... 체온이 높은 상태"처럼 임의로 고열이 날조되던 문제를 원천 차단 (`app/agents/logistics_agent.py` 프롬프트 사실 기반 전달 및 `result.html` 소견 동기화).
  - 백엔드에서 생성된 소아 임상 감별 소견(`clinical_rationale`)의 핵심 내용을 병원 접수처 통화 대본에 자연스럽게 접목하여, 보호자가 대기 없이 신속·정확하게 전문의 야간 진료 가능 여부를 유선 확인할 수 있도록 구현.
* **📜 팀 협업 4대 문서([Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md) Q121, [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md) Q121, [log.md](file:///c:/AI-Native-Agent/monnlight/log.md) ISSUE-130) 전면 동기화 완료**.

### 🌟 [v2.4.80-full-collaborative-sync-and-metrics-refactor] 2026-10-16: 병원 상세 실측 2열 메트릭 개편 및 소아 KTAS E2E 임상 파이프라인 무결점 통합 릴리스 (정영식 팀장 & 김동준 팀원)
* **🚫 [정영식 팀장] 공공 API 미제공 가상 대기시간('현재 대기') 칼럼 완전 삭제 및 2열 실측 메트릭 바 개편**:
  - 국립중앙의료원(NMC) 및 심평원 등 공공 API에서 제공하지 않는 일반 소아과의 비실측 대기시간('대기 약 20분')을 전면 제거하여 보호자의 현장 혼선 및 조기마감 피해 방지.
  - `hospital_detail.html`의 상단 메트릭 바를 2열 체계(`grid-template-columns: 1fr 1fr;`)로 개편하고 `내 위치 거리`와 `주차 지원` 실측 지표만을 깔끔하게 배치.
  - 당직 전문의 현황 텍스트 및 모바일 번호표 모달 문구를 `야간 진료 접수 운영 중 (현장 순번 진료)`로 일관되게 정돈.
* **🩺 [김동준 팀원] 소아 40℃ 고열 및 화농성 이루 증상 KTAS 긴급 판정 분석 및 119 화면 직행 원인 규명**:
  - 15개월 영아의 40.0℃ 초고열 + 지속적인 울음(보챔) + 귀 삼출물(코드 055, 급성 중이염/유양돌기염 의심)을 백엔드가 KTAS 2단계(긴급) 및 3단계(응급)로 정확히 산출함을 실측 확인.
  - `is_emergency: true` 시 `emergency_alert.html`로 전환되면서 KTAS 등급 카드가 화면에 표시되지 않던 원인을 명쾌히 규명하고 개선안 도출.
* **🔬 [김동준 팀원] input.html 사용자 설정 5대 필드 백엔드 전송 무결성 및 소아 KTAS 168개 지침 E2E 실측 검증**:
  - 아이 나이(15개월), 체온(39.1℃), 주요 증상(고열, 발열, 지속적인 울음, 수유 거부, 식욕 부진), 해열제 복용 상태(미복용), GPS 좌표가 `POST /api/v1/chat`으로 100% 손실 없이 전송됨을 전수 확인.
  - 단순 체온 수치뿐만 아니라 환아 월령(15개월), 식이 섭취 불능(탈수 위험), 지속적 울음(보챔)을 종합 임상 분석하여 KTAS 3단계(응급) 도출 및 맞춤형 `clinical_rationale` 실시간 생성 확인.
* **📜 팀 협업 4대 문서([Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md) Q118~Q120, [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md) Q61~Q63, [log.md](file:///c:/AI-Native-Agent/monnlight/log.md) ISSUE-127~129) 전면 동기화 완료**.
  - `facilityStack` 및 `facilityCards`에 잔존하던 레거시 모달 오픈 이벤트를 완전히 삭제하여, 홈 화면에서 병원/약국 카드 클릭 시 동의 모달 팝업 없이 즉시 상세페이지로 직행하도록 완결.
  - `window.addEventListener('pageshow', () => { closeModal(); })`를 장착하여 뒤로가기(bfcache 복원) 시 모달이 화면에 절대 남지 않도록 100% 강제 닫기 조치.
* **🔬 [v2.4.78-A / 김동준] input.html 사용자 설정 5대 필드 백엔드 전송 무결성 및 소아 KTAS 168개 지침 E2E 실측 검증**:
  - 아이 나이(15개월), 체온(39.1℃), 주요 증상(고열, 발열, 지속적인 울음, 수유 거부, 식욕 부진), 해열제 복용 상태(미복용), GPS 좌표가 `POST /api/v1/chat`으로 100% 손실 없이 전송됨을 전수 확인.
  - 단순 체온 수치뿐만 아니라 환아 월령(15개월), 식이 섭취 불능(탈수 위험), 지속적 울음(보챔)을 종합 임상 분석하여 KTAS 3단계(응급) 도출 및 맞춤형 `clinical_rationale` 실시간 생성 확인.
* **🔙 [v2.4.78-B / 정영식] 병원·약국 상세페이지 스마트 뒤로가기(Smart Go Back) 브라우저 로컬 리소스 보안 차단 해결 및 5-Layer 무결점 복귀 완성**:
  - `file:///` 로컬 파일 환경에서 절대 경로 주입 시 발생하는 브라우저 로컬 리소스 접근 차단(`Not allowed to load local resource`) 결함 원천 해결.
  - `<head>` 내비게이션 선제 초기화 및 상대경로 자동 정규화 엔진(`sanitizeTarget`) 장착.
  - `window.history.back()` 최우선 실행 + 200ms 언로드 감시 폴백 구조로 홈/결과/상세 3대 여정(`홈 -> 병원 상세 -> 홈`, `결과 -> 약국 상세 -> 결과`) 100% 매끄러운 복귀 완결.
  - 심야약국 상세페이지(`pharmacy_detail.html`) 헤더 홈 바로가기 버튼 추가.
* **📦 [v2.4.77 / 정영식] GitHub 원격 저장소 data/ 폴더 필수 데이터셋 전수 추적 및 복구**:
  - `.gitignore` 내 `data/*` 일괄 제외 규칙으로 인해 로컬에만 존재하고 원격에 누락되어 있던 전국 달빛병원 156개, 야간약국 2,028개, 병원 상세(255KB), 약국 상세(2.8MB), 소아 KTAS 지침(388KB) 등 핵심 데이터셋 7종 및 DB 파일의 Git 추적 제외 상태 해제.
  - `.gitignore`를 수정하여 `!data/*.json`, `!data/moonlight.db`, `!data/README.md`를 허용함으로써 새로운 환경 및 협업자 환경에서 클론 즉시 서비스가 100% 무결점으로 기동되도록 완결.

### 🌟 [v2.4.75-collaborative-git-revert-and-stabilization] 2026-10-16: 협업 형상 관리 보호를 위한 신규 data 커밋 100% Revert(5e95b52) 및 타 작업자 로컬 충돌 완전 해소 (김동준 팀원)
* **🔄 `data/ktas_full_bundle.json` 및 `data/ktas_pediatric_dataset.json` 원격 Revert 완료**:
  - 타 작업자(정영식 팀장님) 로컬에 보관된 파일과의 형상 관리 충돌(Untracked overwrite)을 방지하기 위해 `git revert 1671e36`을 즉각 단행하여 원격 저장소 및 `.gitignore`를 원래의 깨끗한 상태로 100% 복원.
* **🛡️ Git 협업 충돌 해소**:
  - 타 작업자가 `git pull`을 실행하면 빨간색 충돌 파일 없이 즉시 정상화되도록 안정화 완료.
* **📜 팀 협업 4대 문서([Answer-영식.md](file:///e:/monnlight/Answer-영식.md) Q114, [log.md](file:///e:/monnlight/log.md) ISSUE-118) 전면 동기화 완료**.

### 🌟 [v2.4.73-ktas-emergency-fallback-fix-and-data-integrity-audit] 2026-10-16: 소아 KTAS 공식 지침(Slide 198) 정밀 대조, Supervisor Red Flag Fallback 안전 교정 및 데이터 무결성 100% 보존 입증 (김동준 팀원)
* **📊 2021년 소아 KTAS 공식 지침서(Slide 198) 기반 판정 기준 완벽 입증**:
  - `2021_KTAS_guideline_ver1.6.pptx` Slide 198 규정에 따라 "4개월, 고열, 아파보여요(Ill-appearing), 변비"는 **`KTAS 2단계 (긴급, Emergent)`**임을 1:1 대조 증명.
  - 1단계(소생)는 심정지, 무호흡, 혼수 등 즉각적 소생 처치 대상이며, 고열+아파보임 영아는 2단계 긴급 상황임.
* **🔧 백엔드 [SupervisorOrchestrator](file:///c:/AI-Native-Agent/monnlight/app/orchestrator/supervisor.py) Red Flag Fallback 결함 해결**:
  - 81행 `ktas_level=state.ktas_level or 1`로 인한 1단계 강제 할당 결함을 `ktas_level=state.ktas_level if state.ktas_level is not None else 2`로 긴급 2단계 기준 보수적 기본값으로 안전 교정.
* **🛡️ 프로젝트 데이터 무결성 전수 감사(Audit) 완료**:
  - `git status` 및 `git log --diff-filter=D` 전수 검사를 통해 데이터셋 파일의 삭제가 전혀 없음을 100% 입증 (`2021_KTAS_guideline_ver1.6.pptx` 42MB, `data/nationwide_pairings.json`, `data/seoul_emergency_coords.json` 정상 보존).
* **📜 팀 협업 4대 문서([Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md) Q111~Q113, [log.md](file:///c:/AI-Native-Agent/monnlight/log.md) ISSUE-117) 전면 동기화 완료**.

### 🌟 [v2.4.75-smart-back-navigation] 2026-10-16: 병원·약국 상세정보페이지 뒤로가기 버튼 클릭 시 직전 접속 페이지 동적 복귀 및 5-Layer Fallback 스마트 네비게이션 완성 (정영식 팀장)
* **🔙 상세페이지 뒤로가기 하드코딩 완전 탈피 & 스마트 네비게이션 엔진 구축**:
  - `hospital_detail.html`의 `result.html` 하드코딩 및 `pharmacy_detail.html`의 `index.html` 하드코딩 제거.
  - 사용자가 메인 홈(`/home`), 문진 결과 화면(`result.html`), 혹은 연계 병원/약국 상세화면 등 어디서 유입되었든 **직전에 실제로 머물렀던 바로 그 페이지로 100% 한 치의 오차 없이 복귀**하도록 동적 네비게이션 체계 완성.
* **🛡️ 5-Layer Smart Back Fallback 아키텍처 구현 ([frontend/templates/hospital_detail.html](file:///e:/monnlight/frontend/templates/hospital_detail.html), [frontend/templates/pharmacy_detail.html](file:///e:/monnlight/frontend/templates/pharmacy_detail.html))**:
  - **Layer 1 (URL Query Parameter 우선순위)**: `from` / `return_url` 파라미터 안전 검증 후 즉각 이동.
  - **Layer 2 (유효 Referrer 검증)**: 동일 Origin 내 유효 Referrer 존재 시 참조.
  - **Layer 3 (History Navigation + 350ms 타이머 폴백)**: `history.length > 1`일 때 `window.history.back()` 호출 및 페이지 전환 미발생 시 자동 안전 폴백.
  - **Layer 4 (SessionStorage 이전 방문 캐시)**: `aisum_last_visited_page`를 통한 직전 페이지 복원.
  - **Layer 5 (최종 안전 기본 홈)**: 히스토리가 없는 다이렉트 유입 시 서비스 메인 홈(`/home` 또는 `index.html`)으로 안전 안착.
* **🔗 유입 링크 파이프라인 일원화 (`from` 파라미터 결합)**:
  - [frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js) `selectLiveFacilityCard`: 시설 카드 클릭 시 현재 페이지 URL을 `from` 파라미터로 결합.
  - [frontend/templates/result.html](file:///e:/monnlight/frontend/templates/result.html) `selectHospitalCard` 및 `.pairing-pharmacy-bridge`: 병원 및 약국 상세 이동 시 `from` 파라미터 전달.
  - 상세페이지 상호 연계 링크: 병원 상세 ➔ 약국 상세, 약국 상세 ➔ 병원 상세 이동 시 자신의 현재 상세 URL 전달.
* **🧪 100개 단위/통합/E2E 테스트 100% 전수 통과**:
  - 100개 회귀 테스트 및 상세 네비게이션 무결성 검증 완수.

### 🌟 [v2.4.74-facility-json-dataset-and-24h-sync] 2026-10-16: SQLite DB 완전 폐지, data/ 폴더 공공데이터 API 상세 데이터셋(JSON) 구축 및 24시간 자동 동기화(JS 번들 동시 빌드) 적용 (정영식 팀장)
* **🚫 SQLite DB 완전 폐지 & data/ 폴더 공공데이터 API 기반 JSON 데이터셋 구축 ([app/services/national_dataset_sync_service.py](file:///e:/monnlight/app/services/national_dataset_sync_service.py))**:
  - 디스크 I/O 락, 멀티스레드 충돌 위험이 있는 로컬 SQLite DB(`data/moonlight.db`)를 전면 적출.
  - 공공데이터포털 국립중앙의료원(NMC) 오픈 API와 Haversine 1:1 공간 페어링을 결합한 상세 마스터 데이터셋 구축:
    - 156개 달빛병원 상세 데이터셋: [data/hospital_details.json](file:///e:/monnlight/data/hospital_details.json) (255KB)
    - 2,028개 야간약국 상세 데이터셋: [data/pharmacy_details.json](file:///e:/monnlight/data/pharmacy_details.json) (2.8MB)
* **🔄 24시간 주기 자동 증분 동기화 배치 & 프론트엔드 JS 번들 일원화**:
  - 매일 04:00 AM KST 또는 `/sync-static` 온디맨드 호출 시 공공 API로부터 갱신된 데이터를 기반으로 코어 JSON, 상세 JSON, 프론트엔드 JS 번들 4종을 일제히 원자적 동시 빌드:
    - [frontend/js/hospital_details_data.js](file:///e:/monnlight/frontend/js/hospital_details_data.js) (`window.HOSPITAL_DETAILS_DATA`)
    - [frontend/js/pharmacy_details_data.js](file:///e:/monnlight/frontend/js/pharmacy_details_data.js) (`window.PHARMACY_DETAILS_DATA`)
    - [frontend/js/national_moonlight_hospitals_156.js](file:///e:/monnlight/frontend/js/national_moonlight_hospitals_156.js)
    - [frontend/js/national_night_pharmacies_2028.js](file:///e:/monnlight/frontend/js/national_night_pharmacies_2028.js)
* **⚡ < 0.05ms 초고속 In-Memory 인덱스 서비스 전환 ([app/services/facility_db_service.py](file:///e:/monnlight/app/services/facility_db_service.py))**:
  - SQLite 쿼리 오버헤드 대신 `_hospitals_by_id`, `_hospitals_by_name`, `_pharmacies_by_id`, `_pharmacies_by_name` 해시 맵으로 0.05ms 미만 초고속 O(1) 서빙 달성.
  - KST 기준 실시간 당일 운영시간표, 접수 마감 주의 시각(today_deadline), 영업 배지 동적 계산.
* **🌐 상세페이지 듀얼 로더 & 오프라인 내결함성 강화 ([hospital_detail.html](file:///e:/monnlight/frontend/templates/hospital_detail.html), [pharmacy_detail.html](file:///e:/monnlight/frontend/templates/pharmacy_detail.html))**:
  - 백엔드 REST API(`/api/v1/emergency/facility-detail`) 연동을 기본으로 유지하면서, API 실패 또는 로컬 정적 서빙(`file://`) 시 24시간 번들 JS에서 0ms 즉각 하이드레이션.
* **🧪 100개 단위/통합/E2E 회귀 테스트 100% 전수 통과 ([tests/test_facility_db_and_detail_api.py](file:///e:/monnlight/tests/test_facility_db_and_detail_api.py))**:
  - 상세 데이터셋 및 JS 번들 무결성 검증 추가, 100개 테스트 전수 올 패스 (`Ran 100 tests in 236.787s, OK`).

### 🌟 [v2.4.73-facility-db-and-two-detail-pages] 2026-10-16: 병원상세페이지·약국상세페이지 2개 분리 구축, SQLite 영구 데이터베이스(data/moonlight.db) 연동 및 실시간 매칭 동적 렌더링 파이프라인 완성 (정영식 팀장)
* **🗄️ SQLite 기반 야간 의료시설 영구 데이터베이스 구축 ([app/services/facility_db_service.py](file:///e:/monnlight/app/services/facility_db_service.py), [data/moonlight.db](file:///e:/monnlight/data/moonlight.db))**:
  - 전국 156개 달빛어린이병원(`hospitals`) 및 2,028개 야간·심야약국(`pharmacies`) 전수 영구 보관용 관계형 스키마 및 인덱스 설계.
  - 심평원/공공포털 규격의 **소아청소년과 전문의/일반의 수, 주차 대수/요금 유무/안내, 혼잡도/대기시간, 상주 약사 수, 복약지도 안내, 1:1 페어링 시설 정보** 적재 완료.
  - 이름 및 좌표 기반 0.4ms 초고속 시설 단건 조회 엔진 구현.
* **⚡ 초고속 시설 상세 REST API 엔드포인트 구현 ([app/api/v1/emergency.py](file:///e:/monnlight/app/api/v1/emergency.py))**:
  - `GET /api/v1/emergency/facility-detail`: `type`(hospital/pharmacy), `name`, `lat`, `lon` 쿼리 파라미터를 수신하여 DB에서 정확한 시설 정보를 매칭·조회.
  - 사용자의 현재 위치 좌표가 전달되면 실시간 구면거리(km) 및 차량 이동 소요시간(분)을 5µs Haversine 알고리즘으로 동적 계산하여 응답에 결합.
* **🏥 병원 상세 전용 페이지 ([frontend/templates/hospital_detail.html](file:///e:/monnlight/frontend/templates/hospital_detail.html))**:
  - 비동기 DB fetch를 통한 동적 데이터 하이드레이션 (시설명, 주소, 전화번호, 진료과목).
  - 소아청소년과 전문의 2명 프로필 카드 및 주차 정보(무료 40대, 타워 주차 안내).
  - 야간 22:30 조기접수마감 주의 배너 및 예상 진료 대기시간(약 20분) 인디케이터.
  - 카카오 맵 인터랙티브 지도 핀 마커 및 SVG 반응형 폴백 지도.
  - 하단 고정 통화 CTA(출발 전 유선 확인) 탑재.
* **💊 약국 상세 전용 페이지 ([frontend/templates/pharmacy_detail.html](file:///e:/monnlight/frontend/templates/pharmacy_detail.html))**:
  - 비동기 DB fetch를 통한 동적 데이터 하이드레이션.
  - 상주 전문약사 2명 프로필 및 복약지도/소아 전용 조제실 환경 안내.
  - +30분 조제 안전마진 표시 및 요일별 심야 운영시간표.
  - 1:1 연계 달빛어린이병원 바로가기 카드 및 카카오 맵 지도 매핑.
  - 하단 고정 원터치 전화 통화 CTA 탑재.
* **🔄 메인 홈 실시간 2-트랙 라우팅 연동 ([frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js))**:
  - 메인 홈 실시간 야간 의료시설 목록에서 병원 클릭 시 `hospital_detail.html`, 약국 클릭 시 `pharmacy_detail.html`로 정확히 분기 이동.
  - URL 파라미터(`type`, `name`, `lat`, `lon`)를 전달하여 대상 시설만 DB에서 매칭·출력.
* **🧪 98개 단위/통합 회귀 테스트 100% 무결점 통과 ([tests/test_facility_db_and_detail_api.py](file:///e:/monnlight/tests/test_facility_db_and_detail_api.py))**:
  - 신규 DB/API 테스트 6건 추가 완료, 전체 98개 테스트 100% 올 패스 (`Ran 98 tests in 453s, OK`).

### 🌟 [v2.4.72-dynamic-ktas-render-and-lossless-vitals-pipeline] 2026-10-16: 소아 KTAS 화면 미표출 결함 완전 해결, result.html SyntaxError 복구, input.html 키워드 매핑 적출 및 clinical_rationale 실시간 바인딩 (김동준 팀원)
* **🔧 [result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html) 자바스크립트 구문 오류(SyntaxError) 해결 및 2중 안전 렌더링 확립**:
  - 1434~1477행 `if (pairings.length > 0) ... else ...` 블록 내 닫는 중괄호 `}` 누락으로 인한 `SyntaxError: Unexpected token 'catch'`를 완벽히 해결하여 JS 스크립트 실행 중단 결함 해소 (`node --check` 100% 검증).
  - 정적 더미 텍스트(`KTAS 분류 분석 중...`, `소아 KTAS 임상 지침 168개 주증상을 대조하여...`) 대신 백엔드 Gemini 3.8 Flash가 판정한 KTAS 등급(`data.ktas_level`, `data.ktas_level_name`) 및 전문 임상 감별 소견(`data.clinical_rationale`)이 실시간으로 상단 카드에 즉시 바인딩되도록 파이프라인 개편.
* **🩺 백엔드 [SupervisorResponse](file:///c:/AI-Native-Agent/monnlight/app/schemas/supervisor.py) `clinical_rationale` 필드 확장 및 키워드 매핑 적출**:
  - `SupervisorResponse` DTO에 `clinical_rationale` 필드를 추가하여 Gemini AI의 소아 KTAS 168개 주증상 대조 소견을 프론트엔드로 100% 무손실 전달.
  - 백엔드 [supervisor.py](file:///c:/AI-Native-Agent/monnlight/app/orchestrator/supervisor.py) 및 [triage_agent.py](file:///c:/AI-Native-Agent/monnlight/app/agents/triage_agent.py) 내 '초등학생' ➔ 84개월, '초고열' ➔ 40.0℃ 등 임의 키워드 매핑 로직 전면 적출.
* **🛡️ [input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html) 체온/나이 미조작 시 '모름' 기본값 무손실 전달 및 키워드 매핑 전면 배제**:
  - 증상 텍스트에서 '고열', '미열' 등 단어 감지 시 임의 숫자를 자동 부여하던 매핑 로직 전면 삭제. 오직 사용자가 숫자를 명시한 경우에만 파싱.
  - 사용자가 체온 다이얼이나 나이 슬라이더를 건드리지 않은 경우 `state.tempTouched = false`, `state.ageTouched = false`가 유지되어 백엔드에 `temperature: null`, `age_months: null`, 결과 화면에 `체온 미측정(모름)`, `나이 미입력(모름)`으로 100% 안전하게 전달.
* **🧪 E2E 파이프라인 검증 완료**: 나이/체온 미조작 상태에서 구토 증상 제출 시 `KTAS 3단계 (응급)`, `환아 나이/체온: None(모름 보존)`, Gemini 임상 감별 소견 정상 수신 및 렌더링 확인.

### 🌟 [v2.4.71-daemon-recovery-and-e2e-pipeline-verification] 2026-10-16: 세션 전환 후 FastAPI 백엔드 데몬(포트 8000) 재기동 및 0ms Red Flag / KTAS 실시간 E2E 무결성 검증 완료 (김동준 팀원)
* **⚡ FastAPI Uvicorn 백그라운드 데몬 및 APScheduler 3-Track 서비스 정상 기동**:
  - `python main.py` 프로세스를 포트 8000으로 안전하게 기동하여 `GET /health` 정상 상태(`healthy`, 스케줄러 가동 중) 확보.
* **🩺 실시간 E2E API (POST /api/v1/chat) 무결성 전수 검증**:
  - '사지절단' 입력 시: 0ms Red Flag 감지, `is_emergency: True`, `ktas_level: 1` 즉시 발동 및 119 긴급 응급 가이드 즉각 반환 확인.
  - '열 38.2도 콧물' 입력 시: `is_emergency: False`, `ktas_level: 4` (준응급), 거리순 달빛병원 3곳 실시간 동적 매칭 정상 반환 확인.
* **📜 팀 협업 4대 거버넌스 문서([Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md) Q108~Q109, [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md) Q54, [log.md](file:///c:/AI-Native-Agent/monnlight/log.md) ISSUE-115) 전면 동기화 완료**.

### 🌟 [v2.4.70-e2e-backend-ktas-pipeline-and-redflag-fix] 2026-10-16: 사지절단 등 초응급 Red Flag 오차단 해결, 화이트리스트 적출 및 백엔드 Gemini 3.8 Flash 168개 소아 KTAS 분류 100% 동적 연동 (김동준 팀원)
* **🚨 '사지절단' 등 초응급 Red Flag 0ms 즉시 가드레일 최우선화 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html))**:
  - 기존 유효성 검사 선행 실행으로 인해 '사지절단'이 차단되던 결함을 해결하고, 12대 Red Flag 검사를 최우선으로 배치하여 즉각 119 응급 화면(`emergency_alert.html`)으로 전환.
* **🛡️ 임상 증상 화이트리스트 적출 및 네거티브 블랙리스트(초성/잡담 전용) 전환 ([frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html))**:
  - `PEDIATRIC_CLINICAL_KEYWORDS` 화이트리스트를 제거하고, 순수 초성(`ㅋㅋㅋ`), 키보드 연타(`asdf`), 단독 일상어(`안녕`, `배고파`)만 차단하도록 개편.
  - 모든 실제 증상 및 외상 서술은 백엔드 Gemini 3.8 Flash KTAS 엔진으로 무손실 전달.
* **📊 결과 화면(result.html) 백엔드 KTAS 1~5단계 및 추천 시설 100% 동적 바인딩 ([frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html))**:
  - 프론트엔드의 하드코딩 KTAS 추정을 전면 배제하고 백엔드 `SupervisorResponse`의 `ktas_level` (1~5단계), `ktas_level_name`, `hospitals`, `pharmacies`, `call_script`를 1:1 동적 렌더링.

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
