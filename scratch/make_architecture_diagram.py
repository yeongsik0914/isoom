import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. Font setup - use clean Korean font
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 2. Figure setup (16:9 Widescreen, 300 DPI)
fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
ax.set_xlim(0, 1600)
ax.set_ylim(0, 900)
ax.axis('off')

# Background
fig.patch.set_facecolor('#0B0F19') # Sleek Dark Obsidian Slate
ax.set_facecolor('#0B0F19')

# Helper for drawing rounded boxes with drop shadow
def draw_card(ax, x, y, w, h, bg_color, border_color=None, border_width=1.5, radius=12, alpha=1.0):
    # Shadow
    shadow = patches.FancyBboxPatch(
        (x + 3, y - 3), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor='#020408', edgecolor='none', alpha=0.45, zorder=2
    )
    ax.add_patch(shadow)
    # Box
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=bg_color, edgecolor=border_color if border_color else 'none',
        linewidth=border_width, alpha=alpha, zorder=3
    )
    ax.add_patch(box)
    return box

# Helper for arrow
def draw_arrow(ax, x1, y1, x2, y2, color='#64748B', lw=2, style='->', rad=0.0):
    ax.annotate(
        '', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}", shrinkA=3, shrinkB=3
        ),
        zorder=4
    )

# --- HEADER TITLE ---
ax.text(800, 855, "아이숨 (i-Soom) 백엔드 시스템 로직 & 지능형 오케스트레이션 아키텍처",
        fontsize=20, weight='bold', color='#FFFFFF', ha='center', va='center', zorder=5)
ax.text(800, 822, "0ms 세이프티 가드레일 · 6-State FSM 멀티 에이전트 · 3-Tier 고가용성 무중단 데이터 인프라",
        fontsize=11.5, color='#94A3B8', ha='center', va='center', zorder=5)

# ==============================================================================
# 1. CLIENT LAYER (Left)
# ==============================================================================
draw_card(ax, 40, 480, 250, 290, '#1E293B', '#334155', radius=14)
ax.text(165, 740, "사용자 단말 계층 (Client)", fontsize=13, weight='bold', color='#38BDF8', ha='center', zorder=5)
ax.text(165, 718, "PWA Mobile Web & Fixed App Shell", fontsize=8.5, color='#94A3B8', ha='center', zorder=5)

# Sub boxes inside Client
draw_card(ax, 55, 615, 220, 80, '#0F172A', '#38BDF8', radius=8)
ax.text(165, 665, "스마트 원스톱 문진 (input.html)", fontsize=10, weight='bold', color='#FFFFFF', ha='center', zorder=5)
ax.text(165, 638, "• 5대 연령 · 다이얼 체온 · STT 음성\n• 비증상 잡담 사전 필터링 탑재", fontsize=8.5, color='#94A3B8', ha='center', zorder=5)

draw_card(ax, 55, 500, 220, 100, '#0F172A', '#10B981', radius=8)
ax.text(165, 570, "PWA 서비스워커 & 토스 TDS", fontsize=10, weight='bold', color='#FFFFFF', ha='center', zorder=5)
ax.text(165, 532, "• Service Worker v4 (정적 캐시 제어)\n• 초경량 0.1s 순수 Vanilla HTML5/CSS3\n• 야간 부모 시각보호 다크 테마 이식", fontsize=8.5, color='#94A3B8', ha='center', zorder=5)

# ==============================================================================
# 2. PASS 1 GUARDRAIL (Middle Left)
# ==============================================================================
draw_card(ax, 325, 480, 275, 290, '#1E293B', '#334155', radius=14)
ax.text(462, 740, "Pass 1 : 0ms 안전 감시망", fontsize=13, weight='bold', color='#F43F5E', ha='center', zorder=5)
ax.text(462, 718, "Zero-Latency Pre-Interceptor", fontsize=8.5, color='#FDA4AF', ha='center', zorder=5)

draw_card(ax, 340, 610, 245, 85, '#2A1215', '#EF4444', radius=8)
ax.text(462, 665, "26µs 정규식 인터셉터", fontsize=10.5, weight='bold', color='#FECDD3', ha='center', zorder=5)
ax.text(462, 635, "생후 100일 미만 38℃ 고열, 경련,\n호흡곤란, 의식저하 등 12대 Red Flag", fontsize=8.5, color='#FDA4AF', ha='center', zorder=5)

draw_card(ax, 340, 500, 245, 95, '#1E293B', '#F59E0B', radius=8)
ax.text(462, 565, "한국어 복합 부정문 감별 엔진", fontsize=10, weight='bold', color='#FDE68A', ha='center', zorder=5)
ax.text(462, 532, "has_affirmative_match 알고리즘\n'열은 나는데 경련은 없어요' 감별\n허위 119 오경보율 0.0% 달성", fontsize=8.5, color='#CBD5E1', ha='center', zorder=5)

