# -*- coding: utf-8 -*-
import os

q_text = """### Q227. [아이숨 중간프로젝트 발표 PPT 전면 고도화 & 15단계 엔지니어링 로드맵 및 백엔드 로직 시각화 수립] 15대 핵심 개발 로드맵 완벽 반영, 백엔드 오케스트레이션 고해상도 아키텍처 다이어그램 삽입, 토스 디자인 시스템(TDS) 기반 16:9 슬라이드 정렬 및 레이아웃 완결 보고

* **기록 일시**: 2026-10-20 19:15
* **질문 내용**:
  > 아이숨 프로젝트 기획안과 중간프로젝트 발표 PPT 내용을 고도화하고 싶어. 내가 개발했던 15단계 로드맵을 발표 내용으로 꼭 활용하고 싶고, 백엔드의 로직 구조도 시각화해서 볼 수 있었으면 좋겠어 이왕이면 그림으로 한번에 볼 수 있게 잘 만들어주고 PPT를 만들때 글자 정렬과 위치들이 일정하게 잘 정리 되어있었으면 좋겠어 진행해줘.

---

#### 💡 답변 및 고도화 엔지니어링 결과 보고

팀장님의 지시 사항에 따라, 기존 12장의 발표 자료를 **15단계 엔지니어링 로드맵, 백엔드 오케스트레이션 고해상도 시각화 다이어그램, 토스 디자인 시스템(TDS) 기반 정밀 그리드 정렬**이 완비된 총 13장의 **최고급 임원 보고/투자 유치용 슬라이드 덱([아이숨(ISOOM) 중간프로젝트 발표.pptx](file:///c:/AI-Native-Agent/isoom/아이숨(ISOOM)%20중간프로젝트%20발표.pptx))**으로 전면 재구축 및 승격 완료하였습니다.

기존 발표 자료는 안전하게 [`아이숨(ISOOM) 중간프로젝트 발표_backup.pptx`](file:///c:/AI-Native-Agent/isoom/아이숨(ISOOM)%20중간프로젝트%20발표_backup.pptx)로 백업 보관되었습니다.

---

#### 1. 📌 팀장님 15단계 개발 로드맵의 슬라이드별 완벽 매핑 내역

| 로드맵 단계 | 세부 엔지니어링 내용 | 발표 PPT 배치 슬라이드 |
| :--- | :--- | :--- |
| **Step 1** | **사회적 이슈**: 소아 응급실 뺑뺑이 현상 (전문의 부족 & 중증 골든타임 실종) | **Slide 3** (01. 개발 목적 및 사회적 배경) & **Slide 6** |
| **Step 2** | **데이터 분석**: 국립중앙의료원(NMC) E-Gen 실시간 병상 & 심평원 9.4만 건 통계 검증 | **Slide 4** (02. 데이터 분석 & 통계 실증) & **Slide 6** |
| **Step 3** | **원인 규명**: 야간 당직의 부재 + 20~24시 경증 환아 쏠림 집중 현상(74.0%) 실측 | **Slide 4** (02. 데이터 분석 & 통계 실증) & **Slide 6** |
| **Step 4** | **2-트랙 분리 고안**: 중증 환아는 응급실로, 경증 환아는 달빛병원/약국으로 분산 유도 | **Slide 5** (03. 해결 방향 & 핵심 솔루션) & **Slide 6** |
| **Step 5** | **목표 및 기능 검증**: 주피터 노트북 기반의 기능 프로토타이핑 및 데이터 가설 검증 | **Slide 6** (04. 로드맵 Part 1 - Step 5) |
| **Step 6** | **AI 거버넌스 뼈대**: 4대 핵심 불변 문서(Answer, Log, README, PLAN) 규칙 및 협업 체계 수립 | **Slide 6** (04. 로드맵 Part 1 - Step 6) |
| **Step 7** | **맞춤형 데이터셋 구축**: 전국 156개 달빛어린이병원, 2,028개 야간약국(+30분 마진), 168개 소아 KTAS 정제 | **Slide 6** (04. 로드맵 Part 1 - Step 7) |
| **Step 8** | **백엔드 모듈화**: 주피터 프로토타입을 `app/services`, `app/tools`의 파이썬 정규 서비스 모듈로 이식 | **Slide 6** (04. 로드맵 Part 1 - Step 8) |
| **Step 9** | **백엔드 AI 결합**: Gemini 3.8 Flash 기반 Direct Grounding 및 2-Tier 안전 가드레일 접목 | **Slide 7** (05. 로드맵 Part 2 - Step 9) |
| **Step 10** | **에이전트 오케스트레이션**: Supervisor 6-State FSM 기반 3대 특화 에이전트(Triage, Matching, Logistics) 제어 | **Slide 7** (05. 로드맵 Part 2 - Step 10) & **Slide 8** |
| **Step 11** | **무중단 인프라 구축**: 서킷 브레이커 & 3-Tier Multi-Storage Fallback(Memory -> Firestore -> Canonical JSON) | **Slide 7** (05. 로드맵 Part 2 - Step 11) & **Slide 10** |
| **Step 12** | **프론트엔드 혁신(피봇)**: Stitch MCP 폐기(뷰포트 깨짐 및 CDN 종속) -> Toss TDS/모니모 모바일 퍼스트 순수 PWA 구축 | **Slide 7** (05. 로드맵 Part 2 - Step 12) & **Slide 10** |
| **Step 13** | **화면단 E2E 풀스택 연결**: FastAPI 비동기 백엔드와 6대 반응형 클라이언트 스크린 실시간 결합 | **Slide 7** (05. 로드맵 Part 2 - Step 13) & **Slide 9** |
| **Step 14** | **AI EVALS 골든 시나리오 검증**: 50대 골든 케이스 실측, 128개 Pytest All-Green, 언더트리아제 0% 임상 안전성 입증 | **Slide 7** (05. 로드맵 Part 2 - Step 14) & **Slide 11** |
| **Step 15** | **Cloud Run 프로덕션 배포**: Docker 컨테이너화, GCP Secret Manager 보안 키 주입, gcloud CLI 무중단 배포 | **Slide 7** (05. 로드맵 Part 2 - Step 15) & **Slide 11** |

---

#### 2. 🖼️ 백엔드 시스템 로직 구조 원샷(One-Shot) 시각화 다이어그램 ([Slide 8](file:///c:/AI-Native-Agent/isoom/images/backend_logic_architecture.png))
* **시각화 에셋**: `images/backend_logic_architecture.png` (300 DPI 초고해상도 다이어그램 생성 및 PPT 중앙 전면 배치)
* **표현된 아키텍처 흐름**:
  1. **[Client Layer]**: PWA 6대 화면 (문진 입력 -> 실시간 분류 -> 대시보드 -> 야간약국)
  2. **[Pass 1 Pre-Interceptor (0ms)]**: 26µs 정규식 기반 초응급(심정지, 청색증 등) 즉각 119 트리거 + 한국어 복합 부정어 오분류 방지
  3. **[Supervisor Multi-Agent FSM]**:
     - `TriageAgent`: Gemini 3.8 Flash 기반 KTAS 1~5단계 직접 그라운딩
     - `MatchingAgent`: 5µs Haversine 기반 전국 156개 달빛병원 실시간 거리·진료시간 매칭
     - `LogisticsAgent`: 병원 반경 3km 내 2,028개 야간약국 연계 및 복약 지도 생성
  4. **[Pass 2 Medical Guardrail]**: 소아 약물 용량 및 환각(Hallucination) 필터링
  5. **[3-Tier Multi-Storage Fallback]**: L1 Memory -> L2 Firestore Hash Diffing (-93.9% 비용 절감) -> L3 Canonical JSON (오프라인 100% 무중단)
  6. **[2-Track Output]**: Track A(중증 응급실 병상 사수) vs Track B(경증 달빛병원 + 안심약국 분산)

---

#### 3. 📐 글자 정렬 및 위치 표준화 (Pixel-Perfect Alignment & Typography)
* **표준 16:9 와이드스크린 규격**: 33.87cm x 19.05cm 일괄 적용
* **균일 마진 및 그리드 시스템**: 좌측 여백 1.69cm(0.67in), 상단 헤더 1.0~2.8cm, 본문 콘텐츠 4.2~16.0cm 엄격 정렬
* **카드 레이아웃 정합성**:
  - 4열 그리드: 폭 7.2cm, 간격 0.6cm
  - 3열 그리드: 폭 9.8cm, 간격 0.6cm
  - 카드 내부 여백: 상하좌우 0.6~0.9cm 패딩 확보로 텍스트 잘림 및 경계 침범 원천 차단
* **일관된 폰트 위계 체계**:
  - 슬라이드 카테고리 태그: 11pt 볼드 (Teal Accent)
  - 메인 헤드라인: 22pt 볼드 (Dark Navy / White)
  - 부제목: 10pt (Slate Neutral)
  - 카드 헤더: 12~14pt 볼드
  - 본문 세부 설명: 9~10pt 균일 자간 및 줄간격

---

#### 4. 🚀 결론 및 성과
발표자가 청중 및 심사위원 앞에서 **"단순 아이디어성 챗봇이 아닌, 실측 공공데이터 분석부터 FSM 멀티 에이전트, 3-Tier 인프라 방어선, 실서버 클라우드 런 배포까지 E2E로 완성된 엔지니어링 프로젝트"**임을 압도적인 시각 자료와 정갈한 타이포그래피로 명확하게 전달할 수 있도록 완성되었습니다.
"""

