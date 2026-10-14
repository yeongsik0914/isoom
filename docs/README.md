# 📚 기술 기획 및 아키텍처 문서 허브 (`docs`)

> **위치**: `docs/`  
> **역할**: MoonlightCare 프로젝트의 프로덕트 요구사항(PRD), 데이터베이스 설계서, 소아 KTAS Direct Triage 아키텍처, 타 서비스 비교 분석서, 공공데이터 특성 고찰 보고서 등 **8대 핵심 기술 기획 문서가 집대성된 공식 기술 문서고**입니다.

---

## 📑 목차 및 문서 맵 (Index of Documents)

| 문서 파일명 | 문서 성격 | 핵심 내용 요약 |
| :--- | :---: | :--- |
| [**`PROJECT_PLAN.md`**](file:///e:/monnlight/docs/PROJECT_PLAN.md) | **종합 기획서 (PRD)** | • 프로젝트 기획 배경, 사회적 문제 정의 (야간 소아 응급실 뺑뺑이)<br/>• 사용자 페르소나 및 핵심 유저 여정 (User Journey)<br/>• 법적 규제 검토 (의료법 제27조, 국민건강보험법 본인확인 의무화)<br/>• 3+1 멀티 에이전트 아키텍처 및 단계별 로드맵 |
| [**`KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md`**](file:///e:/monnlight/docs/KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md) | **AI Triage 설계서** | • Gemini 3.8 Flash + `ktas_pediatric_dataset.json`(168개 주증상/841개 세부기준) 직접 대조 엔진<br/>• 키워드 정규식 추출 결함(절단/의식저하 4단계 오분류) 극복 원리<br/>• 사지 vs 손가락 절단 감별, Pydantic 스키마, 9대 임상 시나리오 실증 및 2계층 안전 가드레일 |
| [**`DATABASE_DESIGN.md`**](file:///e:/monnlight/docs/DATABASE_DESIGN.md) | **DB 설계서** | • Cloud Firestore 컬렉션 구조 (`emergency_beds`, `emergency_summary`)<br/>• 문서 스키마, 인덱싱 전략 및 읽기/쓰기 쿼터 예산 관리(FinOps)<br/>• 심평원 요양기호(`ykiho`)와 E-Gen 기관코드(`hpid`) 엔티티 연계 |
| [**`DATA_CONSIDERATIONS.md`**](file:///e:/monnlight/docs/DATA_CONSIDERATIONS.md) | **데이터 기술 고찰** | • 공공데이터포털 NMC 및 HIRA API 데이터 품질 이상치 고찰<br/>• 위경도 좌표 결측치 보정 및 자정 넘김(`Overnight`) 진료시간 처리<br/>• KASI 특일 API와 요일별 시간표(`dutyTime1~8`) 매핑 원칙 |
| [**`EMERGENCY_DDK_COMPARISON_AND_IMPROVEMENT.md`**](file:///e:/monnlight/docs/EMERGENCY_DDK_COMPARISON_AND_IMPROVEMENT.md) | **경쟁 서비스 벤치마킹** | • 기존 대표 상용 서비스(똑닥 응급실 찾기 등) 한계점 분석<br/>• MoonlightCare의 3대 차별점: ① 0ms Red Flag 가드레일, ② 달빛병원-약국 30분 마진 페어링, ③ 비정형 공지 NLP 필터링 |
| [**`NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md`**](file:///e:/monnlight/docs/NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md) | **도메인 기획서** | • 야간 및 공휴일 소아 외래 진료 공백 현황 분석<br/>• 달빛어린이병원 지정 제도 및 공식 당번약국 운영 실태<br/>• 야간 처방전 조제 사각지대 해소를 위한 +30분 안전 마진 규칙 설계 |
| [**`BACKEND_AND_AGENT_IMPLEMENTATION_ROADMAP.md`**](file:///e:/monnlight/docs/BACKEND_AND_AGENT_IMPLEMENTATION_ROADMAP.md) | **엔지니어링 로드맵** | • 백엔드 모듈화부터 에이전트 결합, REST API 서빙까지의 기술 사양서<br/>• 레이턴시 목표, 캐싱 전략 및 에이전트 투입 타이밍 정의 |
| [**`VIBE_CODING_ROADMAP.md`**](file:///e:/monnlight/docs/VIBE_CODING_ROADMAP.md) | **개발 실행 가이드** | • AI 페어 프로그래밍을 위한 모듈별 개발 단계 및 프롬프트 가이드<br/>• 단계별 단위 테스트 수립 기준 및 리팩토링 체크리스트 |

---

## 🧭 프로젝트 전체 마스터 문서들과의 연계

MoonlightCare 프로젝트의 문서 체계는 다음과 같이 위계적으로 연계되어 관리됩니다:

* **[README.md](file:///e:/monnlight/README.md)**: 레포지토리 최상단 공식 소개, 빠른 시작(Quickstart), 뱃지 및 기술 스택.
* **[PLAN.md](file:///e:/monnlight/PLAN.md)**: 전체 6단계 개발 로드맵 진행 현황 및 누적 테스트 결과 공식 백서.
* **[CONNECTIVITY_MAP.md](file:///e:/monnlight/CONNECTIVITY_MAP.md)**: 모듈 및 에이전트 상호 연결 매트릭스 및 데이터 파이프라인 흐름도.
* **[Answer.md](file:///e:/monnlight/Answer.md)**: 개발 중 나눈 모든 질문과 심층 분석 가이드 누적 Q&A 아카이브 (Q1~Q27).
* **[docs/](file:///e:/monnlight/docs/)**: 개별 도메인 및 데이터베이스, 경쟁사 분석에 대한 심층 기획 원천 문서고.
