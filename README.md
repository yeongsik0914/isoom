# MoonlightCare (달빛케어)

> **HIRA 오픈 API 및 공공데이터 기반 야간·휴일 소아청소년과 매칭 하네스 멀티 에이전트 시스템**

## 📚 프로젝트 문서
* **[종합 기획안 (PROJECT_PLAN.md)](file:///e:/monnlight/docs/PROJECT_PLAN.md)**: 시스템 아키텍처, 의료법 컴플라이언스 가드레일, 멀티 에이전트 역할 분담(R&R), 전처리 및 노트북 설계안, 개발 로드맵
* **[공공의료 데이터 분석 주의사항 및 결함 보고서 (DATA_CONSIDERATIONS.md)](file:///e:/monnlight/docs/DATA_CONSIDERATIONS.md)**: HIRA/E-Gen API의 시간 괴리, 조기 접수마감, 소아 표방 vs 전문의 괴리, 실시간 병상 비정형 텍스트 파싱 등 실무 주의사항 요약

## ⚖️ 의료법 컴플라이언스 지식 베이스 (`references/medical_law/`)
* **[의료법 핵심 조항 해설 (01_medical_service_act.md)](file:///e:/monnlight/references/medical_law/01_medical_service_act.md)**: 제27조 무면허의료행위/알선금지 및 제56조 의료광고 기준
* **[복지부 비의료 가이드라인 (02_mohw_guidelines.md)](file:///e:/monnlight/references/medical_law/02_mohw_guidelines.md)**: 비의료 건강관리 허용 범위 및 진단/처방 금지 가이드
* **[대법원 판례 기준 (03_court_precedents.md)](file:///e:/monnlight/references/medical_law/03_court_precedents.md)**: 의료행위 정의 및 유인·알선죄 판례 요약
* **[금칙어 및 대체표현 사전 (04_forbidden_lexicon.json)](file:///e:/monnlight/references/medical_law/04_forbidden_lexicon.json)**: 메모리 적재용 0ms 정규식 금칙어 사전
* **[표준 법적 면책고지 템플릿 (05_legal_disclaimers.md)](file:///e:/monnlight/references/medical_law/05_legal_disclaimers.md)**: 세션별/카드별 필수 고지문

## 🧪 AI 평가(Evals) 및 골든 테스트 데이터셋 (`tests/evals/`)
* **[골든 테스트 케이스 40선 (golden_test_cases.json)](file:///e:/monnlight/tests/evals/golden_test_cases.json)**: 5대 루브릭 차원(DIM-1~5)별 골든 데이터셋 및 치명적 탈락(Critical Fail) 판정 기준
