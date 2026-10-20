# -*- coding: utf-8 -*-
import os

# 1. Update docs/project-core/log.md
log_path = 'docs/project-core/log.md'
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()

    toc_row = '| **[ISSUE-221]** | 프레젠테이션 & 시스템 시각화 | 중간프로젝트 발표 PPT 15단계 개발 로드맵 미반영 및 백엔드 로직 시각화 부재, 슬라이드 텍스트 정렬 결함 고도화 | **해결 완료 (Resolved)** | 2026-10-20 |'
    
    # insert before end of table
    if 'ISSUE-220' in log_content:
        lines = log_content.split('\n')
        new_lines = []
        inserted_toc = False
        for line in lines:
            new_lines.append(line)
            if 'ISSUE-220' in line and '|' in line and not inserted_toc:
                new_lines.append(toc_row)
                inserted_toc = True
        log_content = '\n'.join(new_lines)

    issue_detail = """

---

### [ISSUE-221] 중간프로젝트 발표 PPT 전면 고도화 & 15단계 E2E 엔지니어링 로드맵 및 백엔드 로직 시각화 수립

* **발생 일자**: 2026-10-20
* **작업자**: 김동준 (팀원), 정영식 (팀장)
* **분류**: 프레젠테이션 고도화 & 시스템 아키텍처 시각화 및 그리드 레이아웃 표준화
* **문제 상황**:
  * 기존 `아이숨(ISOOM) 중간프로젝트 발표.pptx`가 12슬라이드 구성에 머물러 있어, 실제 프로젝트 폴더에서 개발된 핵심 과정(15단계 E2E 엔지니어링 로드맵, 소아 KTAS 데이터셋 구축, 주피터 모듈화, 3-Tier Multi-Storage Fallback, Stitch 폐기 및 Toss TDS PWA 피봇, AI EVALS 50대 골든 테스트, Cloud Run 배포)이 상당수 누락되어 있었음.
  * 백엔드 시스템의 내부 오케스트레이션 로직(Pass 1 Pre-Interceptor -> Supervisor 6-State FSM -> Pass 2 Guardrail -> 3-Tier Fallback)을 직관적으로 조망할 수 있는 시각화 다이어그램이 부재함.
  * 슬라이드 간 카드 좌표, 마진, 폰트 크기 및 텍스트 박스 줄바꿈이 불균일하여 시각적 완성도 저해.
* **원인 분석**:
  1. **초기 기획과 실제 구현 간 간극**: 초기 발표 자료 작성 이후 무중단 인프라, 서킷 브레이커, 프론트엔드 피봇 등 수많은 엔지니어링 고도화가 진행되었으나 PPT에 동기화되지 않음.
  2. **아키텍처 시각화 부재**: 복잡한 비동기 멀티 에이전트 및 데이터 폴백 파이프라인을 텍스트로만 설명하기에 한계가 있음.
* **해결 및 조치 내용**:
  1. **원본 PPT 백업**: 기존 발표 자료를 `아이숨(ISOOM) 중간프로젝트 발표_backup.pptx`로 안전하게 백업.
  2. **15단계 엔지니어링 로드맵 전면 반영**:
     - Slide 6 (Part 1, Steps 1~8): 사회적 이슈 발견 -> 공공데이터 분석 -> 원인 규명 -> 2-트랙 분리 -> 목표/검증 -> 거버넌스 수립 -> 데이터셋 구축 -> 백엔드 모듈화.
     - Slide 7 (Part 2, Steps 9~15): AI 결합 -> FSM 오케스트레이션 -> 무중단 인프라 -> 프론트 피봇 -> 화면단 E2E 연동 -> AI EVALS 검증 -> Cloud Run 배포.
  3. **300 DPI 초고해상도 백엔드 시스템 로직 다이어그램 제작 및 Slide 8 중앙 전면 배치**:
     - `images/backend_logic_architecture.png`를 렌더링하여 클라이언트 -> 세이프티 가드레일 -> 6-State FSM 멀티 에이전트 -> 3-Tier 스토리지 폴백 -> 2-트랙 라우팅의 전 과정을 한눈에 조망하도록 시각화.
  4. **16:9 와이드스크린(33.87cm x 19.05cm) 정밀 그리드 정렬**:
     - 카드 마진(좌측 1.69cm, 간격 0.6cm), 폰트 위계(22pt 헤더, 12~14pt 카드 타이틀, 9.5~10pt 본문), 내부 패딩(0.6~0.9cm)을 일괄 적용하여 텍스트 오버플로 0건 달성.
* **적용 파일**:
  * `아이숨(ISOOM) 중간프로젝트 발표.pptx` (총 13장 전면 개편)
  * `images/backend_logic_architecture.png` (300 DPI 시스템 로직 아키텍처 다이어그램)
  * `아이숨(ISOOM) 중간프로젝트 발표_backup.pptx` (원본 백업)
"""
    log_content = log_content.rstrip() + issue_detail + '\n'
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(log_content)
    print("log.md updated with ISSUE-221")

