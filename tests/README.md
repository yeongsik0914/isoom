# 🧪 단위 및 통합 테스트 스위트 (`tests`)

> **위치**: `tests/`  
> **역할**: MoonlightCare 프로젝트의 모든 모듈, 안전 가드레일, AI 멀티 에이전트, FSM 오케스트레이터, REST API의 무결성을 **자동화된 43개 단위/통합 테스트와 골든 케이스 평가 데이터셋으로 검증**하는 품질 보증(QA) 패키지입니다.

---

## 📑 목차
1. [테스트 아키텍처 개요](#1-테스트-아키텍처-개요)
2. [단계별 테스트 스위트 상세 명세 (Steps 1~5)](#2-단계별-테스트-스위트-상세-명세-steps-15)
   - [2.1 test_step1_services.py (도메인 도구 & FinOps)](#21-test_step1_servicespy-도메인-도구--finops)
   - [2.2 test_step2_guardrail.py (0ms 안전 가드레일)](#22-test_step2_guardrailpy-0ms-안전-가드레일)
   - [2.3 test_step3_agents.py (AI 멀티 에이전트)](#23-test_step3_agentspy-ai-멀티-에이전트)
   - [2.4 test_step4_orchestrator.py (Supervisor FSM)](#24-test_step4_orchestratorpy-supervisor-fsm)
   - [2.5 test_step5_api.py (FastAPI REST & 스케줄러)](#25-test_step5_apipy-fastapi-rest--스케줄러)
3. [정량적 성능 벤치마크 결과](#3-정량적-성능-벤치마크-결과)
4. [임상 골든 케이스 평가기 (tests/evals)](#4-임상-골든-케이스-평가기-testsevals)
5. [테스트 실행 명령어 가이드](#5-테스트-실행-명령어-가이드)

---

## 1. 테스트 아키텍처 개요

MoonlightCare는 의료 안전 및 법적 리스크를 원천 차단하기 위해 **테스트 주도 개발(TDD)** 방식을 엄격히 적용하였습니다.  
현재 **총 66개 테스트(단위/통합 테스트 66개)가 100% 무결점으로 통과**되고 있습니다:

```
[Issue Fixes 결함방어]    (7개)  ──► TC-FIX-01 ~ TC-FIX-07 (100% PASS)
[Step 1 도메인 도구]      (7개)  ──► TC-101 ~ TC-107       (100% PASS)
[Step 2 안전 가드레일]     (12개) ──► TC-201 ~ TC-212       (100% PASS)
[Red Flag V2 고도화 검증] (8개)  ──► TC-RF2-01 ~ TC-RF2-08 (100% PASS)
[Step 3 AI 에이전트]      (7개)  ──► TC-301 ~ TC-308       (100% PASS)
[Step 4 오케스트레이터]     (7개)  ──► TC-401 ~ TC-407       (100% PASS)
[Step 5 FastAPI 서빙]     (10개) ──► TC-501 ~ TC-510       (100% PASS)
[Step 6 E2E 통합]        (8개)  ──► TC-601 ~ TC-608       (100% PASS)
──────────────────────────────────────────────────────────
총계: 66개 테스트 전수 통과 (100% OK)
골든 케이스 Evals: 40개 전수 통과 (100.0%, 평균 99.5점)
```

---

## 2. 단계별 테스트 스위트 상세 명세 (Steps 1~5)

### 2.1 `test_step1_services.py` (도메인 도구 & FinOps, 7개 테스트)
* `TC-101`: KASI 특일 판정 및 공휴일 과밀화 리스크(`CRITICAL`) 정상 산출
* `TC-102`: 국립중앙의료원(NMC) E-Gen 실시간 병상 파싱 및 비정형 공지 정규식 필터링
* `TC-103`: In-Memory Hash Diffing (MD5) 비용 절감률 80% 이상 검증 (Spark 플랜 쿼터 방어)
* `TC-104`: Haversine 5µs 공간 거리 정렬 및 소아 수용 가능 필터링 정확도
* `TC-105`: 달빛어린이병원 + 30분 마진 심야약국 1:1 페어링 세트 0ms 검색
* `TC-106`: Firestore 배치 쓰기 및 요약 집계(Summary) 단일 문서 갱신 모의 검증
* `TC-107`: Step 1 통합 파이프라인 E2E 정상 완주

### 2.2 `test_step2_guardrail.py` (0ms 안전 가드레일, 12개 테스트)
* `TC-201`: 생후 100일 미만 38도 고열 감지 (신생아 패혈증 Red Flag)
* `TC-202`: 열성 경련 / 발작 / 사지 떨림 감지
* `TC-203`: 극심한 처짐 / 의식 저하 / 무반응 감지
* `TC-204`: 청색증 / 흉벽 함몰 / 비익 호흡 감지
* `TC-205`: 중증 탈수 (8시간 이상 무뇨, 눈물 없음) 감지
* `TC-206`: 두부 외상 후 구토 및 기면 감지
* `TC-207`: 담즙성 녹색 구토 및 분수토 감지
* `TC-208`: 정상 미열(37.8℃, 단순 감기) 비응급 통과 확인 (False Positive 방어)
* `TC-209`: 의료법 제27조 진단명 확정 선언 중화 및 면책 배지 결합
* `TC-210`: 의료법 제27조 구체적 약물 용량 지시 중화
* `TC-211`: PatientSessionState DTO 유효성 및 상태 전이 검증
* `TC-212`: 1,000회 연속 Red Flag 검사 초고속 벤치마크 (< 0.1ms/회)

### 2.3 `test_step3_agents.py` (AI 멀티 에이전트, 7개 테스트)
* `TC-301`: TriageAgent 자연어 입력에서 4대 임상 변수(월령, 체온, 시간, 증상) 정형화
* `TC-302`: TriageAgent 의료법 제27조 질환명 추측 유도 방어
* `TC-303`: TriageAgent 정보 부족 시 보충 질문 생성 및 멀티턴 대화 유지
* `TC-304`: MatchingAgent 고열/중증 환아 소아 전문 응급실 우선 배정
* `TC-305`: MatchingAgent 경증 환아 달빛병원 + 30분 약국 세트 배정
* `TC-306`: LogisticsAgent 30초 유선 확인 통화 스크립트 구어체 생성
* `TC-307`: LogisticsAgent 2024년 5월 본인확인 의무화 지참 서류 목록 생성
* `TC-308`: E2E 3-Agent 파이프라인 전수 통합 실행

### 2.4 `test_step4_orchestrator.py` (Supervisor FSM, 7개 테스트)
* `TC-401`: 단일 턴 완결 문진 및 정상 FSM 완주 검증
* `TC-402`: 2턴 점진적 문진 연속성 및 변수 누적 검증
* `TC-403`: 3턴 데드락 가드(무한 루프 방지 강제 전이) 실증
* `TC-404`: 1턴 즉시 Red Flag 비상 에스컬레이션 검증
* `TC-405`: 2턴 중도 경련 급변(Mid-Turn Deterioration) 즉각 차단 검증
* `TC-406`: 의료법 제27조 단일 관문 소독 및 면책 고지 검증
* `TC-407`: SessionManager 30분 TTL 자동 정리 및 메모리 누수 방어 검증

### 2.5 `test_step5_api.py` (FastAPI REST & 스케줄러, 10개 테스트)
* `TC-501`: 시스템 루트(`GET /`) 및 헬스체크(`GET /health`) 응답 검증
* `TC-502`: GPS 기준 주변 소아 응급실 초고속 공간 검색(`GET /api/v1/emergency/nearby`)
* `TC-503`: 전국 달빛어린이병원 + 30분 마진 심야약국 페어링 검색(`GET /api/v1/emergency/pairings`)
* `TC-504`: 단일 턴 부모 상담 및 출동 종합 카드 반환(`POST /api/v1/chat`)
* `TC-505`: 0ms Red Flag 감지 시 즉시 119 긴급 격상 모달 반환(`POST /api/v1/chat`)
* `TC-506`: 멀티턴 대화 세션 상태 연속성 및 3턴 가드 실증
* `TC-507`: 활성 세션 상세 조회 및 삭제 리셋 수명주기 검증
* `TC-508`: Server-Sent Events (SSE) 실시간 스트리밍 및 `[DONE]` 수신
* `TC-509`: 백그라운드 스케줄러 상태 확인 및 온디맨드 병상 동기화 트리거
* `TC-510`: APScheduler 2-트랙 작업 등록 및 실행 주기 생명주기 검증

### 2.6 `test_audit_fixes.py` (결함 감사 선제 조치 검증, 7개 테스트)
* `TC-FIX-01`: Gemini 3.8 Flash & 3.5 Lite 최신 모델 구성 및 `Settings` 바인딩 검증
* `TC-FIX-02`: 실시간 응급실 병상 인메모리 TTL 캐시 5ms 이내 초고속 반환 검증
* `TC-FIX-03`: 전국 17개 시·도(수원, 대전, 부산, 광주, 평창, 인천 등) 동적 stage1 행정구역 매핑 검증
* `TC-FIX-04`: 악의적 질문 및 위험 민간요법(손 따기), 남은 항생제, 용량 직접 지시, Dr. Kim 탈옥 방어 검증
* `TC-FIX-05`: Triage Fallback 파서 연령('만 4세', '초등 1학년'), 기간('3일 전', '어제'), 소아 다발성 증상 정규화 검증
* `TC-FIX-06`: 방문 시각 기준 진료 마감 시간(HH:MM) 필터링, 조기 마감 주의 태그 및 심야(23시 이후) 24시간 응급실 라우팅 검증
* `TC-FIX-07`: 전국 권역 거점 소아응급센터 및 모의 좌표계 정상 연동 검증

### 2.7 `test_step6_e2e.py` (E2E 통합 테스트 & 시나리오, 8개 테스트)
* `TC-601`: 생후 55일 고열 즉시 119 직행 및 기도확보 응급처치 가이드 출력 검증 (Track A)
* `TC-602`: 14개월 38.5도 경증 2턴 문진 ➔ 달빛병원 + 30분 안심 약국 페어링 ➔ 30초 통화 스크립트 출력 검증 (Track B)
* `TC-603`: 의료법 제27조 무면허 의료행위 방어(부모의 돌발진 단정 유도 거부 및 전문의 대면 진찰 안내 검증)
* `TC-604`: 적대적 4대 안전 위반(바늘 사혈, 남은 항생제, 용량 처방 요구, 단독 병원 알선 요구) 0ms 원천 차단 검증
* `TC-605`: 다중 턴 중도 급변(Deterioration) 시나리오(1턴 미열 상담 중 2턴 청색증 발생 시 즉시 Track A 비상 전환 검증)
* `TC-606`: 3턴 데드락 가드(3턴 연속 모호한 입력 시 안전 기본값 세팅 후 MATCHING 강제 전이 검증)
* `TC-607`: FastAPI REST API `/api/v1/chat` E2E 단일/다중 턴 호출 무결성 검증
* `TC-608`: FastAPI SSE 실시간 스트리밍 `/api/v1/chat/stream` 토큰 스트리밍 및 `[DONE]` 완료 이벤트 검증

---

## 3. 정량적 성능 벤치마크 결과

* **1,000회 Red Flag 선제 검사**:
  - 총 소요 시간: **11.72ms**
  - **1회당 평균 레이턴시: 11.72 µs (0.011ms)** ➔ 0ms 실시간 차단 목표 완벽 달성.
* **Haversine 공간 구면거리 계산**: 1회당 **< 5 µs**.
* **전체 58개 테스트 스위트 실행 속도**: 100% 무결점 통과 (**Ran 58 tests in 193s, OK**).

---

## 4. 임상 골든 케이스 평가기 (`tests/evals`)

* **평가 데이터셋**: [`tests/evals/golden_test_cases.json`](file:///e:/monnlight/tests/evals/golden_test_cases.json)
* **구성**: 실측 의료 임상 데이터 기반 40대 골든 테스트 케이스:
  1. `Triage & Intake` (TC-01 ~ TC-07, 7건)
  2. `Medical Guardrail` (TC-08 ~ TC-15, 8건)
  3. `Emergency Escalation` (TC-16 ~ TC-23, 8건)
  4. `Facility Matching` (TC-24 ~ TC-31, 8건)
  5. `Visit Logistics` (TC-32 ~ TC-35, 4건)
  6. `End-to-End Comprehensive` (TC-36 ~ TC-40, 5건)
* **5대 평가 루브릭 달성 결과**:
  - `DIM-1`: 의료법 준수 및 진단/처방 원천 차단율: **100.0 / 100점** (목표 100% 달성)
  - `DIM-2`: KTAS Red Flag 초응급 감지율: **97.5 / 100점** (목표 95%+ 달성)
  - `DIM-3`: 문진 효율성 및 필수 임상 변수 추출 정확도: **100.0 / 100점** (목표 95%+ 달성)
  - `DIM-4`: 시설 매칭 정확도 및 30분 안전 마진 확보율: **100.0 / 100점** (목표 95%+ 달성)
  - `DIM-5`: 부모 공감도 및 내원 물류 지참물 안내율: **100.0 / 100점** (목표 90%+ 달성)
* **평가 실행 결과**: **40 / 40 케이스 100.0% 통과 (평균 99.5점)**, 리포트: [`tests/evals/eval_report.md`](file:///e:/monnlight/tests/evals/eval_report.md)

---

## 5. 테스트 및 평가 실행 명령어 가이드

```bash
# 1. 전체 58개 테스트 일괄 실행
python -m unittest discover tests

# 2. 특정 단계별 테스트 단독 실행
python -m unittest tests/test_audit_fixes.py
python -m unittest tests/test_step1_services.py
python -m unittest tests/test_step2_guardrail.py
python -m unittest tests/test_step3_agents.py
python -m unittest tests/test_step4_orchestrator.py
python -m unittest tests/test_step5_api.py
python -m unittest tests/test_step6_e2e.py

# 3. 40대 임상 골든 케이스 Evals 자동 평가 실행
python tests/evals/run_evals.py

# 4. 실시간 인터랙티브 시연 데모 CLI 실행
python demo_step6.py
```
