# i-Soom (아이숨) 기술 고도화 및 최신 논문·AI 아키텍처 적용 기획안

> **목적**: `MiniProject`(Naver Webtoon AI)에서 검증된 **LangGraph 멀티 에이전트 · 앙상블 RAG · 시맨틱 캐시 · 정량 평가(Golden/Stress/RAGAS) · LLMOps 관제** 수준으로 `isoom`(소아 야간 응급·달빛어린이병원 AI 트리아제)을 기술적으로 도약시키기 위한 설계 및 단계별 실행 기획안입니다.  
> **작성 기준일**: 2026-11-16

---

## 1. 현재 `isoom` vs 목표 아키텍처 (`MiniProject` 벤치마크) 갭 분석

| 기술 영역 | 현재 `isoom` 구현 | 한계점 | 목표 고도화 방향 (논문·최신 기법) |
| :--- | :--- | :--- | :--- |
| **임상 지침 참조 (KTAS)** | `triage_agent.py`에서 168개 증상(~8,500 토큰)을 매 호출 프롬프트에 통째로 삽입 | 토큰 낭비·응답 지연, `Lost in the Middle` 현상, 근거 조항 미검증 | **Hybrid RAG (Dense + BM25 + RRF)** + **Cross-Encoder Reranking** + **CRAG / Self-RAG 근거 검증** |
| **에이전트 오케스트레이션** | `SupervisorOrchestrator`의 절차적 `if/else` 파이프라인 | 조건 분기·재시도·자기교정 루프 확장 어려움, 상태 추적 빈약 | **LangGraph `StateGraph`** 기반 상태 머신 + **Self-Correction 순환 루프** + **Early-Exit** |
| **트리아제 불확실성 제어** | LLM 단일 출력(`ktas_level`) 의존 및 정규식 폴백 | 경계 사례(KTAS 2 vs 3)에서 과소분류(Under-triage) 위험 정량화 부재 | **Conformal Prediction / Selective Prediction** 기반 보수적 상위 등급 에스컬레이션 |
| **의료 안전 가드레일** | 정규식·키워드 기반 1차 차단 (`guardrail_agent.py`) | 우회 표현·은유적 진단명/투약량 권고에 취약 | **2단계 Semantic Safety Classifier (NLI / ShieldGemma)** + **출력 Factuality Verifier** |
| **병원·약국 매칭 랭킹** | Haversine 직선거리 + 30분 마진 + 병상 단순 정렬 | 응급실 과밀도, 야간 대기시간, 실제 사용자 선택 피드백 미반영 | **Multi-Objective Pareto 랭킹** + **Contextual Bandit (Thompson Sampling)** 보정 |
| **성능·캐시·LLMOps** | 모듈별 개별 `genai_client` 호출, 비용/지연 계측 미흡 | 중복 질의 비용 발생, 모델 장애/품질 저하 실시간 관제 부재 | **중앙 `LLMGateway` + 2계층 시맨틱 캐시** + **Prometheus `/metrics` + Admin LLMOps 콘솔** |
| **품질·안전 정량 평가** | 단위/통합 테스트 위주 (134개 테스트) | 임상 안전성(Under-triage 0%), RAG 근거성 수치화 부재 | **Golden-100 Pediatric Eval** + **RAGAS** + **Red-Teaming Stress-200** |

---

## 2. 핵심 적용 논문 기법 및 최신 AI 기술 (5대 기술 축)

### 축 1. KTAS 임상 근거 기반 Hybrid RAG + CRAG / Self-RAG
> **관련 연구**: *Hybrid Retrieval with Reciprocal Rank Fusion (Cormack et al., 2009)* · *Corrective Retrieval Augmented Generation (CRAG, Yan et al., 2024)* · *Self-RAG (Asai et al., ICLR 2024)* · *Lost in the Middle (Liu et al., TACL 2024)*