# 2. Update docs/project-core/README.md
readme_path = 'docs/project-core/README.md'
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    new_release = """### 🌟 [v2.9.32-presentation-deck-elevation] 2026-10-20: 아이숨 중간프로젝트 발표 PPT 전면 고도화 & 15단계 로드맵 및 백엔드 로직 시각화 다이어그램 수립 (정영식 팀장, 김동준 팀원)
* **📊 중간프로젝트 발표 슬라이드 덱([아이숨(ISOOM) 중간프로젝트 발표.pptx](file:///c:/AI-Native-Agent/isoom/아이숨(ISOOM)%20중간프로젝트%20발표.pptx)) 전면 승격**:
  - 기존 12장 자료를 16:9 표준 와이드스크린(33.87cm x 19.05cm), 토스 디자인 시스템(TDS) 테마 기반의 총 13장 프리미엄 발표 자료로 고도화.
  - 팀장님 지시 15대 E2E 개발 로드맵(사회적 문제 발견 -> 공공데이터 분석 -> 원인 규명 -> 2-트랙 고안 -> 백엔드 모듈화 -> AI 결합 -> FSM 오케스트레이션 -> 무중단 3-Tier 인프라 -> Toss TDS 프론트 피봇 -> AI EVALS 50대 골든 테스트 -> Cloud Run 배포) 전면 수록.
* **🖼️ 백엔드 시스템 로직 초고해상도 시각화 다이어그램([images/backend_logic_architecture.png](file:///c:/AI-Native-Agent/isoom/images/backend_logic_architecture.png)) 신규 구축**:
  - 클라이언트 레이어부터 0ms 사전 인터셉터, 6-State FSM Supervisor, 3-Tier Multi-Storage Fallback, 2-트랙 라우팅의 전 과정을 원샷(One-Shot)으로 조망할 수 있는 300 DPI 다이어그램을 신규 제작하여 Slide 8에 배치.
* **📐 픽셀 퍼펙트 타이포그래피 & 그리드 정렬**:
  - 카드 마진, 폰트 위계(22pt 헤더, 12~14pt 카드 타이틀, 9.5~10pt 본문), 내부 패딩을 정밀하게 수학적으로 정렬하여 텍스트 잘림 및 경계 침범 완전 차단.

"""
    idx = readme_content.find('### 🌟 [v2.9.31')
    if idx != -1:
        readme_content = readme_content[:idx] + new_release + readme_content[idx:]
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("docs/project-core/README.md updated with v2.9.32")

# 3. Update docs/project-core/PLAN.md
plan_path = 'docs/project-core/PLAN.md'
if os.path.exists(plan_path):
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan_content = f.read()

    backlog_item = """
14. **[완료] 중간프로젝트 발표 PPT 15단계 엔지니어링 로드맵 반영 & 백엔드 시스템 로직 초고해상도 시각화(Phase 13)**:
    - `아이숨(ISOOM) 중간프로젝트 발표.pptx` 전면 승격(13슬라이드 16:9 와이드스크린, 토스 TDS 다크테마).
    - 팀장님 개발 로드맵 15단계(문제 발견 -> 데이터셋 -> 백엔드 모듈화 -> AI 결합 -> 오케스트레이션 -> 무중단 인프라 -> 프론트 피봇 -> EVALS -> Cloud Run) 완벽 수록.
    - 300 DPI 초고해상도 시스템 아키텍처 다이어그램(`images/backend_logic_architecture.png`) 생성 및 Slide 8 전면 배치.
    - 카드 그리드 여백 및 텍스트 박스 줄바꿈 정렬 완료, 오버플로 0건 달성."""
    
    idx = plan_content.rfind('## 11. 추가 심화 고도화 백로그')
    if idx != -1:
        plan_content = plan_content.rstrip() + backlog_item + '\n'
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        print("docs/project-core/PLAN.md updated with Phase 13")
