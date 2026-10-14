# 🛠️ 도메인 서비스 & 백엔드 도구 레이어 (`app/services`)

> **위치**: `app/services/`  
> **역할**: LLM의 환각(Hallucination) 없이 공공데이터포털, 공간 지리 연산, 약국 마진 매칭, 클라우드 DB 동기화를 수행하는 **결정론적 도메인 엔진(Zero-LLM Tools)** 및 **백그라운드 스케줄러** 패키지입니다.

---

## 📑 목차
1. [서비스 레이어 개요](#1-서비스-레이어-개요)
2. [5대 핵심 서비스 모듈 상세 명세](#2-5대-핵심-서비스-모듈-상세-명세)
   - [2.1 특일 판정 및 과밀화 평가 서비스 (holiday_service.py)](#21-특일-판정-및-과밀화-평가-서비스-holiday_servicepy)
   - [2.2 실시간 병상 수집 & Firestore 동기화 서비스 (emergency_sync_service.py)](#22-실시간-병상-수집--firestore-동기화-서비스-emergency_sync_servicepy)
   - [2.3 Haversine 공간 거리 및 랭킹 서비스 (spatial_service.py)](#23-haversine-공간-거리-및-랭킹-서비스-spatial_servicepy)
   - [2.4 달빛병원-심야약국 30분 마진 페어링 서비스 (pairing_service.py)](#24-달빛병원-심야약국-30분-마진-페어링-서비스-pairing_servicepy)
   - [2.5 APScheduler 2-트랙 백그라운드 데몬 (scheduler.py)](#25-apscheduler-2-트랙-백그라운드-데몬-schedulerpy)
3. [FinOps 최적화: In-Memory Hash Diffing 메커니즘](#3-finops-최적화-in-memory-hash-diffing-메커니즘)
4. [테스트 및 검증 파일](#4-테스트-및-검증-파일)

---

## 1. 서비스 레이어 개요

AI 에이전트가 아무리 정교해도, 병원의 위·경도 좌표나 실시간 잔여 병상 수치, 약국의 폐문 시각을 LLM에게 물어보면 거짓 정보를 생성할 위험이 있습니다.  
`app/services`는 **의료 데이터의 신뢰도 100%를 보장하기 위해 모든 계산과 데이터 필터링을 순수 Python 코드와 수학 공식으로만 처리**하는 결정론적 기반 도구층입니다.

---

## 2. 5대 핵심 서비스 모듈 상세 명세

### 2.1 특일 판정 및 과밀화 평가 서비스 (`holiday_service.py`)
* **핵심 클래스**: `HolidayService`
* **개발 목적**:
  - 공공데이터포털 병원 진료시간 데이터의 8번 코드(`dutyTime8s~8c`)는 **공휴일 전용**입니다. 오늘이 공휴일인지 판별하지 못하면 평일 시간표로 잘못 안내하는 사고가 발생합니다.
  - 외래 소아과가 전멸하는 공휴일·주말에는 응급실 과밀화 리스크를 사전에 산정하여 보호자에게 경고해야 합니다.
* **주요 기능**:
  - 한국천문연구원(KASI) 특일 정보 API(`getRestDeInfo`) 실시간 연동 (API 결측 시 주말 판별 Fallback).
  - 과밀화 리스크 3단계 산정:
    - `NORMAL`: 평일 (외래 소아과 운영)
    - `HIGH`: 토요일 / 일요일 (외래 축소, 응급실 내원 2배 증가)
    - `CRITICAL`: 법정공휴일 / 명절 연휴 (외래 전멸, 응급실 환자 4배 폭증)

---

### 2.2 실시간 병상 수집 & Firestore 동기화 서비스 (`emergency_sync_service.py`)
* **개발 목적**:
  - 국립중앙의료원(NMC) E-Gen 실시간 병상 데이터를 파싱하고, 비정형 공지사항의 당직의 부재를 정규식으로 검증하여 Cloud Firestore에 동기화.
* **주요 함수/클래스**:
  - `PEDIATRIC_BLOCK_PATTERN`:
    - 정규식: `(소아|영유아|신생아|소아청소년|소아과).*(불가|제한|부재|중단|불가능|진료안됨|수술불가|마감)`
    - 비정형 공지(`hpmg`)에서 *"소아 당직의 부재로 진료 제한"* 등의 문구를 100% 감지하여 `pediatric_acceptable`을 `False`로 강제 보정.
  - `fetch_emergency_beds(stage1)`:
    - 실시간 병상 수(`hv28`), 격리병상(`hv29`), 일반병상(`hvec`) 파싱 및 정규화.
  - `fetch_hospital_coordinates(stage1)`:
    - 530개 응급실 위경도를 로컬 캐시(`data/seoul_emergency_coords.json`)에서 1ms 내로 우선 로드.
  - `BedStateHashCache`:
    - MD5 해시 기반 상태 변경 감지기.
  - `sync_to_firestore(hospitals, holiday_meta)`:
    - Firestore `emergency_beds` 컬렉션에 변경분만 배치 쓰기하고, `emergency_summary/realtime`에 집계 요약 단일 문서 갱신.

---

### 2.3 Haversine 공간 거리 및 랭킹 서비스 (`spatial_service.py`)
* **개발 목적**:
  - 지오코딩 및 지도 API를 매번 부르면 1.5초 이상 지연되므로, 순수 구면 삼각법으로 사용자 GPS 기준 반경 10km 이내 병원을 5µs(마이크로초) 내에 정렬.
* **주요 함수**:
  - `haversine_distance(lat1, lon1, lat2, lon2) -> float`:
    - 지구 반경 6,371km 기준 두 위경도 좌표 간의 구면 거리를 km 단위로 정밀 계산.
  - `rank_emergency_hospitals(hospitals, user_lat, user_lon, max_radius_km, only_acceptable, limit)`:
    - 반경 필터링 및 소아 수용 가능 여부(`pediatric_acceptable`) 필터 적용 후 최단 거리순 정렬 반환.

---

### 2.4 달빛병원-심야약국 30분 마진 페어링 서비스 (`pairing_service.py`)
* **개발 목적**:
  - 야간에 진료하는 달빛어린이병원을 찾아도 인근 약국이 먼저 문을 닫아 처방약을 조제받지 못하는 **"야간 74% 조제 실패 사고"를 차단**.
* **주요 함수**:
  - `load_nationwide_pairings()`:
    - 전국 17개 시·도 29개 거점 달빛병원 및 30분 이상 늦게 닫는 안심 약국 1:1 매핑 데이터셋(`data/nationwide_pairings.json`) 로드.
  - `find_nearby_pairings(user_lat, user_lon, max_radius_km, limit)`:
    - 사용자 좌표 기준 반경 내 가장 가까운 달빛병원 + 30분 안심 약국 세트를 0ms 내에 검색하여 반환.

---

### 2.5 APScheduler 2-트랙 백그라운드 데몬 (`scheduler.py`)
* **핵심 클래스**: `BackgroundDaemon` (글로벌 싱글톤 `background_daemon`)
* **개발 목적**:
  - 사용자 조회 시 공공 API를 동기 호출하지 않고, 백그라운드 워커가 주기적으로 최신화하여 사용자 요청 시 0ms로 응답하도록 보장.
* **2-트랙 스케줄링 구조**:
  - **Track 1 (5분 주기 실시간 병상 폴러)**:
    - `poll_realtime_beds()` 실행 ➔ NMC E-Gen 호출 ➔ MD5 Hash Diffing ➔ 변경된 병상만 Firestore Write.
  - **Track 2 (24시간 주기 정적 데이터 갱신 워커, 매일 04:00 AM)**:
    - `sync_static_datasets()` 실행 ➔ 응급실 위경도 및 전국 달빛병원-약국 매스터셋 증분 동기화.

---

## 3. FinOps 최적화: In-Memory Hash Diffing 메커니즘

Cloud Firestore 무료 티어(Spark Plan)는 **일일 쓰기 20,000회**로 엄격히 제한됩니다.  
서울 시내 50개 응급실을 5분마다 무조건 Firestore에 Write하면:
$$\text{일일 쓰기 수} = 50\text{개} \times 12\text{회/시간} \times 24\text{시간} = 14,400\text{회 (무료 쿼터의 72% 소진)}$$

`BedStateHashCache`는 병상의 `(소아병상수, 공지사항, 수용여부)` 지문(Fingerprint)을 MD5로 캐싱하여, **실제 상태가 변경된 병상(보통 1~5곳)만 Firestore에 쓰기(Write)**를 수행합니다:

```
[NMC E-Gen 50개 병상 수집]
           │
           ▼
[MD5 Fingerprint 계산: p_beds + notice + acceptable]
           │
     ┌─────┴────────────────┐
     ▼                      ▼
[해시 변경 감지 (1~3곳)]  [해시 동일 (47~49곳)]
     │                      │
     ▼                      ▼
Firestore Batch Write    쓰기 완전 생략 (Skipped)
(비용 90~100% 절감 실증, 일일 무료 티어 완벽 수호)
```

---

## 4. 테스트 및 검증 파일

* **단위/통합 테스트**: [`tests/test_step1_services.py`](file:///e:/monnlight/tests/test_step1_services.py)
  - `TC-101`: KASI 특일 판정 및 과밀화 리스크 산정 검증
  - `TC-102`: E-Gen 비정형 공지 정규식 필터링 검증
  - `TC-103`: In-Memory Hash Diffing 비용 절감률(80%+) 검증
  - `TC-104`: Haversine 5µs 공간 거리 정렬 및 소아 필터 검증
  - `TC-105`: 달빛어린이병원 + 30분 마진 약국 1:1 페어링 검증
  - `TC-106`: Firestore 배치 쓰기 모의 검증
  - `TC-107`: Step 1 통합 파이프라인 E2E 검증
* **인터랙티브 CLI 시연기**: [`app/demo_step1.py`](file:///e:/monnlight/app/demo_step1.py)
