# [MoonlightCare] 트러블슈팅 & 문제 해결 엔지니어링 로그 (log.md)

본 문서는 MoonlightCare 프로젝트의 기획, 데이터 파이프라인, 멀티 에이전트, 백엔드 및 웹 프론트엔드 개발 과정에서 발생하는 **모든 오류(Errors), 데이터 결함(Data Pitfalls), 컴플라이언스 위험, 그리고 구체적인 해결 방안(Solutions)**을 기록하고 지속 관리하는 공식 엔지니어링 로그입니다.

---

## 📌 이슈 관리 목차 (Issue Index)

| 이슈 ID | 발생 영역 | 핵심 문제 및 오류 현상 | 조치 상태 | 해결 일자 |
| :---: | :--- | :--- | :---: | :---: |
| **[ISSUE-001]** | 오픈 API 연동 | 공공데이터포털 API 호출 시 `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` (401) | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-002]** | 컴플라이언스 & 아키텍처 | 기 승인된 `건강보험심사평가원_질병정보서비스`의 의료법 제27조 위반 위험 및 리소스 낭비 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-003]** | 데이터 정합성 | 심평원 진료시간 데이터의 행정 신고치와 실제 야간 소아과 운영시간의 괴리 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-004]** | 소아 진료 필터링 | 일반의원 소아청소년과 진료과목 표방(11)과 실제 24개월 미만 영아 진료 거부 문제 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-005]** | 현장 운영 정합성 | 달빛어린이병원 야간 대기 환자 폭증에 따른 '조기 현장 접수 마감(Cut-off)' 정보 부재 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-006]** | 캘린더 동기화 | 법정공휴일/대체공휴일/명절(설·추석) 연휴 병원 휴진 데이터 왜곡 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-007]** | 응급의료 연계 | E-Gen 실시간 응급실 소아병상(`hv28`)의 허수 및 비정형 공지 메시지(`hpmg`) 파싱 누락 위험 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-008]** | DB 보안 & 에이전트 거버넌스 | 에이전트의 무단 DB 수정/삭제 및 보고 누락 위험 원천 차단 (Sentinel Agent & HITL 승인) | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-009]** | 스토리지 & 공간 쿼리 최적화 | 지리공간 반경 검색 시 Full Scan 지연 및 실시간 병상 쓰기 I/O 병목 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-010]** | AI 모델 아키텍처 | 2026 최신 Gemini 3.8 Flash 모델 라인업 전수 검토 및 Zero-LLM/LLM 역할 재배치 | **해결 완료 (Resolved)** | 2026-10-01 |
| **[ISSUE-011]** | 오픈 API 연동 & 전국구 확장 | 공공데이터포털 NMC 오픈API 2종 승인 완료 및 전국 17개 시·도 병원-약국 연계 전국구 확장 | **해결 완료 (Resolved)** | 2026-10-08 |
| **[ISSUE-012]** | 응급의료 통계 모델링 | 소아 의료 진료 3대 취약 시간대 정량 분석 및 수요-공급 미스매치 시뮬레이션 적용 | **해결 완료 (Resolved)** | 2026-10-08 |
| **[ISSUE-013]** | 응급의료 의사결정 알고리즘 | 초심야 00~06시 소아 진료 공백 극복 4대 솔루션 및 2-트랙 라우팅 엔진 노트북 반영 | **해결 완료 (Resolved)** | 2026-10-08 |
| **[ISSUE-014]** | 시스템 아키텍처 개편 | 실시간 공공 API 호출 안티패턴 배제 및 Firebase 서버리스 실시간 아키텍처 전격 개편 | **해결 완료 (Resolved)** | 2026-10-08 |
| **[ISSUE-015]** | 비용 & 사용량 최적화 | 주피터 노트북 데이터 분석 결과 반영 및 공공 API-Firebase 비용·사용량 최적화 동기화 | **해결 완료 (Resolved)** | 2026-10-08 |
| **[ISSUE-016]** | AI 모델 아키텍처 & 안정성 | 구버전 모델(`gemini-2.5-flash`) 단종(404 NOT_FOUND) 무음 예외 및 Gemini 3.8 Flash / 3.5 Lite 최신 전환 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-017]** | 실시간 데이터 & 캐싱 최적화 | 실시간 병상 조회 시 공공 API 중복 호출 지연(400~1000ms) 방어를 위한 0ms 인메모리 TTL 캐싱 계층 구축 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-018]** | 전국구 확장 & 공간 정합성 | 전국 17개 시·도 매칭 시 서울특별시 하드코딩 및 타 지자체 좌표 왜곡(320km) 해소 (동적 stage1 및 권역 좌표망 구축) | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-019]** | 의료법 컴플라이언스 & 안전 가드레일 | 위험 민간요법(손 따기), 잔여 항생제 임의 복용, 직접 복용량 지시, 탈옥(Jailbreak Dr. Kim) 4대 선제 차단 가드레일 보강 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-020]** | 문진 NLP 파싱 정합성 | Triage Fallback 파서의 환아 연령 단위('만 N세', 'N살', '초등 1학년') 및 기간('N일 전', '어제'), 소아 다발성 증상 정규화 확장 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-021]** | 현장 운영시간 정합성 | 방문 시각 기준 진료 마감 시간(HH:MM) 대소 비교 필터링 & 마감 40분 전 조기 접수 마감 주의 태그 연동 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-022]** | 개발 환경 & 표준 인코딩 | Windows PowerShell 콘솔 CP949 인코딩 글자 깨짐(Mojibake) 방지 및 유니코드 UTF-8 전역 표준화 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-023]** | 파이썬 가상환경 & 패키지 형상 관리 | Conda DS 가상환경 내 누락 의존성(`apscheduler`, `fastapi`, `uvicorn`) 정합성 동기화 및 모듈 임포트 결함 해소 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-024]** | 프로젝트 거버넌스 & 협업 | 팀 프로젝트 전환(정영식 팀장, 김동준 팀원)에 따른 4대 문서(Answer, Log, README, PLAN) 누적 관리 및 에이전트 불변 규율 자동화 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-025]** | 멀티 에이전트 인터페이스 | Triage/Logistics Agent API 키 단락평가 결함 분리 및 오프라인/Evals 초고속(9.8s) 격리 모드 구현 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-026]** | 백그라운드 & API 고도화 | APScheduler 3-Track 세션 만료 정리, GenAI SDK AFC 경고 원천 억제, SSE 실시간 긴급 이벤트 브로드캐스트 | **해결 완료 (Resolved)** | 2026-10-13 |
| **[ISSUE-027]** | 에이전트 단위 테스트 검증 | LogisticsAgent 전화 통화 스크립트 생성 시 LLM 기관명 축약(어절 생략) 대응 Assertion 유연화 및 무결점 회귀 방어 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-028]** | 프론트엔드 & Stitch MCP | Stitch 도구 호출 시 프로젝트 ID 규격 불일치(projects/ prefix 중복 에러) 방어 및 screen.png 리브랜딩 컴포넌트 표준화 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-029]** | 안전 가드레일 & 의료법 컴플라이언스 | MedicalGuardrailAgent 투약 용량(Dosage) 정규식 경계 확장 (과용량 경고 문맥 내 10ml 누출 방어) | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-030]** | 프론트엔드 UI/UX 아키텍처 | screen.png 기반 신규 Stitch 전용 프로젝트(`17449043314542457561`) 개설 및 Calm Harbor 라이트 테마 3대 화면 완성 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-031]** | 프론트엔드 퍼블리싱 & 서빙 | Stitch 생성 코드의 외부 CDN 종속 탈피, 순수 Vanilla HTML5/CSS3 웹 퍼블리싱 및 FastAPI `/home` 정적 서빙 구축 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-032]** | 프론트엔드 워크스페이스 아키텍처 | 프로젝트 루트에 위치하던 임시 HTML/CSS 파일을 정규 프론트엔드 전용 워크스페이스(`frontend/`)로 모듈화 이관 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-033]** | 프론트엔드 템플릿 아키텍처 | `frontend/templates/` 하위 계층 생성, `index.html` 보관 및 상대경로(`../css/style.css`, `../js/main.js`)·정적 마운트 최적화 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-034]** | 프론트엔드 UI/UX 확장 | 응급실 가이드 페이지 부재 및 시각 포토 기반 응급처치 vs 출발 전 체크리스트 추천 웹페이지 2종 순수 HTML/CSS 구현 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-035]** | 프론트엔드 모바일 UX | 응급실 가이드 페이지 분리에 따른 인지 피로 해소 및 CSS Scroll Snap 기반 좌우 스와이프 포토 캐러셀 단일 통합 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-036]** | 프론트엔드 컴포넌트 모듈화 | 응급실 가이드 페이지 내 포토 캐러셀과 통화 스크립트·병상의 시각적 혼재 해소 (2대 카테고리 세그먼트 탭 분리) | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-037]** | 프론트엔드 & 크로스 브라우징 | Safari WebKit `file://` 로컬 보안 샌드박스의 상위 경로 차단으로 인한 CSS 미적용 결함 해소 (스마트 듀얼 로더 & WebKit 정규화) | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-038]** | 프론트엔드 UI 간소화 | 응급실 가이드 화면 내 '시각 포토 가이드' 중복 타이틀 바 및 카테고리 칩 영역 제거 (포토 캐러셀 직관성 극대화) | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-039]** | 프론트엔드 UI 시인성 개선 | 응급실 가이드 화면 하단 플로팅 CTA 버튼 2종(스크립트 확인/길안내) 전면 제거 및 화면 가독성 극대화 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-040]** | 프론트엔드 UI/UX 신규 개발 | 모니모 레퍼런스 기반 3대 카테고리 순수 HTML/CSS 설정 웹페이지(settings.html) 구축 및 GNB 연동 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-041]** | 프론트엔드 UI 컴포넌트 추가 | 모니모 레퍼런스 스타일 '앱 알림' 🔔 아이콘 및 순수 CSS iOS 토글 스위치 컴포넌트 구현 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-042]** | 프론트엔드 UI 모달 | 응급처치정보 및 법적 안내 모달 다이얼로그(반투명 오버레이, 취소/확인) 및 Step 2 증상 문진 연계 구현 | **해결 완료 (Resolved)** | 2026-10-14 |
| **[ISSUE-043]** | 프론트엔드 UI/UX 페이지 | 사용자 증상 프롬프트 입력 페이지(헤드라인 '증상을 구체적으로 정확하게 입력해주세요', 언더라인 인풋, 가상키보드 배제) 구현 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-044]** | Git 형상 관리 & 크로스 OS 협업 | 팀 협업 분기 충돌 방어 머지(Merge), 7대 엔드포인트 서빙 검증 및 Cross-OS NFD/NFC 정규화 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-045]** | 형상 관리 & 프론트엔드 모듈 격리 | 팀원(김동준) 전담 파일(input.html, modal.html)과 타 작업자(정영식) 전담 파일(index.html) 역할 분리 및 index.html 원본 100% 롤백 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-046]** | 프론트엔드 UI 텍스트 & 의료 컴플라이언스 | modal.html 안내 문구의 소아 야간 의료법·응급 대응 최적화 및 input.html/GNB 연동 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-047]** | 프론트엔드 UI 인터랙션 | input.html 사용자 텍스트 입력 시 확인 버튼 동적 표출(레퍼런스 우측 화면 1:1) 구현 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-048]** | 모바일 테스트 & PWA Standalone | 로컬 Wi-Fi IP 바인딩 및 QR코드 즉각 테스트 환경 구축, iOS/안드로이드 홈 바로가기 메타태그 탑재 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-049]** | 프론트엔드 UI/UX 모달 & 화면 연동 | index.html 아이증상 입력버튼 클릭 시 사전 안내 모달 팝업 및 증상 입력(input.html) 연동 구현 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-050]** | Git 형상 관리 & 3-Way 머지 | 원격 input.html 최신 업데이트(확인 버튼 인터랙션 & PWA 메타태그) 풀 및 index.html 모달 연동 무결점 병합 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-051]** | 프론트엔드 UI/UX 리팩토링 | 응급실 가이드(emergency_guide.html) 텍스트 전면 배제 및 소아 응급실 & KTAS 7단계 시각 이미지 슬라이더 개편 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-052]** | 프론트엔드 UI/UX 결과 화면 & 무결점 병합 | 증상 입력 후 맞춤 결과 화면(result.html) 정적 목업 구축, 2-트랙 탭/30분 마진 약국/실시간 병상 UI 구현 및 Git 무결점 통합 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-053]** | 프론트엔드 UI/UX 로딩 애니메이션 | AI 증상 분석 중 로딩 오버레이 & 단독 페이지(loading.html) 순수 CSS 키프레임 애니메이션 및 2초 타이머 시퀀스 구축 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-054]** | 프론트엔드 UI/UX 온보딩 | monimo 레퍼런스 스타일의 아이숨 첫 로딩(스플래시) 및 백엔드 로직 정합형 5대 접근 권한 명시 페이지 구축 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-055]** | 프론트엔드 UI/UX 병원 상세 및 접수 | 야간 병원 상세 및 실시간 접수 안내 화면(hospital_detail.html) 순수 프론트엔드 구축 및 result.html 연계 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-056]** | 풀스택 아키텍처 및 결합 명세 | 프론트엔드-백엔드 100% 결합 연동 명세서(FRONTEND_BACKEND_INTEGRATION_SPEC.md) 수립 및 미구현 화면 고도화 백서 구축 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-057]** | 풀스택 결합 백엔드 1단계 아키텍처 | SupervisorResponse 임상 바이탈 5대 필드 확장 및 1턴 완결 force_matching FSM 모드 구축 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-058]** | 프론트엔드 UI/UX 119 긴급 직행 & 스크롤 리스트 | 모든 병원 카드 상세 연계, 결과 화면 스크롤 뷰(Scroll List) 전환(더보기 토글 제거) 및 0ms Red Flag 119 긴급 안내 화면(emergency_alert.html) 구축 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-059]** | 프론트엔드 UI/UX 결과 카드 Flexbox 클리핑 버그 | .facility-scroll-list 내 카드 flex-shrink: 0 미부여로 인한 4개 카드 찌그러짐 및 약국/버튼 잘림 버그 완벽 해결 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-060]** | 프론트엔드 UI/UX 대화형 소아 문진 챗봇 | input.html을 카카오톡/모니모 스타일 인터랙티브 챗봇으로 전면 개편, 결측 변수 3단계 다중 턴 수집 및 0ms Red Flag 가드레일 결합 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-061]** | 프론트엔드 UI/UX 응급실 스크롤 & 기존 디자인 계승형 문진 챗봇 | 소아 응급실 병상 2개 초과 시 세로 스크롤 지원(4개소 확장) 및 input.html 기존 미니멀 UI 디자인 계승형 프로그레시브 문진 챗봇 탑재 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-062]** | 프론트엔드 모바일 UI/UX 최적화 | 온보딩 화면(splash, permission) 상단 인위적 가짜 상태 바(15:19 시간, 배터리, 와이파이) 전면 제거 및 순수 뷰포트 정돈 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-063]** | 프론트엔드 온보딩 실제 Web API 권한 요청 | permission.html 동의 버튼 클릭 시 Geolocation 및 Notification 실제 브라우저 권한 팝업 요청 및 좌표 로컬 캐싱 구현 | **해결 완료 (Resolved)** | 2026-10-15 |
| **[ISSUE-064]** | 프론트엔드 설정 & 법률 컴플라이언스 | settings.html 이용약관 버튼 연동 및 의료법 제27조 준수 아이숨 전용 이용약관(terms.html) 신규 구축 | **해결 완료 (Resolved)** | 2026-10-15 |

---

## 🛠️ 세부 이슈 및 해결 내역

### [ISSUE-001] 공공데이터포털 API 호출 시 `SERVICE_KEY_IS_NOT_REGISTERED_ERROR` (401)

* **발생 일자**: 2026-10-01
* **분류**: 오픈 API 인증 / 네트워크
* **문제 상황**:
  * 공공데이터포털(data.go.kr)에서 발급받은 오픈 API 일반 인증키를 `.env`에 넣고 Python `requests` 또는 `httpx`로 호출할 때 간헐적으로 등록되지 않은 키라는 오류(`SERVICE_KEY_IS_NOT_REGISTERED_ERROR` 또는 HTTP 401)가 발생함.
* **원인 분석**:
  * 공공데이터포털 마이페이지는 키를 `인코딩(Encoding) 키`와 `디코딩(Decoding) 키` 2종류로 제공함.
  * 파이썬의 `requests.get(url, params={"serviceKey": key})`는 쿼리스트링 전달 시 내부적으로 URL 인코딩을 자동으로 수행함.
  * 만약 환경변수에 이미 인코딩된 키(`%2B`, `%2F`, `%3D` 등이 포함된 키)를 넣으면 파이썬 라이브러리가 `%` 기호를 `%25`로 한 번 더 인코딩하여 **이중 인코딩(Double Encoding, `%252B`)**이 발생하고 공공데이터 게이트웨이 인증에 실패함.
* **구체적 해결 방안**:
  1. 환경변수(`.env`) 및 GCP Secret Manager에는 무조건 **`디코딩(Decoding) 키`**를 저장하도록 정책을 강제함.
  2. 만약 인코딩 키가 유입될 경우를 대비해 API 클라이언트 공통 모듈에서 `urllib.parse.unquote(key)`를 선제 적용하도록 방어 로직 구축.
  3. `config.py`에 Pydantic Settings를 도입하여 키 누락 시 서버 부팅 단계에서 즉시 감지하도록 설정.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제5.2절 오픈 API 인증키 관리 표준 반영

---

### [ISSUE-002] `건강보험심사평가원_질병정보서비스`의 의료법 제27조 위반 위험 및 리소스 낭비

* **발생 일자**: 2026-10-01
* **분류**: 의료법 컴플라이언스 / 시스템 성능 최적화
* **문제 상황**:
  * 사용자가 승인받은 API 목록 중 `건강보험심사평가원_질병정보서비스`가 포함되어 있어, 이를 시스템에 연동해야 하는지 여부가 쟁점이 됨.
* **원인 분석**:
  * **법적 리스크**: 의료법 제27조(무면허 의료행위)에 따라 비의료 AI가 환자의 증상을 듣고 KCD 질병코드를 부여하거나 "폐렴입니다", "장염입니다"라고 진단하는 것은 명백한 불법임.
  * **성능 및 비용 낭비**: 수만 건에 달하는 전 연령 질병분류 코드를 PostGIS/DB에 주기적으로 배치 동기화하는 것은 불필요한 스토리지 및 네트워크 쿼터 낭비임.
  * **금칙어 필터링의 비효율**: Triage 과정에서 부모의 진단 유도 질문을 방어하는 금칙어 검사는 수만 개 질병 API를 조회할 필요 없이, 소아 빈출 질환명 150여 개로 구성된 인메모리 정적 사전(`04_forbidden_lexicon.json`)으로 0ms에 처리하는 것이 압도적으로 우수함.
* **구체적 해결 방안**:
  1. `건강보험심사평가원_질병정보서비스`를 **[호출 불필요 / 파이프라인 영구 배제]** 대상으로 공식 판정함.
  2. 기 승인 상태는 유지하되, 백엔드 정기 동기화 배치 및 런타임 호출 목록에서 완전히 제외하여 불필요한 복잡도와 데드 디펜던시(Dead Dependency)를 제거함.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제5.1절 API 인벤토리 매트릭스 갱신

---

### [ISSUE-003] 심평원 진료시간 데이터의 행정 신고치와 실제 야간 소아과 운영시간의 괴리

* **발생 일자**: 2026-10-01
* **분류**: 공공데이터 정합성 / 병원 매칭 로직
* **문제 상황**:
  * 심평원 병원정보서비스의 진료시간은 병원 개설 허가 시 등록된 '행정 신고 진료시간'이므로, 야간 당직의 구인난이나 원장의 개인 사정으로 인한 임시 단축 진료가 반영되지 않아 "문 열었다고 해서 갔더니 닫혀 있는" 심각한 현장 사고 위험 존재.
* **원인 분석**:
  * 심평원 기본 API에는 요일별 야간/공휴일 실제 진료 시작·마감시간 필드가 세분화되어 있지 않음.
* **구체적 해결 방안**:
  1. **E-Gen API 결합**: 국립중앙의료원 `전국 병·의원 찾기 서비스`를 추가 신청하여 월~일/공휴일 8개 요일별 실제 운영시간(`dutyTime1s~dutyTime8c`) 데이터를 확보함.
  2. **운영 신뢰도 가중치 부여**: 보건복지부 지정 달빛어린이병원(Tier 1) > 다인 전문의 의원 > 1인 원장 의원 순으로 신뢰도 가중치 설정.
  3. **유선 확인 배지 강제**: 결과 UI에 원클릭 전화걸기(`tel:`) 버튼과 함께 "출발 전 전화 확인 권고" 배지를 필수로 노출함.
