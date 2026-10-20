# 📚 기술 기획 및 아키텍처 문서 허브 (`docs`)

> **위치**: `docs/`  
> **역할**: MoonlightCare(아이숨) 프로젝트의 모든 마크다운 문서가 카테고리별로 체계적으로 관리되는 **공식 기술 문서고**입니다.

---

## 📁 폴더 구조 (Directory Structure)

```
docs/
├── architecture/          # 시스템 아키텍처 & DB 설계
│   ├── ADDRESS_AND_KEYWORD_LOCATION_ARCHITECTURE.md
│   ├── DATABASE_DESIGN.md
│   └── KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md
│
├── data-references/       # 데이터 고찰 & 참고 자료
│   ├── DATA_CONSIDERATIONS.md
│   └── 전국_달빛어린이병원_및_야간심야약국_현황.md
│
├── planning/              # 기획안 & 개발 로드맵
│   ├── BACKEND_AND_AGENT_IMPLEMENTATION_ROADMAP.md
│   ├── NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md
│   ├── PROJECT_PLAN.md
│   ├── PWA_PLAN.md
│   ├── VIBE_CODING_ROADMAP.md
│   └── 아이숨_프로젝트_기획안.md
│
├── project-core/          # 프로젝트 핵심 문서 (README, PLAN, 로그)
│   ├── log.md
│   ├── PLAN.md
│   ├── README.md
│   └── Reamme.md
│
├── qa-logs/               # Q&A 아카이브 & 질의응답 기록
│   ├── Answer-영식.md
│   └── q_a.md
│
├── reports/               # 분석 보고서 & 검증 리포트
│   ├── AISUM_STITCH_DESIGN_REPORT.md
│   ├── EMERGENCY_DDK_COMPARISON_AND_IMPROVEMENT.md
│   ├── KTAS_TRIAGE_VERIFICATION_REPORT.md
│   └── PROJECT_COMPLETION_REPORT.md
│
├── specs/                 # 기술 스펙 & 연동 사양서
│   ├── CONNECTIVITY_MAP.md
│   ├── FRONTEND_BACKEND_INTEGRATION_SPEC.md
│   ├── FRONTEND_UI_UX_SPECIFICATION.md
│   ├── PUBLIC_API_CIRCUIT_BREAKER_AND_FALLBACK_SPECIFICATION.md
│   └── REDFLAG_MODULE_V2_UPGRADE_SPECIFICATION.md
│
└── README.md              # 이 파일 (문서 허브 인덱스)
```

---

## 📑 카테고리별 문서 목록 (Document Index)

### 🏗️ `architecture/` — 시스템 아키텍처 & DB 설계

