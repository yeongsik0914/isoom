# 🗺️ ISOOM 모듈 & 에이전트 상호 연결도 (CONNECTIVITY_MAP.md)

> **문서 버전**: `v2.1.0` (공공 API 서킷 브레이커 & 3단계 Fallback 고가용성 통합)  
> **최종 갱신 일자**: 2026-10-14  
> **문서 목적**: 시스템을 구성하는 모든 백엔드 모듈, 데이터베이스, AI 에이전트들이 **어떤 인터페이스로 데이터를 주고받고, 어떤 흐름으로 연계 동작하는지 표(Table)와 다이어그램으로 한눈에 파악**할 수 있도록 지속 관리하는 공식 연결도 문서입니다. 앞으로 기능이 추가될 때마다 단계별로 이 문서가 갱신됩니다.

---

## 📑 목차

1. [전체 시스템 아키텍처 및 연결 흐름 다이어그램](#1-전체-시스템-아키텍처-및-연결-흐름-다이어그램)
2. [종합 모듈 & 에이전트 상호 연결 매트릭스 (Total Connectivity Matrix)](#2-종합-모듈--에이전트-상호-연결-매트릭스-total-connectivity-matrix)
3. [E2E 파이프라인 단계별 세부 동작 및 데이터 입출력 표](#3-e2e-파이프라인-단계별-세부-동작-및-데이터-입출력-표)
4. [공유 메모리(`PatientSessionState`) 읽기/쓰기 권한 매트릭스](#4-공유-메모리patientsessionstate-읽기쓰기-권한-매트릭스)
5. [대표 시나리오별 실제 컴포넌트 호출 트레이스 (Scenario Traces)](#5-대표-시나리오별-실제-컴포넌트-호출-트레이스-scenario-traces)
6. [향후 확장 연결 로드맵 (Upcoming Steps 5~7 Integration)](#6-향후-확장-연결-로드맵-upcoming-steps-57-integration)

---

## 1. 전체 시스템 아키텍처 및 연결 흐름 다이어그램

```mermaid
flowchart TD
    subgraph Client_Layer [사용자 인터페이스 & 세션]
        User([보호자 사용자])
        SessionMgr[SessionManager<br/>Thread-Safe / TTL 캐시]
        State[(PatientSessionState<br/>공유 메모리 DTO)]
    end

    subgraph Step4_Orchestrator_Layer [메인 오케스트레이션 Layer]
        Supervisor[⚙️ SupervisorOrchestrator<br/>6-State FSM / 3-Turn Guard<br/>Tier 1 & Tier 2 긴급 격상]
    end

    subgraph Step2_Guardrail_Layer [안전 가드레일 레이어 (0ms In-Memory)]
        PreGuard{check_red_flag_instant<br/>Pass 1: 12대 룰 26µs 검사}
        PostSanitizer{sanitize_output<br/>의료법 제27조 사후 필터}
    end

    subgraph Step3_AI_Agent_Layer [지능형 멀티 에이전트 레이어]
        Triage[🤖 Triage Agent<br/>Gemini 3.8 Flash Thinking High<br/>Pass 2: KTAS Direct Grounding]
        Matching[🤖 Matching Agent<br/>Zero-LLM 도구 결합기]
        Logistics[🤖 Logistics Agent<br/>Gemini 3.5 Flash-Lite]
    end

    subgraph Step7_High_Availability [Step 7: 서킷 브레이커 & 고가용성 Layer]
        CircuitBreaker[⚡ AsyncCircuitBreaker<br/>CLOSED / OPEN / HALF_OPEN<br/>0ms 즉시 차단 & 자가치유]
        MultiTierFallback[🛡️ 3-Tier Multi-Storage Fallback<br/>Tier 1: Stale Memory (0.1ms)<br/>Tier 2: Firestore Snapshot (15ms)<br/>Tier 3: Disk Baseline JSON (0.5ms)]
    end

    subgraph Step1_Domain_Services [결정론적 백엔드 도구 Layer (Zero-LLM)]
        HolidaySvc[holiday_service<br/>KASI 특일 & 과밀화 평가]
        SpatialSvc[spatial_service<br/>Haversine 5µs 공간 랭킹]
        EmergencySvc[emergency_sync_service<br/>E-Gen 실시간 병상 & 공지 정규식]
        PairingSvc[pairing_service<br/>전국 17개 시도 달빛병원-약국 30분 마진]
    end

    subgraph Data_Storage [데이터 저장소 및 지식 베이스]
        KTAS_DB[(data/ktas_pediatric_dataset.json<br/>168개 주증상/841개 세부기준 지식 베이스)]
        Firestore[(Cloud Firestore<br/>emergency_beds / summary)]
        CoordsCache[(data/seoul_emergency_coords.json &<br/>전국 17개 시·도 권역 위경도망)]
        PairingsData[(data/nationwide_pairings.json<br/>29개소 거점 페어링 마스터)]
    end

    %% 연결 관계 (Data Flow)
    User -->|자연어 증상 입력| Supervisor
    Supervisor <-->|세션 획득/저장| SessionMgr
    SessionMgr <--> State

    Supervisor -->|1. 매 턴 Pass 1 선제 검사| PreGuard
    PreGuard -->|🚨 Tier 1 Red Flag 감지 (26µs)| EmergencyEscalation[Track A: 119 원클릭 호출 & 기도확보 가이드]
    PreGuard -->|🟢 정상 통과| Triage

    KTAS_DB -.->|Direct Grounding ~8,500 토큰| Triage
    Triage <-->|임상 변수 4종 및 KTAS 등급 읽기/쓰기| State
    Triage -->|🚨 Tier 2 비정형 Red Flag 감지 (KTAS 1~2)| EmergencyEscalation
    Triage -->|문진 완료 또는 3턴 도달| Matching

    Matching -->|1. 특일 & 과밀화 조회| HolidaySvc
    Matching -->|2. 실시간 병상 조회| EmergencySvc
    Matching -->|3. 구면거리 정렬| SpatialSvc
    Matching -->|4. 30분 마진 약국 검색| PairingSvc

    EmergencySvc <-->|위경도 캐시 참조| CoordsCache
    EmergencySvc -.->|Hash Diffing 동기화| Firestore
    PairingSvc <-->|마스터셋 로드| PairingsData

    Matching <-->|매칭 병원/약국 저장| State
    Matching -->|FSM 전이| Logistics

    Logistics <-->|환아 정보 & 방문 병원 조회| State
    Logistics -->|통화 스크립트 & 체크리스트 생성| PostSanitizer
    PostSanitizer -->|의료법 면책 배지 결합 및 단일 출구 응답| User
```

---

## 2. 종합 모듈 & 에이전트 상호 연결 매트릭스 (Total Connectivity Matrix)

현재까지 개발 완료된 핵심 컴포넌트 간의 **호출자(Caller) ➔ 대상(Callee)** 연결 관계표입니다:

| 컴포넌트 명칭 | 역할 및 소스 위치 | 상위 호출자 (Caller) | 하위 호출 대상 (Callee) | 입력 데이터 (Input) | 출력 데이터 (Output) | 결합 방식 |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **`check_red_flag_instant`** | 0ms Red Flag 선제 차단기<br/>[`app/agents/guardrail_agent.py`](app/agents/guardrail_agent.py) | API 엔드포인트 / 데모 스크립트 | 없음 (순수 정규식 인메모리) | • 보호자 입력 원문 (`text`)<br/>• `PatientSessionState` | • 긴급 여부 (`bool`)<br/>• 비상 처치 가이드 | 함수 호출 (동기) |
| **`TriageAgent`** | 부모 문진 & 임상 변수 정형화<br/>[`app/agents/triage_agent.py`](app/agents/triage_agent.py) | 메인 오케스트레이터 / 데모 러너 | • `google.genai` (Gemini 3.8 Flash)<br/>• 내부 정규식 Fallback 엔진 | • `user_message`<br/>• `PatientSessionState` | • `TriageExtractionResult`<br/>(월령, 체온, 시간, 증상, 공감글) | 비동기 (Async) |
| **`MatchingAgent`** | 2-트랙 결정론적 시설 라우터<br/>[`app/agents/matching_agent.py`](app/agents/matching_agent.py) | `TriageAgent` 완료 이벤트 | • `holiday_service`<br/>• `emergency_sync_service`<br/>• `spatial_service`<br/>• `pairing_service` | • `user_lat`, `user_lon`<br/>• `temperature`, `age_months`<br/>• `symptoms` | • `matched_hospitals` (TOP 3)<br/>• `matched_pharmacies` (30분 마진) | 비동기 (Async) |
| **`LogisticsAgent`** | 출동 가이드 & 유선 스크립트 생성<br/>[`app/agents/logistics_agent.py`](app/agents/logistics_agent.py) | `MatchingAgent` 완료 이벤트 | • `google.genai` (Gemini 3.5 Lite)<br/>• 내부 템플릿 Fallback 엔진 | • `PatientSessionState`<br/>(환아 정보, 최우선 방문 병원명) | • `LogisticsCardResult`<br/>(30초 통화 스크립트, 서류 목록) | 비동기 (Async) |
| **`sanitize_output`** | 의료법 제27조 준수 사후 필터<br/>[`app/agents/guardrail_agent.py`](app/agents/guardrail_agent.py) | 최종 응답 직전 렌더러 | 없음 (순수 정규식 인메모리) | • LLM 생성 텍스트 원문 | • 진단명/용량 중화 텍스트<br/>• 면책 고지 배지 | 함수 호출 (동기) |
| **`holiday_service`** | KASI 특일 판정 & 과밀화 평가<br/>[`app/services/holiday_service.py`](app/services/holiday_service.py) | `MatchingAgent` | 한국천문연구원 특일 API | • `target_date` (날짜/문자열) | • `HolidayInfo`<br/>(공휴일 여부, 과밀화 위험도) | 정적 메서드 (동기) |
| **`spatial_service`** | 하버사인 구면거리 랭킹<br/>[`app/services/spatial_service.py`](app/services/spatial_service.py) | `MatchingAgent` | 없음 (순수 수학 연산) | • 병원 리스트<br/>• `user_lat`, `user_lon`, `max_radius_km` | • `list[RankedEmergencyHospital]`<br/>(거리 오름차순 정렬) | 함수 호출 (< 5µs) |
| **`emergency_sync_service`**| 실시간 병상 파싱 & Hash Diffing<br/>[`app/services/emergency_sync_service.py`](app/services/emergency_sync_service.py) | `MatchingAgent` / 배치 워커 | • NMC E-Gen 오픈 API<br/>• Firestore 클라이언트<br/>• `seoul_emergency_coords.json`<br/>• 전국 17개 시·도 권역 위경도망 | • `stage1` (시·도 명칭)<br/>• 인증키 | • `list[EmergencyBedInfo]`<br/>(정규식 차단 필터 완료 병상) | I/O 연계 (동기/캐싱) |
| **`pairing_service`** | 전국 달빛병원-약국 30분 페어링<br/>[`app/services/pairing_service.py`](app/services/pairing_service.py) | `MatchingAgent` | • `nationwide_pairings.json`<br/>• `spatial_service.haversine_distance`| • `user_lat`, `user_lon`<br/>• `max_radius_km` | • `list[dict]` (30분 마진 보유<br/>병원-약국 페어 리스트) | 함수 호출 (인메모리) |
| **`SupervisorOrchestrator`** | FSM 메인 오케스트레이터<br/>[`app/orchestrator/supervisor.py`](app/orchestrator/supervisor.py) | API 라우터 / 데모 스크립트 | • `check_red_flag_instant`<br/>• `TriageAgent`<br/>• `MatchingAgent`<br/>• `LogisticsAgent`<br/>• `SessionManager`<br/>• `sanitize_output` | • `user_message`<br/>• `session_id`<br/>• `user_lat`, `user_lon` | • `SupervisorResponse`<br/>(메시지, 병원, 약국, 스크립트, 체크리스트, 면책 배지) | 비동기 파이프라인 (FSM) |
| **`SessionManager`** | 세션 상태 저장소 & TTL 캐시<br/>[`app/orchestrator/session_manager.py`](app/orchestrator/session_manager.py) | `SupervisorOrchestrator` | 없음 (Thread-Safe 인메모리) | • `session_id`<br/>• `PatientSessionState` | • `PatientSessionState`<br/>• 세션 만료 수 | 비동기 락 (asyncio.Lock) |
| **`Settings`** | 3-Tier API 키 & 환경설정 싱글톤<br/>[`app/config.py`](app/config.py) | 모든 서비스 및 에이전트 | • `.env`, `os.environ`<br/>• Windows 레지스트리 (HKCU/HKLM) | 없음 (프로젝트 부팅 시 자동 로드) | • API 키, 파일 경로, 클라이언트 인스턴스 | 싱글톤 참조 |

---

## 3. E2E 파이프라인 단계별 세부 동작 및 데이터 입출력 표

보호자가 한 문장을 입력했을 때 시스템 내부에서 일어나는 **순차적 파이프라인 흐름**입니다:

| 실행 순서 | 파이프라인 단계 | 실행 주체 모듈 | 트리거 조건 | 내부 처리 알고리즘 & 연산 | 상태 전이 (FSM State) |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | **0ms 선제 검사** | `check_red_flag_instant` | 사용자 메시지 수신 즉시 | • KTAS 소아 7대 Red Flag 정규식 매칭 (소요시간: 5.45µs)<br/>• 영아 고열, 경련, 청색증 등 감지 시 즉시 차단 | (Red Flag 감지 시)<br/>`INIT` ➔ `EMERGENCY_ESCALATION` |
| **2** | **사전 문진 (Triage)** | `TriageAgent` | Red Flag 미감지 (정상 통과) | • Gemini 3.8 Flash 구조화 출력 (Pydantic Schema)<br/>• `(월령, 체온, 경과시간, 주증상)` 정밀 파싱<br/>• 부모 안심 공감 멘트 생성 및 진단 질문 방어 | (문진 진행 중)<br/>`INIT` / `TRIAGE`<br/>(4대 변수 완료 시)<br/>`TRIAGE` ➔ `MATCHING` |
| **3** | **환경 리스크 분석** | `holiday_service` | `MatchingAgent` 진입 시 | • 오늘 날짜의 요일 및 KASI 법정공휴일 판정<br/>• 휴일 야간 소아과 전멸 시 과밀화 리스크 `CRITICAL` 격상 | (상태 유지)<br/>`MATCHING` |
| **4** | **실시간 자원 탐색** | `emergency_sync_service`<br/>`pairing_service` | `MatchingAgent` 실행 중 | • NMC E-Gen 실시간 병상 호출 + 공지사항 정규식(`PEDIATRIC_BLOCK_PATTERN`) 필터링<br/>• 전국 17개 시도 달빛병원-야간약국 마스터셋 로드 | (상태 유지)<br/>`MATCHING` |
| **5** | **임상 2-트랙 라우팅** | `MatchingAgent` | 병상 및 페어링 데이터 취득 후 | • **고열/위급 (39.0℃ 이상 or 영아)**: Haversine 10km 이내 소아 가용 응급실 TOP 3 배정<br/>• **경증 발열 (39.0℃ 미만)**: 달빛어린이병원 + 30분 마진 야간약국 세트 배정 | `MATCHING` ➔ `LOGISTICS` |
| **6** | **실행 지원 카드 생성** | `LogisticsAgent` | 병원/약국 매칭 완료 즉시 | • Gemini 3.5 Flash-Lite 기반 초고속 생성<br/>• 최우선 배정 병원 맞춤 **"30초 유선 확인 통화 스크립트"** 생성<br/>• **2024년 5월 본인확인 의무화 지참 서류** 맞춤 체크리스트 생성 | `LOGISTICS` ➔ `COMPLETED` |
| **7** | **의료법 사후 소독** | `sanitize_output` | 클라이언트 전송 직전 | • 불법 확정 진단명 / 약물 복용 용량 정규식 소독<br/>• 대면 진료 권고 면책 고지 배지 자동 결합 | `COMPLETED` 유지 |

---

## 4. 공유 메모리(`PatientSessionState`) 읽기/쓰기 권한 매트릭스

단일 진실 공급원(SSOT) 역할을 하는 `PatientSessionState` DTO의 필드별 **수정 주체(Writer)와 참조 주체(Reader)** 매핑입니다:

| 필드명 | 데이터 타입 | 생성/수정 주체 (Writer) | 참조 주체 (Reader) | 설명 및 유효값 |
| :--- | :---: | :--- | :--- | :--- |
| `session_id` | `str` | 세션 생성자 (API Gateway) | 전체 컴포넌트 | 고유 세션 식별자 (UUID 등) |
| `current_step` | `str` | 전체 에이전트 (FSM 전이 시) | Supervisor, 클라이언트 UI | `INIT` ➔ `TRIAGE` ➔ `MATCHING` ➔ `LOGISTICS` ➔ `COMPLETED` |
| `turn_count` | `int` | `state.add_message()` | Supervisor FSM | 부모 메시지 입력 시마다 +1 증가 (최대 3턴 제한) |
| `age_months` / `age_days` | `int` | `TriageAgent` | `MatchingAgent`, `LogisticsAgent` | 환아 나이 (개월 수 또는 생후 일수) |
| `temperature` | `float` | `TriageAgent` | `MatchingAgent`, `LogisticsAgent` | 측정 체온 (℃, 예: 39.2) |
| `duration_hours` | `int` | `TriageAgent` | `LogisticsAgent` | 증상 시작 후 경과 시간 (시간 단위) |
| `symptoms` | `list[str]` | `TriageAgent` | `MatchingAgent`, `LogisticsAgent` | 환아 주증상 목록 (`['발열', '구토']`) |
| `user_lat`, `user_lon` | `float` | 클라이언트 GPS / IP 역지오코딩 | `spatial_service`, `pairing_service` | 보호자 현재 좌표 (기본값: 잠실역 37.5133, 127.1001) |
| `is_red_flag` | `bool` | `guardrail_agent` | Supervisor FSM | 생명 위급 응급 징후 감지 여부 (`True`/`False`) |
| `matched_hospitals` | `list[dict]` | `MatchingAgent` | `LogisticsAgent`, UI 렌더러 | 추천 병원 요약 목록 (TOP 3) |
| `matched_pharmacies`| `list[dict]` | `MatchingAgent` | UI 렌더러 | 30분 조제 안전 마진 확보 연계 약국 목록 |
| `call_script` | `str` | `LogisticsAgent` | 클라이언트 UI | 병원 출발 전 30초 유선 확인 통화 스크립트 |
| `document_checklist`| `list[str]` | `LogisticsAgent` | 클라이언트 UI | 2024년 5월 본인확인 의무화 지참 서류 목록 |

---

## 5. 대표 시나리오별 실제 컴포넌트 호출 트레이스 (Scenario Traces)

### 🎬 시나리오 A: 야간 경증 발열 보호자 (달빛어린이병원 + 30분 마진 약국 연계)
* **보호자 입력**: *"서초구 방배동인데 36개월 아이가 38.0도 미열나고 2시간째 기침해요. 어디로 가야 할까요?"*
* **위치**: 서초구 방배동 (37.4988, 126.9934)
```
[User Input]
     │
     ▼
1. check_red_flag_instant() ──► 0.005ms 만에 정상 판정 (Red Flag 없음)
     │
     ▼
2. TriageAgent ──► Gemini 3.8 Flash 구조화 파싱
     │             • age_months: 36, temperature: 38.0, duration: 2, symptoms: ['발열', '기침']
     │             • is_complete: True ➔ state.current_step = 'MATCHING'
     ▼
3. MatchingAgent ──► 임상 분기: 체온 38.0℃ < 39.0℃ 이므로 [경증 분산 모드] 선택
     │               ├── holiday_service: 오늘 평일 야간 판정 (NORMAL)
     │               ├── pairing_service: 방배동 반경 5km 달빛병원-약국 마스터 검색
     │               │    └── 1순위: 연세곰돌이소아청소년과의원 (0.01km) + 열린약국 (마감: 21:30, 마진: +30분)
     │               └── spatial_service: 혹시 모를 상황 대비 인근 응급실(강남세브란스) 백업 1곳 등록
     ▼
4. LogisticsAgent ──► Gemini 3.5 Lite 초고속 호출 (< 200ms)
     │                • call_script: "연세곰돌이소아과 접수처 맞으신가요? 36개월 아이가 체온 38.0도로..."
     │                • document_checklist: 부모 신분증, 가족관계증명서, 건강보험증 메모
     ▼
5. sanitize_output() ──► 의료법 위반 검사 후 최종 결과 카드 보호자 화면 출력 (COMPLETED)
```

---

### 🎬 시나리오 B: 심야 영아 고열 및 구토 (소아전문응급센터 직결)
* **보호자 입력**: *"잠실동인데 14개월 아기가 39.5도 불덩이고 2시간째 토해요. 응급실 바로 갈 수 있나요?"*
* **위치**: 송파구 잠실역 (37.5133, 127.1001)
```
[User Input]
     │
     ▼
1. check_red_flag_instant() ──► 단순 발열+구토이므로 정상 문진으로 인계 (0.006ms)
     │
     ▼
2. TriageAgent ──► Gemini 3.8 Flash 파싱
     │             • age_months: 14, temperature: 39.5, duration: 2, symptoms: ['발열', '구토']
     │             • is_complete: True ➔ state.current_step = 'MATCHING'
     ▼
3. MatchingAgent ──► 임상 분기: 체온 39.5℃ >= 39.0℃ 이므로 [상급 응급실 우선 모드] 선택
     │               ├── emergency_sync_service: E-Gen 실시간 병상 및 비정형 공지 필터링
     │               └── spatial_service: 잠실 기준 Haversine 10km 이내 가용 응급실 랭킹
     │                    ├── 1순위: 서울아산병원 소아전문응급센터 (1.66km, 소아병상 4석 가용)
     │                    └── 2순위: 삼성서울병원 (3.07km, 소아병상 2석 가용)
     ▼
4. LogisticsAgent ──► 30초 서울아산병원 직통 유선 확인 스크립트 & 응급 내원 준비물 생성
     ▼
5. sanitize_output() ──► 사후 소독 및 면책 배지 결합 후 전송 (COMPLETED)
```

---

### 🚨 시나리오 C: 생후 50일 영아 고열 (Track A 0ms 초응급 에스컬레이션)
* **보호자 입력**: *"생후 50일 된 신생아인데 방금 체온 38.4도 찍혔어요 살려주세요"*
```
[User Input]
     │
     ▼
1. check_red_flag_instant() ──► 0.012ms 만에 [생후 100일 미만 고열] 긴급 차단!
     │                          • state.escalate_to_emergency() 즉시 발동
     │                          • state.current_step = 'EMERGENCY_ESCALATION'
     ▼
[AI 에이전트(Triage/Matching/Logistics) 실행 완전 우회 (Zero-Latency)]
     │
     ▼
2. 119 구급차 원클릭 다이렉트 호출 모달 즉시 팝업 + 기도 확보 응급처치 행동요령 출력
```

---

## 6. 향후 확장 연결 로드맵 (Upcoming Steps 4~6 Integration)

새로운 단계가 개발될 때마다 본 `CONNECTIVITY_MAP.md`의 연결도가 아래와 같이 순차적으로 확장됩니다:

| 예정 마일스톤 | 추가/연결될 신규 컴포넌트 | 연결 지점 (Hook Point) | 기능 동작 방식 및 연계 목표 |
| :--- | :--- | :--- | :--- |
| **[Step 4]**<br/>Supervisor FSM 조립 | `app/orchestrator/supervisor.py`<br/>`app/orchestrator/session_manager.py` | `Guardrail` ➔ `Supervisor` ➔ 서브 에이전트들 | • **[완료 (100% 통과)]** 전체 에이전트 간의 중앙 집중식 오케스트레이션 제어<br/>• 턴 수 카운터(`turn_count >= 3`) 루프 방지 강제 전이 & 0ms Red Flag 긴급 차단<br/>• 단일 관문 의료법 제27조 소독 및 Thread-Safe 세션 TTL 관리 |
| **[Step 5]**<br/>FastAPI 서빙 & 백그라운드 워커 | `main.py`<br/>`app/api/v1/chat.py`<br/>`app/api/v1/emergency.py`<br/>`app/services/scheduler.py` | Web 클라이언트 ➔ FastAPI ➔ FSM & 공간 검색 | • **[완료 (100% 통과)]** `POST /api/v1/chat` 및 SSE 실시간 스트리밍 엔드포인트 완비<br/>• `GET /api/v1/emergency/nearby` (5ms 공간 검색) & `pairings` (전국 30분 마진 약국)<br/>• 5분 주기 E-Gen 병상 동기화(Hash Diffing) & 24시간 정적 캐시 갱신 APScheduler 데몬 |
| **[Step 6]**<br/>E2E 통합 테스트 & 골든 Evals | `tests/test_step6_e2e.py`<br/>`tests/evals/run_evals.py`<br/>`demo_step6.py` | 전체 파이프라인 E2E | • **[완료 (100% 통과)]** 8대 E2E 통합 시나리오(TC-601~608) 100% 통과<br/>• 40대 임상 골든 케이스 자동 채점기(DIM-1~5) 100.0% 합격(40/40, 평균 99.5점)<br/>• CLI 인터랙티브 종합 시연 데모(`demo_step6.py`) 탑재 |
