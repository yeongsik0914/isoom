# [실전 가이드] 테스트 완료 파이프라인 기반 백엔드 & 멀티 에이전트 단계별 구현 로드맵

> **기반 문서**:
> * [MoonlightCare 종합 기획안 (docs/PROJECT_PLAN.md)](file:///e:/monnlight/docs/PROJECT_PLAN.md)
> * [질의응답 아카이브 (Answer.md)](file:///e:/monnlight/Answer.md)
> * [검증 완료 노트북 (notebooks/emergency_bed_firebase_sync.ipynb)](file:///e:/monnlight/notebooks/emergency_bed_firebase_sync.ipynb)
>
> **문서 목적**: 주피터 노트북에서 실데이터(서울 50개소 응급실)와 Firebase로 100% 검증을 마친 코드를 기반으로, **"어떤 순서로 백엔드 코드를 짜야 하고, 에이전트는 언제 투입하며, 각 단계마다 어떻게 테스트해야 하는지"**를 단계별로 명확하게 제시하는 실전 실행 로드맵입니다.

---

## 🧭 1. 엔지니어링 철학: "에이전트는 왜 나중에 투입하는가?"

많은 AI 프로젝트가 실패하는 가장 흔한 이유는 **"에이전트가 호출할 기본 백엔드 도구(Tool)와 데이터베이스도 없는데, LLM 프롬프트부터 먼저 짜기 때문"**입니다. 그렇게 하면 에이전트가 호출할 실제 함수가 없어 환각(Hallucination)만 일으키고 테스트가 불가능해집니다.

올바른 엔지니어링 순서는 **"바텀업(Bottom-Up) 조립 방식"**입니다:

```
[1단계: 기반 스토리지 & Zero-LLM 도구] ──► 노트북에서 검증한 순수 파이썬 함수 모듈화
         │
         ▼
[2단계: 0ms 안전 가드레일 & 세션 DTO] ──► 119 Red Flag 즉시 분기 및 상태 객체 정의
         │
         ▼
[3단계: AI 에이전트 결합 (Gemini 3.8)] ──► 준비된 도구와 가드레일을 장착한 문진 에이전트 투입
         │
         ▼
[4단계: 메인 오케스트레이터 (Supervisor)] ──► 에이전트와 도구를 조율하는 결정론적 FSM 상태머신 조립
         │
         ▼
[5단계: FastAPI API 서빙 & 백그라운드] ──► 클라이언트와 통신할 REST API & 5분 주기 자동 동기화 데몬
         │
         ▼
[6단계: E2E 통합 테스트 & 시나리오 검증] ──► 실제 부모 시나리오 기반 종합 테스트
```

---

## 🗂️ 2. 최종 완성될 백엔드 디렉터리 구조 (`app/`)

```
monnlight/
├── app/
│   ├── __init__.py
│   ├── config.py                     # [Step 1] 환경변수 및 Firebase 키 로더
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── state.py                  # [Step 2] 공유 세션 메모리 DTO (PatientSessionState)
│   │   └── emergency.py              # [Step 1] 응급실 병상 Pydantic 모델
│   ├── services/                     # [Step 1] 노트북에서 검증한 핵심 순수 로직 (Zero-LLM)
│   │   ├── __init__.py
│   │   ├── holiday_service.py        # KASI 특일 판정 (노트북 Cell 3)
│   │   ├── emergency_sync_service.py # E-Gen 수집 & Hash Diffing & Firestore 적재 (노트북 Cell 4, 5, 7)
│   │   └── spatial_service.py        # Haversine 구면거리 계산 & 10km 랭킹 (노트북 Cell 8)
│   ├── agents/                       # [Step 2~3] 에이전트 레이어
│   │   ├── __init__.py
│   │   ├── guardrail_agent.py        # 0ms Red Flag 인터셉터 & 진단명 필터 (Step 2)
│   │   ├── matching_agent.py         # services를 도구로 호출하는 매칭 에이전트 (Step 3)
│   │   ├── triage_agent.py           # Gemini 3.8 Flash 부모 문진 에이전트 (Step 3)
│   │   └── logistics_agent.py        # 서류 체크리스트 & 30초 전화 스크립트 (Step 3)
│   ├── orchestrator/                 # [Step 4] 중앙 오케스트레이션
│   │   ├── __init__.py
│   │   └── supervisor.py             # 결정론적 FSM 상태 전이 라우터
│   └── api/                          # [Step 5] 외부 통신 API 라우터
│       ├── __init__.py
│       └── v1/
│           ├── __init__.py
│           ├── chat.py               # POST /api/v1/chat (에이전트 대화)
│           └── emergency.py          # GET /api/v1/emergency/nearby (주변 응급실 5ms 조회)
├── main.py                           # [Step 5] FastAPI 엔트리포인트 & 5분 주기 스케줄러
├── serviceAccountKey.json            # Firebase 관리자 키 (.gitignore 보호)
└── .env                              # DATA_GO_API_KEY, GEMINI_API_KEY
```

---

## 🚀 3. 단계별 상세 구현 및 테스트 로드맵 (Steps 1 ~ 6)

---

### [Step 1] 순수 도구(Zero-LLM) 및 스토리지 모듈화
* **언제 하는가?**: **[지금 즉시 / 최우선]**
* **에이전트 필요 여부**: ❌ **불필요 (순수 파이썬 코드)**
* **핵심 목표**: 주피터 노트북(`emergency_bed_firebase_sync.ipynb`)에 흩어져 있는 검증된 함수들을 `app/services/`로 깔끔하게 클래스/함수 단위 모듈화.

#### 작성 대상 파일
1. `app/config.py`:
   - `DATA_GO_API_KEY`, `GEMINI_API_KEY`, `FIREBASE_KEY_PATH` 로더
2. `app/services/holiday_service.py`:
   - 노트북 Cell 3의 `get_kasi_holiday_info()` 이식
3. `app/services/emergency_sync_service.py`:
   - 노트북 Cell 4, 5, 7의 `fetch_emergency_beds()`, `BedStateHashCache`, `sync_to_firestore()` 이식
4. `app/services/spatial_service.py`:
   - 노트북 Cell 8의 `haversine_distance()` 및 반경 10km 정렬 이식

#### 테스트 및 검증 방법
* **테스트 스크립트**: `tests/test_step1_services.py`
```bash
python -m unittest tests/test_step1_services.py
```
* **성공 기준**: 공공 API에서 50개 병상 수집 ➔ Hash Diffing ➔ Firestore 적재 ➔ 잠실역 기준 10km 거리 계산이 터미널에서 에러 없이 0.5초 안에 실행 완료.

---

### [Step 2] 세션 상태(State DTO) 및 0ms 안전 가드레일 구축
* **언제 하는가?**: Step 1 완료 직후
* **에이전트 필요 여부**: ❌ **불필요 (0ms 정규식 및 Pydantic 모델)**
* **핵심 목표**: 모든 에이전트가 공유할 메모리 객체(`PatientSessionState`)를 선언하고, 생명 위험 증상(Red Flag)을 0ms에 119로 직행시키는 인터셉터 구축.

#### 작성 대상 파일
1. `app/schemas/state.py`:
   - 세션 ID, 위경도, 월령, 체온, 지속시간, 증상 목록, 현재 단계(`current_step`) 필드 정의
2. `app/agents/guardrail_agent.py`:
   - `check_red_flag_instant(text, state)`: 생후 100일 미만 38.5도 고열, 경련, 청색증 즉시 감지 (노트북 Cell 9 정규식 엔진 활용)
   - `sanitize_output(llm_output)`: 의료법 제27조 금칙어("~로 진단됩니다", "~를 복용시키세요") 사후 필터링

#### 테스트 및 검증 방법
* **테스트 스크립트**: `tests/test_step2_guardrail.py`
```python
# 검증 예시
assert check_red_flag_instant("아이가 경련을 일으켜요", state) == True
assert state.current_step == "EMERGENCY_ESCALATION"
```
* **성공 기준**: 10대 골든 엣지케이스 테스트에서 Red Flag 100% 감지 및 일반 증상 정상 통과.

---

### [Step 3] AI 에이전트 결합 (Gemini 3.8 Flash & Tool Calling)
* **언제 하는가?**: **[에이전트 최초 투입 시점!]** Step 1(도구)과 Step 2(가드레일)가 준비된 후
* **에이전트 필요 여부**: 🤖 **필수 (Gemini 3.8 Flash & Gemini 3.5 Flash-Lite)**
* **핵심 목표**: 부모의 자연어 증상에서 4대 변수를 추출하고, 준비된 Step 1의 도구를 호출하여 맞춤형 추천 카드를 생성.

#### 작성 대상 파일
1. `app/agents/triage_agent.py`:
   - **모델**: `Gemini 3.8 Flash (Thinking Effort: Medium)`
   - **역할**: 부모 대화에서 `(월령, 체온, 경과시간, 주증상)`을 Pydantic JSON으로 안전 추출.
   - **제약**: "절대 병명을 추정하거나 발설하지 마라" 프롬프트 가드레일 강제.
2. `app/agents/matching_agent.py`:
   - **역할**: Step 1의 `spatial_service.py`와 `Firestore`를 호출하여 상위 3곳의 응급실 및 30분 마진 약국을 조합.
3. `app/agents/logistics_agent.py`:
   - **모델**: `Gemini 3.5 Flash-Lite (Thinking: Off)`
   - **역할**: 30초 전화 통화 스크립트 & 2024년 5월 본인확인 서류 체크리스트 카드 생성.

#### 테스트 및 검증 방법
* **테스트 스크립트**: `tests/test_step3_agents.py`
* **입력 예시**: *"잠실동인데 14개월 아기가 39.2도 열나고 2시간째 토해요"*
* **성공 기준**: 
  - Triage Agent가 `월령: 14, 체온: 39.2, 시간: 2, 증상: [열, 구토]`를 정확히 추출.
  - 병명 발언 없이 잠실역 인근 소아 가용 응급실(서울아산병원 등) 3곳과 전화 스크립트가 반환됨.

---

### [Step 4] 메인 오케스트레이터(Supervisor) FSM 조립
* **언제 하는가?**: 개별 에이전트 동작 검증 완료 후
* **에이전트 필요 여부**: 🤖 **조율 레이어**
* **핵심 목표**: Triage ➔ Guardrail ➔ Matching ➔ Logistics 에이전트 간의 핸드오프(Handoff)를 통제하고, 최대 3턴 루프 제한 및 비상 우회로 강제.

#### 작성 대상 파일
1. `app/orchestrator/supervisor.py`:
   - FSM(상태 머신) 루프 구현:
     ```python
     class Supervisor:
         async def run_step(self, user_message: str, state: PatientSessionState):
             # 1. 0ms Red Flag 검사 -> 긴급상황 시 즉시 119 안내로 반환
             # 2. INTAKE 상태 -> Triage Agent 호출
             # 3. 턴 수가 3에 도달했거나 4대 정보 수집 완료 -> MATCHING 전이
             # 4. MATCHING 상태 -> Matching Agent 실행
             # 5. LOGISTICS 상태 -> Logistics Agent 실행 -> 세션 완료
     ```

#### 테스트 및 검증 방법
* **테스트 스크립트**: `tests/test_step4_orchestrator.py`
* **시나리오 1**: Red Flag 입력 시 1턴 만에 119 직행하는지 검증.
* **시나리오 2**: 불완전 입력("열나요") 시 최대 3턴 이내에 강제로 병원 매칭으로 넘어가는지(루프 방지) 검증.

---

### [Step 5] FastAPI REST API 엔드포인트 & 5분 주기 백그라운드 스케줄러
* **언제 하는가?**: 오케스트레이터가 완성된 후
* **에이전트 필요 여부**: ❌ **웹 프레임워크 서빙**
* **핵심 목표**: 프론트엔드와 통신할 REST API 개설 및 5분 주기 자동 데이터 동기화 백그라운드 데몬 가동.

#### 작성 대상 파일
1. `app/api/v1/chat.py`:
   - `POST /api/v1/chat`: 사용자 메시지와 세션 ID를 받아 `supervisor.run_step()` 실행 후 응답 반환.
2. `app/api/v1/emergency.py`:
   - `GET /api/v1/emergency/nearby`: GPS 좌표를 넘기면 5ms 만에 주변 소아 응급실 목록 반환.
3. `main.py`:
   - FastAPI 앱 기동 및 `lifespan` 컨텍스트에서 **5분 주기 BackgroundTask 동기화 루프** 실행 (노트북 Cell 5/7의 Firestore Upsert 데몬화).

#### 테스트 및 검증 방법
* **실행 명령**:
```bash
uvicorn main:app --reload --port 8000
```
* **검증**: `http://localhost:8000/docs` (Swagger UI)에 접속하여 `/api/v1/chat` 및 `/api/v1/emergency/nearby` 직접 호출 테스트.

---

### [Step 6] E2E 통합 테스트 & 시나리오 기반 종합 검증
* **언제 하는가?**: 최종 완성 단계
* **핵심 목표**: [PROJECT_PLAN.md](file:///e:/monnlight/docs/PROJECT_PLAN.md)의 핵심 골든 테스트 케이스 40종을 자동 실행하여 시스템 결함 0건 달성.

#### 검증 시나리오 3선
1. **[시나리오 A] 초응급 케이스 (Red Flag)**:
   - 입력: *"생후 70일 된 아이인데 38.8도 열이 나요"* ➔ 즉각 119 안내 및 권역소아센터 직행 모달 출력 확인.
2. **[시나리오 B] 일반 야간 발열 케이스 (정상 플로우)**:
   - 입력: *"36개월 아이 38.5도 열나요"* ➔ 2턴 문진 ➔ 10km 이내 소아 가용 응급실 3곳 + 30분 마진 당번약국 페어링 + 본인확인 서류 체크리스트 카드 확인.
3. **[시나리오 C] 의료법 진단 유도 방어 (컴플라이언스)**:
   - 입력: *"배 아프고 설사하는데 급성 장염 맞죠?"* ➔ 진단명 확정 없이 증상 공감 및 진료 가능 소아과 매칭으로 우회 안내 확인.

---

## 📅 4. 1주일 완성 스프린트 일정표 (추천 작업 분량)

| 일차 | 개발 목표 | 핵심 작업 내용 | 에이전트 투입 |
| :---: | :--- | :--- | :---: |
| **Day 1** | **[Step 1] 도구 모듈화** | 노트북 코드를 `app/services/`로 이식 및 단위 테스트 | X |
| **Day 2** | **[Step 2] 세션 DTO & 가드레일** | `PatientSessionState` 선언 및 0ms Red Flag 인터셉터 작성 | X |
| **Day 3** | **[Step 3] AI 에이전트 결합** | Gemini 3.8 Flash Triage 프롬프트 및 Matching/Logistics 도구 결합 | **O (Gemini 투입)** |
| **Day 4** | **[Step 4] 메인 FSM 조립** | `Supervisor` 오케스트레이터 완성 및 3턴 루프 제어 테스트 | **O (조율)** |
| **Day 5** | **[Step 5] FastAPI 서빙** | REST API 개설 및 5분 주기 자동 동기화 데몬 구동 | X |
| **Day 6~7**| **[Step 6] 프론트엔드 연동 & E2E**| 지도 UI 연동 및 종합 시나리오 테스트 | **O (전체 가동)** |

---

> 💡 **다음 작업 추천**:  
> 본 로드맵의 가장 첫 단추인 **[Step 1: 주피터 노트북 코드를 `app/services/`로 모듈화하고 단위 테스트 작성하기]**를 바로 시작하시면 가장 막힘없이 진행하실 수 있습니다!
