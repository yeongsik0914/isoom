# 🌐 REST API 서빙 레이어 (`app/api`)

> **위치**: `app/api/` (엔드포인트: `app/api/v1/`)  
> **역할**: 웹 및 모바일 프론트엔드 클라이언트가 즉시 연동할 수 있도록 실시간 AI 상담, Server-Sent Events(SSE) 스트리밍, 5ms 초고속 공간 검색, 백그라운드 동기화 엔드포인트를 제공하는 FastAPI 라우터 패키지입니다.

---

## 📑 목차
1. [API 레이어 개요](#1-api-레이어-개요)
2. [전체 엔드포인트 명세표 (API Specification)](#2-전체-엔드포인트-명세표-api-specification)
3. [실시간 대화 & 스트리밍 라우터 (v1/chat.py)](#3-실시간-대화--스트리밍-라우터-v1chatpy)
   - [3.1 POST /api/v1/chat](#31-post-apiv1chat)
   - [3.2 POST /api/v1/chat/stream (SSE 스트리밍)](#32-post-apiv1chatstream-sse-스트리밍)
   - [3.3 세션 수명주기 관리 엔드포인트](#33-세션-수명주기-관리-엔드포인트)
4. [응급 및 공간 검색 라우터 (v1/emergency.py)](#4-응급-및-공간-검색-라우터-v1emergencypy)
   - [4.1 GET /api/v1/emergency/nearby](#41-get-apiv1emergencynearby)
   - [4.2 GET /api/v1/emergency/pairings](#42-get-apiv1emergencypairings)
   - [4.3 POST /api/v1/emergency/sync & GET /status](#43-post-apiv1emergencysync--get-status)
5. [SSE 스트리밍 이벤트 규격 (Event Protocol)](#5-sse-스트리밍-이벤트-규격-event-protocol)
6. [테스트 및 검증 파일](#6-테스트-및-검증-파일)

---

## 1. API 레이어 개요

ISOOM 백엔드는 오케스트레이터와 도메인 서비스를 직접 클라이언트에 노출하지 않고, **FastAPI 비동기 서빙 아키텍처**를 통해 일관된 스키마 검증과 OpenAPI 스웨거 문서(`/docs`)를 제공합니다:

```
[클라이언트 (React, Next.js, 모바일 뷰)]
                  │
                  ▼ (HTTP / HTTPS)
        [main.py (FastAPI App)]
                  │
    ┌─────────────┴─────────────┐
    ▼                           ▼
[/api/v1/chat]          [/api/v1/emergency]
• 일반 상담             • 5ms 주변 응급실 검색
• SSE 실시간 스트리밍   • 전국 30분 마진 약국
• 세션 상세 / 리셋      • 온디맨드 병상 동기화
                        • 스케줄러 상태 모니터링
```

---

## 2. 전체 엔드포인트 명세표 (API Specification)

| HTTP 메서드 | 경로 (Path) | 주요 기능 요약 | 응답 모델 DTO | 목표 레이턴시 |
| :---: | :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/chat` | 부모-에이전트 실시간 상담 (문진, Red Flag, 매칭 일괄 처리) | `SupervisorResponse` | ~ 1.2s |
| `POST` | `/api/v1/chat/stream` | Server-Sent Events (SSE) 실시간 단어 델타 스트리밍 | `text/event-stream` | 최초 0.05s |
| `GET` | `/api/v1/chat/session/{sid}` | 특정 세션의 수집 변수(체온, 월령 등) 및 대화 이력 조회 | `SessionDetailResponse` | < 1ms |
| `DELETE` | `/api/v1/chat/session/{sid}` | 특정 세션 인메모리 즉시 삭제 및 초기화 | `{"status": "SUCCESS"}` | < 1ms |
| `GET` | `/api/v1/chat/sessions` | 현재 메모리 유지 중인 활성 세션 총 개수 조회 | `{"active_sessions_count"}` | < 1ms |
| `GET` | `/api/v1/emergency/nearby` | GPS 좌표 기준 10km 이내 소아 가용 응급실 초고속 검색 | `NearbyEmergencyResponse` | < 10ms |
| `GET` | `/api/v1/emergency/pairings` | 전국 달빛병원 + 30분 마진 심야약국 1:1 페어링 세트 검색 | `PairingSearchResponse` | < 5ms |
| `POST` | `/api/v1/emergency/sync` | E-Gen 병상 즉시 수집 & In-Memory Hash Diffing 반영 | `SyncTriggerResponse` | ~ 0.5s |
| `GET` | `/api/v1/emergency/status` | APScheduler 2-트랙 워커 가동 상태 및 최근 실행 통계 | `SchedulerStatusResponse` | < 1ms |

---

## 3. 실시간 대화 & 스트리밍 라우터 (`v1/chat.py`)

### 3.1 `POST /api/v1/chat`
* **요청 바디 (`ChatRequest`)**:
  ```json
  {
    "user_message": "14개월 아기 38.5도 열나요. 2시간째 미열이고 해열제 먹였어요.",
    "session_id": "optional-session-id",
    "user_lat": 37.5133,
    "user_lon": 127.1001,
    "user_address": "서울 송파구 잠실동",
    "stream": false
  }
  ```
* **응답 바디 (`SupervisorResponse`)**:
  - `is_emergency`: 0ms Red Flag 감지 여부 (`true` 시 119 가이드 우선 노출).
  - `current_step`: 현재 FSM 상태 (`TRIAGE`, `COMPLETED`, `EMERGENCY_ESCALATION` 등).
  - `hospitals`: 거리순 추천 의료기관 목록 (기관명, 유형, 거리_km, 소아병상수 등).
  - `pharmacies`: 30분 안전 마진 확보 심야약국 목록.
  - `call_script`: 내원 직전 접수처 확인용 30초 구어체 스크립트.
  - `checklist`: 2024년 5월 본인확인 의무화 필수 지참 서류 목록.
  - `disclaimer`: 의료법 제27조 준수 공식 면책 배지.

### 3.2 `POST /api/v1/chat/stream` (SSE 스트리밍)
* 화면에 타이핑되듯 글자가 실시간으로 출력되길 원하는 모바일/웹 UI를 위해 SSE(Server-Sent Events) 스트림을 제공합니다.
* `media_type="text/event-stream"`.

### 3.3 세션 수명주기 관리 엔드포인트
* `GET /api/v1/chat/session/{session_id}`: 부모가 브라우저를 새로고침했을 때 직전까지 입력한 체온, 월령, 증상 데이터를 복원.
* `DELETE /api/v1/chat/session/{session_id}`: 새 진료 상담을 시작하기 위해 이전 세션을 깨끗이 리셋.

---

## 4. 응급 및 공간 검색 라우터 (`v1/emergency.py`)

### 4.1 `GET /api/v1/emergency/nearby`
* **쿼리 파라미터**:
  - `lat`: 사용자 위도 (기본: 37.5133)
  - `lon`: 사용자 경도 (기본: 127.1001)
  - `radius_km`: 검색 반경 (기본 10.0km, 최대 50km)
  - `only_acceptable`: 소아 응급 진료 즉시 가능 기관만 필터링 (`true`)
  - `limit`: 반환 개수 (기본 10개)
* **특징**:
  - KASI 특일 API와 연동된 `surge_risk_level`("NORMAL" / "HIGH" / "CRITICAL")을 함께 반환하여 응급실 과밀화 리스크를 즉시 인지 가능.
  - 서버 내부 연산 소요 시간(`latency_ms`)을 응답에 동봉.

### 4.2 `GET /api/v1/emergency/pairings`
* **쿼리 파라미터**: `lat`, `lon`, `radius_km` (기본 25km), `limit` (기본 5개)
* 전국 17개 시·도 29개 거점 달빛어린이병원과 야간 약국의 1:1 페어링 세트를 거리순으로 정렬하여 반환.

### 4.3 `POST /api/v1/emergency/sync` & `GET /status`
* 개발자/운영자용 엔드포인트:
  - `/sync`: 5분 주기를 기다리지 않고 즉시 공공 API 수집 및 Hash Diffing을 트리거하여 결과 반환.
  - `/status`: 백그라운드 스케줄러의 기동 여부, 등록된 작업 주기, 누적 폴링 횟수 조회.

---

## 5. SSE 스트리밍 이벤트 규격 (Event Protocol)

```
event: status
data: {"status": "PROCESSING", "message": "증상 분석 및 가드레일 검사 중..."}

event: delta
data: {"delta": "아이가 "}

event: delta
data: {"delta": "열이 나서 "}

event: delta
data: {"delta": "걱정되셨겠습니다. "}

event: result
data: {"session_id": "...", "current_step": "COMPLETED", "hospitals": [...], ...}

event: done
data: [DONE]
```

---

## 6. 테스트 및 검증 파일

* **단위/통합 테스트**: [`tests/test_step5_api.py`](file:///e:/monnlight/tests/test_step5_api.py) (TC-501 ~ TC-510 10개 전수 통과)
* **인터랙티브 CLI 시연기**: [`app/demo_step5.py`](file:///e:/monnlight/app/demo_step5.py)