# 1. Update Answer-영식.md
ans_path = 'docs/qa-logs/Answer-영식.md'
if os.path.exists(ans_path):
    with open(ans_path, 'r', encoding='utf-8') as f:
        orig = f.read()
    toc_item = '235. [Q227. [아이숨 중간프로젝트 발표 PPT 전면 고도화 & 15단계 엔지니어링 로드맵 및 백엔드 로직 시각화 수립] 15대 핵심 개발 로드맵 완벽 반영, 백엔드 오케스트레이션 고해상도 아키텍처 다이어그램 삽입, 토스 디자인 시스템(TDS) 기반 16:9 슬라이드 정렬 및 레이아웃 완결 보고](#q227-아이숨-중간프로젝트-발표-ppt-전면-고도화--15단계-엔지니어링-로드맵-및-백엔드-로직-시각화-수립-15대-핵심-개발-로드맵-완벽-반영-백엔드-오케스트레이션-고해상도-아키텍처-다이어그램-삽입-토스-디자인-시스템tds-기반-169-슬라이드-정렬-및-레이아웃-완결-보고)'
    lines = orig.split('\n')
    new_lines = []
    inserted_toc = False
    for line in lines:
        new_lines.append(line)
        if 'Q226.' in line and not inserted_toc and '](#' in line:
            new_lines.append(toc_item)
            inserted_toc = True
    content_with_toc = '\n'.join(new_lines)
    final_content = content_with_toc.rstrip() + '\n\n---\n\n' + q_text + '\n'
    with open(ans_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print("Answer-영식.md updated with Q227")

# 2. Update q_a.md
qa_path = 'docs/qa-logs/q_a.md'
if os.path.exists(qa_path):
    with open(qa_path, 'r', encoding='utf-8') as f:
        qa_orig = f.read()
    q149_text = q_text.replace('### Q227.', '### Q149.').replace('q227-', 'q149-')
    qa_final = qa_orig.rstrip() + '\n\n---\n\n' + q149_text + '\n'
    with open(qa_path, 'w', encoding='utf-8') as f:
        f.write(qa_final)
    print("q_a.md updated with Q149")