- **문제 해결**: 현재 `_get_ktas_grounding_context()`가 168개 KTAS 증상 전체(~8,500 토큰)를 매번 프롬프트에 주입하여 지연시간·비용 증가 및 장문 컨텍스트 중간 정보 누락 발생.
- **적용 설계**:
  1. **Dual Index 구축 (`app/services/ktas_retriever.py`)**:
     - **Dense Index**: Vertex AI `text-embedding-005` 기반 FAISS 인덱스 (증상 표현의 의미적 유사도: *"숨이 가쁘고 갈비뼈가 쑥 들어가요"* ↔ `소아 호흡곤란 / 흉부함몰`)
     - **Sparse Index**: 한국어 형태소/N-gram 기반 BM25 (정확한 의학 용어·NACRS 코드·체온·월령 숫자 매칭)
     - **RRF (Reciprocal Rank Fusion, $k=60$)**: Dense + Sparse 상위 후보를 융합한 뒤 경량 Reranker로 **Top-5 KTAS 증상 조항만** 선별 주입 (프롬프트 토큰 **~85% 절감** 기대)
  2. **CRAG 기반 근거 평가 및 자기교정**:
     - 추출된 증상과 검색된 NACRS 조항의 관련도 점수가 임계치 미만이면 **Query Rewriting** 후 1회 재검색 수행.
  3. **Self-RAG 사후 사실성 검증 (`verify_clinical_grounding`)**:
     - LLM이 산출한 `ktas_level`과 `matched_nacrs_code`가 실제 KTAS 데이터셋의 공식 기준(`secondary_considerations`)과 일치하는지 결정론적으로 교차 검증.

---

### 축 2. LangGraph `StateGraph` 오케스트레이션 + Conformal Triage
> **관련 연구**: *Conformal Prediction for Reliable Uncertainty Quantification (Angelopoulos & Bates, 2023)* · *Active Information Acquisition in Clinical Triage*

- **적용 설계**:
  1. **선언적 LangGraph 에이전트 그래프 (`app/orchestrator/graph.py`)**:
     - `GuardrailNode` → (위험/금칙 시 Early-Exit) → `SemanticCacheNode` → (비응급 FAQ 히트 시 즉시 응답) → `KtasRetrieverNode` → `TriageReasoningNode` → `UncertaintyCheckNode` → `LogisticsNode` → `MatchingNode` → `ResponseVerifierNode`
     - 모든 노드가 `PatientSessionState`를 공유하며 SSE 스트리밍으로 단계별 진행 상태(`event: step`)를 실시간 전송.
  2. **Conformal / Selective Uncertainty Escalation (과소분류 방지)**:
     - LLM 출력의 모호성(증상 누락, 경계 체온 38.0℃ 전후, 월령 경계 90~100일)에 대해 불확실성 점수(Entropy / Confidence Margin)를 계산.
     - 예측 집합(Prediction Set)에 `{KTAS 2, KTAS 3}`이 동시에 포함되면 **보수적 안전 원칙(Conservative Safety Principle)**에 따라 상위 위험 등급(KTAS 2)으로 승격하거나, 정보 이득(Information Gain)이 가장 큰 **감별 질문 1개**를 즉시 생성.

---

### 축 3. 2단계 시맨틱 의료 안전 가드레일 (NLI + Output Verifier)
> **관련 연구**: *Constitutional AI (Bai et al., 2022)* · *DeBERTa-v3 NLI Zero-shot Safety Classification* · *LLM-as-a-Judge Output Guardrails (Inan et al., Llama Guard)*

- **문제 해결**: 정규식 기반 `guardrail_agent.py`는 *"타이레놀 몇 밀리 먹이면 되나요?"* 의 변형 표현(*"해열제 반 알 쪼개 먹여도 괜찮을까요?"*)이나 간접 진단 유도를 놓칠 수 있음.
- **적용 설계**:
  1. **Pre-Guard (입력 의미 분류)**: 응급 119 즉시 우회(0ms 하드 룰 유지) + 의료법 위반 유도/프롬프트 인젝션 의미적 분류.
  2. **Post-Guard (출력 Constitutional Verifier)**:
     - 생성된 `empathy_message`, `clinical_rationale`, `recommended_action`에 **확정 진단명 단정**, **구체적 용량/처방 지시**, **근거 없는 안심 유도**가 포함되었는지 경량 검증 패스로 필터링·자동 교정(`sanitize_medical_response`).

---

### 축 4. Multi-Objective 공간 매칭 + Contextual Bandit (안전 제약 준수)
> **관련 연구**: *Thompson Sampling for Contextual Bandits (Agrawal & Goyal, ICML 2013)* · *Maximal Marginal Relevance / DPP Diversity (Carbonell & Goldstein, 1998)*

