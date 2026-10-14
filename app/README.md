# 🏥 MoonlightCare 애플리케이션 코어 패키지 (`app`)

> **위치**: `app/`  
> **역할**: MoonlightCare 시스템의 전체 비즈니스 로직, AI 멀티 에이전트 파이프라인, 결정론적 도메인 엔진, REST API 서빙 계층이 결합된 메인 애플리케이션 루트 패키지입니다.

---

## 📑 하위 디렉토리 구성 및 전용 문서 링크

| 디렉토리 | 전용 문서 링크 | 핵심 역할 요약 |
| :--- | :--- | :--- |
| **`app/agents/`** | [**`app/agents/README.md`**](file:///e:/monnlight/app/agents/README.md) | 0ms 가드레일, Gemini 3.8 문진, Zero-LLM 시설 매칭, 로지스틱스 4대 에이전트 |
| **`app/orchestrator/`** | [**`app/orchestrator/README.md`**](file:///e:/monnlight/app/orchestrator/README.md) | 6단계 FSM Supervisor, 3턴 데드락 가드, Thread-Safe SessionManager |
| **`app/services/`** | [**`app/services/README.md`**](file:///e:/monnlight/app/services/README.md) | KASI 특일 판정, NMC E-Gen 병상 수집, Haversine 5µs 공간 랭킹, APScheduler 데몬 |
| **`app/api/`** | [**`app/api/README.md`**](file:///e:/monnlight/app/api/README.md) | FastAPI v1 엔드포인트 (`/chat`, `/chat/stream`, `/emergency/nearby`, `/pairings`) |
| **`app/schemas/`** | [**`app/schemas/README.md`**](file:///e:/monnlight/app/schemas/README.md) | Pydantic v2 데이터 스키마 (공유 세션 `PatientSessionState`, `SupervisorResponse` DTO) |

---

## 🏛️ 전체 계층형 아키텍처 다이어그램

```mermaid
flowchart TD
    Client([외부 클라이언트 / Frontend])
    
    subgraph API_Layer [1. REST API 서빙 계층 (app/api)]
        RouterChat["POST /api/v1/chat (일반 & SSE 스트리밍)"]
        RouterER["GET /api/v1/emergency/nearby & pairings"]
    end
    
    subgraph Orchestrator_Layer [2. 메인 오케스트레이션 계층 (app/orchestrator)]
        Supervisor["SupervisorOrchestrator (6-State FSM)"]
        SessionMgr["SessionManager (asyncio.Lock / 30분 TTL)"]
    end
    
    subgraph Agent_Layer [3. AI 멀티 에이전트 계층 (app/agents)]
        Guardrail["GuardrailAgent (0ms Red Flag & 사후 소독)"]
        Triage["TriageAgent (Gemini 3.8 Flash)"]
        Matching["MatchingAgent (Zero-LLM 결정론적 라우터)"]
        Logistics["LogisticsAgent (Gemini 3.5 Lite)"]
    end
    
    subgraph Domain_Services [4. 결정론적 도메인 엔진 (app/services)]
        HolidaySvc["HolidayService (KASI 특일 판정)"]
        SpatialSvc["SpatialService (Haversine 5µs 공간 정렬)"]
        EmergencySvc["EmergencySyncService (E-Gen 실시간 병상)"]
        PairingSvc["PairingService (달빛병원-약국 30분 마진)"]
        Scheduler["BackgroundDaemon (APScheduler 2-트랙 워커)"]
    end
    
    subgraph Schema_Layer [5. 데이터 규격 계층 (app/schemas)]
        StateDTO[("PatientSessionState (단일 진실 공급원)")]
    end

    %% 연결선
    Client <--> API_Layer
    API_Layer <--> Supervisor
    Supervisor <--> SessionMgr
    Supervisor <--> StateDTO
    
    Supervisor --> Guardrail
    Supervisor --> Triage
    Supervisor --> Matching
    Supervisor --> Logistics
    
    Matching --> HolidaySvc
    Matching --> SpatialSvc
    Matching --> EmergencySvc
    Matching --> PairingSvc
    
    Scheduler -.-> EmergencySvc
```

---

## ⚙️ 애플리케이션 전역 설정 (`config.py`)

* **위치**: [`app/config.py`](file:///e:/monnlight/app/config.py)
* **주요 기능**:
  - `.env` 파일 로드 및 환경변수 파싱.
  - **Windows Registry 키 폴백 스캔**: Windows 환경에서 환경변수 재부팅 전 레지스트리(`HKCU\Environment`, `HKLM\SYSTEM\...`)에 등록된 `DATA_GO_API_KEY`, `GEMINI_API_KEY`를 자동 감지.
  - **Firebase Admin SDK 싱글톤 초기화**: `serviceAccountKey.json`을 안전하게 로드하여 지연(Lazy) 초기화.

---

## 🚀 단계별 인터랙티브 CLI 시연기 목록

`app/` 디렉토리에는 각 개발 단계의 성과를 터미널에서 즉시 검증할 수 있는 데모 스크립트들이 준비되어 있습니다:

```bash
# Step 1: 결정론적 도메인 도구 & FinOps Hash Diffing 시연
python app/demo_step1.py

# Step 3: AI 멀티 에이전트(Triage, Matching, Logistics) 결합 시연
python app/demo_step3.py

# Step 4: 메인 오케스트레이터 3대 시나리오(멀티턴, 경련 급변 차단, 3턴 가드) 시연
python app/demo_step4.py

# Step 5: FastAPI REST API 7대 엔드포인트 & SSE 실시간 스트리밍 시연
python app/demo_step5.py
```