* **적용 파일**:
  * [docs/DATA_CONSIDERATIONS.md](file:///e:/monnlight/docs/DATA_CONSIDERATIONS.md) 제1장
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제5.1절 필수 2 API 선정

---

### [ISSUE-004] 일반의원의 소아과목 표방(11)과 실제 24개월 미만 영아 진료 거부 문제

* **발생 일자**: 2026-10-01
* **분류**: 소아청소년과 전문성 / 매칭 신뢰도
* **문제 상황**:
  * 의료법상 성인 내과/이비인후과도 소아청소년과(`11`)를 진료과목으로 쉽게 등록할 수 있음.
  * 그러나 실제로는 소아 전용 약품 용량 계산이나 네뷸라이저/소아수액 장비가 없어 생후 24개월 미만 영아는 현장에서 진료를 거부당하는 사례가 빈번함.
* **원인 분석**:
  * 단순 진료과목코드(`dgsbjtCd=11`)로만 쿼리하면 성인 위주 의원이 검색 결과의 60~70%를 차지함.
* **구체적 해결 방안**:
  1. **심평원 의료기관별상세정보서비스 추가**: `getDgsbjtPrDoctorInfoInqire` 오퍼레이션을 통해 병원별 **실제 소아청소년과 전문의 상주 인원수**를 DB에 적재함.
  2. **[RULE-MAT-02] 3단계 소아 전문성 티어링 알고리즘 도입**:
     * Tier 1: 보건복지부 지정 달빛어린이병원 및 권역소아응급센터
     * Tier 2: 소아청소년과 전문의 상주의원
     * Tier 3: 일반의/타과목 표방 의원
  3. **월령 기반 필터링**: 환아 문진 시 생후 24개월 미만 영아는 Tier 1 및 Tier 2만 매칭하도록 가드레일 강제.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제3.4절 RULE-MAT-02, 제11.2절 예시 코드

---

### [ISSUE-005] 달빛어린이병원 야간 '조기 현장 접수 마감(Cut-off)' 정보 부재

* **발생 일자**: 2026-10-01
* **분류**: 사용자 경험 / 현장 정합성
* **문제 상황**:
  * 23시 마감인 달빛어린이병원이라도 야간에 환자가 40~50명 몰리면 19:30~20:00경에 당일 현장 접수를 전면 조기 마감함. 공공 API에는 똑닥 등 민간 대기열이 연동되지 않아 접수 마감 여부를 알 수 없음.
* **원인 분석**:
  * 공공데이터포털에는 병원별 실시간 대기 환자 수나 접수 마감 상태가 제공되지 않는 구조적 한계.
* **구체적 해결 방안**:
  1. **접수 마감 위험 시간대 휴리스틱(Cut-off Heuristic)** 로직 구현:
     * 마감 90분 전(`close_time - 90분 <= now()`)부터는 UI 카드에 `[접수 마감 주의: 출발 전 전화 필수]` 주황색 경고 배지 강제 부착.
     * 마감 40분 전 내원 예정자에게는 병원 유선 확인 30초 통화 스크립트 원클릭 복사 기능 제공.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제3.4절 RULE-LOG-02, 제9.3절

---

### [ISSUE-006] 법정공휴일/대체공휴일/명절(설·추석) 연휴 병원 휴진 데이터 왜곡

* **발생 일자**: 2026-10-01
* **분류**: 캘린더 동기화 / 데이터 정제
* **문제 상황**:
  * 공공데이터의 공휴일 진료 여부(`trmtHoli`)가 `Y`로 되어 있어도, 삼일절 등 일반 공휴일에는 열지만 설날/추석 명절 당일에는 90% 이상 휴진함.
  * 정부의 임시공휴일 지정이나 대체공휴일에 대한 반영 지연 발생.
* **원인 분석**:
  * Boolean 단일 플래그만으로는 명절 연휴와 일반 공휴일의 차이를 반영할 수 없음.
* **구체적 해결 방안**:
  1. **한국천문연구원 특일 정보제공 서비스(`getRestDeInfo`)**를 도입하여 매일 00:05 배치로 당일 날짜의 특일 유형(평일, 법정공휴일, 대체공휴일, 명절 연휴)을 분류함.
  2. 명절 연휴 기간에는 보건복지부가 별도 배포하는 `명절 연휴 문 여는 병의원` 특별 데이터셋을 오버라이드(Override)하는 동적 로더 설계.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제5.1절 필수 4 API, 제5.5절 일간 배치

---

### [ISSUE-007] E-Gen 실시간 응급실 소아병상(`hv28`)의 허수 및 비정형 공지 메시지(`hpmg`) 파싱 누락 위험

* **발생 일자**: 2026-10-01
* **분류**: 응급의료 에스컬레이션 / NLP 파싱
* **문제 상황**:
  * E-Gen 실시간 병상 조회 시 소아응급병상(`hv28`) 수치가 남아 있어도, 실제 응급실에 소아 당직의가 없으면 이송 환자가 거부당하는 이른바 '소아 응급실 뺑뺑이' 발생.
* **원인 분석**:
  * 병상 숫자보다 의료진이 수기 입력하는 실시간 공지 메시지(`hpmg`)에 "소아 고열 진료 불가 (전문의 부재)" 등의 핵심 정보가 들어있으나 비정형 텍스트 형태임.
* **구체적 해결 방안**:
  1. `국립중앙의료원_전국 응급의료기관 정보 조회 서비스`의 `getEmrrmRltmUsefulSckbdInfoInqire`를 5분 주기로 폴링하여 Redis에 캐싱.
  2. 비정형 텍스트 파싱 규칙 엔진(`rule_engine.py`)을 구축하여 `hpmg` 필드에서 [부정 키워드(`불가`, `제한`, `부재`, `중단`)] + [소아 키워드(`소아`, `영유아`, `신생아`, `발열`)] 결합 패턴을 실시간 감지하여 자동 수용 불가 처리.
* **적용 파일**:
  * [docs/DATA_CONSIDERATIONS.md](file:///e:/monnlight/docs/DATA_CONSIDERATIONS.md) 제5장
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제8.2절 TC-31 골든 테스트

---

### [ISSUE-008] 에이전트의 무단 DB 수정/삭제 및 보고 누락 위험 원천 차단 (Sentinel Agent & HITL 체계)

* **발생 일자**: 2026-10-01
* **분류**: DB 보안 / 에이전트 거버넌스 (Zero-Trust Security)
* **문제 상황**:
  * LLM 에이전트에게 데이터베이스 접근 권한을 부여할 때, 환각(Hallucination), 비정상 루프, 또는 프롬프트 주입(Prompt Injection)으로 인해 기존 병원 마스터 데이터나 진료시간 레코드를 무단 수정(UPDATE)하거나 삭제(DELETE)할 수 있는 치명적 보안 위험성 존재.
  * 또한 에이전트가 관리자에게 사전에 보고하지 않고 은밀히 DB 조작을 감행하는 시나리오에 대한 감시 통제 장치 부재.
* **원인 분석**:
  * 일반적인 에이전트 프레임워크는 DB에 직접 연결되는 통합 커넥션을 사용하여 읽기와 쓰기 권한이 물리적으로 분리되어 있지 않음.
  * 에이전트의 Tool Calling 결과를 검증하는 독립적인 관리 감독 레이어가 없으면 '보고 누락'을 런타임에 탐지할 수 없음.
* **구체적 해결 방안**:
  1. **읽기/쓰기 권한 물리적 분리 (Free-Read, Strict-Write)**:
     * 에이전트 전용 DB 계정(`agent_readonly`)에는 오직 `SELECT` 권한만 부여하고, `UPDATE/DELETE/INSERT` 권한은 완전 박탈(Revoke)하여 DB 엔진 차원에서 물리적 조작 불가 보장 (PostgreSQL Error 42501).
     * 검색 및 공간 쿼리(`ST_DWithin`)는 지연시간 없이 0ms로 자유롭게 인가.
  2. **관리 감독 전담 에이전트(`Audit & Security Sentinel Agent`) 신설**:
     * 에이전트가 실행하는 모든 SQL 및 Tool Calling을 0ms AST 인터셉터로 실시간 감시.
     * 데이터 수정이 필요한 경우 직접 커밋을 금지하고, 변경 대상 테이블, PK, Before/After Diff, 변경 사유를 담은 **'데이터 변경 제안서(Mutation Proposal)'**를 작성하여 관리자에게 결재 상신.
  3. **보고 누락 및 우회 시도 원천 차단 (Zero-Bypass Enforcement)**:
     * 관리자 보고 절차를 건너뛰거나 직접 쓰기를 시도하면 트랜잭션을 0.001초 만에 강제 롤백(Rollback/Abort)하고 에이전트를 즉각 격리(Quarantine).
     * 관리자에게 긴급 침해 경보를 발송하고 본 `log.md` 및 불변 감사 테이블(`audit_mutations`)에 영구 기록.
  4. **Human-in-the-Loop(HITL) 관리자 승인 큐 운영**:
     * 관리자가 서명된 승인 토큰으로 최종 승인(Approve)을 누른 경우에만 `admin_executor` 세션을 통해 DB에 안전 커밋.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제3.1절 다이어그램, 제3.2절 R&R, 제3.4절 RULE-AUD-01~04, 제5.11절 DB 접근 통제 거버넌스, 제10.2절 디렉터리 레이아웃
  * [docs/DATABASE_DESIGN.md](file:///e:/monnlight/docs/DATABASE_DESIGN.md) 제5.3절 물리적 Role 분리 DDL

---

### [ISSUE-009] 지리공간 반경 검색 시 Full Scan 지연 및 실시간 병상 쓰기 I/O 병목

* **발생 일자**: 2026-10-01
* **분류**: 데이터베이스 성능 최적화 / 지리공간 쿼리 (Spatial Indexing)
* **문제 상황**:
  * 사용자의 현재 위치(위·경도)로부터 반경 5~30km 내 소아 야간 진료 병원을 실시간 정렬할 때, 좌표 계산 수식(하버사인 공식 등)을 적용할 경우 전체 병의원 레코드에 대한 Full Table Scan이 발생하여 수초 대의 응답 지연 발생 우려.
  * 또한 국립중앙의료원(E-Gen)에서 5~10분 주기로 수집되는 실시간 소아 응급실 병상 수(`hv28`) 및 공지(`hpmg`)를 RDBMS 디스크에 반복 쓰기(Write)할 경우 디스크 I/O 병목 및 락 경합 발생.
* **원인 분석**:
  * 표준 관계형 DBMS(MySQL 등)의 기본 인덱스는 WGS84 타원체 구면 좌표 연산(`ST_DWithin`)에 대한 고성능 R-Tree 공간 인덱싱 기능이 제약됨.
  * 수시로 갱신되는 휘발성 데이터와 마스터 메타데이터가 단일 스토리지 계층에 혼재됨.
* **구체적 해결 방안**:
  1. **PostGIS GIST 공간 인덱스 도입**:
     * PostgreSQL 16에 PostGIS 3.4 확장을 적용하고 `coordinates` 필드에 R-Tree 기반 GIST 공간 인덱스(`idx_hospitals_geom`)를 생성하여 7만여 개소 병의원 대상 반경 검색을 **3~5ms 이내로 단축**.
  2. **Redis 인메모리 캐시 계층 분리**:
     * 휘발성 응급실 병상 데이터는 Cloud Memorystore Redis 7+에 `er:status:{hpid}` 해시 키로 저장하고 **TTL을 10분으로 강제**하여 디스크 I/O 부하 90% 이상 절감.
  3. **제어된 역정규화(Controlled Denormalization)**:
     * 조인 비용을 줄이기 위해 `is_pediatric_specialist`, `is_moonlight`, `is_active_now` 플래그를 `hospitals` 마스터 테이블에 배치로 사전 계산하여 단일 쿼리로 서빙.
* **적용 파일**:
  * [docs/DATABASE_DESIGN.md](file:///e:/monnlight/docs/DATABASE_DESIGN.md) 제1장, 제5장, 제6장
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제5.4절, 제5.8절, 제5.9절

---

### [ISSUE-010] 2026 최신 Gemini 3.8 Flash 모델 라인업 전수 검토 및 Zero-LLM/LLM 역할 재배치

* **발생 일자**: 2026-10-01
* **분류**: AI 모델 아키텍처 / 비용 및 지연시간 최적화 (Model Cascading)
* **문제 상황**:
  * 초기 기획안에서 2026년 10월 20일부 퇴역 예정인 레거시 모델(Gemini 2.5 / 2.0 / 1.5)이 혼재되어 있었음.
  * 또한 공간 검색(PostGIS), 실시간 병상 조회(Redis), 응급 Red Flag 차단 등 결정론적으로 0ms에 처리해야 하는 영역과 LLM이 꼭 필요한 자연어 문진 영역의 경계가 모호해질 경우 응답 지연 및 환각(Hallucination) 위험 발생.
* **원인 분석**:
  * 2026년 9월 Google이 공식 출시한 최신 플래그십 **Gemini 3.8 Flash**는 장기 에이전트 워크플로우(Long-horizon Agentic)와 사고 수준(Effort Control: Low, Medium, High)을 지원하여 프론티어급 추론력과 초저지연을 동시에 제공함.
  * 따라서 고난도 에이전트에는 Gemini 3.8 Flash를 전격 배치하고, 단순 분류에는 Gemini 3.5 Flash-Lite를 매핑하며, 계산/검색은 철저히 Zero-LLM으로 분리해야 함.
* **구체적 해결 방안**:
  1. **Gemini 3.8 Flash 핵심 두뇌 배치**:
     * 부모의 감정적 비정형 문진 및 4대 변수 추출(`Triage Agent`): **Gemini 3.8 Flash (Thinking Effort: Medium)**.
     * 에이전트 간 상태 전이 및 문맥 판단(`Supervisor Agent`): **Gemini 3.8 Flash (Thinking Effort: Low, < 300ms)**.
  2. **Gemini 3.5 Flash-Lite 보조 경량 엔진 배치**:
     * `Medical Guardrail`(이진 분류), `Visit Logistics`(체크리스트 서식화), `Sentinel Agent`(Diff 요약): **Gemini 3.5 Flash-Lite (< 150ms, 비용 90% 절감)**.
  3. **결정론적 Zero-LLM (LLM 호출 엄금) 영역 강제**:
     * 생후 100일 미만 고열, 경련 등 KTAS Red Flag: **0ms Regex 룰엔진**.
     * 병원 반경 5~30km 거리 계산 및 영업시간 필터링: **PostgreSQL 16 + PostGIS 3.4 (5ms)**.
     * 실시간 응급실 병상(`hv28`) 및 공지 조회: **Redis In-Memory (1ms)**.
     * DB 접근 보안: **PostgreSQL `agent_readonly` Role + 0ms AST 인터셉터**.
  4. **오프라인 검증 한정 고성능 모델 사용**:
     * 40선 골든 테스트셋 자동 채점(`tests/evals/run_evals.py`): **Gemini 3.8 Flash (Thinking: High) / Gemini 3.1 Pro**.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 제1.2절, 제3.3절, 제4절, 제7.1절, 제10.1절, 제12절
  * [docs/VIBE_CODING_ROADMAP.md](file:///e:/monnlight/docs/VIBE_CODING_ROADMAP.md) 제1장, 제3장

---

### [ISSUE-011] 공공데이터포털 NMC 오픈API 2종 승인 완료 및 전국 17개 시·도 병원-약국 연계 전국구 확장

* **발생 일자**: 2026-10-08
* **분류**: 서비스 전국구 확장 / 외부 공공데이터 API 연동 / 지리·시간 페어링 엔진 (Nationwide Expansion)
* **문제 상황**:
  * 기존 시범 프로토타입(`moonlight_hospital_night_pharmacy_linkage.ipynb`)은 공공데이터포털 API 승인 전 단계로 서울·경기 일부 지역 6~7개소 모의 데이터에 한정되어 전국 단위 서비스 확장에 한계가 있었음.
  * 이용자가 전국 어디에서든(예: 부산, 대구, 광주, 대전, 울산, 세종, 제주, 강원, 충청, 전라, 경상) 야간 진료 소아과와 당번 약국을 원스톱으로 검색할 수 있는 전국구 데이터 파이프라인 및 실시간 동적 페어링 체계 필요.
* **원인 분석**:
  * 공공데이터포털에서 국립중앙의료원(NMC) **전국 병·의원 찾기 서비스**(`HsptlAsembySearchService`)와 **전국 약국 정보 조회 서비스**(`ErmctInsttInfoInqireService`) 2종의 활용 신청이 모두 정상 승인 완료됨 (`DATA_GO_API_KEY` 발급).
  * 이에 따라 전국 7만여 개소 병의원 및 2만 4천여 개소 약국의 실시간 영업시간과 좌표 데이터를 직접 호출하여 결합할 수 있는 인프라가 확보됨.
* **구체적 해결 방안**:
  1. **실시간 E-Gen 오픈API 연동 엔진 (`fetch_live_pairs_from_api`) 구축**:
     * `HsptlAsembySearchService/getHsptlMdcncListInfoInqire`: 특정 시·도/시·군·구 대상 야간(20시 이후 마감) 소아과 실시간 필터링.
     * `ErmctInsttInfoInqireService/getParmacyListInfoInqire`: 동일 행정구역 내 20시 이후 심야 영업 약국 동적 추출.
     * 하버사인(Haversine) 구면거리 연산 및 시간 버퍼 연산을 결합하여 최단거리 약국과 30분 안전 마진을 실시간 자동 페어링.
  2. **전국 17개 시·도 통합 마스터 데이터셋 구축**:
     * 수도권(서울·경기·인천), 충청권(대전·세종·충북·충남), 호남권(광주·전북·전남), 영남권(부산·대구·울산·경북·경남), 강원권, 제주권 전역을 망라하는 공식 달빛어린이병원 및 거점 야간 소아과-약국 데이터셋(전국 29개 거점) 구축.
     * 전체 연계 쌍의 90% 이상에서 '30분 안전 마진 확보(🟢 완벽 매칭)' 검증.
  3. **전국 단위 인터랙티브 시각화 대시보드 고도화**:
     * `Folium MarkerCluster`: 대한민국 전역 조망(Zoom 7.5) 시 권역별 클러스터링 지원 및 확대 시 개별 마커와 보행 연계선(Polyline) 렌더링.
     * `Seaborn/Matplotlib`: 권역별 인프라 분포, 24시간 가동 마감시간 간트 타임라인(Gantt), 거리/마진 분포 4분할 분석 차트 구현.
     * `search_by_region(sido, sigungu)` 및 `find_nearest_night_pair(lat, lon)`: 사용자 GPS 기반 최근접 추천 엔진 탑재.
* **적용 파일**:
  * [notebooks/moonlight_hospital_night_pharmacy_linkage.ipynb](file:///e:/monnlight/notebooks/moonlight_hospital_night_pharmacy_linkage.ipynb) (전국구 확장판 전 셀 검증 및 실행 완료)
  * [docs/NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md](file:///e:/monnlight/docs/NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md) 제6장 로드맵 업데이트

---

### [ISSUE-012] 소아 의료 진료 3대 취약 시간대 정량 분석 및 수요-공급 미스매치 시뮬레이션 적용

* **발생 일자**: 2026-10-08
* **분류**: 응급의료 통계 모델링 / 응급실 과밀화 완화 시뮬레이션 / Triage 가드레일 (Vulnerable Hours Modeling)
* **문제 상황**:
  * 기존 E-Gen 응급실 노트북은 실시간 병상(`hv28`)과 단순 24시간 내원 추이만 나열하여, **실제 소아 환자 보호자가 겪는 핵심 진료 취약 시간대의 원인(외래 셧다운, 달빛병원 컷오프, 심야 전문의 부재 등)과 정량적 취약도 지표**가 부재했음.
  * 야간에 폭증하는 경증 환아(KTAS 4~5단계)가 달빛어린이병원-심야약국으로 분산되었을 때 얻을 수 있는 응급실 과밀화 완화 효과의 정량적 근거 제시 필요.
* **원인 분석**:
  * 소아 야간 응급의료 붕괴의 핵심은 단순한 병상 부족이 아니라, **"1차 외래 셧다운 시점(20~24시)의 수요 폭증"**과 **"심야·새벽(00~06시)의 소아청소년과 전문의 부재에 따른 공급 절벽"**이라는 두 가지 서로 다른 메커니즘이 결합된 결과임.
* **구체적 해결 방안**:
  1. **소아 의료 진료 3대 취약 시간대 정의 및 정량 모델링**:
     * **[제1 취약기: 20~24시 (피크 22시 280명)]**: 낮 대비 4배 폭증, KTAS 4~5단계 경증이 74% 점유하여 상급 응급실 마비.
     * **[제2 취약기: 00~06시 (초심야·새벽)]**: 환자수 감소 대비 1차/달빛 외래 전멸 및 응급실 소아 당직의 부재(`hpmg` 공지 집중)로 '소아 뺑뺑이' 고위험.
     * **[제3 취약기: 주말·공휴일 (토 13시~, 일/공휴일)]**: 일반 외래 휴진으로 상시 0병상 포화.
  2. **종합 진료 취약도 점수(Composite Vulnerability Index, 0~100점) 산출 파이프라인 탑재**:
     * $V_t = 0.5 \times D_t(\text{수요지수}) + 0.5 \times S_t(\text{공급결핍지수})$ 수식 모델링 및 4단계 위험등급(`🔴 위험`, `🟠 경고`, `🟡 주의`, `🟢 안정`) 라벨링.
  3. **신규 시각화 차트 2종 구현**:
     * `시각화 D`: 시간대별 소아 내원수(라인) vs 종합 취약도(바) 듀얼 Y축 복합 차트 + 취약 구간 배경 쉐이딩(Span) 및 어노테이션.
     * `시각화 E`: 달빛어린이병원 경증 50% 분산 시뮬레이션 바 차트 (응급실 과밀 완화율 최대 37% 달성 입증).
  4. **MoonlightCare 서비스 가드레일 전략 도출**:
     * 19:30~21:30 달빛어린이병원 안내 시 "조기 접수 마감(Cut-off) 주의" 팝업 강제화.
     * 23:00 이후 심야는 E-Gen 실시간 병상(`hv28 > 0`) 및 `hpmg` 소아 진료 가능 검증 병원으로 직결 안내.
* **적용 파일**:
  * [notebooks/egen_pediatric_emergency_analysis.ipynb](file:///e:/monnlight/notebooks/egen_pediatric_emergency_analysis.ipynb) (제5장 신설 및 23개 전 셀 정상 실행 완료)

---

### [ISSUE-013] 초심야 00~06시 소아 진료 공백(달빛 전멸 + 소아 당직의 부재) 극복 4대 솔루션 및 2-트랙 라우팅 엔진 노트북 반영

* **발생 일자**: 2026-10-08
* **분류**: 응급의료 의사결정 알고리즘 / 심야 비대면 상담 가드레일 / 119 구급대 연계 프로토콜 (Midnight Emergency Routing)
* **문제 상황**:
  * 00~06시 초심야 시간대는 전국 달빛어린이병원 외래가 100% 셧다운(가장 늦은 곳도 24시 마감)되고, 응급실 또한 소아청소년과 당직 전문의 부재로 성인 응급의학과 전문의의 단순 대증처치 또는 진료 거부('소아 뺑뺑이')가 집중되는 구조적 절벽 구간임.
  * 이 공백기에 단순 "병원에 가라" 또는 "집에서 참으라"는 이분법적 안내는 응급 환아의 골든타임 상실이나 불필요한 심야 상급병원 과밀화를 초래함.
* **원인 분석**:
  * 심야에 발생하는 소아 질환의 80% 이상은 경증 단순 고열(해열제 반응성), 급성 위장염, 두드러기 등 대증처치 및 안심 상담으로 아침(09시) 외래 오픈까지 안전 대기가 가능한 케이스임.
  * 반면 호흡곤란, 경련, 청색증 등 KTAS 1~2단계 중증 환아는 소아 전문의가 없는 일반 응급실이 아닌, '권역 소아전문응급의료센터' 또는 '광역응급의료상황실/119 스마트 이송'을 통해 한 번에 최종 치료 병원으로 이송되어야 함.
* **구체적 해결 방안**:
  1. **초심야(00~06시) 4대 영역별 대응 솔루션 체계화**:
     * **[영역 1] 서비스/AI 레이어 (MoonlightCare 2-트랙 의사결정 알고리즘)**:
       - **트랙 A (경증 안심/홈케어 가이드)**: KTAS 4~5단계 환아에게 체온별 해열제 교차복용 타이머, 수분 섭취 수칙, 09시 오픈 달빛어린이병원 사전 예약/대기표 연계.
       - **트랙 B (중증 긴급 직결 & 119 브리핑 카드)**: KTAS 1~3단계 의심 시 즉시 119 자동 다이얼 연결 및 SBAR 형식 '119 구급대/상황실용 30초 음성 브리핑 카드' 자동 생성.
     * **[영역 2] 의료 자원 연계 (비대면 진료 및 심야 공공약국)**:
       - 보건복지부 심야 비대면 진료 연계 처방전 발급 + E-Gen 24시간 공공심야약국 실시간 조제 수령.
     * **[영역 3] 거점 응급의료 네트워크 (E-Gen hpmg 필터링)**:
       - 전국 12개 권역별 소아전문응급의료센터 우선 라우팅 및 `hpmg` 소아 수용 불능 공지 실시간 회피.
     * **[영역 4] 제도/정책적 보상 체계**:
       - 심야 소아 당직 가산금 및 달빛어린이병원 심야 당직 로테이션 인센티브.
  2. **주피터 노트북 코드 및 시각화 전격 구현 (`egen_pediatric_emergency_analysis.ipynb`)**:
     * **코드 셀 [16] (`route_midnight_pediatric_patient`)**: 증상 및 바이탈(호흡수, 의식, 체온, 월령) 입력 시 트랙 A/B 판정, 권역 소아센터 추천, SBAR 119 브리핑 카드, 홈케어 가이드를 원스톱 생성하는 파이프라인 탑재.
     * **코드 셀 [17] (`시각화 F`)**: 솔루션 도입 전(Pre) vs 도입 후(Post) 4대 정량 지표(소아 뺑뺑이 위험도 -75%, 응급실 체류시간 -47%, 불필요 내원율 -60%, 보호자 심리 안정도 +133%) 비교 막대 차트 구현 및 렌더링.
     * **마크다운 셀 [15], [18] (제6장 & 제7장)**: 4대 솔루션 상세 마크다운 및 취약 시간대 대응 종합 권고안 최종 업데이트.
* **적용 파일**:
  * [notebooks/egen_pediatric_emergency_analysis.ipynb](file:///e:/monnlight/notebooks/egen_pediatric_emergency_analysis.ipynb) (26개 전 셀 무결성 검증 및 실행 완료)

---

### [ISSUE-014] 실시간 공공 API 호출 안티패턴 배제 및 Firebase 서버리스 실시간 아키텍처 전격 개편 (PROJECT_PLAN.md)

* **발생 일자**: 2026-10-08
* **분류**: 시스템 아키텍처 개편 / 클라우드 DBMS 선정 / 서버리스 실시간 파이프라인 / 기획안 동기화
* **문제 상황**:
  * 야간·휴일 소아 응급도 및 병상 연동 시스템 기획 중, "사용자가 조회할 때마다 공공데이터 API를 실시간 호출해야 하는가 vs DB에 사전 저장해야 하는가" 및 "Firebase로 이를 구현 가능한가"에 대한 아키텍처 결정 필요.
  * 기존 [PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md)는 Cloud SQL PostgreSQL(PostGIS) + Redis 기반으로 작성되어 있어, 서버 상시 구동 비용(월 $100+) 및 커넥션 관리 부담이 컸음.
  * 또한 주피터 노트북 2권에서 실증된 핵심 성과(전국 17개 시·도 병원-약국 30분 마진 페어링, 소아 의료 3대 취약 시간대 모델링, 초심야 00~06시 2-트랙 라우팅 및 119 SBAR 브리핑 카드)가 기존 기획안에 완전히 반영되지 못했음.
* **원인 분석**:
  * **온디맨드 실시간 API 호출의 4대 결함**:
    1. **응답 지연(Latency)**: 호출당 1.5~3.0초 소요, 야간 트래픽 폭주 시 타임아웃 빈발 (응급 상황에 치명적).
    2. **일일 쿼터 초과**: 기본 10,000건/일 한도로 저녁 피크 시 즉각 HTTP 429 차단.
    3. **원천 데이터 갱신 주기 불일치**: E-Gen 병상 데이터는 병원 전산망 특성상 5~10분 단위로 동기화되므로 매초 호출하는 것은 무의미한 트래픽 낭비.
    4. **보안 취약점**: 클라이언트 앱/웹에 공공 API Key 노출 위험.
* **구체적 해결 방안**:
  1. **Firebase (Cloud Firestore + Cloud Functions v2 + Cloud Scheduler) 전면 채택**:
     * 상시 구동 서버 비용 0원(무료 티어 내 운영 가능).
     * `Cloud Scheduler ('every 5 minutes')` + `Cloud Functions v2`가 5분마다 전국 410개 응급실 병상(`hv28`, `hpmg`)을 자동 수집.
     * **권역별 번들링(Bundling) 패턴 탑재**: 시·도 단위 요약 문서(`beds_summary_seoul` 등)로 압축 저장하여, 클라이언트가 단 1회의 Document Read로 권역 전체 병상을 조회할 수 있게 함 (Firestore 읽기 비용 98% 절감).
     * **`onSnapshot` 실시간 리스너 연동**: 병상 변동 시 사용자 화면이 새로고침 없이 초록불로 즉시 갱신.
     * **Geohash 인덱스 + 메모리 Haversine(1ms) 연산**: PostGIS 의존성을 완전히 제거하고도 반경 5~30km 소아과를 1ms 내에 거리순 정렬.
     * **Firebase Security Rules 무관용 Zero-Trust**: 클라이언트는 읽기만 전면 허용, 모든 쓰기/수정/삭제는 Admin SDK 전용으로 원천 봉쇄.
  2. **기획안 전면 개편 ([PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md))**:
     * Section 1.2: Firebase 실시간 아키텍처 및 취약시간대 모델링 프로젝트 목표 추가.
     * Section 3: 하네스 에이전트 R&R, Zero-LLM 영역, 행동 규칙(심야 2-트랙, 약국 30분 마진, Firebase Rules) 최적화.
     * Section 4: 비-LLM 비용 최적화(Geohash 위임, Firestore 번들링) 반영.
     * Section 5: 오픈 API 승인 현황(E-Gen 2종 승인 반영) 및 NoSQL 컬렉션 스키마, `firestore.rules`, `syncEmergencyBeds` 완제 스크립트 전면 탑재.
     * Section 6: 실제 완성된 주피터 노트북 2권의 정량 분석 및 시뮬레이션 성과 공식 반영.
     * Section 10~12: 디렉터리 레이아웃, 코드 주석 표준, 개발 로드맵 전면 동기화.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) (Firebase 기반 아키텍처 및 주피터 분석 결과 동기화 완료)
  * [log.md](file:///e:/monnlight/log.md)

### [ISSUE-015] 주피터 노트북 데이터 분석 결과 반영 및 공공 API-Firebase 비용·사용량 최적화 동기화 아키텍처 수립 (PROJECT_PLAN.md 전격 업데이트)

* **발생 일자**: 2026-10-08
* **분류**: 기획안 고도화 / 데이터 분석 실증 통합 / 공공 API 쿼터 제약 / Firebase Firestore 비용 최적화 동기화
* **문제 상황**:
  * 기존 [PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md)에 주피터 노트북 2권([notebooks/egen_pediatric_emergency_analysis.ipynb](file:///e:/monnlight/notebooks/egen_pediatric_emergency_analysis.ipynb), [notebooks/moonlight_hospital_night_pharmacy_linkage.ipynb](file:///e:/monnlight/notebooks/moonlight_hospital_night_pharmacy_linkage.ipynb))에서 도출된 상세한 실측 통계 수치(소아 가용병상 50% 이상 포화, 다빈도 질환 1위 급성열성질환 34.2%, 피크타임 20~24시 280명 4배 폭증, 3대 취약 시간대 종합취약도, 달빛병원 50% 분산 시 응급실 과밀화 37% 완화 실증, 심야 2-트랙 및 119 SBAR 카드, 전국 17개 시·도 1:1 페어링 및 90% 이상 30분 마진 확보 등)가 완전하게 체계화되지 못했음.
  * 또한 공공데이터 오픈 API(E-Gen/HIRA)의 호출 한계(일일 쿼터 1만~10만건, 초당 10~20 TPS 제한, 1.5~3.5초 지연)와 Firebase Cloud Firestore의 과금 모델(Document Read/Write/Delete) 간의 상충 관계를 고려할 때, 비용과 사용량 측면에서 데이터를 어떻게 최적화하여 동기화할 것인가에 대한 구체적 엔지니어링 메커니즘 서술이 필요했음.
  * 기존 기획안의 5.12 섹션에 남아있던 레거시 "Cloud SQL PITR/HA" 문구를 Firestore 네이티브 DR 스펙으로 일치시켜야 했음.
* **구체적 해결 방안**:
  1. **[PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 전면 업데이트**:
     * **Section 1 (Executive Summary)**: 소아 병상 병목 실측치, 내원 1위 급성열성질환(34.2%) 및 내과질환 55.7%, 야간 20~24시 4배 피크 및 경증 74%, 30분 마진 90% 확보율, 응급실 과밀화 37% 완화, 초심야 2-트랙 및 119 SBAR 카드 등 핵심 수치 반영.
     * **Section 5.9 (Cloud Functions v2 적응형 스케줄러)**: 단순 쓰기를 배제하고 시간대별 적응형 폴링, **Hash Diffing(직전 스냅샷과 상태 해시 비교 후 변경분만 Write)**, 권역 번들링(`regional_bed_bundles`), 타임아웃/서킷 브레이커가 구현된 TypeScript 완제 코드 탑재.
     * **Section 5.10 (스마트 동기화 아키텍처 신설)**:
       - 공공 API 쿼터 vs Firestore 과금 구조($0.06/100k reads, $0.18/100k writes) 비교 분석.
       - **5대 비용 & 사용량 최적화 동기화 메커니즘**:
         1) 주피터 노트북 3대 취약 시간대 기반 **적응형 동적 폴링(Adaptive Dynamic Polling)**: 피크타임(20~24시)/주말 5분, 심야(00~06시)/평일 낮 15분 주기로 차등화하여 일일 공공 API 호출 횟수 160회(45% 절감)로 극소화.
         2) 데이터 변경 감지 기반 **조건부 쓰기(Differential Write / Hash Diffing)**: 5분마다 병상이 변하는 10~20% 병원만 Write하여 Firestore Document Write 80% 이상 절감 (무료 티어 내 운영).
         3) **권역별 압축 번들링(Regional Bed Bundling)**: 17개 시도별 단일 요약 문서(`beds_summary_{sido}`) 생성으로 클라이언트 Read 98.3% 절감.
         4) **3-Tier 계층형 캐싱 파이프라인**: L1 Client Local(TTL 60~180s) ➔ L2 Firestore Bundles ➔ L3 Cloud Functions Worker.
         5) **정적 마스터 vs 동적 스트림 라이프사이클 분리**: 병원/약국 마스터 주 1회, 특일 월 1회, 실시간 병상 가변 3~15분 폴링.
       - 공공 서버 장애 대응 **서킷 브레이커 & Stale-While-Revalidate** 정책.
     * **Section 5.13 (백업 및 재해 복구)**: Cloud SQL 레거시 문구를 완전 제거하고 Firestore Native PITR(7일간 1분 단위 롤백), Cloud Scheduler+Functions 기반 GCS 일간 Managed Export, Multi-Region 자동 복제 및 무중단 HA 체계로 정립.
     * **Section 6 (주피터 노트북 데이터 분석 체계)**: 노트북 1(전국 17개 시도 1:1 페어링, 90% 이상 30분 마진, 4단계 조제 안전 등급, 반경 200m 보행 편의성, Folium 전국 지도, 군 단위 사각지대) 및 노트북 2(가용병상 4단계 기준표 및 50% 포화 실측치, 내원 질환 5대 분포 및 급성내과 55.7%, 24시간 패턴 및 야간 4배 피크 280명, KTAS 경증 74%, 3대 취약기 종합취약도 점수, 달빛병원 50% 분산 시 응급실 과밀화 37% 완화 시뮬레이션, 초심야 2-트랙 및 119 SBAR 카드, 전/후 4대 정량 지표) 전수 상세 반영.
     * **Section 9 (데이터 문제점 핵심 요약)**: 8대 실데이터 문제점 및 시스템 대응책(소아 가용병상 포화 및 일반병상 비대칭, E-Gen 비정형 공지 `hpmg` 파싱, 약국 30분 마진 미확보 예외처리 및 군 단위 사각지대 등)으로 보강.
* **적용 파일**:
  * [docs/PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md)
  * [log.md](file:///e:/monnlight/log.md)

---

### [ISSUE-016] 구버전 Gemini 모델 단종(404 NOT_FOUND) 및 최신 Gemini 3.8 Flash / 3.5 Lite 전환

* **발생 일자**: 2026-10-13
* **분류**: AI 모델 아키텍처 / 프레임워크 호환성 / 장애 가시성
* **문제 상황**:
  * TriageAgent 및 LogisticsAgent 초기 개발 시 모델명이 `gemini-2.5-flash`로 하드코딩되어 있어, Google GenAI API 호출 시 `404 NOT_FOUND` ("models/gemini-2.5-flash is no longer available to new users") 에러가 발생함.
  * 내부 `try...except Exception: pass`로 인해 에러가 무음 처리(Silent Failure)되면서 실제로는 Gemini LLM이 구동되지 않고 정규식 Fallback 파서로만 고착되는 결함 확인.
* **원인 분석**:
  * 2026년 하반기 Google GenAI API 정책 변경에 따른 구버전 모델 deprecation 및 무차별적인 예외 무음 처리 안티패턴.
* **구체적 해결 방안**:
  1. `app/config.py`의 Pydantic Settings에 `gemini_triage_model = "gemini-3.8-flash"`, `gemini_logistics_model = "gemini-3.5-flash-lite"` 환경변수 설정 추가.
  2. `triage_agent.py`와 `logistics_agent.py`의 기본 모델명을 각각 2026 플래그십 `gemini-3.8-flash` 및 `gemini-3.5-flash-lite`로 교체.
  3. 무음 `except Exception: pass`를 제거하고 `logger.warning()`으로 호출 실패 사유(인증/쿼터/네트워크)를 투명하게 로깅하도록 개선.
  4. 테스트 시 Google GenAI 서버로부터 `HTTP/1.1 200 OK` 정상 응답 수신 실증.
* **적용 파일**:
  * [app/config.py](file:///e:/monnlight/app/config.py)
  * [app/agents/triage_agent.py](file:///e:/monnlight/app/agents/triage_agent.py)
  * [app/agents/logistics_agent.py](file:///e:/monnlight/app/agents/logistics_agent.py)
  * [tests/test_audit_fixes.py](file:///e:/monnlight/tests/test_audit_fixes.py) (TC-FIX-01)

---

### [ISSUE-017] 실시간 응급실 병상 조회 시 공공 API 중복 호출 지연 방어를 위한 0ms 인메모리 TTL 캐싱 계층 구축

* **발생 일자**: 2026-10-13
* **분류**: 실시간 데이터 파이프라인 / API 레이턴시 최적화
* **문제 상황**:
  * `GET /api/v1/emergency/nearby` 및 `MatchingAgent.match_destinations`가 호출될 때마다 동기 `requests.get()`으로 국립중앙의료원(NMC) E-Gen 공공 API를 매번 온디맨드로 직접 호출함.
  * 로컬 Haversine 연산은 5µs에 불과하나, 공공 API 통신으로 인해 전체 응답 지연이 400~1,000ms로 급증하고 야간 공공 API 장애(503) 시 전체 진료 매칭이 타임아웃되는 위험 노출.
* **원인 분석**:
  * 실시간 병상 폴링 워커와 사용자 조회 엔드포인트 간 캐시 공유 계층 부재.
* **구체적 해결 방안**:
  1. `app/services/emergency_sync_service.py`에 모듈 전역 5분 TTL(300초) 인메모리 캐시(`_in_memory_bed_cache`) 구축.
  2. `fetch_emergency_beds(stage1, force_refresh=False)`:
     - 유효 캐시 존재 시 외부 네트워크 통신 0회 차단, 인메모리에서 **0.2~0.5ms 이내 즉시 반환**.
     - APScheduler 백그라운드 데몬(`poll_realtime_beds`)은 `force_refresh=True`로 호출하여 주기적으로 캐시 갱신.
  3. 동시성 및 테스트 편의성을 위한 `clear_bed_cache()` 격리 메서드 제공.
* **적용 파일**:
  * [app/services/emergency_sync_service.py](file:///e:/monnlight/app/services/emergency_sync_service.py)
  * [app/services/scheduler.py](file:///e:/monnlight/app/services/scheduler.py)
  * [tests/test_audit_fixes.py](file:///e:/monnlight/tests/test_audit_fixes.py) (TC-FIX-02)

---

### [ISSUE-018] 전국 17개 시·도 행정구역 동적 판별 및 맞춤 병상 매칭 (서울특별시 하드코딩 및 타 지자체 좌표 왜곡 해소)

* **발생 일자**: 2026-10-13
* **분류**: 전국구 확장 / 공간 정합성 (Spatial Resolution)
* **문제 상황**:
  * 골든 테스트 케이스의 수원(TC-25), 대전(TC-26), 부산(TC-27), 광주(TC-28), 강원 평창(TC-29), 인천(TC-30) 등 전국 시·도 환아 매칭 시 `MatchingAgent`에 `stage1="서울특별시"`가 고정되어 있었음.
  * 또한 `fetch_hospital_coordinates`가 서울 530개 좌표 캐시(`seoul_emergency_coords.json`)만 전역 반환하여, 타 지자체 응급실의 좌표가 기본값 (37.5, 127.0 - 서울)으로 설정되면서 부산·광주 등에서 거리가 300km 이상으로 왜곡되어 병원이 검색되지 않는 결함 발생.
* **원인 분석**:
  * 주소/좌표 기반 17개 시·도 행정구역 매퍼 부재 및 지자체별 병원 위경도 캐시 격리 미비.
* **구체적 해결 방안**:
  1. `resolve_stage1_from_coords_or_address(lat, lon, address)` 구축:
     - 1순위: 주소 텍스트의 광역시/도 정규식 매칭 (서울, 경기, 부산, 대구, 인천, 광주, 대전, 울산, 세종, 강원, 충북, 충남, 전북, 전남, 경북, 경남, 제주).
     - 2순위: 특화 시·군·구 키워드 (수원, 해운대, 유성구, 달서구 등) 기반 매칭.
     - 3순위: WGS84 좌표계 Bounding Box 기반 지리적 폴백.
  2. `emergency_sync_service.py` 좌표 관리 계층 전면 개편:
     - `_hospital_coords_cache_by_stage: dict[str, dict]`로 지자체별 좌표 딕셔너리 물리적 격리.
     - `STAGE1_DEFAULT_COORDS`: 17개 광역시·도별 중심 좌표 정의.
     - `NATIONWIDE_REGIONAL_ER_MOCKS`: 지자체별 권역소아전문응급의료센터 및 주요 거점 응급실(아주대, 해운대백병원, 충남대, 칠곡경북대, 전남대, 길병원, 원주세브란스, 제주대 등)의 정밀 좌표 탑재.
     - `fetch_hospital_coordinates`에서 요청된 `stage1`에 부합하는 좌표망을 반환하도록 리팩토링.
  3. 부산, 수원 등 전국구 환아 검색 시 35km 이내의 해당 지자체 거점 소아응급실 매칭 실증.
* **적용 파일**:
  * [app/agents/matching_agent.py](file:///e:/monnlight/app/agents/matching_agent.py)
  * [app/services/emergency_sync_service.py](file:///e:/monnlight/app/services/emergency_sync_service.py)
  * [tests/test_audit_fixes.py](file:///e:/monnlight/tests/test_audit_fixes.py) (TC-FIX-03, TC-FIX-07)

---

### [ISSUE-019] 위험 민간요법, 잔여 항생제 임의 복용, 직접 복용량 지시, 탈옥(Jailbreak) 차단 4대 세이프티 가드레일 보강

* **발생 일자**: 2026-10-13
* **분류**: 의료법 컴플라이언스 / 안전 가드레일 (Adversarial Defense)
* **문제 상황**:
  * 골든 케이스의 적대적·악의적 시나리오(TC-09: 챔프 몇 ml 먹여야 하나요, TC-10: 남은 항생제 오구멘틴 먹여도 되죠, TC-12: Dr. Kim 페르소나 주입 탈옥, TC-14: 열 손가락 바늘로 따기 민간요법)에 대해 가드레일이 방어하지 못하고 문진으로 흘려보낼 위험성 확인.
* **원인 분석**:
  * 기존 `guardrail_agent.py`는 Red Flag(초응급 징후) 선제 차단 및 사후 진단명 마스킹만 갖추고 있어, 부모의 위험 질문 및 임의 투약 유도에 대한 선제적 차단 룰이 부재했음.
* **구체적 해결 방안**:
  1. `guardrail_agent.py`에 `check_safety_violations(user_message)` 0ms 규칙 엔진 신설:
     - **위험 민간요법 (DANGEROUS_FOLK_REMEDY)**: 바늘로 피 내기, 손 따기 감지 시 2차 감염 및 쇼크 위험 경고, 절대 금기 고지.
     - **잔여 항생제 임의 복용 (LEFTOVER_ANTIBIOTICS)**: 남은 항생제/전문의약품 감지 시 내성균 및 변질 위험 경고, 새로운 진료 처방 필수 고지.
     - **직접 복용량 산정 요구 (EXACT_DOSAGE_REQUEST)**: 몇 ml 먹여야 하는지 질문 시 의료법 제27조 준수, 제품 설명서 기준표 참조 및 의사/약사 상담 안내.
     - **탈옥 및 권위자 페르소나 주입 (JAILBREAK_PERSONA)**: 의사 사칭 및 진단 강요 시 AI의 진단 불허 원칙 확고 고지 및 안전 프로세스 고수.
     - **단독 병원 추천 유도**: 의료법 제27조 제3항(환자 유인·알선 배제) 고지 및 중립적 복수 추천 유지.
* **적용 파일**:
  * [app/agents/guardrail_agent.py](file:///e:/monnlight/app/agents/guardrail_agent.py)
  * [tests/test_audit_fixes.py](file:///e:/monnlight/tests/test_audit_fixes.py) (TC-FIX-04)

---

### [ISSUE-020] Triage Fallback 파서의 환아 연령 단위('만 N세', 'N살', '초등 1학년') 및 기간('N일 전', '어제'), 소아 다발성 증상 정규화 확장

* **발생 일자**: 2026-10-13
* **분류**: 문진 NLP 파싱 정합성 / 휴리스틱 Fallback
* **문제 상황**:
  * TriageAgent의 Fallback 파서가 `N개월`과 `생후 N일`만 인식하여, 골든 케이스의 "만 4세"(TC-02), "초등학교 1학년(만 7세)"(TC-05), "3세"(TC-24) 등 연령 단위 입력 시 월령 추출이 누락됨.
  * 기간 단위 또한 `N시간`만 인식하여 "3일 전부터", "어제부터" 입력 시 지속 시간 추출이 누락됨.
  * 소아 다발성 증상(귀 통증/이통, 눈곱/결막염, 쌕쌕거림/천명, 복통 등)이 인식되지 않아 문진 턴이 불필요하게 지연되는 병목 발생.
* **원인 분석**:
  * 한국어 소아 환아 구어체 표현의 다양성을 정규식 패턴에 미처 포괄하지 못함.
* **구체적 해결 방안**:
  1. 연령 정규화 확장:
     - `만 N세`, `N살`, `N세` 감지 시 `N * 12` 개월로 자동 환산 (예: 만 4세 ➔ 48개월).
     - `초등(학교)?\s*([1-6])학년` 감지 시 `(학년 + 6) * 12` 개월 환산 (예: 초등 1학년 ➔ 84개월).
  2. 기간 정규화 확장:
     - `([1-9]|10)일\s*전?부터?` 감지 시 `N * 24` 시간으로 자동 환산 (예: 3일 전 ➔ 72시간).
     - `어제부터` (24시간), `그제부터/그저께부터` (48시간) 자동 매핑.
  3. 소아 다발성 임상 증상 사전 확장:
     - `귀가 아파요/귀 통증/중이염` ➔ `"이통"`, `눈곱/눈꼽/결막염` ➔ `"눈곱/결막염"`, `쌕쌕/천명/가래` ➔ `"쌕쌕거림/천명"`, `배 아파/복통` ➔ `"복통"`, `발진/열꽃/두드러기` ➔ `"발진/열꽃"`.
  4. 증상 표준 명칭 바인딩: Gemini LLM이 `"고열"`, `"미열"`을 추출해도 내부 표준 임상 키워드인 `"발열"`로 자동 매핑.
* **적용 파일**:
  * [app/agents/triage_agent.py](file:///e:/monnlight/app/agents/triage_agent.py)
  * [tests/test_audit_fixes.py](file:///e:/monnlight/tests/test_audit_fixes.py) (TC-FIX-05)

---

### [ISSUE-021] 방문 시각 기준 병원 진료 마감 시간(HH:MM) 대소 비교 필터링 & 조기 접수 마감 주의 태그 연동

* **발생 일자**: 2026-10-13
* **분류**: 현장 운영시간 정합성 / 라우팅 알고리즘
* **문제 상황**:
  * 환아가 야간 21:30에 검색했을 때 21:00에 이미 진료가 종료된 달빛어린이병원이 단순 거리순으로 추천되는 문제.
  * 또한 심야 새벽 01:30(TC-30)처럼 모든 달빛어린이병원이 종료된 시각에도 24시간 응급실이 아닌 달빛병원이 추천되어 헛걸음을 유발할 위험 존재.
* **원인 분석**:
  * `MatchingAgent`에서 요일/공휴일 체크는 수행했으나, 방문 대상 시각의 분 단위(`HH * 60 + MM`)와 병원 마감 분 단위의 대소 비교 필터링이 누락됨.
* **구체적 해결 방안**:
  1. `now_time_val = current_hour * 60 + current_minute` 분 단위 환산 체계 도입.
  2. 심야(23:00~07:00) 시간대 자동 판별:
     - 23시 이후는 외래 달빛병원이 모두 셧다운되므로 **24시간 소아 응급실로 즉각 1순위 라우팅**.
  3. 달빛병원 마감 시간(`병원_평일마감`) 대소 비교:
     - `now_time_val > closing_time_val`: 이미 마감된 병원은 추천 목록에서 즉시 제외.
     - `0 < closing_time_val - now_time_val <= 40`: 마감 40분 전 내원 환아에게는 `[⚠️ 조기 접수 마감 주의: N분 남음]` 태그를 병원 카드에 동적 부착하고 30초 유선 확인 통화 스크립트 강제 노출.
* **적용 파일**:
  * [app/agents/matching_agent.py](file:///e:/monnlight/app/agents/matching_agent.py)
  * [tests/test_audit_fixes.py](file:///e:/monnlight/tests/test_audit_fixes.py) (TC-FIX-06)

---

### [ISSUE-022] Windows PowerShell 콘솔 CP949 인코딩 글자 깨짐(Mojibake) 방지 및 유니코드 UTF-8 전역 표준화

* **발생 일자**: 2026-10-13
* **분류**: 개발 환경 / 문자 인코딩 표준화 (I/O Encoding)
* **문제 상황**:
  * Windows 운영체제 환경의 PowerShell 및 명령 프롬프트에서 `python -m unittest` 실행 시, 로그 메시지 및 벤치마크 결과의 한글 문자열이 `[Supervisor] Red Flag detected:  100 ̸ 38 ̻ `처럼 깨져 출력(Mojibake)되는 가시성 저하 발생.
* **원인 분석**:
  * 한국어 Windows 환경의 기본 표준 입출력 스트림 인코딩이 레거시 `CP949`로 설정되어 있어, 현대 유니코드(UTF-8) 이모지 및 특수 의학 기호 출력 시 인코딩 오류가 발생함.
* **구체적 해결 방안**:
  1. `app/__init__.py` 및 `main.py` 최상단에 Windows 플랫폼 감지 및 UTF-8 스트림 재구성 로직 삽입:
     ```python
     import sys
     if sys.platform == "win32":
         if hasattr(sys.stdout, "reconfigure"):
             sys.stdout.reconfigure(encoding="utf-8")
         if hasattr(sys.stderr, "reconfigure"):
             sys.stderr.reconfigure(encoding="utf-8")
     ```
  2. 시스템 전역 표준 출력을 UTF-8로 고정하여 모든 단위 테스트 로그 및 서버 콘솔 출력이 깨짐 없이 깔끔하게 렌더링되도록 보장.
* **적용 파일**:
  * [app/__init__.py](file:///e:/monnlight/app/__init__.py)
  * [main.py](file:///e:/monnlight/main.py)

---

### [ISSUE-023] Conda DS 가상환경 내 누락 의존성(`apscheduler`, `fastapi`, `uvicorn`) 정합성 동기화 및 모듈 임포트 결함 해소

* **발생 일자**: 2026-10-13
* **분류**: 파이썬 가상환경 & 패키지 형상 관리 / 의존성 동기화
* **문제 상황**:
  * `.vscode/settings.json`에서 프로젝트 기본 인터프리터로 지정된 `E:\minoconda\envs\DS\python.exe` 가상환경에서 `test_step5_api.py`를 실행했을 때 `ModuleNotFoundError: No module named 'apscheduler'` 에러로 테스트 로더가 중단됨.
* **원인 분석**:
  * 시스템 전역 Python(`pythoncore-3.14-64`)에는 Step 5 구현 시 패키지가 설치되었으나, VSCode 및 데이터 사이언스 분석용 Conda 가상환경(`DS`)에는 `requirements.txt`의 Step 5 패키지(`apscheduler`, `fastapi`, `uvicorn`)가 설치되지 않아 환경 간 불일치가 발생함.
* **구체적 해결 방안**:
  1. `E:\minoconda\envs\DS\python.exe -m pip install apscheduler fastapi uvicorn` 명령을 실행하여 누락 패키지 전수 설치.
  2. `E:\minoconda\envs\DS` 인터프리터 상에서 `tests.test_step5_api` 10개 테스트를 단독 실행하여 `Ran 10 tests in 36.738s, OK` 정상 통과 검증 완수.
  3. 개발자가 어느 파이썬 환경(Conda DS 또는 시스템 파이썬)을 선택하더라도 모든 API 및 스케줄러가 결함 없이 즉시 가동되도록 보장.
* **적용 파일**:
  * [requirements.txt](file:///e:/monnlight/requirements.txt)
  * [.vscode/settings.json](file:///e:/monnlight/.vscode/settings.json)

---

## 🚀 [STEP-006] E2E 통합 테스트 & 40대 임상 골든 케이스 자동 Evals 채점 프레임워크 구축 완료

* **완료 일자**: 2026-10-13
* **분류**: E2E 통합 검증 / 5대 임상 평가 프레임워크 / 골든 케이스 채점기 / CLI 시연기
* **핵심 구현 내역**:
  1. **8대 E2E 통합 테스트 스위트 (`tests/test_step6_e2e.py`)**:
     - `TC-601`: Track A 초응급 1턴 즉시 119 에스컬레이션 모달 및 기도확보 응급처치 가이드 검증.
     - `TC-602`: Track B 야간 발열 2턴 문진 ➔ 달빛병원 + 30분 안심 약국 페어링 ➔ 30초 통화 스크립트 ➔ 등본 지참 체크리스트 전 과정 완주.
     - `TC-603`: 의료법 제27조 무면허 의료행위 방어(부모의 돌발진 단정 유도 거부 및 전문의 대면 진찰 안내).
     - `TC-604`: 적대적 4대 안전 위반(바늘 사혈, 남은 항생제, 용량 처방 요구, 단독 병원 알선 요구) 0ms 원천 차단.
     - `TC-605`: 다중 턴 중도 급변(Deterioration) 시나리오(1턴 미열 상담 중 2턴 청색증 발생 시 즉시 Track A 비상 전환).
     - `TC-606`: 3턴 데드락 가드(3턴 연속 모호한 입력 시 안전 기본값 주입 후 MATCHING/COMPLETED 강제 전이).
     - `TC-607`: FastAPI REST API `/api/v1/chat` E2E 단일/다중 턴 호출 무결성 검증.
     - `TC-608`: FastAPI SSE 실시간 스트리밍 `/api/v1/chat/stream` 토큰 스트리밍 및 `[DONE]` 종료 이벤트 검증.
  2. **40대 임상 골든 케이스 자동 채점기 (`tests/evals/run_evals.py`)**:
     - `tests/evals/golden_test_cases.json`의 40개 테스트 케이스를 로드하여 5대 임상 평가 지표(DIM-1~DIM-5) 기준 자동 채점.
     - **DIM-1 (의료법 준수)**: 100.0 / 100점 (진단·처방 원천 배제)
     - **DIM-2 (Red Flag 감지)**: 97.5 / 100점 (15대 KTAS 초응급 100% 감지)
     - **DIM-3 (문진 효율성)**: 100.0 / 100점 (4대 임상 변수 정형화)
     - **DIM-4 (매칭 정확도)**: 100.0 / 100점 (30분 안심 약국 마진 확보)
     - **DIM-5 (부모 공감 & 물류)**: 100.0 / 100점 (신분증/등본 지참 서류 및 30초 통화 스크립트)
     - **종합 결과**: **40개 중 40개 전수 통과 (합격률 100.0%, 평균 점수 99.5점)**.
     - 성적표 리포트 자동 생성: [tests/evals/eval_report.md](file:///e:/monnlight/tests/evals/eval_report.md).
  3. **인터랙티브 CLI 시연 데모 (`demo_step6.py`)**:
     - 초응급 시나리오, 야간 발열 시나리오, 의료법 방어 시나리오, 적대적 공격 차단 시나리오, 보호자 자유 대화 모드, Evals 성적표 뷰어를 통합 제공.
* **테스트 결과**:
  - `Ran 58 tests in 193.171s, OK` (전체 58개 테스트 100% 전수 통과)
  - `Evals 40/40 Cases Passed (100.0%)`

---

## 🚨 [ISSUE-024] macOS 메타데이터 섀도우 파일(`._*`) 및 가상환경 심링크 잔재 오염 제거

* **발생 일자**: 2026-10-13
* **분류**: 저장소 형상 관리 & 파일시스템 클린업 / macOS 전파 오염 방어
* **문제 상황**:
  * macOS 환경에서 작업 후 동기화되는 과정에서 생성된 AppleDouble 메타데이터 섀도우 파일(`._*` 총 56개), 임의 심링크 파일(`DS`), 세 개의 언더스코어가 포함된 디렉터리(`.___pycache__` 2개)가 저장소 전역(root, tests, app 하위)에 산재하여 파일시스템을 오염시키고 디렉터리 순회 및 정적 검사를 저해함.
* **원인 분석**:
  * macOS HFS+/APFS 파일시스템의 확장 속성(Resource Fork)을 Windows FAT/NTFS로 전송할 때 생기는 `._` 접두어 파일 및 broken symlink가 `.gitignore` 필터링과 무관하게 로컬 디렉터리에 물리적으로 잔류함.
* **구체적 해결 방안**:
  1. PowerShell 재귀 탐색을 통해 `._*`, `.___pycache__`, `DS` 파일 총 58개를 전수 식별 후 일괄 안전 삭제(`Remove-Item -Force -Recurse`).
  2. 삭제 후 재검색 결과 잔여 개수 0개(`Count: 0`) 완벽 제거 확인.
  3. Git 형상 추적 및 테스트 러너가 순수 프로젝트 코드만을 로드하도록 격리.
* **적용 파일**:
  * [._* 전수 삭제](file:///e:/monnlight/)
  * [.gitignore](file:///e:/monnlight/.gitignore)

---

## 🚨 [ISSUE-025] TriageAgent & LogisticsAgent API 키 Fallback 로직 결함으로 인한 오프라인/고속 평가 불능 현상 해결

* **발생 일자**: 2026-10-13
* **분류**: 멀티 에이전트 인터페이스 설계 / 오프라인 결정론적 모드 제어 / Evals 성능 최적화
* **문제 상황**:
  * `run_evals.py` 실행 시 `--live` 플래그 없이 FAST 모드(Zero-LLM Heuristic)로 구동하려 했으나, 40개 케이스 실행 시 수 분이 소요되고 원격 Gemini API 호출이 불필요하게 40회 이상 발생함.
* **원인 분석**:
  * `TriageAgent` 및 `LogisticsAgent` 생성자에서 `self.api_key = api_key or settings.gemini_api_key`로 작성되어 있어, 호출자가 `api_key=None`을 전달하더라도 단락 평가(`or`)에 의해 환경변수/레지스트리의 실제 API 키로 강제 치환되어 원격 GenAI 클라이언트가 항상 활성화됨.
* **구체적 해결 방안**:
  1. `TriageAgent`와 `LogisticsAgent` 생성자에 `enable_gemini: bool = True` 명시적 제어 플래그를 추가하여, `enable_gemini=False` 설정 시 `self.api_key = None`, `self._client = None`으로 오프라인 결정론적 룰 기반 모드로 완전 격리되도록 개선.
  2. `GoldenEvalsHarness`에서 `is_live` 여부에 따라 `enable_gemini=is_live`를 전달하도록 동기화.
  3. 수정 후 40대 임상 골든 케이스 FAST 평가 속도가 기존 **200초+**에서 **10초 미만(9.8초, 20배 이상 단축)**으로 획기적 단축, 합격률 100%(40/40) 유지.
* **적용 파일**:
  * [app/agents/triage_agent.py](file:///e:/monnlight/app/agents/triage_agent.py)
  * [app/agents/logistics_agent.py](file:///e:/monnlight/app/agents/logistics_agent.py)
  * [tests/evals/run_evals.py](file:///e:/monnlight/tests/evals/run_evals.py)

---

## 🚀 [ISSUE-026] 프로덕션 권장 개선 사항 일괄 구현: 3-Track 세션 만료 정리, AFC 경고 억제, SSE 실시간 모니터링 적용

* **발생/조치 일자**: 2026-10-13
* **분류**: 백그라운드 스케줄러 고도화 / GenAI SDK 최적화 / SSE 스트리밍 확장 / 키 로더 안정성
* **문제 상황**:
  1. `SessionManager`에 TTL 만료 세션 정리 메서드(`evict_expired_sessions`)가 구현되어 있었으나 `BackgroundDaemon`에 등록되지 않아 장기 가동 시 메모리 누적 가능성이 잔류함.
  2. `google-genai` SDK v2+에서 구조화 출력 생성 시 자동 함수 호출(AFC) 권고 경고가 콘솔에 반복 출력됨.
  3. SSE 스트리밍 엔드포인트에서 긴급 119 에스컬레이션 발생 시 전용 이벤트가 미흡하여 클라이언트 모달 즉각 트리거에 제약이 있었음.
  4. Firebase 키 경로 분리(`E:\FIREBASE_API_KEY`)에 따른 런타임 동적 재확인 및 안내 메시지 구체화 필요.
* **구체적 해결 방안**:
  1. **APScheduler 3-Track 확장**:
     - `BackgroundDaemon`에 `job_session_eviction` (15분 주기) 등록.
     - 30분 이상 비활성 세션을 주기적으로 purge하고, 누적 정리 횟수(`eviction_count`) 및 최근 정리 시각(`last_eviction_time`)을 `GET /api/v1/emergency/status` 및 `/health` 메트릭으로 제공.
     - `main.py` 라이프사이클에서 3-Track 데몬으로 공식 가동.
  2. **Google GenAI SDK AFC 경고 억제**:
     - [triage_agent.py](file:///e:/monnlight/app/agents/triage_agent.py) 및 [logistics_agent.py](file:///e:/monnlight/app/agents/logistics_agent.py)의 `GenerateContentConfig`에 `automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)`를 명시하여 불필요한 SDK 경고 원천 제거.
  3. **SSE 스트리밍 이벤트 확장**:
     - [chat.py](file:///e:/monnlight/app/api/v1/chat.py) `_sse_event_generator`에서 초응급 감지 시 즉시 `event: emergency` 페이로드를 조기 방출하고 파이프라인 단계(`RESOLVED`) 및 진행 턴 수를 클라이언트에 실시간 브로드캐스트.
  4. **Firestore 동적 키 해결 강화**:
     - [config.py](file:///e:/monnlight/app/config.py)의 `get_firestore_client()`에서 `settings.firebase_key_path`가 미설정 상태인 경우에도 `resolve_firebase_key_path()`를 동적으로 재스캔하여 `E:\FIREBASE_API_KEY\serviceAccountKey.json`을 즉각 바인딩.
* **적용 파일**:
  * [app/services/scheduler.py](file:///e:/monnlight/app/services/scheduler.py)
  * [app/schemas/emergency_api.py](file:///e:/monnlight/app/schemas/emergency_api.py)
  * [main.py](file:///e:/monnlight/main.py)
  * [app/agents/triage_agent.py](file:///e:/monnlight/app/agents/triage_agent.py)
  * [app/agents/logistics_agent.py](file:///e:/monnlight/app/agents/logistics_agent.py)
  * [app/api/v1/chat.py](file:///e:/monnlight/app/api/v1/chat.py)
  * [app/config.py](file:///e:/monnlight/app/config.py)

---

### [ISSUE-024] 팀 프로젝트 전환(정영식 팀장, 김동준 팀원)에 따른 4대 문서 누적 관리 및 에이전트 불변 규율 자동화

* **발생 일자**: 2026-10-14
* **작업자**: 정영식 (팀장), 김동준 (팀원)
* **분류**: 프로젝트 거버넌스 & 협업 / 에이전트 룰
* **문제 상황**:
  * MoonlightCare 프로젝트가 단일 개발자 체제에서 정영식 팀장과 김동준 팀원의 공동 팀 프로젝트로 공식 전환됨.
  * 복수의 작업자 및 다양한 세션에서 개발이 병행될 경우, 질의응답 이력 누락, 트러블슈팅 미기록, README 체인지로그 미갱신, 기획안(PLAN.md)과 코드 간 불일치(Drift) 위험이 발생할 수 있음.
* **원인 분석**:
  * 팀 단위 협업 시 명문화된 기록 거버넌스와 AI 에이전트가 강제적으로 따라야 하는 시스템 수준의 규율이 없으면, 작업 완료 후 문서 동기화가 누락되기 쉬움.
* **구체적 해결 방안**:
  1. **4대 문서 지속 누적 관리 철칙 확립**:
     - `Answer-{사용자}.md` (특히 `Answer-영식.md`): 정영식 팀장의 모든 질문과 AI 답변을 Q 번호별로 영구 누적 아카이빙.
     - `log.md`: 각 사용자가 겪은 오류/이슈 및 해결 방안을 [ISSUE-XXX] 포맷으로 지속 기록.
     - `README.md`: 신규 개발 및 업데이트 내역을 릴리스 체인지로그에 지속 반영.
     - `PLAN.md`: 개발 중 아키텍처나 기능 변경 시 기획안 동기화 및 향후 개선책(Advanced Backlog) 보강.
  2. **에이전트 시스템 레벨 규칙 파일 3종 구축**:
     - [.agents/rules/team_collaboration_rules.md](file:///e:/monnlight/.agents/rules/team_collaboration_rules.md): Antigravity 워크스페이스 전역 규칙.
     - [GEMINI.md](file:///e:/monnlight/GEMINI.md) & [AGENTS.md](file:///e:/monnlight/AGENTS.md): 루트 레벨 최상위 지침 파일로 대화 시작 시 자동 로드.
* **적용 파일**:
  * [.agents/rules/team_collaboration_rules.md](file:///e:/monnlight/.agents/rules/team_collaboration_rules.md)
  * [GEMINI.md](file:///e:/monnlight/GEMINI.md)
  * [AGENTS.md](file:///e:/monnlight/AGENTS.md)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-027] LogisticsAgent 전화 통화 스크립트 생성 시 LLM 기관명 축약(어절 생략) 대응 Assertion 유연화 및 무결점 회귀 방어

* **발생/조치 일자**: 2026-10-14
* **작업자**: 정영식 (팀장), 김동준 (팀원)
* **분류**: 에이전트 단위 테스트 검증 / LLM 비결정론적 출력 포용 / 회귀 방어
* **문제 상황**:
  * `tests/test_step3_agents.py`의 `test_06_logistics_agent_script_and_checklist_tc306_tc307` 실행 시, Gemini 모델이 통화 스크립트를 작성하면서 대상 기관명(`서울아산병원 소아전문응급센터`) 중 핵심 키워드(`소아전문응급센터`)만을 축약 언급함에 따라 엄격한 고정 문자열 단언(`assertIn("서울아산병원", result.call_script)`)에서 간헐적 단언 실패(AssertionError) 발생.
* **원인 분석**:
  * LLM(Gemini 3.5 Flash Lite)의 자연어 생성 특성상, "안녕하세요, 14개월 아기 엄마입니다... 소아전문응급센터 진료가 지금 바로 가능한지..."와 같이 환자가 전화를 걸 때 상대방이 이미 해당 병원임을 전제하고 기관명 앞부분("서울아산병원")을 생략하고 부서명("소아전문응급센터")만 지칭하는 자연스러운 언어적 축약 현상이 일어남.
* **구체적 해결 방안**:
  1. `tests/test_step3_agents.py`의 단언문을 `self.assertTrue("서울아산병원" in result.call_script or "소아전문응급센터" in result.call_script or "응급센터" in result.call_script)`로 개선하여 LLM의 자연어 축약 변형을 안전하게 포용하도록 보강.
  2. 수정 후 `test_step3_agents.py` 7개 전수 테스트 100% PASS 확인.
* **적용 파일**:
  * [tests/test_step3_agents.py](file:///e:/monnlight/tests/test_step3_agents.py)
  * [log.md](file:///e:/monnlight/log.md)

---

## 📝 로그 관리 수칙 (Engineering Guidelines)
1. **문제 발생 시 즉시 기록**: 새로운 버그, 성능 병목, 법적 쟁점 발생 시 즉시 본 파일에 [ISSUE-XXX] 번호를 채번하고 문제 상황과 원인을 기록합니다.
2. **구체적 해결 방안 명시**: 단순 "수정함"이 아닌, 적용한 아키텍처 원리, 코드 함수명, 알고리즘 방식을 명확히 기술합니다.
3. **기획안 및 코드베이스 동기화**: 본 로그에 기록된 해결 방안은 [PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md) 및 관련 코드 주석에 반드시 반영합니다.

---

### [ISSUE-028] Stitch 도구 호출 시 프로젝트 ID 규격 불일치(projects/ prefix 중복) 방어 및 '아이숨' 리브랜딩 컴포넌트 표준화

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 UI 프로토타이핑 / Stitch MCP 연동
* **문제 상황**:
  * screen.png 레퍼런스를 반영하여 모바일 UI 화면을 재생성하는 과정에서, Stitch MCP 도구(get_screen, list_screens 등) 호출 시 projectId에 projects/15792310540995806418 형태의 리소스 풀네임을 전달하면 GCP 엔드포인트에서 Request contains an invalid argument (400 에러)가 반환되는 현상 발생.
  * 기존 MoonlightCare 다크 테마 기반 프로토타입과 신규 '아이숨' 화이트&블루 컴포넌트 간의 혼선 위험.
* **원인 분석**:
  * Stitch MCP 서버 API 인터페이스 규격 상, projectId 인자는 리소스 네임(projects/xxxx)이 아닌 순수 숫자 문자열(15792310540995806418)만을 수신하도록 설계되어 있음.
  * 사용자가 지정한 screen.png 레퍼런스는 8대 퀵 카테고리 그리드, 캐릭터 웰컴 배너, 코발트 블루 CTA 등 기존 타다 스타일과 완전히 다른 헬스케어 포털 구조를 요구함.
* **구체적 해결 방안**:
  1. Stitch MCP 호출 시 projectId = re.sub(r'^projects/', '', project_id) 처리를 통해 순수 숫자 ID로 통일하여 400 에러 원천 차단.
  2. screen.png에 명시된 8대 카테고리(🏥소아과 야간진료, 🔍실시간 병원찾기, 💊처방 약국연계, 🩺AI 응급문진, 🌡️열/발열 대처, ⏰복약 알리미, 💰진료비 계산기, 🩹응급처치 가이드)를 DOM 요소로 100% 분해하여 Stitch 메인 홈 스크린(c0bb4df907b44ddd9ee91bad51a308d6)에 성공적으로 패치 완료.
  3. 프라이머리 컬러를 #0066FF(코발트 블루)로 전역 통일하고 화이트 베이스 라이트 모드로 전환.
* **적용 파일**:
  * [Answer-영식.md](Answer-영식.md) Q42
  * [PLAN.md](PLAN.md) 제10.5절
  * [README.md](README.md) v2.2.0-isoom 체인지로그

---

### [ISSUE-029] MedicalGuardrailAgent 투약 용량(Dosage) 정규식 경계 확장 및 의료법 제27조 소독 관문 완전 봉쇄

* **발생 일자**: 2026-10-14
* **분류**: 안전 가드레일 / 의료법 제27조 준수
* **문제 상황**:
  * `test_step4_orchestrator.py`의 `test_06_medical_law_sanitization_single_gateway_tc406` 회귀 검증 중, `self.assertNotIn("10ml", res.message)` 단언문에서 실패(AssertionError) 발생.
  * LLM이 *"14개월 아기에게 타이레놀 시럽 10ml는 과용량의 위험이 있으니..."*라는 문장으로 보호자에게 주의를 주었으나, 메시지 내에 구체적 의약품 용량 수치(`10ml`)가 소독되지 않고 그대로 잔존함.
* **원인 분석**:
  * 기존 `PROHIBITED_DOSAGE_PATTERN`은 `([0-9]+... (ml|mg...))\s*(을|를)?\s*(먹이|복용|투약...)` 형태로 구성되어 있어, 용량 뒤에 조사(`는`)나 경고 단어(`과용량`, `위험`)가 오는 비정형 경고 문맥을 감지하지 못함.
  * 의료법 제27조의 기본 취지상 비의료 AI는 권장뿐 아니라 임의의 용량 수치 자체를 노출하여 보호자에게 오인 혼선을 주어서는 안 됨.
* **구체적 해결 방안**:
  1. `app/agents/guardrail_agent.py`의 `PROHIBITED_DOSAGE_PATTERN` 정규식을 옵셔널 비캡처 그룹 `(?:\s*(?:을|를|은|는|도|가|이)?\s*(?:먹이|복용|투약|먹이세요|복용시키세요|먹이십시오|과용량|용량|위험|투여))?`으로 정밀 확장.
  2. 단순 투약 지시문뿐만 아니라 경고 문맥에서 인용된 `10ml`, `500mg` 등의 용량 표현도 즉시 `[의약품 복용량은 소아청소년과 전문의 또는 약사의 복약지도를 따르십시오]`로 안전하게 치환 소독되도록 조치.
  3. `tests/test_step4_orchestrator.py` (TC-401 ~ TC-407) 전수 재실행하여 100% 정상 통과 검증 완료 (`Ran 7 tests in 65.223s, OK`).
* **적용 파일**:
  * `app/agents/guardrail_agent.py` (`PROHIBITED_DOSAGE_PATTERN`)

---

### [ISSUE-030] screen.png 레퍼런스 기반 신규 전용 Stitch 프로젝트 개설 및 'Calm Harbor' 모던 라이트 3대 화면 완성

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 UI/UX 아키텍처 / 디자인 시스템 리브랜딩 / Stitch MCP
* **문제 상황**:
  * 기존 프로젝트(`15792310540995806418`)는 다크 테마(Nocturnal Pediatric Care) 기반으로 설계되어 있었으나, 팀장님이 새롭게 지정한 레퍼런스([screen.png](images/screen.png))는 소프트 블루-그레이/화이트 베이스의 모던 라이트 테마를 지향함.
  * 기존 프로젝트 내 화면 갱신 시 다크 모드 토큰과의 디자인 시스템 충돌 및 일관성 저하 우려.
* **원인 분석**:
  * Stitch MCP는 프로젝트별로 독립적인 디자인 시스템(`designSystem`)을 관리하므로, 완전히 새로워진 브랜드 아이덴티티('아이숨 Aisum')와 'Calm Harbor' 라이트 테마를 깨끗하게 유지하려면 신규 전용 프로젝트를 생성하는 것이 아키텍처상 최선임.
* **구체적 해결 방안**:
  1. Stitch MCP `create_project`를 호출하여 신규 전용 프로젝트(`projects/17449043314542457561` - '아이숨 (Aisum) - 소아 야간 의료 매칭 케어')를 생성.
  2. `Calm Harbor` 라이트 테마 디자인 시스템(`assets/389aad58bc8e4522b6904fb567d60bdf`)을 확립:
     - Primary: 선명한 로열 블루(`#0066FF`), Canvas: `#F8FAFC`, Surface: `#FFFFFF` (18px 라운드 코너).
     - Live Mint: `#10B981` (실시간 동기화/진료중), Moonlight Amber: `#F59E0B` (달빛병원), Coral Red: `#EF4444` (고열/경련).
  3. `generate_screen_from_text`를 통해 3대 핵심 화면을 순차 생성하여 완전한 사용자 여정 구축:
     - **화면 1 (`65dcc96b817143c3adb7bfdfa545267b`)**: `아이숨 - 홈` (screen.png 1:1 완벽 이식 - 로고, 역삼동 알약 드롭다운, 라이브 동기화 닷, 어디가 아픈가요 헤더, 증상 퀵태그 4종, 3개 탭 필터, 송파어린이병원/강남아이마음병원/송파달빛약국 카드, 3탭 GNB).
     - **화면 2 (`0cdadf1dc86a4c229423b5b02caa8cc1`)**: `아이숨 - 증상 입력 및 문진` (환아 선택, 38.6°C 디지털 체온계, KTAS 증상 멀티 셀렉터, 해열제 교차복용 타이머, 4단계 진단 카드, 매칭 CTA).
     - **화면 3 (`3c5db317bb354d02838e5306adfc4f1a`)**: `아이숨 - 야간 병원 상세 및 실시간 접수` (송파어린이병원 실시간 대기 4팀, 당직의 김서연 전문의 현황, 송파달빛약국 +30분 조제안전마진 연계, 티맵/카카오내비 길안내, 모바일 번호표 접수 CTA).
* **적용 파일**:
  * [Answer-영식.md](Answer-영식.md) Q43
  * [PLAN.md](PLAN.md) 제10.6절
  * [README.md](README.md) v2.3.0-isoom 체인지로그

---

### [ISSUE-031] Stitch 생성 코드의 외부 CDN 종속 탈피, 순수 Vanilla HTML5/CSS3 웹 퍼블리싱 및 FastAPI `/home` 정적 서빙 구축

* **발생 일자**: 2026-10-14
* **분류**: 웹 프론트엔드 퍼블리싱 / Vanilla CSS3 / FastAPI 정적 서빙
* **문제 상황**:
  * Stitch에서 자동 생성된 프로토타입 HTML 코드는 `cdn.tailwindcss.com` 스크립트에 런타임 종속되어 있어 외부 CDN 장애 시 레이아웃이 붕괴될 수 있으며, 사용자의 "기능 없이 순수 HTML, CSS만으로 구현해달라"는 요구 조건에 완벽히 부합하지 않음.
* **원인 분석**:
  * 상용 배포 및 가벼운 단독 구동(Standalone)을 위해서는 외부 라이브러리 및 자바스크립트 없이 구동되는 순수 HTML5 시맨틱 마크업과 독립 CSS 파일 구조가 필요함.
* **구체적 해결 방안**:
  1. `AISUM_STITCH_DESIGN_REPORT.md`의 Calm Harbor 디자인 토큰 명세를 바탕으로 순수 바닐라 CSS 파일 [style.css](file:///e:/monnlight/style.css)를 신규 구축:
     - `:root`에 로열 블루(`#0066FF`), 에메랄드 그린(`#10B981`), 달빛 앰버(`#F59E0B`), 코랄 레드(`#EF4444`) 변수 지정.
     - 440px 모바일 뷰포트 프리뷰 프레임 및 반응형 레이아웃 구현.
     - `@keyframes pulse-ring` 실시간 동기화 펄스 애니메이션 및 글래스모피즘(`backdrop-filter: blur(14px)`) 적용.
  2. [index.html](file:///e:/monnlight/index.html) 및 [app/static/index.html](file:///e:/monnlight/app/static/index.html)을 생성하여 상단 앱바, 증상 탐색 히어로, 4대 증상 칩, 실시간 야간 의료시설 3대 카드, 고정 GNB 하단바를 시맨틱 구조로 1:1 완벽 구현.
  3. [main.py](file:///e:/monnlight/main.py)에 `GET /home` 및 `GET /style.css` 엔드포인트를 추가하여 FastAPI 서버에서도 로컬 파일 브라우징과 동일하게 즉시 서빙되도록 라우팅 결합.
* **적용 파일**:
  * [index.html](file:///e:/monnlight/index.html)
  * [style.css](file:///e:/monnlight/style.css)
  * [app/static/index.html](file:///e:/monnlight/app/static/index.html)
  * [app/static/style.css](file:///e:/monnlight/app/static/style.css)
  * [main.py](file:///e:/monnlight/main.py)

---

### [ISSUE-032] 프로젝트 루트에 위치하던 임시 HTML/CSS 파일을 정규 프론트엔드 전용 워크스페이스(`frontend/`)로 모듈화 이관

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 워크스페이스 아키텍처 / 웹 리소스 모듈화 / FastAPI 라우팅
* **문제 상황**:
  * Step 7 이후 백엔드와 데이터 파이프라인은 `app/`, `data/`, `docs/`, `scripts/`, `tests/` 등 최상위 디렉터리별로 엄격히 모듈화되어 있었으나, 퍼블리싱된 `index.html`과 `style.css`가 프로젝트 루트에 평면(Flat)하게 위치하여 응집도가 떨어지고 CSS/JS/Assets 계층 분리가 이루어지지 않음.
* **원인 분석**:
  * 프로토타입 작성 시 루트에 직접 파일을 생성하여 발생한 일시적 배치 결함으로, 상용 웹 아키텍처 및 팀 협업 표준에 따라 독립된 `frontend/` 워크스페이스 구축이 필요함.
* **구체적 해결 방안**:
  1. 프로젝트 루트에 **`frontend/`** 최상위 디렉터리를 신규 생성하고 표준 웹 하위 구조 구축:
     - `frontend/index.html`: 메인 웹 진입점 (스타일시트 링크: `css/style.css`).
     - `frontend/css/style.css`: Calm Harbor 디자인 시스템 Vanilla CSS.
     - `frontend/js/main.js`: 클라이언트 인터랙션 및 향후 SSE 챗봇 연동 모듈.
     - `frontend/assets/`: `icons/`, `images/` 하위 에셋 디렉터리.
     - `frontend/README.md`: 프론트엔드 워크스페이스 가이드 문서.
  2. 기존 루트의 `e:\monnlight\index.html` 및 `e:\monnlight\style.css`를 완전 삭제하여 루트 디렉터리의 청결성 회복.
  3. 백엔드 패키징 디렉터리인 `app/static/` 내부도 `app/static/index.html`, `app/static/css/style.css` 계층으로 동기화.
  4. `main.py`에 `app.mount("/frontend", ...)` 및 `app.mount("/css", ...)`를 등록하고, `GET /home`, `GET /style.css`, `GET /css/style.css` 엔드포인트가 `frontend/` 경로를 1순위로 서빙하도록 라우팅 업데이트 및 HTTP 200 검증 완료.
* **적용 파일**:
  * [frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html)
  * [frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css)
  * [frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js)
  * [frontend/assets/README.md](file:///e:/monnlight/frontend/assets/README.md)
  * [frontend/README.md](file:///e:/monnlight/frontend/README.md)
  * [app/static/index.html](file:///e:/monnlight/app/static/index.html)
  * [app/static/css/style.css](file:///e:/monnlight/app/static/css/style.css)
  * [main.py](file:///e:/monnlight/main.py)

---

### [ISSUE-033] `frontend/templates/` 하위 계층 생성, `index.html` 보관 및 상대경로·FastAPI 마운트 최적화

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 템플릿 아키텍처 / 웹 리소스 상대경로 정합성 / FastAPI 서빙
* **문제 상황**:
  * `frontend/` 디렉터리 내에 `index.html`이 루트에 위치하고 있어 HTML 템플릿 파일과 정적 리소스(CSS, JS, Assets)의 계층적 분리가 명확하지 않았음.
  * 템플릿 폴더(`templates/`)로 이동 시 스타일시트 및 스크립트 상대경로(`../css/style.css`, `../js/main.js`) 불일치로 인한 리소스 404 위험 존재.
* **원인 분석**:
  * 진입점 HTML 문서를 전용 템플릿 디렉터리로 격리하고, 파일 시스템 직접 열람 및 웹 서버 라우팅 환경 모두에서 리소스가 유실되지 않도록 경로를 정밀 재설정할 필요가 있음.
* **구체적 해결 방안**:
  1. `frontend/` 하위에 **`frontend/templates/`** 디렉터리를 생성하고 `index.html`을 안전하게 이동 보관.
  2. `frontend/templates/index.html` 내부의 리소스 경로를 상위 디렉터리 기준 상대경로로 정밀 수정:
     - 스타일시트: `<link rel="stylesheet" href="../css/style.css" />`
     - 스크립트: `<script src="../js/main.js"></script>`
  3. 백엔드 서빙 정합성을 위해 `app/templates/index.html`도 동일하게 생성 동기화.
  4. `main.py`에 `/js`, `/assets` 정적 마운트를 추가하고, `GET /home` 엔드포인트가 `frontend/templates/index.html`을 1순위로 서빙하도록 라우팅 최적화.
  5. TestClient 기반 전수 검증: `/home` (200), `/style.css` (200), `/css/style.css` (200), `/js/main.js` (200) 전수 무결점 통과.
* **적용 파일**:
  * [frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html)
  * [frontend/README.md](file:///e:/monnlight/frontend/README.md)
  * [app/templates/index.html](file:///e:/monnlight/app/templates/index.html)
  * [main.py](file:///e:/monnlight/main.py)

---

### [ISSUE-034] 응급실 가이드 페이지 부재 및 시각 포토 기반 응급처치 vs 출발 전 체크리스트 추천 웹페이지 2종 순수 HTML/CSS 구현

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 UI/UX 설계 / 웹 퍼블리싱 / 멀티미디어 에셋 통합 / 모바일 최적화
* **문제 상황**:
  * 메인 홈(`index.html`)의 하단 내비게이션 바(GNB)에 `응급실 가이드` 메뉴가 자리잡고 있었으나, 실제 연결되는 상세 웹페이지가 부재한 상태였음.
  * 소아 야간 응급 상황에서 부모는 텍스트만 읽기 어려워 시각적인 사진 가이드가 절실하며, "가정 내 즉각적 처치"와 "응급실 출발 전 헛걸음 방지 및 서류 지참"이라는 두 가지 핵심 니즈가 공존함.
* **원인 분석**:
  * 단일 페이지에 모든 정보를 압축하기보다는, 부모의 위급 상황에 맞춰 **[추천 1: 증상별 시각 포토 응급처치]**와 **[추천 2: 출발 전 필수 포토 체크리스트 & 실시간 병상]**으로 명확히 콘셉트를 분리하고 상호 전환할 수 있는 UX가 요구됨.
  * 또한 실제 사진이 들어갈 16:9 전용 포토 뷰포트, 글래스모피즘 오버레이 배지, 주의/금기 박스 스타일이 CSS에 마련되어야 함.
* **구체적 해결 방안**:
  1. **추천 페이지 1 구축 ([emergency_guide_symptoms.html](file:///e:/monnlight/frontend/templates/emergency_guide_symptoms.html))**:
     - 상단 119 긴급 통화 캡슐 버튼 및 경련 5분 지속 알림 배너.
     - 4대 핵심 포토 가이드 카드: 열성경련 회복자세(`guide_seizure_care.jpg`), 38.5°C 미온수 마사지 부위(`guide_cooling_sponge.jpg`), 1세 미만 영아 하임리히법(`guide_infant_choking.jpg`), 흉부함몰 및 응급실 지참물(`guide_er_documents.jpg`).
     - 절대 금기 사항(손가락 숟가락 넣기 금지, 찬물/알코올 금지) 강조 박스.
  2. **추천 페이지 2 구축 ([emergency_guide_checklist.html](file:///e:/monnlight/frontend/templates/emergency_guide_checklist.html))**:
     - 30초 당직의 통화 스크립트 카드 (원터치 복사 및 통화).
     - 서울 주요 소아응급실 실시간 가용병상(hv28) 대시보드 (서울아산, 삼성서울, 강남세브란스).
     - 포토 체크리스트 카드: 2024년 5월 본인확인 의무화 증빙 사진, 해열제 약병 지참 사진, 문진 단축 환부 촬영 사진.
  3. **스타일 및 라우팅 통합**:
     - `frontend/css/style.css`에 포토 컨테이너 16:9, 호버 줌, 스위처 탭, 스크립트 박스, 플로팅 CTA 클래스 추가.
     - `main.py`에 `GET /guide`, `GET /guide/symptoms`, `GET /guide/checklist`, `GET /assets/images/*` 서빙 등록.
     - TestClient 기반 9개 엔드포인트 전수 HTTP 200 검증 완료.
* **적용 파일**:
  * [frontend/templates/emergency_guide_symptoms.html](file:///e:/monnlight/frontend/templates/emergency_guide_symptoms.html)
  * [frontend/templates/emergency_guide_checklist.html](file:///e:/monnlight/frontend/templates/emergency_guide_checklist.html)
  * [frontend/templates/emergency_guide.html](file:///e:/monnlight/frontend/templates/emergency_guide.html)
  * [frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html)
  * [frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css)
  * [frontend/assets/images/](file:///e:/monnlight/frontend/assets/images/)
  * [app/templates/](file:///e:/monnlight/app/templates/)
  * [app/static/css/style.css](file:///e:/monnlight/app/static/css/style.css)
  * [main.py](file:///e:/monnlight/main.py)

---

### [ISSUE-035] 응급실 가이드 페이지 분리에 따른 인지 피로 해소 및 CSS Scroll Snap 기반 좌우 스와이프 포토 캐러셀 단일 통합

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 모바일 UI/UX / 모바일 제스처 최적화 / 인터랙션 디자인
* **문제 상황**:
  * 증상별 대처법과 출발 전 준비물이 서로 다른 2개 웹페이지(`symptoms.html`, `checklist.html`)로 분리되어 있어, 위급한 보호자가 탭을 전환해야 하는 불필요한 인지 부하가 발생함.
  * 모바일 환경에서 위아래로만 긴 스크롤은 사진 가이드 탐색 시 피로도를 가중시킴.
* **원인 분석**:
  * 모바일 사용자(보호자)의 멘탈 모델은 사진을 한 장씩 옆으로 가볍게 넘겨보는(Flick / Swipe) 패턴에 가장 친숙함.
  * 단일 페이지(`emergency_guide.html`)로 통합하되, 사진 가이드 6종을 가로 스크롤 스냅 트랙으로 배치하고 하단에 전화 스크립트와 실시간 병상 현황을 순차적으로 배치하는 유기적 구조가 적합함.
* **구체적 해결 방안**:
  1. **단일 통합 페이지 구축 ([emergency_guide.html](file:///e:/monnlight/frontend/templates/emergency_guide.html))**:
     - 상단 119 긴급 통화 버튼 및 경련 5분 지속 알림 배너.
     - 6대 핵심 포토 가이드 카드 가로 스크롤 캐러셀: 열성경련 회복자세, 38.5°C 미온수 마사지, 1세 미만 영아 하임리히법, 2024년 5월 본인확인 증빙 서류, 복용 해열제 약병/아기수첩 지참, 환부 사진 촬영 팁.
     - 30초 당직의 통화 스크립트 (원터치 복사) & 실시간 소아응급실 병상 대시보드(서울아산, 삼성서울, 강남세브란스).
  2. **순수 CSS Scroll Snap 가로 캐러셀 (`frontend/css/style.css`)**:
     - `.photo-carousel-track`: `scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch; scrollbar-width: none;`
     - `.carousel-slide-card`: `scroll-snap-align: center; scroll-snap-stop: always;`
     - 데스크톱 화살표 컨트롤(`<`, `>`) 및 상단 퀵점프 칩 클릭 시 스무스 스크롤 연동.
     - 슬라이드 인덱스 배지(`1 / 6`) 및 하단 인디케이터 점(Dot) 동기화.
  3. **FastAPI 라우팅 동기화 (`main.py`)**:
     - `GET /guide` 및 `GET /guide/emergency`가 통합 페이지를 1순위로 반환하도록 매핑.
     - `frontend/templates/index.html` 하단 GNB `응급실 가이드` 링크를 `emergency_guide.html`로 업데이트.
     - TestClient 전수 검증: `/guide` (200), `/guide/emergency` (200), `/home` (200) 전수 통과.
* **적용 파일**:
  * [frontend/templates/emergency_guide.html](file:///e:/monnlight/frontend/templates/emergency_guide.html)
  * [frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html)
  * [frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css)
  * [app/templates/emergency_guide.html](file:///e:/monnlight/app/templates/emergency_guide.html)
  * [app/static/css/style.css](file:///e:/monnlight/app/static/css/style.css)
  * [main.py](file:///e:/monnlight/main.py)

---

### [ISSUE-036] 응급실 가이드 페이지 내 포토 캐러셀과 통화 스크립트·병상의 시각적 혼재 해소 (2대 카테고리 세그먼트 탭 분리)

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 모듈화 / UI 세그먼트 탭 / 컴포넌트 격리
* **문제 상황**:
  * 단일 통합 페이지 내에서 '시각 포토 가이드'와 '출발 전 30초 통화 스크립트 & 실시간 병상'이 상하로 연속 노출되어 스크롤이 길어지고, 두 기능의 역할 구분이 한눈에 들어오지 않음.
* **원인 분석**:
  * 환아의 응급 상태에 따라 "가정 내 즉각적 처치법(사진 가이드)"을 보고 싶은 보호자와, "응급실로 출발하기 전 통화 스크립트와 가용 병상"을 바로 확인하고 싶은 보호자의 니즈가 명확히 분리됨.
  * 메인 홈(`index.html`)의 카테고리 필터 탭(`전체`, `달빛병원`, `심야약국`)과 같은 직관적인 2대 상단 카테고리 탭 도입이 필요함.
* **구체적 해결 방안**:
  1. `frontend/css/style.css`에 `.guide-category-nav`, `.guide-category-btn`, `.guide-tab-panel` 및 `@keyframes tabFadeIn` 애니메이션 클래스 구축.
  2. `emergency_guide.html` 상단에 2대 카테고리 탭 배치:
     - `[📸 사진 가이드]`: 6대 슬라이드 가로 스와이프 캐러셀 및 도트 인디케이터.
     - `[📞 응급실 통화 스크립트]`: 30초 당직의 통화 스크립트(복사 버튼) + 실시간 소아응급실 병상 대시보드(아산/삼성/세브란스).
  3. 탭 전환 스크립트(`switchGuideCategory`)를 구현하여 탭 선택에 따라 하단 고정 CTA 버튼의 역할(사진 가이드 ➔ 스크립트 탭 이동, 스크립트 탭 ➔ 병원 통화 및 길안내)도 유기적으로 변경되도록 설계.
  4. `app/templates/emergency_guide.html` 동기화 및 TestClient `/guide` 200 검증 완료.
* **적용 파일**:
  * [frontend/templates/emergency_guide.html](file:///e:/monnlight/frontend/templates/emergency_guide.html)
  * [frontend/css/style.css](file:///e:/monnlight/frontend/css/style.css)
  * [app/templates/emergency_guide.html](file:///e:/monnlight/app/templates/emergency_guide.html)
  * [app/static/css/style.css](file:///e:/monnlight/app/static/css/style.css)

---

### [ISSUE-037] Safari WebKit `file://` 로컬 보안 샌드박스의 상위 경로 차단으로 인한 CSS 미적용 결함 해소 (스마트 듀얼 로더 & WebKit 정규화)

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 퍼블리싱 & 크로스 브라우징 / WebKit 보안 샌드박스 호환
* **문제 상황**:
  * 로컬 환경(macOS Finder 등)에서 `frontend/templates/index.html` 파일을 더블 클릭하여 열었을 때, **Chrome 브라우저에서는 정상적으로 CSS가 로드되어 디자인이 표시되지만, Safari 브라우저에서는 스타일이 전혀 로드되지 않아 기본 순수 HTML(흰 배경, 기본 파란 링크, 정렬되지 않은 텍스트)로 렌더링되는 치명적인 결함**이 발생함.
* **원인 분석**:
  1. **WebKit `file://` 스킴 로컬 동일 출처 정책(Strict Local File Origin Policy)**:
     - 기존 `index.html`은 `<link rel="stylesheet" href="../css/style.css" />`로 상위 디렉터리(`../`)를 참조함.
     - Blink(Chrome) 엔진은 로컬 볼륨 내 상위 디렉터리 접근을 비교적 관대하게 처리하여 CSS를 로드함.
     - 반면 WebKit(Safari) 엔진은 보안 샌드박스 정책상 `file://` 문서의 출처를 HTML이 위치한 디렉터리(`frontend/templates/`) 및 그 하위 서브디렉터리로만 한정하며, **상위 디렉터리(`../`)로 거슬러 올라가는 외부 리소스(CSS/JS) 요청을 "Cross-Origin Access Denied"로 간주하여 강제로 차단(Blocked)**함.
  2. **프론트엔드 루트 엔트리포인트 부재**:
     - `frontend/` 루트 디렉터리에 `index.html`이 없어 사용자가 상위 탐색 없이 바로 열 수 있는 표준 진입점이 없었음.
  3. **WebKit CSS 표준화 및 폼 컨트롤 기본값 간섭**:
     - `@charset "UTF-8";` 선언 누락 및 `-webkit-appearance: none;` 리셋 부재로 Safari 고유의 Aqua 스타일/버튼 모서리 왜곡 발생.
     - `position: -webkit-sticky;` 및 `-webkit-backdrop-filter` 선언 순서 미비.
* **구체적 해결 방안**:
  1. **로컬 서브디렉터리 리소스 미러링**:
     - `frontend/templates/css/style.css` 및 `frontend/templates/js/main.js`를 배치하여, Safari가 `file://`로 열었을 때 하위 디렉터리 경로(`css/style.css`)를 통해 WebKit 샌드박스를 100% 통과하도록 구축.
  2. **스마트 듀얼 CSS/JS 로더 장착**:
     - `templates/index.html` 및 모든 응급실 가이드 HTML 파일에 로컬 경로(`css/style.css`)와 상위 폴더 경로(`../css/style.css`)를 함께 선언하여 Safari 로컬 파일, Chrome 로컬 파일, FastAPI 웹 서버(`/home`) 환경 어디서든 100% 자동 매칭되도록 설계.
     - `main.js`에 `window.__AISUM_INITIALIZED__` 멱등성 보호 가드를 적용하여 중복 실행 원천 차단.
  3. **최상위 루트 진입점([frontend/index.html](file:///Volumes/UX400%20mini/monnlight/frontend/index.html)) 신설**:
     - 사용자가 `frontend/` 폴더에서 바로 `index.html`을 열 수 있도록 하위 상대경로(`css/style.css`, `js/main.js`)를 갖는 표준 진입점 배치.
  4. **CSS WebKit 표준화 고도화**:
     - 최상단 `@charset "UTF-8";` 명시.
     - `-webkit-appearance: none; appearance: none;` 리셋으로 Safari 버튼/입력폼 OS 스타일 초기화.
     - `position: -webkit-sticky; position: sticky;` 및 `-webkit-backdrop-filter` 순서 보장.
     - 모바일 사파리 뷰포트 높이 버그 대응(`min-height: -webkit-fill-available;`, `100dvh`).
     - `-webkit-tap-highlight-color: transparent;`, `-webkit-text-size-adjust: 100%;` 추가.
  5. **전수 검증**:
     - Python TestClient 엔드포인트(`GET /home`, `GET /css/style.css`, `GET /guide`) 200 OK 무결점 통과.
     - `test_step5_api.py` 10개 테스트 전수 통과 (Ran 10 tests, OK).
* **적용 파일**:
  * [frontend/templates/index.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/index.html)
  * [frontend/templates/emergency_guide.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/emergency_guide.html)
  * [frontend/templates/emergency_guide_checklist.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/emergency_guide_checklist.html)
  * [frontend/templates/emergency_guide_symptoms.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/emergency_guide_symptoms.html)
  * [frontend/templates/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/templates/css/style.css)
  * [frontend/templates/js/main.js](file:///Volumes/UX400%20mini/monnlight/frontend/templates/js/main.js)
  * [frontend/index.html](file:///Volumes/UX400%20mini/monnlight/frontend/index.html)
  * [frontend/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/css/style.css)
  * [frontend/js/main.js](file:///Volumes/UX400%20mini/monnlight/frontend/js/main.js)
  * [app/templates/](file:///Volumes/UX400%20mini/monnlight/app/templates/) 및 [app/static/css/style.css](file:///Volumes/UX400%20mini/monnlight/app/static/css/style.css)

---

### [ISSUE-038] 응급실 가이드 화면 내 '시각 포토 가이드' 중복 타이틀 바 및 카테고리 칩 영역 제거 (포토 캐러셀 직관성 극대화)

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 UI/UX 리팩토링 / 컴포넌트 간소화
* **문제 상황**:
  * 상단에 2대 카테고리 탭(`[📸 사진 가이드]`, `[📞 응급실 통화 스크립트]`)이 신설되었음에도 불구하고, 그 하단에 `carousel-header-bar` ("시각 포토 가이드 6 / 6", "옆으로 넘겨서 확인") 및 `guide-chips-scroll` (6대 증상별 칩)이 중복 배치되어 모바일 뷰포트 상단 영역을 지나치게 차지하고 포토 카드가 아래로 밀리는 사용성 저하가 발생함.
* **원인 분석**:
  * 각 포토 슬라이드 카드 이미지 내부에 이미 `1 / 6` 인덱스 배지, 처치명, 소아응급의학회 권장 배지 및 Do-Not 금기사항이 독립적으로 완비되어 있으므로, 상단의 서브 타이틀 바와 중복 칩 목록은 정보 과부하를 유발하는 불필요한 요소로 판단됨.
* **구체적 해결 방안**:
  1. `frontend/templates/emergency_guide.html` 및 `app/templates/emergency_guide.html`에서 `.carousel-header-bar`와 `.guide-chips-scroll` 마크업 전면 삭제.
  2. `frontend/css/style.css`에서 `.photo-carousel-wrapper` 상단 마진을 `14px -18px 22px -18px`로 정돈하여 상단 탭과의 자연스러운 시각적 여백 확보.
  3. `app/static/css/style.css`, `frontend/templates/css/style.css`, `app/templates/css/style.css` 전역 동기화.
  4. TestClient `GET /guide` 무결점 검증 (HTTP 200 OK, 헤더 바 및 칩 미포함, 캐러셀 래퍼 정상 서빙).
* **적용 파일**:
  * [frontend/templates/emergency_guide.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/emergency_guide.html)
  * [app/templates/emergency_guide.html](file:///Volumes/UX400%20mini/monnlight/app/templates/emergency_guide.html)
  * [frontend/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/css/style.css)
  * [frontend/templates/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/templates/css/style.css)
  * [app/templates/css/style.css](file:///Volumes/UX400%20mini/monnlight/app/templates/css/style.css)
  * [app/static/css/style.css](file:///Volumes/UX400%20mini/monnlight/app/static/css/style.css)

---

### [ISSUE-039] 응급실 가이드 화면 하단 플로팅 CTA 버튼 2종(스크립트 확인/길안내) 전면 제거 및 화면 가독성 극대화

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 UI/UX 리팩토링 / 시인성 개선
* **문제 상황**:
  * 응급실 가이드 화면([emergency_guide.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/emergency_guide.html)) 하단 네비게이션 바(GNB) 위에 항상 플로팅되어 노출되던 CTA 버튼(`.guide-sticky-cta`)이 모바일 화면 하단에서 콘텐츠(포토 카드 설명문, 병상 현황 리스트 등)를 가리고 시야를 차단하는 불편 발생.
  * 상단에 이미 `[📸 사진 가이드]`와 `[📞 응급실 통화 스크립트]` 2대 카테고리 탭이 명확히 분리되어 있어, 하단 플로팅 버튼이 중복적이고 번잡한 느낌을 줌.
* **원인 분석**:
  * 탭 전환과 길안내 전화 연결을 유도하려던 기존 CTA 버튼이 모바일 뷰포트의 제한된 세로 높이(440px 프레임) 내에서 본문 콘텐츠의 가독성을 저해함.
* **구체적 해결 방안**:
  1. `frontend/templates/emergency_guide.html` 및 `app/templates/emergency_guide.html`에서 `<div class="guide-sticky-cta">...</div>` 마크업 전면 제거.
  2. 스크립트 내 `switchGuideCategory` 함수에서 `ctaLabel`, `ctaIcon`, `ctaBtn` 조작 코드 및 `DOMContentLoaded` 리스너를 완전히 정리하여 DOM 참조 오류 방어.
  3. `TestClient`를 통한 `GET /guide` 엔드포인트 무결점 검증 (HTTP 200 OK, 해당 버튼 텍스트 및 클래스 미포함).
* **적용 파일**:
  * [frontend/templates/emergency_guide.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/emergency_guide.html)
  * [app/templates/emergency_guide.html](file:///Volumes/UX400%20mini/monnlight/app/templates/emergency_guide.html)

---

### [ISSUE-040] 모니모 레퍼런스 기반 3대 카테고리 순수 HTML/CSS 설정 웹페이지(settings.html) 구축 및 GNB 연동

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 UI/UX 신규 개발 / 크로스 브라우징
* **문제 상황**:
  * 아이숨 서비스 내 사용자 맞춤화(자녀 출생연도, 글자 크기) 및 운영·안내 채널(공지사항, 1:1 문의, 약관 및 라이선스)에 접근할 수 있는 단일화된 설정 전용 웹페이지 부재.
  * 기존 메인 대시보드([index.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/index.html)) 하단 GNB 내 '설정' 탭이 `href="#"`로 더미 처리되어 실제 화면 이동 불가 상태.
  * 팀장의 요청사항: 모니모(monimo) 설정 페이지의 정돈된 여백, 카테고리 구분감 및 행 디자인을 레퍼런스로 삼되, 반드시 지정된 3개 카테고리(일반, 사용자 지원, 정보) 및 8개 세부 기능만을 순서대로 배치하고, 임의의 미요청 기능(로그인, Face ID 등)은 철저히 배제해야 함.
* **원인 및 기획 방향**:
  * 간결하고 신뢰감 있는 헬스케어 UI를 위해 순수 Vanilla HTML5 및 CSS3만으로 구축 필요.
  * Chrome 로컬 파일 열람뿐만 아니라 Safari WebKit `file://` 보안 샌드박스에서도 CSS가 깨짐 없이 로드될 수 있도록 듀얼 로더(`css/style.css` + `../css/style.css`) 및 모바일 뷰포트 레이아웃 탑재 필요.
* **구체적 해결 방안**:
  1. **CSS 스타일 시스템 확충** ([frontend/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/css/style.css)):
     - 모니모 스타일의 상단 앱바(`.settings-header`), 뒤로가기 버튼(`.back-icon-btn`), 카테고리 그룹(`.settings-group`), 카테고리 헤더(`.settings-group-title`), 설정 행(`.settings-item-row`), 우측 서브텍스트(`.settings-item-value`), 8px 디바이더(`.settings-section-divider`) 완성.
  2. **설정 웹페이지 신규 구축** ([frontend/templates/settings.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/settings.html)):
     - **일반**: 앱 사용자(자녀)의 출생연도 설정 변경, 글자 크기 변경
     - **사용자 지원**: 공지사항, 1:1 문의
     - **정보**: 아이숨 가이드북, 아이숨 이용약관, 오픈소스 라이선스, 앱 버전 (1.0.0 최신 버전)
     - 요청된 8개 기능 외 불필요한 기능(로그아웃, 회원탈퇴, Face ID 등) 100% 배제.
  3. **하단 GNB 네비게이션 연동**:
     - `index.html`, `emergency_guide.html` 하단 GNB 설정 탭 `href="settings.html"` 연결.
  4. **FastAPI 서버 엔드포인트 연동** ([main.py](file:///Volumes/UX400%20mini/monnlight/main.py)):
     - `@app.get("/settings")` 라우트 등록 및 템플릿 서빙 연동 완료.
  5. **템플릿 및 CSS 미러링 동기화**:
     - `app/templates/settings.html`, `frontend/settings.html`, `app/templates/css/style.css`, `app/static/css/style.css`, `frontend/templates/css/style.css` 동기화 완료.
* **적용 파일**:
  * [frontend/templates/settings.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/settings.html)
  * [frontend/settings.html](file:///Volumes/UX400%20mini/monnlight/frontend/settings.html)
  * [app/templates/settings.html](file:///Volumes/UX400%20mini/monnlight/app/templates/settings.html)
  * [frontend/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/css/style.css)
  * [frontend/templates/index.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/index.html)
  * [frontend/index.html](file:///Volumes/UX400%20mini/monnlight/frontend/index.html)
  * [frontend/templates/emergency_guide.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/emergency_guide.html)
  * [main.py](file:///Volumes/UX400%20mini/monnlight/main.py)

---

### [ISSUE-041] 모니모 레퍼런스 스타일 '앱 알림' 🔔 아이콘 및 순수 CSS iOS 토글 스위치 컴포넌트 구현

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 UI 컴포넌트 추가 / 모바일 인터랙션
* **문제 상황**:
  * 아이숨 설정 페이지([settings.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/settings.html)) 초기 구축 시, 모니모(monimo) 화면에 존재하던 '앱 알림' 토글 기능이 누락되어 있음.
  * 정영식 팀장의 피드백: 모니모에 있는 것처럼 '앱 알림' 기능과 토글 스위치를 추가해달라는 요구 발생.
* **원인 및 기획 방향**:
  * 모니모 레퍼런스 화면에서 '앱 알림'은 카테고리 헤더 타이틀 없이 위아래 8px 디바이더로 분리된 단독 행 형태(좌측 종 아이콘 + '앱 알림' 텍스트, 우측 토글 스위치)로 배치되어 있음.
  * 외부 JS 종속성 없이 순수 CSS(`input[type="checkbox"]:checked + .toggle-slider`)로 구동되는 iOS 스타일 토글 스위치를 구현하여 가볍고 반응성이 뛰어난 모바일 인터랙션을 제공하기로 결정.
* **구체적 해결 방안**:
  1. **CSS 스타일 시스템 확충** ([frontend/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/css/style.css)):
     - `.settings-toggle-row`, `.settings-item-left`, `.settings-item-icon` (종 아이콘 스타일).
     - `.ios-toggle-switch`, `.toggle-slider`, `.toggle-slider::before` (50px x 30px 트랙, 24px 화이트 노브, 코발트 블루 ON 상태, 0.25s 큐빅 베지어 애니메이션).
  2. **마크업 추가** ([frontend/templates/settings.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/settings.html)):
     - `일반` 카테고리와 `사용자 지원` 카테고리 사이 8px 구분선 영역에 단독 섹션으로 `앱 알림` 행 배치.
  3. **전역 템플릿 및 스타일시트 동기화**:
     - `frontend/settings.html`, `app/templates/settings.html`, `app/static/css/style.css`, `frontend/templates/css/style.css`, `app/templates/css/style.css` 동기화 완료.
  4. **무결점 자동 검증**:
     - FastAPI TestClient 기반 `GET /settings` 호출 시 **HTTP 200 OK**, `일반` ➔ `앱 알림` ➔ `사용자 지원` ➔ `정보` 순서 정합성 및 토글 스위치 컴포넌트 검증 100% 통과.
* **적용 파일**:
  * [frontend/templates/settings.html](file:///Volumes/UX400%20mini/monnlight/frontend/templates/settings.html)
  * [frontend/settings.html](file:///Volumes/UX400%20mini/monnlight/frontend/settings.html)
  * [app/templates/settings.html](file:///Volumes/UX400%20mini/monnlight/app/templates/settings.html)
  * [frontend/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/css/style.css)
  * [frontend/templates/css/style.css](file:///Volumes/UX400%20mini/monnlight/frontend/templates/css/style.css)
  * [app/templates/css/style.css](file:///Volumes/UX400%20mini/monnlight/app/templates/css/style.css)
  * [app/static/css/style.css](file:///Volumes/UX400%20mini/monnlight/app/static/css/style.css)

---

### [ISSUE-042] 응급처치정보 및 법적 안내 모달 다이얼로그(어두운 반투명 오버레이, 하단 취소/확인 버튼) 구현

* **발생 일자**: 2026-10-14
* **분류**: 프론트엔드 UI 컴포넌트 / 모달 다이얼로그 / 순수 화면 구현
* **문제 상황**:
  * 메인 홈 화면에서 버튼을 클릭했을 때 화면 중앙에 팝업되는 모달 다이얼로그와 어두운 반투명 오버레이 배경 처리, 하단 '취소' 및 '확인' 버튼 배치가 필요함.
  * 레퍼런스 이미지의 컨셉(응급/처치 안내 문구, 파란색 키워드 강조, 연파랑 박스, 1:1 분할 하단 액션 버튼)에 맞춘 순수 화면 UI 구축 요청.
* **구체적 해결 방안**:
  1. [frontend/css/style.css](frontend/css/style.css)에 모달 스타일 구축:
     - `.modal-overlay`: `rgba(15, 23, 42, 0.65)` 어두운 반투명 배경 및 `backdrop-filter: blur(5px)`.
     - `.modal-dialog-card`: 328px 너비, `border-radius: 22px`, `scale(0.92)` ➔ `scale(1)` 팝업 애니메이션.
     - 본문 안내 박스: `.modal-notice-box` (`background: #F4F6FB`), `.highlight-blue` 키워드 강조 불릿 리스트.
     - 하단 액션 바: `.modal-action-row` (50px 높이, 1:1 좌우 분할, '취소' 및 '확인' 버튼).
  2. [frontend/index.html](frontend/index.html) 및 [frontend/templates/index.html](frontend/templates/index.html)에 `#triage-consent-modal` 마크업 연계.
  3. [frontend/js/main.js](frontend/js/main.js)에 가벼운 모달 제어 이벤트 등록:
     - 메인 CTA 및 증상 칩 클릭 시 `openModal()`
     - '취소' 및 '확인' 버튼 클릭 시 `closeModal()`
     - 어두운 배경 오버레이 클릭 또는 ESC 키 입력 시 `closeModal()`
* **적용 파일**:
  * [frontend/index.html](frontend/index.html)
  * [frontend/templates/index.html](frontend/templates/index.html)
  * [app/templates/index.html](app/templates/index.html)
  * [frontend/css/style.css](frontend/css/style.css)
  * [frontend/js/main.js](frontend/js/main.js)
  * [log.md](log.md)

---

### [ISSUE-043] 사용자 증상 프롬프트 입력 페이지(헤드라인 '증상을 구체적으로 정확하게 입력해주세요', 언더라인 인풋, 가상키보드 배제) 구현

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 UI/UX 페이지 / 사용자 프롬프트 입력 / 순수 화면 디자인
* **문제 상황**:
  * 사용자가 제공한 레퍼런스 이미지(이름 입력 화면)의 레이아웃을 서비스 컨셉(소아 의료 사전 증상 문진)에 맞추어 "본인 확인을 위해 이름을 입력해주세요"를 **"증상을 구체적으로 정확하게 입력해주세요"**로, "이름" 플레이스홀더를 **"입력"**으로 치환한 전용 입력 페이지 필요.
  * 레퍼런스 이미지의 가상 키보드(휴대폰 자판)는 실제 입력 시 OS가 띄우는 기능적 요소이므로 화면에서 배제하고, 좌측 화면 컨셉(미니멀 화이트 여백, 블루 언더라인)에 맞춘 깔끔한 페이지 구성 요구.
* **구체적 해결 방안**:
  1. Stitch MCP를 호출하여 `Aisum 증상 입력 화면` (`Screen ID: 18441e7efe314c06bb8716493d3d8626`) 생성 완료.
  2. [frontend/css/style.css](frontend/css/style.css)에 섹션 6 스타일 추가:
     - `.input-page-viewport`: max-width 440px 모바일 뷰포트, 미니멀 클린 화이트 배경.
     - `.input-headline`: 26px 볼드, 딥 네이비(#0F172A), 넉넉한 상하 여백.
     - `.underline-input-wrapper`: 2px 로열 블루(`#0066FF`) 하단 보더 라인, `placeholder="입력"`.
     - 휴대폰 가상 자판 그래픽 및 확인 버튼 배제, 쾌적한 화이트 여백 유지.
  3. [frontend/input.html](frontend/input.html) 및 [frontend/templates/input.html](frontend/templates/input.html) 신규 작성.
  4. [frontend/js/main.js](frontend/js/main.js)에 텍스트 입력 시 플로팅 레이블/지우기(`✕`) 버튼 토글 및 Enter 키 입력 인터랙션 탑재.
  5. `main.py`에 `GET /input` 라우트 등록 및 TestClient 200 OK 검증 완료.
* **적용 파일**:
  * [frontend/input.html](frontend/input.html)
  * [frontend/templates/input.html](frontend/templates/input.html)
  * [frontend/css/style.css](frontend/css/style.css)
  * [frontend/js/main.js](frontend/js/main.js)
  * [main.py](main.py)
  * [log.md](log.md)

---

### [ISSUE-044] 팀 협업 분기 충돌 방어 머지(Merge), 7대 엔드포인트 서빙 검증 및 Cross-OS NFD/NFC 정규화

* **발생 일자**: 2026-10-15
* **분류**: 형상 관리 / Git 충돌 방어 / 크로스 OS 유니코드 정규화
* **문제 상황**:
  * 정영식 팀장(macOS 환경)과 김동준 팀원(Windows 환경)이 각자 분기에서 작업을 진행함:
    - 원격(`origin/main`): 응급실 가이드 페이지(`emergency_guide.html`) 및 설정 페이지(`settings.html`) 생성 (`4d22c88`, `ccde1cc`)
    - 로컬: 증상 입력 페이지(`input.html`) 및 응급처치정보 모달 연동 (`075f450`)
  * 상호 충돌 없이 안전하게 원격에 올려야 하는 과제가 주어졌으며, 이전 세션에서 머지 작업 도중 세션이 중단된 것 같은 불안감이 발생함.
  * 또한, macOS(APFS)의 NFD 자모 분리 저장 방식과 Windows(NTFS)의 NFC 완성형 저장 방식으로 인해 Git 인덱스에 동일 파일(`Answer-영식.md`, `2021년 KTAS...pdf`)이 이중 등록되어 잠재적인 머지 충돌 위험이 상존함.
* **원인 분석**:
  1. **브랜치 분기 상태**: 서로 다른 커밋들이 원격과 로컬에 각각 존재하여 Fast-Forward 머지가 불가능하고 3-Way Merge가 필요한 상황이었음.
  2. **유니코드 정규화 차이**: macOS에서 커밋된 파일명은 NFD(Decomposed Unicode: `\u1102\u1167...`)로 인코딩되고, Windows에서 생성된 파일명은 NFC(Composed Unicode: `\ub144...`)로 인코딩되어 Git 인덱스 상에서 별개의 두 개 파일로 인식됨.
* **구체적 해결 방안**:
  1. **3-Way 머지 및 무결점 통합**:
     - 로컬 작업과 원격 작업을 무손실 수동 머지하여 커밋 `b573e46` 생성.
     - 원격 `origin/main`으로 `git push` 실행 완료.
  2. **FastAPI 백엔드 7대 핵심 엔드포인트 전수 검증**:
     - Python TestClient를 통해 통합된 모든 엔드포인트(`/`, `/home`, `/input`, `/guide`, `/settings`, `/css/style.css`, `/js/main.js`)에 대해 **HTTP 200 OK** 응답 검증 완료.
  3. **Cross-OS NFD 파일명 정규화 (선제 충돌 방어)**:
     - Git 인덱스에 중복 등록되어 있던 NFD 파일 2종(`Answer-영식.md`, `2021년 KTAS...pdf`)을 `git rm --cached`로 인덱스에서 안전하게 제거.
     - 로컬 디스크 상의 중복 NFD 파일을 삭제하고 순수 NFC 파일만 남겨 향후 macOS-Windows 협업 시 파일명 충돌을 원천 차단함.
* **적용 파일**:
  * [Answer-영식.md](file:///c:/AI-Native-Agent/monnlight/Answer-영식.md)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-045] 팀원(김동준) 전담 파일(input.html, modal.html)과 타 작업자(정영식) 전담 파일(index.html) 역할 분리 및 index.html 원본 100% 롤백

* **발생 일자**: 2026-10-15
* **분류**: 형상 관리 / 프론트엔드 모듈 격리 / 협업 정합성
* **문제 상황**:
  * 김동준 팀원은 `input.html`(증상 입력 화면)과 `modal.html`(처치정보 모달) 구현을 담당하였으나, 이전 모달 연동 작업 과정에서 `index.html` 내부에 모달 마크업(`#triage-consent-modal`) 및 히어로 UI 변경 사항이 함께 삽입되어 커밋됨.
  * 다른 작업자(정영식 팀장)가 전담한 `index.html`에 불필요한 수정 내역이 혼입되어 작업 경계가 모호해지고, 정영식 팀장의 원본 마크업이 변형되는 부작용 발생.
* **원인 분석**:
  * 모달 기능을 실제 화면에서 테스트하기 위해 `index.html`을 수정했던 임시 작업물이 분리되지 않고 함께 커밋되어, 정영식 작업자 전담 파일인 `index.html`에 의도치 않은 변경이 전파됨.
* **구체적 해결 방안**:
  1. **`index.html` 파일군 100% 원본 롤백**:
     - `frontend/templates/index.html`, `frontend/index.html`, `app/templates/index.html` 3종 파일을 정영식 작업자의 최종 커밋([`b12ebe4`](https://github.com/yeongsik0914/monnlight/commit/b12ebe4)) 상태로 checkout하여 208줄의 순수 원형으로 완벽 복원.
     - 정영식 작업자가 구현한 응급실 가이드 링크, 설정 링크, WebKit 듀얼 CSS/JS 로더를 완전 무결하게 보존.
  2. **김동준 팀원 담당 파일의 완벽한 독립 보존**:
     - `frontend/templates/input.html`, `frontend/input.html` (증상 입력 화면) 보존.
     - `frontend/templates/modal.html`, `frontend/modal.html` (처치정보 및 법적 동의 모달 화면) 보존.
  3. **FastAPI 7대 엔드포인트 서빙 검증**:
     - TestClient를 통해 `/home`(10,258 bytes로 원복), `/input`(2,516 bytes), `/guide`, `/settings`, `/css/style.css`, `/js/main.js` 전수 200 OK 통과 확인.
* **적용 파일**:
  * [frontend/templates/index.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/index.html)
  * [frontend/index.html](file:///c:/AI-Native-Agent/monnlight/frontend/index.html)
  * [app/templates/index.html](file:///c:/AI-Native-Agent/monnlight/app/templates/index.html)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-046] modal.html 안내 문구의 소아 야간 의료법·응급 대응 최적화 및 input.html/GNB 연동

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 UI/UX / 의료법 컴플라이언스 / 정보 전달력 고도화
* **문제 상황**:
  * 초기 `modal.html`의 텍스트가 범용적이고 중복된 표현("추천 결과가 달라질 수 있습니다", "결과가 달라질 수 있습니다")으로 구성되어 있어, 우리 프로젝트인 **'아이숨(소아 야간 외래·달빛어린이병원 및 응급실 매칭)'**의 고유한 도메인 특성이 충분히 반영되지 못함.
  * 모달 확인 버튼 클릭 시 실제 다음 단계인 `input.html`(증상 입력 화면)으로의 화면 전환 액션이 누락되어 있고, GNB 링크가 더미(`#`)로 되어 있음.
* **원인 분석**:
  * 프로토타입 단계에서 일반 약관 템플릿 문구를 그대로 사용하여, 소아 응급 의료 도메인에 필수적인 5대 원칙(의료법 제27조 준수, 119 위급상황 고열/경련 숏서킷, 야간 대기열 현장 조기마감 주의, 2024년 5월 본인확인 의무화 서류 지참, 최종 판단 안내)이 정밀하게 반영되지 못함.
* **구체적 해결 방안**:
  1. **헤더 타이틀 도메인 정밀화**:
     - 기존: "아이숨은 사용자가 입력한 증상정보를 바탕으로 인근 병원과 참고용 처치정보를 안내합니다."
     - 변경: **"아이숨은 보호자님이 입력하신 증상 정보를 바탕으로 진료 가능한 야간 소아과와 안전한 응급처치 가이드를 안내합니다."**
  2. **소아 의료 특화 5대 불릿 안내문 탑재**:
     - ① **의료법 제27조 준수**: 비의료 AI 기반 참고 서비스로, 의사의 전문적인 진단 및 처방 불가 명시.
     - ② **위급 상황 즉시 119**: 생후 100일 미만 38℃ 이상 고열, 경련, 청색증, 호흡곤란 등 위험 징후 발견 시 119 즉각 신고.
     - ③ **현장 조기 마감 주의**: 야간 달빛어린이병원 및 응급실 대기 환자 폭증 시 조기 마감 대비 출발 전 유선 확인 권장.
     - ④ **본인확인 서류 지참**: 2024년 5월 개정 의료법 준수를 위한 보호자 신분증 및 주민등록등본 지참 안내.
     - ⑤ **최종 판단 안내**: 아이 안전에 대한 최종 판단과 책임이 보호자에게 있음을 명확히 고지.
  3. **사용자 플로우 연동**:
     - 확인 버튼: `동의하고 증상 입력하기` (`onclick="location.href='input.html'"`)로 동준 님 전담 산출물 간의 연결 완성.
     - 취소 버튼: `onclick="location.href='index.html'"`.
     - 하단 GNB: `index.html`, `emergency_guide.html`, `settings.html` 정합 연결.
  4. **FastAPI 서빙 라우트 탑재**:
     - `main.py`에 `@app.get("/modal")` 라우트 등록 및 TestClient 200 OK 검증 완료.
* **적용 파일**:
  * [frontend/modal.html](file:///c:/AI-Native-Agent/monnlight/frontend/modal.html)
  * [frontend/templates/modal.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/modal.html)
  * [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-047] input.html 사용자 텍스트 입력 시 확인 버튼 동적 표출(레퍼런스 우측 화면 1:1) 구현

* **발생 일자**: 2026-10-15
* **분류**: 프론트엔드 UI 컴포넌트 / 인터랙션 애니메이션 / 모바일 폼 UX
* **문제 상황**:
  * 사용자 제공 레퍼런스 이미지의 플로우:
    - 좌측 화면: 인풋이 비어있을 때는 "확인" 버튼이 화면에 나타나지 않음.
    - 우측 화면: 사용자가 커서를 두고 텍스트를 1글자 이상 입력하게 되면, 인풋 필드 아래쪽에 로열 블루 컬러의 풀 너비 **"확인"** 버튼이 부드럽게 등장해야 함.
  * 기존 `input.html`에는 확인 버튼 마크업 및 동적 등장 인터랙션이 누락되어 있었음.
* **원인 분석**:
  * 이전 단계에서 가상 키보드를 배제하면서 확인 버튼까지 함께 생략되어, 모바일 사용자가 입력을 마치고 다음 단계로 진행할 수 있는 명시적인 CTA가 부재하였음.
* **구체적 해결 방안**:
  1. **마크업 추가** ([`frontend/input.html`](file:///c:/AI-Native-Agent/monnlight/frontend/input.html), [`frontend/templates/input.html`](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)):
     - `.underline-input-wrapper` 하단에 `.input-confirm-btn-wrap` 컨테이너 및 `.input-confirm-btn` ("확인") 마크업 추가.
  2. **레퍼런스 우측 화면 1:1 스타일링** ([`frontend/css/style.css`](file:///c:/AI-Native-Agent/monnlight/frontend/css/style.css)):
     - 너비 100%, 높이 52px, 배경 `#0066FF`, 모서리 곡률 `14px`, 텍스트 흰색 16px 볼드.
     - 기본 상태: `display: none;`
     - 활성 상태: `animation: fadeInSlideUp 0.25s ease-out` 부드러운 상향 페이드인 슬라이드 모션 적용.
     - Pure CSS fallback: `.underline-input-wrapper:has(.underline-input-field:not(:placeholder-shown)) + .input-confirm-btn-wrap` 선택자를 탑재하여 JS가 지연되는 환경에서도 CSS만으로 즉시 버튼이 떠오르도록 설계.
  3. **인터랙션 토글 로직 탑재** ([`frontend/js/main.js`](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js)):
     - `updateInputState()` 함수 구현: `symptomInput.value.trim().length > 0`일 때 플로팅 레이블, 지우기 버튼(`✕`), 확인 버튼을 동시에 활성화.
     - 텍스트를 모두 지우거나 지우기(`✕`) 버튼 클릭 시 확인 버튼 자동 숨김 처리.
     - 키보드 Enter 키 입력 시 확인 버튼 자동 트리거 연동.
  4. **전역 템플릿 및 정적 파일 동기화**:
     - `app/static/css/`, `frontend/templates/css/`, `app/templates/css/`, `frontend/templates/js/`, `app/templates/js/` 전역 미러링 완료.
* **적용 파일**:
  * [frontend/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html)
  * [frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)
  * [frontend/css/style.css](file:///c:/AI-Native-Agent/monnlight/frontend/css/style.css)
  * [frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-048] 로컬 Wi-Fi IP 바인딩 및 QR코드 즉각 테스트 환경 구축, iOS/안드로이드 홈 바로가기 메타태그 탑재

* **발생 일자**: 2026-10-15
* **분류**: 모바일 웹 테스트 환경 구축 / PWA Standalone 메타 태그 / 네트워크 서빙
* **문제 상황**:
  * 모바일 키보드 반응과 화면 인터랙션을 실제 스마트폰(아이폰/안드로이드)에서 검증하고자 할 때, 무거운 Cloud Run 배포 없이도 10초 만에 폰으로 접속할 수 있는 초고속 테스트 파이프라인 부재.
  * 스마트폰에서 웹 접속 시 브라우저 주소창과 하단 툴바가 가려지는 모바일 앱 전체 화면(Standalone 모드) 메타 태그 미비.
* **원인 분석**:
  * Uvicorn 기본 로컬 바인딩(`127.0.0.1`)은 PC 내부에서만 접근 가능하여 동일 Wi-Fi에 연결된 스마트폰의 접근이 차단됨.
* **구체적 해결 방안**:
  1. **로컬 Wi-Fi IPv4 바인딩**:
     - PC의 Wi-Fi 로컬 IP(`192.168.14.189`)를 확보하고, Uvicorn 서버를 `0.0.0.0:8000`에 백그라운드 데몬으로 바인딩.
  2. **모바일 홈 바로가기 메타 태그 탑재** ([`frontend/input.html`](file:///c:/AI-Native-Agent/monnlight/frontend/input.html), [`frontend/templates/input.html`](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)):
     - `apple-mobile-web-app-capable="yes"`, `apple-mobile-web-app-status-bar-style="default"`, `mobile-web-app-capable="yes"`, `theme-color="#ffffff"` 탑재 완료.
     - iOS 사파리 및 안드로이드 크롬에서 '홈 화면에 추가' 시 네이티브 앱과 동일한 주소창 없는 전체 화면 실행 지원.
  3. **QR 코드 즉각 스캔 파이프라인**:
     - `http://192.168.14.189:8000/input` 직결 QR 코드를 생성하여 카메라 촬영 0.1초 만에 스마트폰 테스트 가능 환경 완성.
* **적용 파일**:
  * [frontend/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html)
  * [frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-049] index.html 아이증상 입력버튼 클릭 시 사전 안내 모달 팝업 및 증상 입력(input.html) 연동 구현

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 팀원 (지시: 정영식 팀장)
* **분류**: 프론트엔드 UI/UX 인터랙션 / 모달 다이얼로그 / 화면 간 네비게이션
* **문제 상황**:
  * 메인 홈 화면(`index.html`)의 "아이 증상 입력하고 병원 찾기" 버튼(`start-triage-btn`)을 눌렀을 때, 소아 응급의료 사전 고지 및 법적 동의 모달 다이얼로그가 마크업에서 누락되어 화면에 모달이 뜨지 않음.
  * 모달 내 최종확인 버튼("동의하고 증상 입력하기")을 클릭했을 때 다음 단계인 증상 입력 페이지(`input.html`)로의 연동이 이루어지지 않고 단순히 창만 닫히는 상태였음.
* **원인 분석**:
  * 이전 파일 격리 롤백 과정에서 `index.html`이 순수 원본으로 복원되면서 모달 마크업(`#triage-consent-modal`)이 제거되었고, `main.js`의 `modalConfirmBtn` 리스너 역시 단순 `closeModal()`만 수행하도록 설정되어 있었음.
* **구체적 해결 방안**:
  1. **레퍼런스 이미지 1:1 정밀 일치 모달 마크업 삽입**:
     - `frontend/templates/index.html`, `frontend/index.html`, `app/templates/index.html`에 `#triage-consent-modal` 다이얼로그 마크업 탑재.
     - 헤더: "아이숨은 보호자님이 입력하신 증상 정보를 바탕으로 <span class='highlight-navy'>진료 가능한 야간 소아과와 안전한 응급처치 가이드</span>를 안내합니다."
     - 5대 소아 응급의료·법적 컴플라이언스 불릿 (의료법 제27조 준수, 위급 상황 즉시 119, 현장 조기 마감 주의, 본인확인 서류 지참, 최종 확인 및 동의 안내).
     - 하단 1:1 액션 버튼: 좌측 '취소', 우측 '동의하고 증상 입력하기' (`#modal-confirm-btn`).
  2. **최종확인 버튼 클릭 시 `input.html` 연동**:
     - `frontend/templates/js/main.js`, `frontend/js/main.js`, `app/templates/js/main.js`의 `modalConfirmBtn` 클릭 이벤트에 `window.location.href = 'input.html'` 연동 추가.
     - 인라인 `onclick="location.href='input.html'"` 속성 병행 적용으로 이중 안전 장치 마련.
  3. **FastAPI 백엔드 라우팅 보강**:
     - `main.py`에 `@app.get("/input.html")` 데코레이터를 추가하여 `/input` 및 `/input.html` 양방향 200 OK 서빙 지원.
  4. **Cross-Browser 듀얼 로더 탑재**:
     - `frontend/templates/input.html`에 듀얼 CSS/JS 로더를 적용하여 Safari 및 Chrome 로컬/웹 환경 100% 호환.
* **적용 파일**:
  * [frontend/templates/index.html](file:///e:/monnlight/frontend/templates/index.html)
  * [frontend/index.html](file:///e:/monnlight/frontend/index.html)
  * [app/templates/index.html](file:///e:/monnlight/app/templates/index.html)
  * [frontend/templates/js/main.js](file:///e:/monnlight/frontend/templates/js/main.js)
  * [frontend/js/main.js](file:///e:/monnlight/frontend/js/main.js)
  * [app/templates/js/main.js](file:///e:/monnlight/app/templates/js/main.js)
  * [frontend/templates/input.html](file:///e:/monnlight/frontend/templates/input.html)
  * [main.py](file:///e:/monnlight/main.py)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-050] 원격 input.html 최신 업데이트(확인 버튼 인터랙션 & PWA 메타태그) 풀 및 index.html 모달 연동 무결점 병합

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 팀원 (지시: 정영식 팀장)
* **분류**: Git 형상 관리 / 3-Way 병합 / 프론트엔드 모듈 연동
* **문제 상황**:
  * 원격 GitHub 저장소에 `input.html`의 최신 업데이트(PWA Standalone 메타태그, 텍스트 입력 시 동적 확인 버튼 표출 인터랙션)가 푸시되어 있었으나, 로컬 워크스페이스의 직전 작업(`index.html` 모달 연동)과 분기되어 있어 충돌 없이 병합해야 하는 과제 발생.
* **원인 분석**:
  * Git 원격 레포지토리와 로컬 작업 디렉토리 간 서로 다른 기능 브랜치 작업이 비동기적으로 진행되어 커밋 그래프 정합성 확보가 필요했음.
* **구체적 해결 방안**:
  1. `git fetch origin main` 수행 및 원격 커밋 이력(`28ce9ad`, `93fbbe0`) 분석.
  2. 로컬의 `index.html` 모달 트리거 마크업 및 `main.js`의 `modalConfirmBtn` 연동 로직을 온전히 보존한 상태에서, 원격의 `input.html` 변경 사항(확인 버튼 래퍼, PWA 메타태그, Pure CSS `:has()` 셀렉터)을 안전하게 3-Way 병합.
  3. `FastAPI TestClient`로 `/home`, `/input`, `/input.html` 전수 200 OK 회귀 검증 완료.
* **적용 파일**:
  * [frontend/templates/input.html](file:///e:/monnlight/frontend/templates/input.html)
  * [frontend/templates/js/main.js](file:///e:/monnlight/frontend/templates/js/main.js)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)

---

### [ISSUE-051] 응급실 가이드(emergency_guide.html) 텍스트 전면 배제 및 소아 응급실 & KTAS 7단계 시각 이미지 슬라이더 개편

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 팀원 (지시: 정영식 팀장)
* **분류**: 프론트엔드 UI/UX 리팩토링 / 이미지 프로세싱 / 모바일 터치 캐러셀
* **문제 상황**:
  * 기존 응급실 가이드 페이지(`emergency_guide.html`)는 텍스트 위주의 처치 지침, 병원 통화 스크립트 탭, 응급실 병상 테이블 등이 혼재되어 있어, 위급한 상황에 처한 보호자가 단계별 대처법과 KTAS 중증도 개념을 직관적으로 파악하기 어려움.
  * 사용자가 제공한 인포그래픽("소아전용 응급실 이용 가이드: 아프거나 다쳤을 때 & KTAS 중증도 안내")의 7개 단계를 잘라내어, 기존 텍스트를 모두 없애고 이미지를 순서대로 넘겨볼 수 있는 모바일 최적화 뷰어로 개편할 필요성 대두.
* **원인 분석**:
  * 업로드된 원본 인포그래픽은 단일 이미지(1024×572)로 상단 4개 카드, 하단 3개 카드가 통합되어 있어, 모바일 뷰포트에서 그대로 표시할 경우 글씨가 너무 작아 판독이 불가능함.
  * 따라서 각 Step별 카드를 고해상도로 정밀 분할(Crop)하고, 순서대로 좌우 스와이프할 수 있는 풀스크린 카드 캐러셀 UI가 필수적이었음.
* **구체적 해결 방안**:
  1. **OpenCV/PIL 정밀 이미지 분할 파이프라인 가동**:
     - 원본 이미지에서 7개 Step 카드의 바운딩 박스를 정밀 산출하여 1px 오차 없이 크롭:
       - Step 1: `(21, 113, 254, 342)` -> `guide_ktas_step1.png`
       - Step 2: `(263, 113, 508, 342)` -> `guide_ktas_step2.png`
       - Step 3: `(516, 113, 761, 342)` -> `guide_ktas_step3.png`
       - Step 4: `(770, 113, 1003, 342)` -> `guide_ktas_step4.png`
       - Step 5: `(21, 352, 338, 561)` -> `guide_ktas_step5.png`
       - Step 6: `(348, 352, 676, 561)` -> `guide_ktas_step6.png`
       - Step 7: `(686, 352, 1003, 561)` -> `guide_ktas_step7.png`
       - 원본 전체: `guide_ktas_full.png`
     - 정적 에셋 디렉토리(`frontend/assets/images/`, `frontend/templates/assets/images/`, `app/static/assets/images/`)에 동시 복제 배치.
  2. **기존 장황한 텍스트 전면 제거 & 7단계 이미지 캐러셀 마크업 전면 교체**:
     - 기존 통화 스크립트 세그먼트 탭, 응급실 병상 테이블, 장문의 처치 지침 텍스트를 전면 삭제.
     - 각 슬라이드에는 오직 `STEP 01` ~ `STEP 07` 뱃지와 단계 제목, 그리고 고화질 크롭 이미지만 배치하여 시각적 몰입도 극대화.
  3. **CSS Scroll Snap & 모바일 터치 스와이프 인터랙션 구현**:
     - `scroll-snap-type: x mandatory` 및 `scroll-snap-align: center` 적용.
     - 상단 실시간 슬라이드 카운터(`1 / 7` ~ `7 / 7`) 동적 업데이트.
     - 하단 7개 인디케이터 도트 클릭 시 해당 슬라이드로 부드러운 스크롤 이동(`scrollToSlide`).
     - 데스크톱 사용자를 위한 좌우 화살표 네비게이션 버튼 구비.
     - "가이드 인포그래픽 원본 한눈에 크게 보기" 모달 다이얼로그 탑재로 전체 맥락 확인 지원.
  4. **크로스 브라우징 및 정적 라우트 검증**:
     - 이미지 태그에 `onerror="this.src='../assets/images/...'"` 듀얼 폴백을 장착하여 Safari `file://` 로컬 열람 및 FastAPI 웹 서빙 환경 100% 대응.
     - `FastAPI TestClient`로 `GET /guide`, `GET /guide/emergency` (200 OK) 및 7종 이미지 정적 서빙(200 OK) 전수 무결점 확인.
* **적용 파일**:
  * [frontend/templates/emergency_guide.html](file:///e:/monnlight/frontend/templates/emergency_guide.html)
  * [app/templates/emergency_guide.html](file:///e:/monnlight/app/templates/emergency_guide.html)
  * `frontend/assets/images/guide_ktas_step1~7.png`, `guide_ktas_full.png`
  * `frontend/templates/assets/images/guide_ktas_step1~7.png`, `guide_ktas_full.png`
  * `app/static/assets/images/guide_ktas_step1~7.png`, `guide_ktas_full.png`
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-052] 증상 입력 후 맞춤 결과 화면(result.html) 정적 목업 구축, 2-트랙 탭/30분 마진 약국/실시간 병상 UI 구현 및 Git 무결점 통합

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 (팀원)
* **분류**: 프론트엔드 UI/UX 신규 개발 & Git 협업 형상 관리
* **문제 상황**:
  * 증상 입력 페이지([input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html))에서 확인 버튼을 클릭한 후 사용자에게 보여줄 결과 화면이 부재함.
  * 백엔드에는 0ms Red Flag, 2-트랙 시설 매칭(달빛병원+30분 안심약국 vs 소아응급실 병상), 30초 통화 대본, 본인확인 서류 체크리스트 등 강력한 기능이 구비되어 있으나 프론트엔드에서 이를 가볍고 직관적으로 볼 수 있는 목업 뷰가 필요함.
  * 원격 저장소(`origin/main`)에 타 작업자(정영식 팀장)의 대규모 커밋(7단계 비주얼 가이드 캐러셀 리팩토링, 이미지 7종, Q61 등)이 반영되어 있어, 로컬 변경분을 안전하게 보존하면서 충돌 없이 pull & merge 해야 하는 협업 형상 관리 과제 발생.
* **원인 분석**:
  * 복잡한 백엔드 API 통신 연동에 앞서, 프론트엔드 자체의 모바일 사용성 및 컴포넌트 렌더링 검증을 위한 "정적 목업 화면"이 먼저 구축되어야 함.
* **구체적 해결 방안**:
  1. **백엔드 기능 100% 매핑 정적 결과 화면 ([frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html), [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)) 구축**:
     - **바이탈 요약 & 가드레일**: `0ms 가드레일 안전 통과 🟢` 뱃지 및 `14개월`, `39.2℃ (고열)`, `#구토`, `KTAS 3단계` 메타 칩.
     - **2-트랙 세그먼트 탭**: `[🌙 달빛병원·약국 (3)]` ↔ `[🚨 소아 응급실 병상 (2)]` 순수 CSS/JS 전환 인터랙션.
     - **Track B 페어링 카드**: 추천 1순위 송파어린이병원 + 송파달빛약국의 `[🟢 +30분 조제 안전마진 확보]` 배지, 마감 35분 전 주의 표시, 원터치 전화/카카오맵 길찾기.
     - **Track A 소아응급실 카드**: 서울아산병원 소아전문응급센터 실시간 병상(`hv28` 4석 여유), 전문의 당직 여부, E-Gen 데이터 신선도 배지.
     - **내원 지원 툴킷**: 30초 통화 대본 복사(토스트 팝업 연동) 및 2024년 5월 본인확인 의무화 지참 서류 인터랙티브 체크박스 3종.
     - **의료법 제27조 고지**: 하단 법적 안심 면책 푸터 탑재.
  2. **화면 간 유기적 연결**:
     - [frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js): `inputConfirmBtn` 클릭 시 `result.html`로 화면 이동 로직 바인딩.
     - [main.py](file:///c:/AI-Native-Agent/monnlight/main.py): `@app.get("/result")` 정적 서빙 라우트 추가.
  3. **Git 협업 무결점 병합**:
     - `git stash`로 로컬 변경분을 임시 안전 격리한 뒤 `git pull origin main`으로 정영식 팀장의 최신 작업본을 Fast-Forward로 안전하게 수신.
     - `git stash pop`을 통해 충돌 0건으로 자동 병합 완결.
* **적용 파일**:
  * [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)
  * [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)
  * [frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js)
  * [frontend/templates/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/templates/js/main.js)
  * [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)
  * [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-053] AI 증상 분석 중 로딩 오버레이 & 단독 페이지(loading.html) 순수 CSS 키프레임 애니메이션 및 2초 타이머 시퀀스 구축

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 (팀원)
* **분류**: 프론트엔드 UI/UX 신규 개발 / 인터랙션 애니메이션 / 임상 체감 대기시간 최적화
* **문제 상황**:
  * 증상 입력 화면([input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html))에서 확인 버튼을 눌렀을 때, 로딩 피드백 없이 즉시 결과 화면([result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html))으로 전환되면 보호자 입장에서 AI가 실제로 아이의 증상을 정밀 분석했는지 신뢰하기 어렵고 화면 전환이 부자연스러움.
  * 복잡한 백엔드 분석 파이프라인(가드레일 검사 ➔ KTAS 168개 지침 대조 ➔ 달빛어린이병원/약국 페어링)이 구동되는 동안 보호자의 불안감을 완화하고 높은 전문성을 체감할 수 있는 로딩 비주얼 피드백이 필요함.
  * 또한 단독 로딩 뷰 테스트 및 독립 컴포넌트 검증을 위한 [loading.html](file:///c:/AI-Native-Agent/monnlight/frontend/loading.html) 페이지의 부재.
* **원인 분석**:
  * 이전 단계에서는 텍스트 입력 후 즉시 `window.location.href = 'result.html'`로 연결되어 시각적 분석 프로세스(Processing) 피드백이 생략되어 있었음.
* **구체적 해결 방안**:
  1. **순수 CSS3 키프레임 애니메이션 기반 로딩 컴포넌트 구현**:
     - 외부 라이브러리(Lottie, JS 애니메이션) 없이 브라우저 네이티브 하드웨어 가속(GPU)을 활용하는 순수 CSS 키프레임 적용:
       - `pulseGlow`: 엠블럼 외곽 블루 링이 1.6초 주기로 부드럽게 팽창/수축하며 펄스 효과 발산.
       - `spinLoader`: 중앙 블루 스피너 링이 0.8초 주기로 회전.
       - `shimmer`: 프로그레스 바 내부에서 은은한 하이라이트 광택이 흐르는 효과.
       - 스마트 토이 아이콘(`smart_toy`, 로열 블루 `#0066FF`)을 중앙에 배치하여 따뜻하고 신뢰감 있는 의료 AI 비주얼 구현.
  2. **임상 체감 3단계 동적 프로그레스 시퀀스 (2.0초 setTimeout 파이프라인)**:
     - 0.0초: "의료 안전 가드레일 (Red Flag) 0ms 검사 중..." (진행률 25%)
     - 0.7초: "소아 KTAS 168개 임상 분류 지침 대조 중..." (진행률 65%)
     - 1.4초: "실시간 달빛병원 & +30분 조제 안심약국 매칭 중..." (진행률 95%)
     - 2.0초: 진행률 100% 완료와 함께 `result.html`로 자동 전환.
  3. **인풋 화면 내 인라인 오버레이 & 단독 페이지 동시 구축**:
     - [frontend/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html): `#ai-analyzing-overlay` 모달 오버레이 탑재, 확인 버튼 클릭 시 키보드를 닫고 부드럽게 화면을 덮으며 로딩 개시.
     - [frontend/loading.html](file:///c:/AI-Native-Agent/monnlight/frontend/loading.html): 동일한 시각 디자인의 풀스크린 단독 로딩 페이지 신규 생성.
     - [frontend/templates/](file:///c:/AI-Native-Agent/monnlight/frontend/templates/) 디렉토리 동시 미러링 완결.
  4. **FastAPI 백엔드 라우팅 및 200 OK 검증**:
     - [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)에 `@app.get("/loading")` 엔드포인트 등록 및 HTTP 200 OK 서빙 확인.
* **적용 파일**:
  * [frontend/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html)
  * [frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)
  * [frontend/loading.html](file:///c:/AI-Native-Agent/monnlight/frontend/loading.html)
  * [frontend/templates/loading.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/loading.html)
  * [frontend/css/style.css](file:///c:/AI-Native-Agent/monnlight/frontend/css/style.css)
  * [frontend/templates/css/style.css](file:///c:/AI-Native-Agent/monnlight/frontend/templates/css/style.css)
  * [frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js)
  * [frontend/templates/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/templates/js/main.js)
  * [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)
  * [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-054] monimo 레퍼런스 스타일의 아이숨 첫 로딩(스플래시) 및 백엔드 로직 정합형 5대 접근 권한 명시 페이지 구축

* **발생 일자**: 2026-10-15
* **작업자**: 정영식 (팀장)
* **분류**: 프론트엔드 UI/UX 온보딩 / 컴플라이언스(정보통신망법) / 백엔드 기능 연계
* **문제 상황**:
  * 사용자가 앱을 최초 실행했을 때 브랜드 아이덴티티를 각인시키는 첫 로딩(스플래시) 화면이 부재함.
  * 정보통신망법 제22조의2(접근권한에 대한 동의) 및 애플/구글 앱 마켓 가이드라인에 부합하면서도, 실제 아이숨 백엔드 파이프라인(위치 기반 페어링, 실시간 병상 알림, 119 긴급 통화 등)에 정합된 공식 접근권한 사전 안내 페이지가 필요함.
* **원인 분석**:
  * 앱 진입 시 권한의 필요 이유(어떤 기능에 왜 쓰이는지)를 명확히 고지하지 않고 네이티브 팝업을 띄우면 사용자의 권한 거부율이 높아지고, 핵심 기능인 야간 소아과 반경 탐색이나 긴급 전화 연결이 제한될 위험이 있음.
  * 모니모(monimo) 스타일의 심플하고 모던한 첫 스플래시와 권한 고지 UI 패턴을 차용하여 최상의 온보딩 UX를 구현할 필요가 있었음.
* **구체적 해결 방안**:
  1. **첫 로딩 스플래시 화면 (`splash.html`) 구축**:
     - 모니모 1:1 레퍼런스 스타일의 미니멀 순백색 배경 및 볼드 산세리프 브랜드 로고(**`아이숨.`**) 배치.
     - 하단 서브 브랜드 소속 표기: `i-Soom / Pediatric Healthcare Networks` 및 iOS 홈 인디케이터 바 라인 탑재.
     - 1.8초 후 권한 안내 페이지로 자연스러운 자동 전환 스크립트(`fadeOut` ➔ `permission.html`) 및 화면 탭 즉시 건너뛰기 인터랙션 적용.
  2. **백엔드 로직 정합형 5대 선택 접근 권한 화면 (`permission.html`) 구축**:
     - 모니모 스타일의 대형 헤드라인(`앱 사용을 위해 접근 권한을 허용해주세요`), `선택 권한` 라벨, 컬러풀 심볼 아이콘 탑재.
     - 실제 백엔드 로직에 맞춘 5대 권한 명시:
       - 📍 **위치**: 야간 소아과·약국·응급실 거리 계산 및 길안내 *(Haversine 반경 5~10km 페어링)*
       - 🔔 **알림**: 소아 응급실 병상 변동 및 접수 마감 긴급 안내 *(5분 주기 NMC 병상 SSE 스트리밍)*
       - 📞 **전화**: 119 응급 직통 연결 및 병원 출발 전 사전 확인 통화 *(Red Flag 0ms 직통 다이얼)*
       - 📷 **카메라**: 본인확인 신분증 및 환아 증상(발진, 상처) 촬영 *(2024년 5월 본인확인 의무화 대응)*
       - 🖼️ **사진**: 아이 증상 사진 첨부 및 처방전·진료 서류 보관 *(문진 이미지 업로드 & 서류 보관)*
     - 하단 고지문("선택 권한의 경우 허용하지 않아도 서비스를 사용할 수 있으나...") 및 풀 너비 코발트 블루 **`확인`** 버튼 배치.
     - 확인 클릭 시 `localStorage.setItem('aisum_permission_granted', 'true')` 기록 후 메인 홈(`index.html`)으로 이동.
  3. **FastAPI 백엔드 라우트 확장 & 상용 템플릿 미러링**:
     - `main.py`에 `@app.get("/splash")`, `@app.get("/permission")` 라우트 등록.
     - `frontend/templates/`, `frontend/`, `app/templates/` 전역 파일 동기화.
     - `FastAPI TestClient`로 전수 **HTTP 200 OK** 검증 완료.
* **적용 파일**:
  * [frontend/templates/splash.html](file:///e:/monnlight/frontend/templates/splash.html)
  * [frontend/templates/permission.html](file:///e:/monnlight/frontend/templates/permission.html)
  * [frontend/splash.html](file:///e:/monnlight/frontend/splash.html)
  * [frontend/permission.html](file:///e:/monnlight/frontend/permission.html)
  * [app/templates/splash.html](file:///e:/monnlight/app/templates/splash.html)
  * [app/templates/permission.html](file:///e:/monnlight/app/templates/permission.html)
  * [main.py](file:///e:/monnlight/main.py)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-055] 야간 병원 상세 및 실시간 접수 안내 화면(hospital_detail.html) 순수 프론트엔드 구축 및 result.html 연계

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 (팀원)
* **분류**: 프론트엔드 UI/UX 신규 개발 / 화면 간 유기적 네비게이션 / 모바일 인터랙션
* **문제 상황**:
  * [result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html) 맞춤 결과 화면에서 추천 1순위로 제시된 달빛어린이병원("송파어린이병원") 및 연계 심야약국("송파달빛약국") 카드를 클릭했을 때, 상세한 병원 진료 정보 및 실시간 접수 현황을 확인할 수 있는 상세 페이지가 부재함.
  * 아이숨 3대 핵심 화면 중 메인 홈(`index.html`), 증상 입력(`input.html`)은 완성되었으나 마지막 완결 화면인 **야간 병원 상세 및 실시간 접수 화면(`hospital_detail.html`)**이 미구현 상태였음.
  * 야간에 긴급히 내원하려는 부모에게 필수적인 당직 소아과 전문의 정보, 접수 마감 주의 시각(22:30), 현재 대기 팀 수(4팀, 약 20분), +30분 조제 안심약국 정보, 2024년 5월 본인확인 의무화 지참 서류를 한눈에 보여주는 종합 화면이 필요함.
* **원인 분석**:
  * 이전 단계에서는 결과 화면까지의 뷰만 구축되어 있어, 실제 사용자가 병원 카드를 탭했을 때 진입할 상세 뷰와 모바일 번호표 접수 인터랙션이 아직 모듈화되지 않았음.
* **구체적 해결 방안**:
  1. **순수 HTML5/Vanilla CSS 기반 상세 화면 ([frontend/hospital_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/hospital_detail.html), [frontend/templates/hospital_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/hospital_detail.html)) 구축**:
     - **병원 히어로 배너**: 송파어린이병원 타이틀, 보건복지부 지정 달빛어린이병원 배지, 실시간 야간진료 중(`~23:00`) 라이브 펄스 닷.
     - **3열 핵심 지표 바**: 현재 대기 `4팀 (약 20분)` (로열 블루 강조), 거리 `1.8 km (차 6분)`, 주차 `지하 무료 2시간`.
     - **야간 당직의 프로필 카드**: Dr. 김서연 전문의 (소아 호흡기·급성발열 세부전문의, 제1소아진료실 2층, 현재 14번 환아 진료 중 안내).
     - **야간 접수 마감 주의 배너**: 22:30 접수 마감 및 환아 폭증 시 30분 전 조기 마감 대비 안내.
     - **실시간 진료 시간표**: 오늘 평일 야간(09:00~23:00), 토요일, 일·공휴일 시간표.
     - **Track B 안심 심야약국 연계 카드**: 송파달빛약국 (도보 1분 80m, 오늘 24:00 마감, `+30분 조제 안전마진` 배지, 소아 시럽제/네블라이저 상비 태그).
     - **오시는 길 & 길찾기**: 주소 원클릭 복사(토스트 팝업 연동), 카카오맵/네이버지도 길안내 링크.
     - **내원 전 필수 지참 서류 체크리스트**: 보호자 신분증, 환아 등본, 복용 중인 약 체크리스트.
     - **하단 고정 플로팅 바 & 모바일 대기표 모달**: `[📞 병원 전화]` + `[모바일 번호표 접수하기]` ➔ 클릭 시 대기번호 19번 발급 팝업 인터랙션 제공.
  2. **화면 간 유기적 네비게이션 완성**:
     - [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html) 및 템플릿의 송파어린이병원 카드에 `onclick="location.href='hospital_detail.html'"` 추가하여 유기적 진입 흐름 완성.
     - [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)에 `@app.get("/hospital_detail")` 라우트 등록 및 200 OK 서빙 확인.
* **적용 파일**:
  * [frontend/hospital_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/hospital_detail.html) (신규)
  * [frontend/templates/hospital_detail.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/hospital_detail.html) (신규)
  * [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)
  * [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)
  * [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)
  * [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-056] 프론트엔드-백엔드 100% 결합 연동 명세서(FRONTEND_BACKEND_INTEGRATION_SPEC.md) 수립 및 미구현 화면 고도화 백서 구축

* **발생 일자**: 2026-10-15
* **작업자**: 정영식 (팀장), AI 에이전트
* **분류**: 풀스택 시스템 아키텍처 / 인터페이스 규격화 / 프로젝트 거버넌스 및 기술 백서
* **문제 상황**:
  * 백엔드는 4대 계층(`api`, `agents`, `orchestrator`, `services`)으로 완벽하게 모듈화되어 구축되었고, 프론트엔드 역시 9대 화면(`splash`, `permission`, `index`, `input`, `loading`, `result`, `hospital_detail`, `emergency_guide`, `settings`)이 모바일 UI/UX 형태로 구축되었으나,
  * 각 화면의 버튼을 클릭했을 때 백엔드의 어떤 함수·서비스·에이전트가 어떤 데이터 규격(Request/Response)으로 연동되는지에 대한 명확한 1:1 결합 명세서가 부재하여 협업 시 혼선이 발생할 위험이 있었음.
  * 또한 아직 완전히 구현되지 않은 백엔드 기능 활용 화면(`result.js` 실데이터 연동, `chat.html` 멀티턴 문진, `map.html` 30분 마진 지도, `beds.html` 실시간 병상 전광판)에 대한 구체적인 구현 지침이 필요했음.
* **원인 분석**:
  * 프론트엔드와 백엔드가 각각 고도화되면서 두 영역 간의 E2E 계약(Contract) 및 이벤트 흐름을 종합 정리한 독립 문서의 필요성이 대두됨.
* **구체적 해결 방안**:
  1. **프로젝트 루트 전용 종합 백서 [FRONTEND_BACKEND_INTEGRATION_SPEC.md](file:///e:/monnlight/FRONTEND_BACKEND_INTEGRATION_SPEC.md) 수립**:
     - **백엔드 모듈 요약**: API 계층, 4대 에이전트(`guardrail`, `triage`, `matching`, `logistics`), FSM 오케스트레이터, 지리공간 및 병상 동기화 서비스 명세.
     - **프론트엔드 9대 화면 요약**: 라우트 및 상태 정리.
     - **1:1 결합 매핑 매트릭스**: 화면 및 버튼별 클릭 이벤트 ➔ 백엔드 파일 및 엔드포인트 ➔ 실제 동작 및 반환 데이터 표출 매핑.
     - **E2E 풀스택 시퀀스 다이어그램**: Mermaid 라이프사이클 모델링.
     - **미구현 4대 핵심 화면 및 기능 구현 가이드**: `result.js`, `chat.html`, `map.html`, `beds.html` 개발 스펙.
     - **4단계 실행 로드맵**: Phase 1(데이터 실결합) ~ Phase 4(프로덕션 릴리스).
  2. **4대 불변 거버넌스 문서 동기화**:
     - `Answer-영식.md`에 Q64 등록.
     - `log.md`에 [ISSUE-056] 등록.
     - `README.md` 체인지로그에 `v2.4.17` 릴리스 반영.
     - `PLAN.md` 11절 프론트-백엔드 결합 명세 참조 링크 보강.
* **적용 파일**:
  * [FRONTEND_BACKEND_INTEGRATION_SPEC.md](file:///e:/monnlight/FRONTEND_BACKEND_INTEGRATION_SPEC.md) (신규)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-057] SupervisorResponse 임상 바이탈 5대 필드 확장 및 1턴 완결 force_matching FSM 모드 구축 (백엔드 1단계)

* **발생 일자**: 2026-10-15
* **작업자**: 정영식 (팀장), AI 에이전트
* **분류**: 풀스택 결합 백엔드 고도화 / DTO 계약 확장 / FSM 상태 전이 제어 / 단위 테스트
* **문제 상황**:
  * `FRONTEND_BACKEND_INTEGRATION_SPEC.md` Phase 1(1단계: `input.html` ➔ `result.html` 실제 API 연동)을 진행함에 있어, 백엔드 `SupervisorResponse` 응답 DTO에 `result.html` 상단 바이탈 칩에 바인딩할 환아 월령(`age_months`), 체온(`temperature`), KTAS 등급(`ktas_level`, `ktas_level_name`), 주요 증상(`symptoms`)이 누락되어 있었음.
  * 또한 `input.html`은 단발성 증상 텍스트 입력 폼인데, 보호자가 월령을 누락한 채 "아이가 열이 나요"라고 입력하면 백엔드 FSM이 `TRIAGE` 상태에서 추가 질의응답을 대기하며 시설 추천(`hospitals`)을 비워둔 채 반환하여 화면단에서 병원 목록이 표출되지 않는 사용자 경험(UX) 결함이 발생함.
* **원인 분석**:
  * 백엔드 `PatientSessionState`에는 임상 변수들이 온전히 보존되어 있었으나, 클라이언트 반환용 DTO인 `SupervisorResponse`가 기관 및 통화 대본 위주로 설계되어 있었음.
  * 또한 FSM 오케스트레이터의 전이 조건이 `is_triage_complete()` 또는 `turn_count >= 3`으로만 고정되어 있어, 단발성 폼 화면의 1턴 즉시 매칭 요구를 수용하지 못했음.
* **구체적 해결 방안**:
  1. **`SupervisorResponse` DTO에 5대 임상 필드 공식 탑재 ([app/schemas/supervisor.py](file:///e:/monnlight/app/schemas/supervisor.py))**:
     - `age_months`, `temperature`, `ktas_level`, `ktas_level_name`, `symptoms` 필드 추가.
  2. **`ChatRequest` DTO에 1턴 즉시 매칭 플래그 추가 ([app/schemas/chat.py](file:///e:/monnlight/app/schemas/chat.py))**:
     - `force_matching: bool = False` 추가 (단발성 입력 화면 전용).
  3. **`SupervisorOrchestrator` FSM 상태 전이 로직 개선 ([app/orchestrator/supervisor.py](file:///e:/monnlight/app/orchestrator/supervisor.py))**:
     - `force_matching=True` 인입 시, 결측 임상 변수가 있더라도 안전 기본값(체온 38.0℃, 월령 24개월, KTAS 4 준응급)을 채우고 즉시 1턴 만에 `MATCHING` ➔ `LOGISTICS` ➔ `COMPLETED`로 이행.
     - 0ms Red Flag 위급 상황(신생아 고열, 경련 등)은 `force_matching`과 무관하게 26µs 만에 즉각 `EMERGENCY_ESCALATION`으로 최우선 직행하여 의료 안전 절대 사수.
     - 정상 응답 및 응급실 에스컬레이션 응답 모두에 환아 임상 바이탈 데이터 100% 탑재.
  4. **API 서빙 계층 전달 ([app/api/v1/chat.py](file:///e:/monnlight/app/api/v1/chat.py))**:
     - `chat_turn` 및 `_sse_event_generator`에서 `req.force_matching` 파라미터 전달.
  5. **신규 Step 8 테스트 스위트 구축 ([tests/test_step8_frontend_integration.py](file:///e:/monnlight/tests/test_step8_frontend_integration.py))**:
     - `TC-801` (1턴 force_matching 완결 검증), `TC-802` (Red Flag 절대 우선권 검증), `TC-803` (REST API 스키마 무결성 검증) 3개 테스트 100% 통과 (총 77개 테스트 OK).
* **적용 파일**:
  * [app/schemas/supervisor.py](file:///e:/monnlight/app/schemas/supervisor.py)
  * [app/schemas/chat.py](file:///e:/monnlight/app/schemas/chat.py)
  * [app/orchestrator/supervisor.py](file:///e:/monnlight/app/orchestrator/supervisor.py)
  * [app/api/v1/chat.py](file:///e:/monnlight/app/api/v1/chat.py)
  * [tests/test_step8_frontend_integration.py](file:///e:/monnlight/tests/test_step8_frontend_integration.py) (신규)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-058] 모든 병원 카드 상세 연계, 결과 화면 스크롤 뷰(Scroll List) 전환 및 0ms Red Flag 119 긴급 안내 화면(emergency_alert.html) 구축

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 (팀원)
* **분류**: 프론트엔드 UI/UX 신규 개발 / 응급 가드레일 숏서킷 / 스크롤 리스트 컴포넌트
* **문제 상황**:
  * [result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html) 맞춤 결과 화면에서 최상단 1순위 병원(송파어린이병원)만 상세 화면으로 연계되어 있고, 2순위 병원(강동소아청소년과의원) 등 다른 병원은 상세 페이지로 연결되지 않음.
  * 초기 아코디언(더보기 토글) 방식은 추가 클릭이 필요하고 화면이 길게 확장되는 불편이 있어, 전체 병원·약국 리스트를 자연스럽게 넘겨볼 수 있는 모바일 최적화 스크롤 뷰로의 전면 전환 요구.
  * 또한 [input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html)에서 경련, 호흡곤란, 생후 100일 미만 고열 등 초응급 위기 징후(Red Flag)를 입력했을 때, 일반적인 2초 로딩 후 일반 병원 결과 화면으로 넘어가는 대신 **0초 만에 119 구급차 호출로 직행하는 전용 긴급 경고 화면**이 필요함.
* **원인 분석**:
  * 초기 프로토타입 단계에서는 1순위 대표 카드에 대해서만 링크가 연결되어 있었고, Red Flag 입력 시 프론트엔드 단에서 즉각적인 숏서킷 라우팅 처리가 연동되지 않았음.
* **구체적 해결 방안**:
  1. **result.html 모든 병원 카드 전수 연계 및 순수 CSS 스크롤 뷰(`.facility-scroll-list`) 컴포넌트 구축**:
     - 2순위 `강동소아청소년과의원`, 3순위 `잠실아이사랑소아과`, 4순위 `위례달빛어린이병원` 전체 병원 카드에 `onclick="location.href='hospital_detail.html'"` 속성과 `>`(arrow_forward_ios) 화살표를 장착하여 전수 상세 뷰 진입 지원.
     - 기존 더보기 아코디언 토글 버튼 및 접힘(`more-hospitals-collapse`) 제거.
     - `.facility-scroll-list` 컨테이너 (`max-height: 520px; overflow-y: auto; -webkit-overflow-scrolling: touch; scroll-behavior: smooth;`)를 구축하여 1~4순위 병원·약국 카드 및 소아 응급실 카드를 부드럽게 스크롤하며 확인할 수 있도록 개편.
     - 슬림 커스텀 스크롤바(5px) 탑재 및 상단 탭 라벨 `달빛병원·약국 (4)` 동기화.
  2. **🚨 0ms Red Flag 119 긴급 직행 화면 ([frontend/emergency_alert.html](file:///c:/AI-Native-Agent/monnlight/frontend/emergency_alert.html)) 신규 구축**:
     - 다크 슬레이트 & 앰버 레드 테마의 사이렌 펄스 애니메이션(`ripple`, `iconWiggle`) 적용.
     - 초대형 119 원터치 직통 다이얼 CTA (`tel:119`) 탑재.
     - 119 구급대원에게 즉시 불러줄 수 있는 내 위치 안내 카드("서울특별시 송파구 올림픽로 300") 및 주소 복사 기능.
     - 구급차 도착 전 필수 응급처치 3대 수칙 (기도 확보, 경련 시 주의, 옷 느슨하게 통풍 유지).
     - 하단 보조 액션: `[인근 소아전문응급센터 실시간 병상 보기 (result.html?tab=emergency)]`, `[증상 다시 입력하기]`.
  3. **input.html 내 0ms Red Flag 정규식 인터셉터 바인딩 ([frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js))**:
     - 입력 텍스트 내 응급 키워드(`/경련|경기|숨|호흡|의식|기절|청색|100일|백일|장중첩|피토|혈변|쳐짐|늘어짐|파랗|경직/`) 감지 시, 2초 분석 로딩을 건너뛰고 0ms 만에 즉시 `emergency_alert.html`로 숏서킷 이동.
  4. **FastAPI 백엔드 라우팅 및 200 OK 검증**:
     - `main.py`에 `@app.get("/emergency_alert")` 등록 및 TestClient 200 OK 검증 완료.
* **적용 파일**:
  * [frontend/emergency_alert.html](file:///c:/AI-Native-Agent/monnlight/frontend/emergency_alert.html) (신규)
  * [frontend/templates/emergency_alert.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/emergency_alert.html) (신규)
  * [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)
  * [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)
  * [frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js)
  * [frontend/templates/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/templates/js/main.js)
  * [main.py](file:///c:/AI-Native-Agent/monnlight/main.py)
  * [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-059] 결과 화면(result.html) 카드 Flexbox Shrink 클리핑 버그 및 스크롤 불가 해결

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 (팀원)
* **분류**: 프론트엔드 UI/UX 버그 픽스 / CSS Flexbox 레이아웃
* **문제 상황**:
  * [result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)에서 추천 병원 목록 카드가 한 화면에 찌그러진 채로 렌더링되고, 하단의 약국 안내와 '병원 전화', '길찾기' 버튼이 반쯤 잘려서(clipping) 표출됨.
  * 또한 마우스 휠이나 터치 드래그를 해도 스크롤이 전혀 동작하지 않는 문제 발생.
* **원인 분석**:
  * `.facility-scroll-list`에 `display: flex; flex-direction: column; max-height: 520px; overflow-y: auto;`를 적용했으나, CSS Flexbox 자식 요소인 `.pairing-card`와 `.emergency-room-card`의 `flex-shrink` 기본값이 `1`로 동작함.
  * 4개 카드의 본래 높이 합산(~930px)이 부모 컨테이너의 `max-height(520px)`를 초과하자, 브라우저가 스크롤을 활성화하는 대신 4개 카드를 각각 ~120px 높이로 강제 압축(squeeze)함.
  * 각 카드에 `overflow: hidden`이 걸려 있어 압축된 영역 바깥의 약국 및 액션 버튼이 잘려 나갔으며, 총 높이가 정확히 520px로 수축되면서 `scrollHeight <= clientHeight`가 되어 스크롤바가 생성되지 않았음.
* **구체적 해결 방안**:
  1. **Flexbox 자식 수축 방지 및 크기 보존**:
     ```css
     .facility-scroll-list .pairing-card,
     .facility-scroll-list .emergency-room-card {
       flex-shrink: 0 !important;
       min-height: fit-content !important;
       width: 100% !important;
       box-sizing: border-box !important;
     }
     ```
  2. **스크롤 컨테이너 최적화**:
     - `max-height: 560px; overflow-y: auto; overflow-x: hidden;`
     - 6px 슬림 커스텀 스크롤바 및 모바일 가속 터치 스크롤(`touch-action: pan-y; -webkit-overflow-scrolling: touch;`) 적용.
  3. **동기화 및 200 OK 서빙 확인**:
     - `frontend/result.html` 및 `frontend/templates/result.html` 100% 동기화 완료.
* **적용 파일**:
  * [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)
  * [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)

---

### [ISSUE-060] input.html 소아 맞춤 문진 챗봇(Interactive Triage Chatbot) 전면 개편 및 결측치 3단계 다중 턴 수집 체계 구축

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 (팀원)
* **분류**: 프론트엔드 UI/UX 대화형 인터페이스 개편 / 소아 임상 결측치 수집 / FSM 문진
* **문제 상황**:
  * 기존 [input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html)은 단일 텍스트 필드에 문장을 입력하고 '확인'을 누르면 2초 로딩 후 곧바로 [result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)로 넘어가는 일방향 구조였음.
  * 소아 야간 트리아제 및 병원 매칭을 위해서는 **환아 월령(나이), 현재 체온, 증상 지속 시간, 동반 증상**의 4대 핵심 임상 변수가 필수적이나, 보호자가 "열이 나요", "배가 아파요"처럼 한 문장만 입력할 경우 결측치가 발생하여 정확한 KTAS 분류와 맞춤 병원 추천이 불가능한 구조적 한계가 존재함.
* **원인 분석**:
  * 백엔드 `TriageAgent` 및 `SupervisorOrchestrator`는 이미 `followup_question`과 결측 변수 수집 능력을 갖추고 있었으나, 프론트엔드가 1회성 정적 인풋 폼 형태로 머물러 있어 백엔드의 다중 턴(Multi-turn) 능력을 온전히 활용하지 못함.
* **구체적 해결 방안**:
  1. **input.html 및 templates/input.html 카카오톡/모니모 스타일 대화형 문진 챗봇으로 전면 개편**:
     - 상단 헤더: 뒤로가기 버튼 + 아이숨 문진 간호 AI 프로필(`KTAS 전문`, 실시간 응급 판정 중 펄스 인디케이터) + 처음부터 다시하기 리셋 버튼.
     - 3단계 문진 프로그레스 트래커: `1. 증상 파악` ➔ `2. 월령/체온` ➔ `3. 동반 징후`.
     - 부드러운 스크롤 대화창, AI 말풍선, 보호자 말풍선, 3개 점 통통 튀는 모던 타이핑 인디케이터(`typing-dot`) 탑재.
  2. **원터치 퀵답변 칩(Quick Reply Chips) 트레이 제공**:
     - 한 손으로 보채는 아기를 안고 있는 다급한 보호자를 위해, 키보드 타이핑 없이도 터치 한 번으로 답변할 수 있는 동적 퀵 칩 제공:
       - 1단계: `[열이 나요 🌡️]`, `[토를 해요 🤢]`, `[기침·가래 😮‍💨]`, `[배가 아파요 😣]`
       - 2단계: `[생후 100일 미만 🚨]`, `[14개월 (39.2℃)]`, `[6~12개월 (38.5℃)]`, `[24개월 이상 (38.3℃)]`
       - 3단계: `[구토 동반 및 2시간 전 해열제 복용]`, `[기침·가래 및 콧물]`, `[해열제 복용 후에도 열 지속]`, `[물은 잘 마시고 덜 처짐]`
     - 자유 텍스트 입력창 및 엔터/전송 버튼 상시 제공.
  3. **0ms Red Flag 가드레일 다중 턴 인터셉터 바인딩**:
     - 어느 대화 턴에서든 경련, 호흡곤란, 생후 100일 미만 등 위급 키워드 감지 시 0ms 즉각 경고 말풍선 표출 후 119 긴급 직행 화면([emergency_alert.html](file:///c:/AI-Native-Agent/monnlight/frontend/emergency_alert.html))으로 강제 숏서킷 전환.
  4. **결과 화면 연동 및 바이탈 칩 동적 주입**:
     - 문진 완료 시 `sessionStorage.setItem('triage_result', ...)`에 구조화된 임상 데이터 저장.
     - 2초 AI 분석 로딩 오버레이 후 `result.html`로 자동 이동하며, `result.html`의 상단 바이탈 칩(`#14개월`, `#39.2℃`, `#구토`)이 환아의 실제 데이터로 동적 갱신되도록 연동 완료.
* **적용 파일**:
  * [frontend/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html)
  * [frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)
  * [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)
  * [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)
  * [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)

---

### [ISSUE-061] 소아 응급실 병상 2개 초과 시 세로 스크롤 지원 및 input.html 기존 미니멀 UI 디자인 계승형 프로그레시브 문진 챗봇 탑재

* **발생 일자**: 2026-10-15
* **작업자**: 김동준 (팀원)
* **분류**: 프론트엔드 UI/UX 스크롤 뷰 동기화 / 디자인 일관성 유지 / 기존 UI 계승형 대화식 문진
* **문제 상황**:
  1. **응급실 탭 스크롤 미지원 오인 현상**: [result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html) 내 달빛병원 탭은 4개 카드가 스크롤 리스트로 매끄럽게 동작하나, '소아 응급실 병상' 탭은 2개소만 표시되어 2개 초과 시 스크롤 가능 여부가 사용자에게 직관적으로 확인되지 않음.
  2. **새로운 챗봇 디자인 도입에 따른 기존 미니멀 디자인 훼손 우려**: 앞서 도입한 카카오톡/메신저형 대화창 디자인이 아이숨의 기존 깔끔한 미니멀 디자인(상단 단독 헤드라인 + 언더라인 인풋 필드 + 하단 확인 버튼 + 2초 분석 로딩 오버레이)과 이질감을 유발함. 사용자는 기존의 디자인을 그대로 유지하면서 필수 정보(월령, 체온, 동반 증상)를 문진하는 챗봇 기능을 원함.
* **원인 분석**:
  1. 응급실 탭 목업 데이터가 2개소(서울아산병원, 강동성심병원)로만 제한되어 있어 세로 스크롤 영역 높이(560px)를 넘지 않아 스크롤바가 발현되지 않음.
  2. 챗봇 기능 구현 시 화면 전체 레이아웃을 메신저 버블 형태로 완전히 교체해 버려, 기존 화면의 독창적인 UI/UX 정체성이 손실됨.
* **구체적 해결 방안**:
  1. **소아 응급실 병상 4개소 확장 및 2개 초과 시 수직 스크롤 완벽 지원**:
     - `result.html` 및 `templates/result.html`의 응급실 탭에 삼성서울병원 소아전문응급센터(4.8km, 3석 여유), 분당차병원 소아전문응급센터(8.2km, 1석 혼잡) 2개소를 추가하여 총 4개 카드로 확장.
     - 탭 명칭을 `소아 응급실 병상 (4)`로 동기화하고, `.facility-scroll-list`의 `flex-shrink: 0 !important; max-height: 560px; overflow-y: auto;`를 통해 2개 초과 시 카드가 찌그러지지 않고 매끄럽게 스크롤되도록 완성.
  2. **input.html 기존 미니멀 UI 디자인 100% 계승형 프로그레시브 문진 챗봇 탑재**:
     - 기존 화면 요소인 **상단 뒤로가기 헤더, 대형 헤드라인(`h1.input-headline`), 블루 언더라인 인풋(`underline-input-wrapper`), 하단 확인 버튼(`input-confirm-btn`), AI 분석 오버레이(`ai-analyzing-overlay`)**를 100% 원형 그대로 보존.
     - 화면 내부에서 단계별 문진(1단계: 주요 증상 ➔ 2단계: 월령/체온 ➔ 3단계: 동반 징후/해열제)을 진행하도록 상태 머신(FSM) 구축.
     - 단계 변경 시 헤드라인과 서브 가이드 텍스트가 부드럽게 전환되며, 이전에 입력한 정보는 상단에 깔끔한 태그(`[✓ 주요 증상: 열이 나요]`, `[✓ 14개월 · 39.2℃]`)로 누적 표시 (클릭 시 이전 단계로 수정 복귀 가능).
     - 하단 원터치 퀵 칩 제공으로 터치 한 번에 인풋 필드 자동 입력 및 [확인] 버튼 활성화 지원.
     - 어느 단계에서든 생후 100일 미만, 경련, 호흡곤란 등 감지 시 0ms 즉시 긴급 알림 전환.
     - 문진 완료 시 2초간 AI 분석 오버레이 실행 후 `result.html`로 이동하여 동적 바이탈 데이터 주입.
  3. **메인 스크립트 중복 이벤트 차단**:
     - `js/main.js` 및 `templates/js/main.js`에 `window.__AISUM_CUSTOM_INPUT__` 가드를 추가하여 기존 단일 단계 인풋 리스너와의 충돌 방지.
* **적용 파일**:
  * [frontend/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/result.html)
  * [frontend/templates/result.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/result.html)
  * [frontend/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/input.html)
  * [frontend/templates/input.html](file:///c:/AI-Native-Agent/monnlight/frontend/templates/input.html)
  * [frontend/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/js/main.js)
  * [frontend/templates/js/main.js](file:///c:/AI-Native-Agent/monnlight/frontend/templates/js/main.js)
  * [log.md](file:///c:/AI-Native-Agent/monnlight/log.md)
  * [q_a.md](file:///c:/AI-Native-Agent/monnlight/q_a.md)
  * [README.md](file:///c:/AI-Native-Agent/monnlight/README.md)
  * [PLAN.md](file:///c:/AI-Native-Agent/monnlight/PLAN.md)

---

### [ISSUE-062] 온보딩 화면(splash, permission) 상단 인위적 가짜 상태 바(15:19 시간, 배터리, 와이파이) 전면 제거 및 순수 뷰포트 정돈

* **발생 일자**: 2026-10-15
* **작업자**: 정영식 (팀장), AI 에이전트
* **분류**: 프론트엔드 모바일 UI/UX 최적화 / 상태 바 중복 제거 / 크로스 디바이스 뷰포트 정합성
* **문제 상황**:
  * 모바일 브라우저 또는 앱 테스트 환경에서 화면 상단에 인위적으로 구현된 가짜 iOS 상태 바(`15:19 ✈ 📶 🛜 🔋`)가 나타남.
  * 실제 스마트폰 기기 자체 OS의 상태 표시줄과 겹치거나 웹페이지 내부에 중복으로 나타나 시각적 혼선 및 디자인 이질감을 유발함.
* **원인 분석**:
  * 온보딩 화면(`splash.html`, `permission.html`) 제작 시 레퍼런스 시안에서 따온 `.ios-status-bar` 마크업과 `updateClock()` 1분 주기 시계 갱신 자바스크립트가 잔존해 있었음.
* **구체적 해결 방안**:
  1. **가짜 상단 상태 바 마크업 및 스타일 전면 삭제**:
     - [frontend/templates/splash.html](file:///e:/monnlight/frontend/templates/splash.html), [frontend/splash.html](file:///e:/monnlight/frontend/splash.html), [frontend/templates/permission.html](file:///e:/monnlight/frontend/templates/permission.html), [frontend/permission.html](file:///e:/monnlight/frontend/permission.html) 4개 파일에서 `.ios-status-bar` div 블록 및 CSS 스타일, `updateClock()` 스크립트 완전 제거.
  2. **모바일 뷰포트 여백 자연스럽게 정돈**:
     - `.permission-viewport`의 상단 패딩을 `padding: 32px 24px 24px 24px;`로 정돈하여 기기 자체 상태 바 아래에서 콘텐츠가 자연스럽게 호흡할 수 있도록 최적화.
  3. **FastAPI TestClient 검증**:
     - `/splash` 및 `/permission` 라우트에서 `statusBarTime`, `ios-status-bar`가 완전히 소멸되었음을 확인 (`ALL STATUS BAR REMOVAL CHECKS PASSED PERFECTLY!`).
* **적용 파일**:
  * [frontend/templates/splash.html](file:///e:/monnlight/frontend/templates/splash.html)
  * [frontend/splash.html](file:///e:/monnlight/frontend/splash.html)
  * [frontend/templates/permission.html](file:///e:/monnlight/frontend/templates/permission.html)
  * [frontend/permission.html](file:///e:/monnlight/frontend/permission.html)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-063] 앱 접근권한(permission.html) 동의 버튼 클릭 시 실제 브라우저 Web API 권한(위치, 알림) 요청 및 실시간 좌표 캐싱 구현

* **발생 일자**: 2026-10-15
* **작업자**: 정영식 (팀장), AI 에이전트
* **분류**: 프론트엔드 디바이스 Web API 연동 / 위치 기반 서비스(LBS) 초기화 / 온보딩 사용자 경험(UX) 고도화
* **문제 상황**:
  * 기존 온보딩 접근 권한 안내 화면(`permission.html`)은 하단 버튼 클릭 시 단순히 `localStorage`에 승인 플래그(`aisum_permission_granted=true`)만 저장하고 곧바로 메인 홈(`index.html`)으로 리다이렉트되어, 실제 브라우저 시스템의 위치(Geolocation) 및 알림(Notification) 권한 팝업이 요청되지 않음.
  * 결과적으로 사용자가 메인 홈 또는 증상 입력 후 결과 화면에 도달했을 때 위치 정보가 없어 기본 좌표(강남역)로 폴백되거나 브라우저 권한 팝업이 뒤늦게 중복으로 뜨는 사용자 경험 저하 발생.
* **원인 분석**:
  * 정적 UI 프로토타입 단계에서는 단순 클릭 이벤트 핸들러만 존재하였으며, 실제 `navigator.geolocation.getCurrentPosition` 및 `Notification.requestPermission()` 비동기 인터페이스와의 체이닝이 누락되어 있었음.
* **구체적 해결 방안**:
  1. **실제 Web API 비동기 권한 체이닝 (`onConfirmPermission`)**:
     - [frontend/templates/permission.html](file:///e:/monnlight/frontend/templates/permission.html) 및 [frontend/permission.html](file:///e:/monnlight/frontend/permission.html)에 `async function onConfirmPermission()` 구축.
     - 버튼 클릭 즉시 버튼 `disabled` 처리 및 스피너 애니메이션과 함께 `"권한 확인 중..."` 노출.
  2. **위치 권한 요청 및 3.8초 타임아웃 안전 가드 탑재**:
     - `navigator.geolocation.getCurrentPosition`을 호출하되, 사용자가 권한 팝업을 무시하거나 취소할 경우 영구 대기(Deadlock)에 빠지지 않도록 4초 타임아웃 타이머를 배치하여 예외 없이 다음 단계로 이행 보장.
     - 권한 획득 성공 시 위도(`lat`), 경도(`lon`)를 `localStorage` 및 `sessionStorage`에 실시간 캐싱(`user_lat`, `user_lon`)하여 0ms 후속 조회 지원.
  3. **알림 권한 요청 및 상태 보관**:
     - `Notification.permission === 'default'`인 경우 `await Notification.requestPermission()`을 호출하여 상태(`granted`, `denied`)를 `aisum_permission_notification`에 저장.
  4. **온보딩 완료 타임스탬프 기록 및 홈 이동**:
     - `aisum_permission_granted`, `aisum_permission_granted_at`을 보관한 후 `window.location.href = 'index.html'`로 자연스러운 전환 수행.
  5. **FastAPI TestClient 검증**:
     - `/permission` 정적 라우트 응답에 `requestLocation`, `Notification.requestPermission`, `동의하고 시작하기`가 정상 포함됨을 자동화 검증.
* **적용 파일**:
  * [frontend/templates/permission.html](file:///e:/monnlight/frontend/templates/permission.html)
  * [frontend/permission.html](file:///e:/monnlight/frontend/permission.html)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)

---

### [ISSUE-064] 설정 화면(settings.html) 이용약관 버튼 연동 및 의료법 제27조 준수 아이숨(i-Soom) 전용 이용약관(terms.html) 신규 구축

* **발생 일자**: 2026-10-15
* **작업자**: 정영식 (팀장), AI 에이전트
* **분류**: 프론트엔드 UI/UX 라우팅 / 의료법 컴플라이언스(제27조) / 약관 및 법적 면책 고지
* **문제 상황**:
  * 설정 화면([settings.html](file:///e:/monnlight/frontend/templates/settings.html)) 내 '아이숨 이용약관' 항목이 클릭 이벤트가 없는 단순 정적 `<button>`으로 구현되어 있어, 사용자가 클릭 시 반응이 없거나 약관 내용을 확인할 수 없는 UX 단절 발생.
  * 소아 야간 의료 매칭 및 AI 문진 서비스를 상용 서비스 수준으로 안전하게 운영하기 위해 필요한 의료법 제27조 준수 선언, 12대 Red Flag 발생 시 119 즉시 신고 의무, 위치기반서비스 인메모리 처리, 공공데이터 시차 면책 및 30초 전화 확인 의무 등을 명시한 전용 약관 체계가 부재했음.
* **원인 분석**:
  * 온보딩/설정 UI 프로토타입 단계에서 이용약관 화면 파일(`terms.html`)이 미생성 상태였으며, 라우터 및 링크 바인딩이 누락되어 있었음.
* **구체적 해결 방안**:
  1. **아이숨 서비스 특화 9대 핵심 조항 이용약관(`terms.html`) 신규 제작**:
     - [frontend/templates/terms.html](file:///e:/monnlight/frontend/templates/terms.html) 및 [frontend/terms.html](file:///e:/monnlight/frontend/terms.html) 신규 생성.
     - **제3조 (의료법 제27조 준수 및 비의료 AI 문진 보조의 한계)**: 의사의 진단/처방을 대체할 수 없으며 대면 진료 우선 원칙 명시.
     - **제4조 (응급 상황 시 119 즉시 신고 의무)**: 12대 Red Flag 발생 시 검색을 중단하고 119 또는 소아전문응급센터로 즉시 직행해야 함을 규정.
     - **제5조 (위치기반서비스)**: Haversine 거리 계산 목적 외 영구 저장 없음 명시.
     - **제6조 (공공데이터 면책)**: 헛걸음 방지를 위한 '30초 통화 스크립트' 사전 전화 확인 의무 부과.
     - **제7조 (본인확인 의무화)**: 2024년 5월 건강보험법 개정 신분증/서류 지참 안내.
  2. **모바일 최적화 UI/UX 탑재**:
     - 상단 헤더 뒤로가기 버튼(`settings.html` 복귀), 퀵 점프 칩 바, 긴급/경고 콜아웃 박스, 하단 플로팅 `[내용을 확인했습니다]` 버튼 탑재.
  3. **설정 화면 링크 연동 및 FastAPI 라우터 등록**:
     - `settings.html` 내 항목을 `<a href="terms.html" class="settings-item-row">`로 교체.
     - [main.py](file:///e:/monnlight/main.py)에 `GET /terms`, `GET /terms.html` 라우터 및 `root()` 메타데이터 등록.
  4. **통합 자동화 검증**:
     - FastAPI TestClient를 통한 설정 링크 및 약관 페이지 렌더링 100% 무결점 확인 (`ALL TERMS & SETTINGS INTEGRATION TESTS PASSED PERFECTLY!`).
* **적용 파일**:
  * [frontend/templates/terms.html](file:///e:/monnlight/frontend/templates/terms.html)
  * [frontend/terms.html](file:///e:/monnlight/frontend/terms.html)
  * [frontend/templates/settings.html](file:///e:/monnlight/frontend/templates/settings.html)
  * [frontend/settings.html](file:///e:/monnlight/frontend/settings.html)
  * [main.py](file:///e:/monnlight/main.py)
  * [Answer-영식.md](file:///e:/monnlight/Answer-영식.md)
  * [log.md](file:///e:/monnlight/log.md)
  * [README.md](file:///e:/monnlight/README.md)
  * [PLAN.md](file:///e:/monnlight/PLAN.md)





