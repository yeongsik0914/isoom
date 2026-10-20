# 📦 Pydantic 데이터 스키마 & DTO 레이어 (`app/schemas`)

> **위치**: `app/schemas/`  
> **역할**: ISOOM 시스템 전체에서 주고받는 모든 데이터의 유효성을 검증(Validation)하고, 에이전트 간 공유 메모리 및 클라이언트 통신 인터페이스를 정의하는 **Pydantic v2 표준 데이터 모델(DTO) 패키지**입니다.

---

## 📑 목차
1. [스키마 레이어 개요](#1-스키마-레이어-개요)
2. [5대 모듈별 스키마 상세 명세](#2-5대-모듈별-스키마-상세-명세)
   - [2.1 공유 세션 상태 (state.py)](#21-공유-세션-상태-statepy)
   - [2.2 응급실 및 특일 도메인 모델 (emergency.py)](#22-응급실-및-특일-도메인-모델-emergencypy)
   - [2.3 오케스트레이터 표준 출력 (supervisor.py)](#23-오케스트레이터-표준-출력-supervisorpy)
   - [2.4 상담 REST DTO (chat.py)](#24-상담-rest-dto-chatpy)
   - [2.5 응급 및 공간 검색 DTO (emergency_api.py)](#25-응급-및-공간-검색-dto-emergency_apipy)
3. [데이터 변환 파이프라인 (Data Mapping Flow)](#3-데이터-변환-파이프라인-data-mapping-flow)

---

## 1. 스키마 레이어 개요

ISOOM는 런타임 데이터 오염과 타입 불일치 버그를 0%로 만들기 위해, 시스템 내부의 모든 객체를 **Pydantic v2 `BaseModel`**로 엄격히 통제합니다.  
공공 API의 원천 XML/JSON부터 Firestore 문서, AI 에이전트 간 공유 메모리, 최종 프론트엔드 반환값까지 모두 명확한 스키마 정의를 따릅니다.

---

## 2. 5대 모듈별 스키마 상세 명세

### 2.1 공유 세션 상태 (`state.py`)
* **핵심 모델**: `PatientSessionState`, `MessageRecord`
* **역할**: **시스템 전체의 단일 진실 공급원 (Single Source of Truth)**. 모든 에이전트가 이 객체를 참조하고 갱신합니다.
* **주요 필드 구성 (6대 영역)**:
  1. **세션 식별 & FSM**: `session_id`, `current_step`(`INIT`, `TRIAGE`, `MATCHING`, `LOGISTICS`, `EMERGENCY_ESCALATION`, `COMPLETED`), `turn_count`
  2. **환아 4대 필수 임상 변수**: `age_months`, `age_days`, `temperature`, `duration_hours`, `symptoms`
  3. **보호자 위치 정보**: `user_lat`, `user_lon`, `user_address`
  4. **Red Flag 응급 프로토콜**: `is_red_flag`, `red_flag_reason`, `emergency_action_guide`
  5. **매칭 및 로지스틱스 결과**: `matched_hospitals`, `matched_pharmacies`, `call_script`, `document_checklist`
  6. **대화 이력 히스토리**: `conversation_history: list[MessageRecord]`, `created_at`, `updated_at`

---

### 2.2 응급실 및 특일 도메인 모델 (`emergency.py`)
* **핵심 모델**:
  - `EmergencyBedInfo`: 국립중앙의료원(NMC) E-Gen 실시간 병상 파싱 모델 (`pediatric_beds`, `general_beds`, `is_pediatric_blocked`, `pediatric_acceptable` 등).
  - `HolidayInfo`: KASI 한국천문연구원 특일 정보 및 과밀화 리스크 메타데이터 (`date`, `is_holiday`, `holiday_name`, `surge_risk_level`).
  - `RankedEmergencyHospital`: 사용자 좌표 기준 Haversine 구면거리로 정렬된 추천 응급실 모델 (`distance_km`, `hospital_name`, `pediatric_acceptable` 등).
  - `EmergencyBedSyncRecord`: Firestore `emergency_beds` 컬렉션 적재 문서 규격.
  - `EmergencySummary`: Firestore `emergency_summary/realtime` 대시보드 뷰용 단일 집계 문서 규격.

---

### 2.3 오케스트레이터 표준 출력 (`supervisor.py`)
* **핵심 모델**: `SupervisorResponse`
* **역할**: `SupervisorOrchestrator`가 FSM 파이프라인 수행 후 API 레이어 또는 프론트엔드에 최종 반환하는 표준 규격 객체.
* **주요 필드**:
  ```python
  session_id: str          # 고유 세션 ID
  current_step: str        # 현재 FSM 단계
  turn_count: int          # 진행된 대화 턴 수 (최대 3턴)
  is_emergency: bool       # 0ms Red Flag 긴급 감지 여부
  message: str             # 보호자 전달 본문 (공감 멘트, 추가 질문 또는 종합 진료 안내)
  emergency_guide: Optional[str]  # 119 구급차 대기 시 행동 요령
  hospitals: list[dict]    # 추천 응급실 또는 달빛어린이병원 (TOP 3)
  pharmacies: list[dict]   # 30분 마진 심야 약국 목록
  call_script: Optional[str] # 30초 유선 확인 통화 스크립트
  checklist: list[str]     # 2024년 5월 본인확인 의무화 지참 서류
  disclaimer: str          # 의료법 제27조 준수 법적 면책 고지문
  ```

---

### 2.4 상담 REST DTO (`chat.py`)
* **`ChatRequest`**:
  - 클라이언트가 `POST /api/v1/chat` 및 `/stream`에 전송하는 페이로드.
  - 필드: `user_message`, `session_id`, `user_lat`, `user_lon`, `user_address`, `stream`.
* **`SessionDetailResponse`**:
  - `GET /api/v1/chat/session/{sid}`에서 반환하는 활성 세션 상태 및 전체 대화 히스토리(`messages`).

---

### 2.5 응급 및 공간 검색 DTO (`emergency_api.py`)
* **`NearbyEmergencyResponse`**: `GET /api/v1/emergency/nearby` 응답 DTO (정렬된 병원 목록, 특일 정보, 연산 소요 시간 `latency_ms`).
* **`PairingSearchResponse`**: `GET /api/v1/emergency/pairings` 응답 DTO (달빛병원-심야약국 1:1 페어링 세트, `total_found`, `latency_ms`).
* **`SyncTriggerResponse`**: `POST /api/v1/emergency/sync` 온디맨드 동기화 결과 통계 (수집 수, 갱신 수, 생략 수, 비용 절감율 `saving_rate_percent`).
* **`SchedulerStatusResponse`**: `GET /api/v1/emergency/status` 스케줄러 가동 여부 및 등록된 작업 목록.

---

## 3. 데이터 변환 파이프라인 (Data Mapping Flow)

```
[NMC 공공데이터 XML] ──► EmergencyBedInfo ──► BedStateHashCache (MD5)
                                                      │
                                                      ▼
[사용자 자연어 입력] ──► ChatRequest ──► PatientSessionState (공유 메모리)
                                                      │
                                                      ├─► TriageExtractionResult
                                                      ├─► RankedEmergencyHospital
                                                      └─► LogisticsCardResult
                                                      │
                                                      ▼
                                             SupervisorResponse (클라이언트 반환)
```