| 문서 | 핵심 내용 |
| :--- | :--- |
| [ADDRESS_AND_KEYWORD_LOCATION_ARCHITECTURE.md](file:///e:/isoom/docs/architecture/ADDRESS_AND_KEYWORD_LOCATION_ARCHITECTURE.md) | 주소 및 키워드 기반 위치 검색 아키텍처 |
| [DATABASE_DESIGN.md](file:///e:/isoom/docs/architecture/DATABASE_DESIGN.md) | Cloud Firestore 컬렉션 구조, 인덱싱 전략, FinOps |
| [KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md](file:///e:/isoom/docs/architecture/KTAS_PEDIATRIC_DIRECT_TRIAGE_ARCHITECTURE.md) | Gemini + KTAS 소아 Direct Triage 엔진 설계 |

### 📊 `data-references/` — 데이터 고찰 & 참고 자료

| 문서 | 핵심 내용 |
| :--- | :--- |
| [DATA_CONSIDERATIONS.md](file:///e:/isoom/docs/data-references/DATA_CONSIDERATIONS.md) | 공공데이터 품질 이상치 고찰, 위경도 보정, 진료시간 처리 |
| [전국_달빛어린이병원_및_야간심야약국_현황.md](file:///e:/isoom/docs/data-references/전국_달빛어린이병원_및_야간심야약국_현황.md) | 전국 달빛어린이병원 및 야간/심야 약국 데이터 현황 |

### 📋 `planning/` — 기획안 & 개발 로드맵

| 문서 | 핵심 내용 |
| :--- | :--- |
| [BACKEND_AND_AGENT_IMPLEMENTATION_ROADMAP.md](file:///e:/isoom/docs/planning/BACKEND_AND_AGENT_IMPLEMENTATION_ROADMAP.md) | 백엔드 모듈화 → 에이전트 결합 → API 서빙 로드맵 |
| [NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md](file:///e:/isoom/docs/planning/NIGHT_HOLIDAY_HOSPITAL_PHARMACY_PLAN.md) | 야간/공휴일 소아 진료 공백 분석 & 달빛병원-약국 페어링 |
| [PROJECT_PLAN.md](file:///e:/isoom/docs/planning/PROJECT_PLAN.md) | 종합 기획서 (PRD): 배경, 페르소나, 법적 검토, 로드맵 |
| [PWA_PLAN.md](file:///e:/isoom/docs/planning/PWA_PLAN.md) | PWA(Progressive Web App) 전환 계획 |
| [VIBE_CODING_ROADMAP.md](file:///e:/isoom/docs/planning/VIBE_CODING_ROADMAP.md) | AI 페어 프로그래밍 모듈별 개발 가이드 |
| [아이숨_프로젝트_기획안.md](file:///e:/isoom/docs/planning/아이숨_프로젝트_기획안.md) | 아이숨 프로젝트 종합 기획안 |

### 📌 `project-core/` — 프로젝트 핵심 문서

| 문서 | 핵심 내용 |
| :--- | :--- |
| [PLAN.md](file:///e:/isoom/docs/project-core/PLAN.md) | 6단계 개발 로드맵 진행 현황 & 누적 테스트 결과 백서 |
| [README.md](file:///e:/isoom/docs/project-core/README.md) | 레포지토리 공식 소개, Quickstart, 뱃지, 기술 스택 |
| [log.md](file:///e:/isoom/docs/project-core/log.md) | 트러블슈팅 & 엔지니어링 이슈 로그 |
| [Reamme.md](file:///e:/isoom/docs/project-core/Reamme.md) | 보조 README (초기 버전) |

### 💬 `qa-logs/` — Q&A 아카이브

| 문서 | 핵심 내용 |
| :--- | :--- |
| [Answer-영식.md](file:///e:/isoom/docs/qa-logs/Answer-영식.md) | 정영식 팀장 질의응답 누적 아카이브 |
| [q_a.md](file:///e:/isoom/docs/qa-logs/q_a.md) | 일반 질의응답 기록 |

### 📝 `reports/` — 분석 보고서 & 검증 리포트

| 문서 | 핵심 내용 |
| :--- | :--- |
| [AISUM_STITCH_DESIGN_REPORT.md](file:///e:/isoom/docs/reports/AISUM_STITCH_DESIGN_REPORT.md) | AISUM Stitch 디자인 리포트 |
| [EMERGENCY_DDK_COMPARISON_AND_IMPROVEMENT.md](file:///e:/isoom/docs/reports/EMERGENCY_DDK_COMPARISON_AND_IMPROVEMENT.md) | 경쟁 서비스(똑닥 등) 벤치마킹 & 차별화 분석 |
| [KTAS_TRIAGE_VERIFICATION_REPORT.md](file:///e:/isoom/docs/reports/KTAS_TRIAGE_VERIFICATION_REPORT.md) | KTAS Triage 검증 리포트 |
| [PROJECT_COMPLETION_REPORT.md](file:///e:/isoom/docs/reports/PROJECT_COMPLETION_REPORT.md) | 프로젝트 완료 보고서 |

### ⚙️ `specs/` — 기술 스펙 & 연동 사양서

| 문서 | 핵심 내용 |
| :--- | :--- |
| [CONNECTIVITY_MAP.md](file:///e:/isoom/docs/specs/CONNECTIVITY_MAP.md) | 모듈 & 에이전트 상호 연결 매트릭스, 데이터 파이프라인 |
| [FRONTEND_BACKEND_INTEGRATION_SPEC.md](file:///e:/isoom/docs/specs/FRONTEND_BACKEND_INTEGRATION_SPEC.md) | 프론트엔드-백엔드 연동 사양서 |
| [FRONTEND_UI_UX_SPECIFICATION.md](file:///e:/isoom/docs/specs/FRONTEND_UI_UX_SPECIFICATION.md) | 프론트엔드 UI/UX 설계 명세 |
| [PUBLIC_API_CIRCUIT_BREAKER_AND_FALLBACK_SPECIFICATION.md](file:///e:/isoom/docs/specs/PUBLIC_API_CIRCUIT_BREAKER_AND_FALLBACK_SPECIFICATION.md) | 공공 API 서킷 브레이커 & 3단계 Fallback 고가용성 설계 |
| [REDFLAG_MODULE_V2_UPGRADE_SPECIFICATION.md](file:///e:/isoom/docs/specs/REDFLAG_MODULE_V2_UPGRADE_SPECIFICATION.md) | Red Flag v2 모듈 고도화 설계서 |

---

## 🧭 루트 유지 문서 (Root Level)

아래 문서들은 프로젝트 루트(`E:\isoom\`)에 그대로 유지됩니다:

| 문서 | 역할 |
| :--- | :--- |
| `AGENTS.md` | AI 에이전트 거버넌스 규칙 (루트 필수) |
| `GEMINI.md` | AI 에이전트 설정 규칙 (루트 필수) |

---

## 🔗 하위 모듈 README (유지됨)

각 소스 폴더의 `README.md`는 해당 모듈의 가이드로서 원래 위치에 유지됩니다:

- `app/README.md`, `app/agents/README.md`, `app/api/README.md`, `app/orchestrator/README.md`, `app/schemas/README.md`, `app/services/README.md`
- `data/README.md`
- `frontend/README.md`, `frontend/assets/README.md`
- `notebooks/README.md`
- `tests/README.md`
- `references/medical_law/*.md` (법률 참고 문서)
- `tests/evals/eval_report.md`