# ==============================================================================
# 3. AI AGENT ORCHESTRATION (Middle Center)
# ==============================================================================
draw_card(ax, 635, 420, 500, 350, '#1E293B', '#3B82F6', radius=14)
ax.text(885, 740, "지능형 멀티 에이전트 오케스트레이션", fontsize=13, weight='bold', color='#60A5FA', ha='center', zorder=5)
ax.text(885, 718, "Supervisor 6-State FSM (유한상태머신 기반 자동 라우팅)", fontsize=8.5, color='#93C5FD', ha='center', zorder=5)

# Agent 1: Triage
draw_card(ax, 650, 550, 230, 145, '#0F172A', '#8B5CF6', radius=8)
ax.text(765, 670, "TriageAgent", fontsize=11, weight='bold', color='#C4B5FD', ha='center', zorder=5)
ax.text(765, 648, "Gemini 3.8 Flash (Thinking)", fontsize=8.5, color='#A78BFA', ha='center', zorder=5)
ax.text(765, 605, "• 168개 소아 KTAS 지침 Direct 주입\n• 키워드 RAG 폐기 -> 문맥 완독 추론\n• 언더트리아제 0% / 민감도 100%", fontsize=8, color='#E2E8F0', ha='center', zorder=5)

# Agent 2: Matching
draw_card(ax, 890, 550, 230, 145, '#0F172A', '#10B981', radius=8)
ax.text(1005, 670, "MatchingAgent", fontsize=11, weight='bold', color='#6EE7B7', ha='center', zorder=5)
ax.text(1005, 648, "2-트랙 지리공간 LBS 엔진", fontsize=8.5, color='#34D399', ha='center', zorder=5)
ax.text(1005, 605, "• 5µs Haversine 구면거리 인덱싱\n• 병원 마감 +30분 안심약국 페어링\n• 비정형 공지 '소아불가' 실시간 차단", fontsize=8, color='#E2E8F0', ha='center', zorder=5)

# Agent 3: Logistics & Pass 2
draw_card(ax, 650, 435, 470, 100, '#0F172A', '#38BDF8', radius=8)
ax.text(885, 510, "LogisticsAgent & Pass 2 의료법 소독 게이트웨이", fontsize=10, weight='bold', color='#7DD3FC', ha='center', zorder=5)
ax.text(885, 480, "• 119 구급대원 인계용 실시간 브리핑 카드 생성 (환아 프로필, 바이탈, 타임라인)\n• 병원 출발 전 소아 당직의 30초 유선확인 대본 & 2024년 5월 본인확인 의무화 서류 체크리스트\n• 의료법 제27조 사후 소독: 불법 확정 진단명 / 전문의약품 임의 투약 용량 자동 검열·소독", fontsize=8, color='#CBD5E1', ha='center', zorder=5)

# ==============================================================================
# 4. HIGH-AVAILABILITY DATA INFRASTRUCTURE (Right)
# ==============================================================================
draw_card(ax, 1170, 420, 390, 350, '#1E293B', '#10B981', radius=14)
ax.text(1365, 740, "고가용성 무중단 데이터 인프라", fontsize=13, weight='bold', color='#34D399', ha='center', zorder=5)
ax.text(1365, 718, "3-State 서킷 브레이커 & 3-Tier Multi-Storage Fallback", fontsize=8.5, color='#6EE7B7', ha='center', zorder=5)

# Circuit Breaker Box
draw_card(ax, 1185, 630, 360, 68, '#0F172A', '#F59E0B', radius=8)
ax.text(1365, 675, "비동기 서킷 브레이커 (3-State FSM)", fontsize=10, weight='bold', color='#FDE68A', ha='center', zorder=5)
ax.text(1365, 650, "공공망 500/504 장애 시 3회 실패 -> 즉각 차단(OPEN)\n대기시간 0ms 단축 및 하위 Fallback 즉각 전환", fontsize=8, color='#CBD5E1', ha='center', zorder=5)

# 3-Tier Fallback Layers
draw_card(ax, 1185, 435, 360, 180, '#0F172A', '#10B981', radius=8)
ax.text(1365, 595, "3-Tier 계층형 스토리지 무중단 폴백", fontsize=10, weight='bold', color='#A7F3D0', ha='center', zorder=5)

# L1
draw_card(ax, 1195, 542, 340, 38, '#1E293B', '#10B981', radius=6)
ax.text(1365, 561, "Tier 1 : In-Memory TTL Cache (< 0.05ms, 5분 동기화)", fontsize=8.5, weight='bold', color='#6EE7B7', ha='center', zorder=5)

# L2
draw_card(ax, 1195, 492, 340, 38, '#1E293B', '#3B82F6', radius=6)
ax.text(1365, 511, "Tier 2 : Cloud Firestore (< 25ms, Hash Diffing -93.9%)", fontsize=8.5, weight='bold', color='#93C5FD', ha='center', zorder=5)

# L3
draw_card(ax, 1195, 442, 340, 38, '#1E293B', '#EC4899', radius=6)
ax.text(1365, 461, "Tier 3 : Canonical JSON Masterset (< 1ms, 외부망 0%)", fontsize=8.5, weight='bold', color='#F472B6', ha='center', zorder=5)

