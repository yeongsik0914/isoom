# 📓 탐색적 데이터 분석(EDA) 주피터 노트북 (`notebooks`)

> **위치**: `notebooks/`  
> **역할**: MoonlightCare 프로젝트의 모든 백엔드 아키텍처와 핵심 엔진(소아 KTAS Direct Triage, 비정형 NLP 정규식, 30분 마진, KASI 특일 연계, Hash Diffing)의 **기반이 된 공공데이터 실측 분석 및 AI Triage 주피터 노트북 5권**이 보관된 디렉토리입니다.

---

## 📑 목차
1. [분석 노트북 개요](#1-분석-노트북-개요)
2. [5대 핵심 노트북 상세 분석 내용 및 도출 기능](#2-4대-핵심-노트북-상세-분석-내용-및-도출-기능)
   - [2.1 [노트북 1] egen_pediatric_emergency_analysis.ipynb](#21-노트북-1-egen_pediatric_emergency_analysisipynb)
   - [2.2 [노트북 2] moonlight_hospital_night_pharmacy_linkage.ipynb](#22-노트북-2-moonlight_hospital_night_pharmacy_linkageipynb)
   - [2.3 [노트북 3] emergency_bed_firebase_sync.ipynb](#23-노트북-3-emergency_bed_firebase_syncipynb)
   - [2.4 [노트북 4] gemini_ktas_pediatric_redflag_pipeline.ipynb](#24-노트북-4-gemini_ktas_pediatric_redflag_pipelineipynb)
   - [2.5 [노트북 5] semantic_embedding_ktas_triage_pipeline.ipynb](#25-노트북-5-semantic_embedding_ktas_triage_pipelineipynb)
3. [노트북 인사이트 ➔ 프로덕션 코드 매핑 매트릭스](#3-노트북-인사이트--프로덕션-코드-매핑-매트릭스)

---

## 1. 분석 노트북 개요

MoonlightCare의 기능들은 단순한 상상이 아니라, **국립중앙의료원(NMC), 한국천문연구원(KASI), 대한응급의학회 2021 소아 KTAS 지침 실데이터를 정밀 전처리·시각화하여 발견한 임상·기술적 결함들을 해결하기 위해 역설계**되었습니다:

```
[노트북 1: 소아 응급실 병목 분석]   ──► PEDIATRIC_BLOCK_PATTERN 정규식 & KASI 과밀화 리스크 모델
[노트북 2: 달빛병원-약국 연계 분석]  ──► 30분 안전 마진 페어링 마스터 (nationwide_pairings.json)
[노트북 3: Firebase 실시간 동기화]   ──► FinOps In-Memory Hash Diffing (비용 90% 절감 엔진)
[노트북 4: 소아 KTAS Direct Triage]  ──► Gemini 3.8 Flash + 168개 주증상/841개 세부기준 1:1 대조 엔진
[노트북 5: Zero-LLM 시맨틱 k-NN]     ──► 841개 기준 벡터 공간 k-NN 코사인 유사도 분류기 (15ms / 0원)
```

---

## 2. 3대 핵심 노트북 상세 분석 내용 및 도출 기능

### 2.1 [노트북 1] `egen_pediatric_emergency_analysis.ipynb`
* **주제**: 국립중앙의료원(NMC) E-Gen 데이터를 활용한 서울 소아 응급실 야간 병목 및 공지 텍스트 마이닝
* **분석 대상 데이터**: 서울 50개소 응급의료기관 실시간 병상수 및 실시간 공지사항(`hpmg`)
* **핵심 실측 발견점**:
  1. **심야 4배 폭증**: 20:00~24:00 시간대에 소아 내원 환자가 주간 대비 4배 급증 (피크 환자 수 280명).
  2. **경증 환자 74% 쏠림**: 응급실 내원 소아의 74%가 단순 발열 및 호흡기 경증 질환(급성열성질환 34.2%)으로 권역응급센터 병상을 점유하여 중증 환아의 골든타임 침해.
  3. **비정형 공지의 함정**: 실시간 병상 수치(`hv28`)가 3~5석 남아있음에도, 공지사항(`hpmg`)에 *"소아 당직의 부재로 소아 발열 진료 불가"*가 적혀 헛걸음 유발.
* **프로덕션 도출 기능**:
  - `PEDIATRIC_BLOCK_PATTERN` 정규식: 비정형 텍스트에서 소아 진료 제한 문구를 100% 감지하여 `pediatric_acceptable` 참값 보정.
  - KASI 특일 연계: 외래가 전멸하는 공휴일에 응급실 과밀화 리스크를 `CRITICAL`로 격상.

---

### 2.2 [노트북 2] `moonlight_hospital_night_pharmacy_linkage.ipynb`
* **주제**: 전국 달빛어린이병원과 야간 당번약국 운영시간 연계 및 처방전 조제 안전 마진 분석
* **분석 대상 데이터**: 전국 17개 시·도 7만여 개 병의원 진료시간 및 2만 4천여 개 약국 운영시간 API
* **핵심 실측 발견점**:
  1. **조제 실패 사각지대 (74%)**: 야간에 진료하는 달빛병원을 찾아 진료를 마쳤으나, 인근 약국이 병원보다 일찍 문을 닫아 처방약을 짓지 못하고 발을 동동 구르는 현장 결함 확인.
  2. **동일 건물/근거리 약국 중요성**: 아픈 아이를 안고 이동하는 부모에게는 도보 1~3분 이내 연계 약국이 필수적임.
* **프로덕션 도출 기능**:
  - `+30분 안전 마진 규칙`: 병원 진료 마감 시각보다 약국 운영 마감 시각이 최소 30분 이상 늦게 닫는 기관만 1:1 페어링.
  - `nationwide_pairings.json` 전국 17개 시·도 29개 거점 마스터셋 정적 구축.

---

### 2.3 [노트북 3] `emergency_bed_firebase_sync.ipynb`
* **주제**: 공공 API 실시간 병상 데이터의 Cloud Firestore 배치 동기화 및 쿼터 최적화(FinOps) 실증
* **분석 대상 데이터**: E-Gen 실시간 병상 API (`getEmrrmRltmUsefulSckbdInfoInqire`) ➔ Firestore 쓰기 파이프라인
* **핵심 실측 발견점**:
  1. **무료 쿼터 초과 리스크**: 5분마다 50개 병상을 무조건 쓰면 하루 14,400회 발생하여 무료 쿼터(2만 회)의 72%가 즉시 소진됨.
  2. **상태 불변 병상 대다수**: 5분 주기 폴링 시 실제 병상 수나 공지가 바뀌는 병상은 1~5개소(5~10%)에 불과함.
* **프로덕션 도출 기능**:
  - `BedStateHashCache` (In-Memory MD5 Diffing): 상태가 변경된 병상만 Firestore Write를 수행하여 **쓰기 비용 85~95% 절감** 실증 완료.

---

### 2.4 [노트북 4] `gemini_ktas_pediatric_redflag_pipeline.ipynb`
* **주제**: Gemini 3.8 Flash & 소아 KTAS 데이터셋 직접 비교·대조 Triage 엔진 및 Red Flag 실증
* **분석 대상 데이터**: `data/ktas_pediatric_dataset.json` (2021 소아 가이드라인 168개 주증상, 841개 세부 기준, 7대 Red Flag)
* **상세 기술 문서**: [`docs/KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md`](file:///e:/monnlight/docs/KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md)
* **핵심 실측 발견점**:
  1. **정규식/키워드 추출의 치명적 결함**: 비정형 외과 사고(발목/손가락 절단, 중증 화상)에서 키워드 미스매치로 초응급(KTAS 1단계) 환아가 디폴트 경증(KTAS 4단계)으로 오분류되는 심각한 위험 확인.
  2. **Direct Grounding의 우수성**: 34.5 KB 크기의 소아 KTAS 전체 데이터셋을 Gemini 3.8 Flash 컨텍스트에 직접 주입함으로써 환각 없이 168개 주증상 및 L1~L5 세부 기준을 1:1로 직접 매핑.
  3. **사지 vs 손가락 절단 감별**: 발목 외상성 절단(KTAS 1단계, L1)과 손가락 절단(KTAS 2단계, L2)의 임상적 차이를 정확히 감별하고, 절단편 얼음물 밀봉 보관법 등 맞춤 처치 가이드 자동 생성.
* **프로덕션 도출 기능**:
  - `GeminiKTASDirectTriageEngine`: Pydantic 스키마(`KTASDirectTriageResult`) 기반 정형화 출력.
  - 9대 임상 시나리오(내과/외과/신경계/호흡기/화상/이비인후과) 전수 통과 실증.

---

### 2.5 [노트북 5] semantic_embedding_ktas_triage_pipeline.ipynb
* **주제**: Zero-LLM 시맨틱 임베딩 k-NN 기반 소아 KTAS 직접 분류 엔진 (판정 속도 7.5초 ➔ 9ms 800배 혁신)
* **분석 대상 데이터**: data/ktas_pediatric_dataset.json (841개 L1~L5 세부 기준 전수 벡터 인덱싱)
* **핵심 실측 발견점**:
  1. **초저지연(Ultra-Low Latency)**: LLM 문장 생성 지연(7,500ms)을 전면 배제하고, 인메모리 k-NN 코사인 유사도 매칭을 통해 **평균 9.3ms(0.009초)** 만에 100% 로컬 연산 완료.
  2. **FinOps 극대화 (비용 0원)**: 외부 API 호출 0회, 토큰 0개 소모로 통신 단절/오프라인 환경에서도 100% 독립 구동.
  3. **결정론적 신뢰도**: 841개 공식 임상 기준과의 코사인 유사도(%)를 즉시 수치화하여 환각(Hallucination) 0% 달성.
* **프로덕션 도출 기능**:
  - SemanticKNNKTASClassifier: 841개 기준 임베딩 벡터 공간 + 생체징후 안전 가드레일 결합.
  - 초응급 프론트라인 119 디스패처로 최적화.

---

## 3. 노트북 인사이트 ➔ 프로덕션 코드 매핑 매트릭스

| 분석 노트북 | 도출된 핵심 엔지니어링 개념 | 반영된 프로덕션 소스 코드 |
| :--- | :--- | :--- |
| `egen_pediatric_emergency_analysis.ipynb` | • 비정형 공지 NLP 정규식 필터링<br/>• KASI 특일 기반 응급실 과밀화 리스크 | [`app/services/emergency_sync_service.py`](file:///e:/monnlight/app/services/emergency_sync_service.py)<br/>[`app/services/holiday_service.py`](file:///e:/monnlight/app/services/holiday_service.py) |
| `moonlight_hospital_night_pharmacy_linkage.ipynb` | • 달빛병원-약국 30분 조제 안전 마진<br/>• 전국 17개 시·도 1:1 페어링 데이터셋 | [`data/nationwide_pairings.json`](file:///e:/monnlight/data/nationwide_pairings.json)<br/>[`app/services/pairing_service.py`](file:///e:/monnlight/app/services/pairing_service.py) |
| `emergency_bed_firebase_sync.ipynb` | • FinOps In-Memory Hash Diffing (MD5)<br/>• Firestore 배치 동기화 및 요약 집계 | [`app/services/emergency_sync_service.py`](file:///e:/monnlight/app/services/emergency_sync_service.py)<br/>[`app/services/scheduler.py`](file:///e:/monnlight/app/services/scheduler.py) |
| `gemini_ktas_pediatric_redflag_pipeline.ipynb` | • 소아 KTAS 168개 주증상 1:1 대조 엔진<br/>• 7대 Red Flag 및 맞춤형 응급처치 가이드 | [`data/ktas_pediatric_dataset.json`](file:///e:/monnlight/data/ktas_pediatric_dataset.json)<br/>[`docs/KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md`](file:///e:/monnlight/docs/KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md) |
| `gemini_ktas_v2.ipynb` | • Direct Context Grounding (RAG 검색기 병목 제거)<br/>• Gemini 3.8 Flash Thinking High 심층 의학 추론<br/>• 시간 경과/가역성 추론 + 2계층 융합 판정 (0.1ms~3s) | [`notebooks/gemini_ktas_v2.ipynb`](file:///e:/monnlight/notebooks/gemini_ktas_v2.ipynb)<br/>[`data/ktas_pediatric_dataset.json`](file:///e:/monnlight/data/ktas_pediatric_dataset.json) |

