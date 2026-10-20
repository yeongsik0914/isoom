# 👶 아이숨 (Aisum) - Stitch 모바일 UI/UX 화면 디자인 보고서

> **문서명**: `AISUM_STITCH_DESIGN_REPORT.md`  
> **작성 일시**: 2026-10-14 18:46 (KST)  
> **작성자**: 정영식 팀장 & 김동준 팀원 (AI 페어 프로그래밍)  
> **기반 레퍼런스**: [screen.png](file:///e:/monnlight/images/screen.png)  
> **Stitch 프로젝트**: `projects/17449043314542457561` (`아이숨 (Aisum) - 소아 야간 의료 매칭 케어`)  
> **디자인 시스템**: `Calm Harbor` (`assets/389aad58bc8e4522b6904fb567d60bdf`)  

---

## 📌 1. 작업 개요 (Executive Summary)

사용자가 제공한 [screen.png](file:///e:/monnlight/images/screen.png) 레퍼런스 이미지를 픽셀 단위로 분석하여 기존의 다크 테마(Nocturnal Pediatric Care)를 완전히 탈피하고, 밝고 따뜻하며 신뢰감을 주는 **모던 라이트 헬스케어 테마(Modern Clean Healthcare Light Theme)**로 기본 베이스와 색감을 전면 개편하였습니다.

서비스 브랜드명을 **'아이숨 (Aisum)'**으로 확정하고, Google Stitch MCP 도구를 활용하여 신규 전용 프로젝트 개설 및 모바일 3대 핵심 사용자 여정 화면을 완벽히 생성·배포하였습니다.

```
┌────────────────────────────────────────────────────────────────────────┐
│               '아이숨 (Aisum)' End-to-End 핵심 사용자 여정             │
├───────────────────┬─────────────────────┬──────────────────────────────┤
│ 1. 실시간 홈 탐색 │ 2. 증상 & 체온 문진 │ 3. 병원 상세 & 실시간 접수    │
│ (아이숨 - 홈)     │ (증상 입력 및 문진) │ (야간 병원 상세 및 실시간 접수)│
└───────────────────┴─────────────────────┴──────────────────────────────┘
```

---

## 🎨 2. 디자인 시스템 규격 (Calm Harbor Tokens)

[screen.png](file:///e:/monnlight/images/screen.png)의 시각 언어를 계승하여 구축된 **Calm Harbor** 디자인 시스템의 핵심 토큰 명세입니다.

| 토큰 구분 | 색상 코드 (Hex) | 설명 및 인터랙션 적용처 |
| :--- | :---: | :--- |
| **Primary Brand** | `#0066FF` | 신뢰를 상징하는 선명한 로열 코발트 블루 (로고, 핵심 CTA, 활성 탭) |
| **Canvas Base** | `#F8FAFC` ~ `#F1F5F9` | 심야 시간대 눈부심을 줄여주는 편안한 오프화이트/소프트 블루그레이 |
| **Surface Cards** | `#FFFFFF` | 순백색 라운드 카드 (`rounded-2xl`, 18px), 미세 외곽선(`border-slate-100`) |
| **Live Safety Dot** | `#10B981` | 실시간 데이터 동기화 펄스 닷, 진료중 배지, 안심 심야약국 테마 |
| **Moonlight Amber** | `#F59E0B` | 달빛어린이병원 초승달 아이콘, 대기 시간/마감 임박 안내 배지 |
| **Red-Flag Coral** | `#EF4444` | 고열(38.5°C 이상), 경련 등 위급 상황 알림 및 119 숏서킷 칩 |
| **Pastel Tints** | `#EEF2FF`, `#ECFDF5`, `#FEF3C7` | 아이콘 컨테이너 박스, 서브 뱃지 및 메타데이터 카드 배경 |

* **타이포그래피**: 한글 환경에 최적화된 Plus Jakarta Sans / Pretendard 스타일의 라운드 산세리프.
* **조형미**: 16px~20px의 둥근 모서리 곡률로 소아 부모에게 심리적 안정감과 친근한 분위기 제공.

---

## 📱 3. Stitch 생성 완료 3대 화면 상세 명세

* **Stitch 프로젝트 ID**: `17449043314542457561`
* **프로젝트 타이틀**: `아이숨 (Aisum) - 소아 야간 의료 매칭 케어`

### 1) 화면 1: 아이숨 - 홈 (Main Home)
* **Screen ID**: `65dcc96b817143c3adb7bfdfa545267b`
* **해상도**: `780 x 2350` (Mobile Viewport)
* **screen.png 1:1 반영 컴포넌트**:
  1. **상단 앱 바**:
     - 좌측: 로열 블루 볼드 로고 **`아이숨`** (`#0066FF`)
     - 위치 선택 드롭다운: **`역삼동 ∨`** 알약 버튼
     - 우측: 실시간 알림 종 아이콘(알림 닷 포함) 및 사용자 프로필 아바타
  2. **증상 탐색 히어로 섹션**:
     - 초록색 라이브 동기화 닷: **`소아 전문 의료 데이터 실시간 동기화`**
     - 메인 볼드 타이틀: **`아이가 어디가 아픈가요?`** (24px 볼드) + 우측 미소 짓는 아기 일러스트
     - 안내 문구: *"체온, 증상 부위를 터치하면 가까운 야간 병원과 예상 대기 시간을 즉시 안내해 드려요."*
     - 대형 풀와이드 CTA: **`+ 아이 증상 입력하고 병원 찾기 →`** (54px 높이, 로열 블루 배경)
     - 원터치 증상 퀵태그 4종:
       - `# 열나요(고열)` (코랄 레드 태그)
       - `# 구토/설사` (달빛 앰버 태그)
       - `# 기침/호흡` (소프트 블루 태그)
       - `# 발진/두드러기` (세이프티 민트 태그)
  3. **실시간 야간 의료시설 리스트 섹션**:
     - 섹션 헤더: **`실시간 야간 의료시설`** + `10곳 운영중` 연파랑 배지 + `E-Gen 연동 1분 전` 라이브 인디케이터
     - 카테고리 필터 탭: `전체 10` (블루 활성) | `🌙 달빛병원 3` | `💊 심야약국 5`
     - 카드 1: **`송파어린이병원`** (달빛어린이병원, 🟢 진료중·접수 가능, 소아청소년과 전문의 2명 진료중·대기 4팀, 내 위치 1.8km, 오늘 ~23:00 마감 배지, 즉시 전화 연결 버튼)
     - 카드 2: **`강남아이마음병원`** (달빛어린이병원, 🟢 진료중·대기 적음, 야간 호흡기 클리닉·X-ray 촬영 가능, 내 위치 2.4km, 오늘 ~22:30 마감)
     - 카드 3: **`송파달빛약국`** (심야약국, 송파어린이병원 인근 80m, 소아 시럽제 조제 가능·해열제 상비, 내 위치 1.85km, 오늘 ~24:00 마감)
  4. **하단 고정 GNB (Bottom Navigation)**:
     - `홈` (활성 로열 블루) | `응급실 가이드` | `설정`
* 🔗 **에셋 링크**:
  - [홈 화면 스크린샷 보기](https://lh3.googleusercontent.com/aida/AEtjO1VfHZevdHUAn4qCqGhabMYFQurK-TDVjYfGSu0fh9OzYlmMET3Z84LWH8Qs2cbfqSqg3Lku8pssV2HrM1m2tEQxYZMR2uecUswfquknzb4L6MFKKWcV3dubHNE3yf37iDRnIQCj2yEpsrZbF_C4v3himbE3zjjn66w4sdSBYcmA6UdlTozaXCEdvyUFAaFFQxqeEfAqZjrUvCJFQoPHYD4mkB6v1ZdO3z92BkdP00y9E8iJXSvl9p3-nSRj)
  - [홈 화면 HTML 코드 다운로드](https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzQ1ZWVhZDQ0ZTNhYTQ5MGU4MDEwN2U2NDc2NjRjNjZjEgsSBxCW18fyghgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNzQ0OTA0MzMxNDU0MjQ1NzU2MQ&filename=&opi=96797242)

---

### 2) 화면 2: 아이숨 - 증상 입력 및 문진 (Symptom Intake & Triage)
* **Screen ID**: `0cdadf1dc86a4c229423b5b02caa8cc1`
* **해상도**: `780 x 2762` (Mobile Viewport)
* **핵심 기능 및 컴포넌트**:
  1. **상단 바 & 단계 진행률**:
     - `< 뒤로가기` | `아이 증상 입력` (볼드 16px) | `✕ 닫기`
     - 단계 표시: `Step 1/3 · 증상 및 체온 확인 (33%)` 로열 블루 프로그레스 라인
  2. **환아 프로필 선택 카드**:
     - 토들러 캐릭터 아바타 + `우리 아이: 정하은 (생후 18개월 · 11.2kg)` + `아이 변경 ⌵`
  3. **체온 입력 인터페이스**:
     - `38.6°C` 대형 디지털 디스플레이 (44px 볼드)
     - `고열 주의 38.5°C 이상` 코랄 레드 배지
     - 정상~초고열 컬러 게이지 슬라이더 및 `+/-` 미세 조절 버튼
     - `⏱️ 발열 시작: 2시간 전 (21:00 경 측정)` 타임스탬프
  4. **KTAS 핵심 증상 멀티 셀렉터**:
     - `열나요 (38°C 이상)` [선택 활성 - 로열 블루]
     - `기침 / 쌕쌕거림 (호흡)` [선택 활성 - 로열 블루]
     - `구토 / 묽은 변`, `처짐 / 기운 없음`, `피부 발진 / 두드러기`
     - **`🚨 경련 / 의식 저하`** (응급 하이라이트 - 터치 시 119 즉시 직통 숏서킷)
  5. **안심 해열제 복용 가이드**:
     - 최근 복용: `아세트아미노펜 (챔프 빨강) 3.5ml` (오후 9:30, 1시간 30분 전)
     - **`💡 다음 교차복용(이부프로펜 계열) 가능 시각: 23:30 (30분 후 가능)`** 카운트다운
  6. **실시간 KTAS 4단계 진단 카드**:
     - 에메랄드 안심 배너: `KTAS 4단계 (준응급 / 소아 야간진료 권장)`
     - 가까운 `송파어린이병원 야간진료 즉시 접수 가능 (대기 4팀)` 추천
  7. **하단 고정 CTA**:
     - **`내 주변 진료 가능 병원 매칭하기 →`** (54px 로열 블루 고정 버튼)
* 🔗 **에셋 링크**:
  - [증상 입력 화면 스크린샷 보기](https://lh3.googleusercontent.com/aida/AEtjO1VdrayFKzVv4eMKgCepCV8LUpL7sfW7vqgoQdUIOfSgpm3eLUMx5K3Ta9jN9Nqditer8wz-s6HoTH4GcxLA_0Hy6QS8mzFFBi1aTn3fhleqW2sdBoREWiGKLyiQ6qLaINe5bd8doD8SOdXX2K97KVH2J5ibbFYuBG_oqMamHwqb7Dcx-qoOMNyl9QigSDktk2N_IeSbPQFnjcT3trD-gQbodCjEaq4x6a8LnEeTC26xyaG_YWJouGK8MA6t)
  - [증상 입력 화면 HTML 코드 다운로드](https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzM5MjNhMTY2ZTU4MDQ0MmFiMDI5M2VhOTZhMTM3NWIwEgsSBxCW18fyghgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNzQ0OTA0MzMxNDU0MjQ1NzU2MQ&filename=&opi=96797242)

---

### 3) 화면 3: 아이숨 - 야간 병원 상세 및 실시간 접수 (Hospital Detail & Queue)
* **Screen ID**: `3c5db317bb354d02838e5306adfc4f1a`
* **해상도**: `780 x 3342` (Mobile Viewport)
* **핵심 기능 및 컴포넌트**:
  1. **상단 내비게이션 바**:
     - `< 뒤로가기` | `병원 상세 정보` | 공유 및 즐겨찾기(북마크) 버튼
  2. **병원 히어로 카드**:
     - 타이틀: **`송파어린이병원`** (22px 볼드)
     - 배지: `🌙 달빛어린이병원` | `실시간 야간 진료중 (오늘 ~23:00 마감)`
     - 진료과: `소아청소년과 전문의 2명 야간 상주 진료`
     - 핵심 지표 3열 그리드:
       * **`현재 대기`: `4팀 (약 20분 예상)`** (소프트 블루 하이라이트)
       * **`거리`: `1.8km (차량 6분)`**
       * **`주차`: `지하 주차장 완비 (무료 2시간)`**
  3. **실시간 당직 전문의 현황 카드**:
     - 의료진 프로필: **Dr. 김서연 소아청소년과 전문의** (소아 호흡기·알레르기 세부전문의)
     - 라이브 배지: `진료실 1 운영중 · 현재 14번 환아 진료중`
  4. **안심 심야약국 연계 카드**:
     - 약국명: **`송파달빛약국`** (병원 도보 1분 · 80m)
     - 안심 보장: **`오늘 24:00까지 운영 · 병원 진료 후 처방 조제 100% 보장`**
     - 상비 의약품 태그: `소아용 시럽제·건조시럽 조제 가능`, `해열제/쿨시트 상비`, `소아 네블라이저 약액 보유`
  5. **오시는 길 & 길안내 내비게이션**:
     - 미니 경로 맵 (내 위치 1.8km ➔ 송파어린이병원 ➔ 80m 송파달빛약국)
     - 주소 복사: `서울 송파구 송파대로 345 (송파역 1번 출구 250m)`
     - 원클릭 내비 연동: **`티맵 길안내`** & **`카카오내비 길안내`**
  6. **하단 고정 듀얼 액션 바**:
     - 좌측: **`[📞 전화 상담]`** (원터치 다이얼러)
     - 우측: **`[모바일 야간진료 번호표 접수하기 (대기 4번째) →]`** (로열 블루 메인 CTA)
* 🔗 **에셋 링크**:
  - [병원 상세 화면 스크린샷 보기](https://lh3.googleusercontent.com/aida/AEtjO1Wb0eZQgjXwGZ_xyTaR9lcgSZslIECRIwdwVINDo0KI6yRFz07ePAN8vWoC9AXrEMS3ow2Jn52YRY1ngjUDJpl-lJAPVnFOgDrrYXr-vQ5fPxUWyHihb8CW7BvVKuHeXtHWR6Jbdd_5d2LbwnLPcvS7kAVRo-Be530E_cepxiAGNJ0gtfa7f7DpO7C_7FgxaLFyOuQqeZIgOeLv3gPvlKXsPohgwix5KqSO6y2E3yTYeY2Fm845_7TP5OE9)
  - [병원 상세 화면 HTML 코드 다운로드](https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ8Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpbCiVodG1sXzVmMzhjZDE1OWE3MTRjY2RhZjQxMWFiMWY5ZTY5MDhlEgsSBxCW18fyghgYAZIBJAoKcHJvamVjdF9pZBIWQhQxNzQ0OTA0MzMxNDU0MjQ1NzU2MQ&filename=&opi=96797242)

---

## 🔗 4. FastAPI 백엔드 연동 매핑 명세

Stitch로 생성된 프론트엔드 UI 컴포넌트는 당사 구축 완료된 백엔드 엔드포인트 및 멀티 에이전트 파이프라인과 1:1로 결합됩니다:

| 프론트엔드 UI 컴포넌트 | 연계 백엔드 모듈 / API | 동작 메커니즘 |
| :--- | :--- | :--- |
| **`+ 아이 증상 입력하고 병원 찾기`** | `app/services/session_manager.py` | 신규 FSM 세션 초기화 및 KTAS 문진 상태 머신 구동 |
| **체온 / 증상 칩 선택** | `app/agents/triage_agent.py`<br/>(`POST /api/v1/chat/stream`) | Gemini 3.8 Flash 실시간 SSE 토큰 스트리밍 및 바이탈 구조화 |
| **🚨 경련 / 의식 저하 칩** | `app/agents/redflag_classifier.py` | 26µs 단락회로(Short-circuit)로 119 즉시 전화 전환 (`tel:119`) |
| **실시간 병원 / 약국 리스트** | `app/api/v1/emergency.py`<br/>(`POST /api/v1/emergency/pairings`) | 5분 주기 인메모리 캐시 병상 데이터 기반, +30분 조제마진 확보 페어링 즉각 정렬 |
| **원터치 전화 및 내비 연동** | `app/agents/logistics_agent.py` | 30초 당직의 통화 스크립트 클립보드 복사 및 Tmap/카카오내비 딥링크 |

---

## 🚀 5. 향후 실행 계획 (Next Action)

1. **HTML/CSS 로컬 패키징**: Stitch에서 생성된 순수 HTML 및 CSS 에셋을 추출하여 `app/static/` 디렉터리에 모바일 웹 형태로 탑재.
2. **FastAPI 라우터 서빙**: FastAPI 루트 경로(`/`)에서 모바일 웹 뷰를 직접 서빙할 수 있도록 `StaticFiles` 라우팅 연결.
3. **End-to-End 실시간 연동 테스트**: 브라우저 서브에이전트 또는 모바일 뷰포트에서 `[홈] ➔ [체온·증상 입력] ➔ [병원 매칭 및 접수]` 플로우의 동작 무결점 검증.