- **적용 설계**:
  1. **다목적 파레토 스코어링 (`app/services/ranking_service.py`)**:
     - 단순 직선거리 대신 **가중 복합 점수** 산출:
       $$\text{Score}(h) = w_1 \cdot \text{ClinicalFit} + w_2 \cdot \text{ETA\_Score} + w_3 \cdot \text{BedAvailability} + w_4 \cdot \text{PharmacyMargin30m}$$
     - 지역 내 동일 유형 시설 쏠림 방지를 위한 **MMR 다양성 보정**(달빛어린이병원 + 소아응급실 + 연계 심야약국 균형 노출).
  2. **Safety-Constrained Thompson Sampling**:
     - **KTAS 1~2단계(소생/긴급)에서는 탐색(Exploration)을 완전 비활성화**하여 최단·최적 응급실만 노출.
     - **KTAS 3~5단계**에서 사용자의 실제 `전화 연결 클릭`·`길찾기 실행`·`방문 완료 피드백`을 보상 신호(Reward)로 수집해 동등 조건 병원 간 추천 가중치를 점진 최적화.

---

### 축 5. 중앙 `LLMGateway`, 안전 인식 시맨틱 캐시, 정량 평가 & LLMOps
> **참고 레퍼런스**: `MiniProject`의 `py/llm_gateway.py`, `agent/semantic_cache.py`, `agent/evaluator.py`, `py/telemetry.py`

- **적용 설계**:
  1. **중앙 `LLMGateway` (`app/services/llm_gateway.py`)**:
     - Vertex AI ADC 호출 일원화, 모델별 토큰/USD 비용 산출, `429/503/RefreshError` 서킷 브레이커 및 자동 모델 폴백(`gemini-2.5-flash` → `gemini-2.5-flash-lite` → 결정론적 룰 폴백).
  2. **Safety-Aware 2계층 시맨틱 캐시**:
     - 일반 소아 가정 케어·약국 운영 문의 등 정적/준정적 질의만 코사인 유사도($\ge 0.94$)로 캐싱.
     - **Red Flag 의심 질의 및 실시간 병상/대기 조회는 캐시 바이패스(Cache Bypass)** 강제.
  3. **정량 평가 벤치마크 구축 (`tests/eval/`)**:
     - **Golden-100 Pediatric Triage**: 소아 응급 100개 시나리오(영아 고열, 크룹, 장중첩증, 아나필락시스 등)에 대해 **Under-triage Rate 0.0%**, **NACRS Top-1/3 정확도**, **환각률 0%** 측정.
     - **RAGAS / Faithfulness 파이프라인**: 검색된 KTAS 조항 대비 응답 충실도 자동 채점.
     - **Red-Teaming Stress-200**: 진단 유도·용량 질문·비정형 오타/구어체·프롬프트 인젝션 방어율 측정.
  4. **LLMOps 관제 (`/metrics` + Admin Dashboard)**:
     - 단계별 지연(Latency Breakdown: Guardrail / Retriever / LLM / Logistics), 일별 토큰·비용, Under-triage 경보 이력 모니터링.

---

## 3. 단계별 구현 로드맵 (권장 우선순위)

| 단계 | 마일스톤 | 핵심 산출물 | 예상 효과 |
| :--- | :--- | :--- | :--- |
| **Phase 1 (기반)** | **중앙 `LLMGateway` + KTAS Hybrid RAG** | `llm_gateway.py`, `ktas_retriever.py` (FAISS + BM25 + RRF) | 프롬프트 토큰 ~85% 절감, 모델 폴백·비용 계측 확보 |
| **Phase 2 (안전·추론)** | **LangGraph 오케스트레이터 + Conformal Escalation + NLI 가드레일** | `orchestrator/graph.py`, `verify_clinical_grounding`, Post-Guard | 과소분류(Under-triage) 차단, 의료법 방어 고도화 |
| **Phase 3 (매칭·최적화)** | **다목적 파레토 랭킹 + Safety-Aware 시맨틱 캐시** | `ranking_service.py`, `semantic_cache.py` | 실시간 병상·약국 마진 정교화, FAQ 지연 단축 |
| **Phase 4 (검증·관제)** | **Golden-100 / Stress-200 평가 + Prometheus `/metrics` & Admin UI** | `tests/eval/`, `/metrics`, `admin.html` | `MiniProject` 수준의 정량 벤치마크 스코어 및 LLMOps 확보 |

---

## 4. `isoom`만의 차별화 포인트 (의료 도메인 특성 반영)

- **0ms Hard Guardrail 불변 원칙**: 생후 100일 미만 발열, 경련, 청색증 등 KTAS 1단계 즉시 위험 신호는 LLM·RAG·캐시를 거치지 않고 **0ms 결정론적 119 에스컬레이션**을 최우선 보장합니다.
- **Zero-Hallucination Clinical Grounding**: 모든 의료기관·약국·병상 정보는 공공데이터/실시간 동기화 DB에 100% 근거하며, LLM이 임의로 병원명·전화번호·운영시간을 생성하지 못하도록 출력 검증 레이어를 강제합니다.