# ==============================================================================
# 5. 2-TRACK OUTPUT & ROUTING DECISION (Bottom)
# ==============================================================================
# Track A Card (Left Bottom)
draw_card(ax, 130, 60, 640, 300, '#1E1B2E', '#EF4444', radius=14)
draw_card(ax, 145, 305, 260, 42, '#EF4444', 'none', radius=6)
ax.text(275, 326, "Track A : 초응급 중증 대응", fontsize=11, weight='bold', color='#FFFFFF', ha='center', zorder=5)
ax.text(530, 326, "(KTAS 1 ~ 3 단계)", fontsize=10, weight='bold', color='#FCA5A5', ha='center', zorder=5)

ax.text(160, 265, "• 119 구급차 즉각 호출 & 원터치 다이얼 직통 연동", fontsize=9.5, weight='bold', color='#FFFFFF', zorder=5)
ax.text(160, 235, "• 권역 소아전문응급센터 및 소아 전용 병상(hv28) 실시간 거리순 랭킹", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(160, 205, "• 119 구급대원 인계용 응급 브리핑 카드 (환아 프로필, 바이탈, 타임라인)", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(160, 175, "• 전문 응급처치 포토 가이드 (영아 CPR, 기도폐쇄 하임리히, 열성경련, 화상 쿨링)", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(160, 145, "• 원내 약국 조제 원칙 -> 불필요한 약국 정보 과감히 배제, 환아 처치 집중", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(160, 100, "결과 화면: result.html (KTAS 1~3 Red 테마) & briefing_card.html", fontsize=8.5, color='#F87171', weight='bold', zorder=5)

# Track B Card (Right Bottom)
draw_card(ax, 830, 60, 640, 300, '#0F2624', '#10B981', radius=14)
draw_card(ax, 845, 305, 260, 42, '#10B981', 'none', radius=6)
ax.text(975, 326, "Track B : 경증 안심 외래 분리", fontsize=11, weight='bold', color='#FFFFFF', ha='center', zorder=5)
ax.text(1230, 326, "(KTAS 4 ~ 5 단계)", fontsize=10, weight='bold', color='#A7F3D0', ha='center', zorder=5)

ax.text(860, 265, "• 전국 156개 달빛어린이병원 LBS 실시간 최단거리 매칭 (응급실 분산 유도)", fontsize=9.5, weight='bold', color='#FFFFFF', zorder=5)
ax.text(860, 235, "• 병원 마감 +30분 안전 마진 안심약국 1:1 페어링 (심야 조제 불가 사고 원천 차단)", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(860, 205, "• 소아청소년과 전문의 당직 여부 30초 유선 확인 통화 스크립트 제공", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(860, 175, "• 2024년 5월 본인확인 의무화 지참 서류(모바일 등본, 신분증) 체크리스트", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(860, 145, "• 불필요한 응급실 병상 정보 배제 -> 응급실 74% 경증 과밀화 해소 기여", fontsize=9, color='#CBD5E1', zorder=5)
ax.text(860, 100, "결과 화면: result.html (KTAS 4~5 Emerald 테마) & hospital_detail.html", fontsize=8.5, color='#34D399', weight='bold', zorder=5)

# ==============================================================================
# CONNECTING ARROWS
# ==============================================================================
# Client -> Pass 1
draw_arrow(ax, 290, 620, 325, 620, color='#38BDF8', lw=2.5)

# Pass 1 Red Flag -> Track A
draw_arrow(ax, 462, 480, 462, 360, color='#EF4444', lw=2.5)
ax.text(485, 420, "초응급 Red Flag 즉각 차단\n(0ms Fast-Track)", fontsize=8, color='#FCA5A5', weight='bold', zorder=5)

# Pass 1 Clean -> Supervisor
draw_arrow(ax, 600, 600, 635, 600, color='#60A5FA', lw=2.5)
ax.text(617, 615, "정상문진", fontsize=8, color='#93C5FD', ha='center', zorder=5)

# Supervisor -> Data Infra
draw_arrow(ax, 1135, 595, 1170, 595, color='#10B981', lw=2)

# Data Infra -> Supervisor
draw_arrow(ax, 1170, 575, 1135, 575, color='#34D399', lw=2)

# Supervisor -> 2-Track 분기
# To Track A
draw_arrow(ax, 750, 420, 560, 360, color='#EF4444', lw=2)
ax.text(640, 385, "KTAS 1~3\n(중증/응급)", fontsize=8.5, weight='bold', color='#FCA5A5', ha='center', zorder=5)

# To Track B
draw_arrow(ax, 1010, 420, 1040, 360, color='#10B981', lw=2)
ax.text(1050, 385, "KTAS 4~5\n(경증/외래)", fontsize=8.5, weight='bold', color='#6EE7B7', ha='center', zorder=5)

plt.tight_layout()
plt.savefig('images/backend_logic_architecture.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
print("Successfully generated clean images/backend_logic_architecture.png without glyph warnings!")
