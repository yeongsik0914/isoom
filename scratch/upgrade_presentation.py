import os
import pptx
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 1. Color Palette Definitions
C_NAVY_DARK = RGBColor(0x0F, 0x17, 0x2A)   # #0F172A
C_SLATE_BG  = RGBColor(0xF8, 0xFA, 0xFC)   # #F8FAFC
C_CARD_BG   = RGBColor(0xFF, 0xFF, 0xFF)   # #FFFFFF
C_DARK_CARD = RGBColor(0x1E, 0x29, 0x3B)   # #1E293B
C_BORDER    = RGBColor(0xE2, 0xE8, 0xF0)   # #E2E8F0
C_BORDER_D  = RGBColor(0x33, 0x41, 0x55)   # #334155
C_TEAL      = RGBColor(0x2B, 0x8A, 0x87)   # #2B8A87
C_TOSS_BLUE = RGBColor(0x31, 0x82, 0xF6)   # #3182F6
C_CORAL     = RGBColor(0xEF, 0x44, 0x44)   # #EF4444
C_EMERALD   = RGBColor(0x10, 0xB9, 0x81)   # #10B981
C_AMBER     = RGBColor(0xF5, 0x9E, 0x0B)   # #F59E0B
C_PURPLE    = RGBColor(0x8B, 0x5C, 0xF6)   # #8B5CF6
C_TEXT_DARK = RGBColor(0x0F, 0x17, 0x2A)   # #0F172A
C_TEXT_MUTED= RGBColor(0x64, 0x74, 0x8B)   # #64748B
C_TEXT_WHITE= RGBColor(0xFF, 0xFF, 0xFF)   # #FFFFFF

FONT_MAIN = "Noto Sans KR"
FONT_FALLBACK = "Malgun Gothic"

def create_presentation():
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333) # 12192000 EMU
    prs.slide_height = Inches(7.500) # 6858000 EMU
    blank_layout = prs.slide_layouts[6] # completely blank

    def add_header(slide, cat_num, title, subtitle, is_dark=False):
        # Category number
        tb_cat = slide.shapes.add_textbox(Cm(1.69), Cm(1.0), Cm(15.0), Cm(0.8))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = cat_num
        p_cat.font.name = FONT_MAIN
        p_cat.font.size = Pt(14)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_TEAL if not is_dark else C_TOSS_BLUE

        # Title
        tb_title = slide.shapes.add_textbox(Cm(1.69), Cm(1.7), Cm(22.0), Cm(1.0))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title
        p_title.font.name = FONT_MAIN
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_TEXT_DARK if not is_dark else C_TEXT_WHITE

        # Subtitle
        tb_sub = slide.shapes.add_textbox(Cm(1.69), Cm(2.75), Cm(26.0), Cm(0.8))
        tf_sub = tb_sub.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_right = tf_sub.margin_top = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = FONT_MAIN
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = C_TEXT_MUTED if not is_dark else RGBColor(0x94, 0xA3, 0xB8)

    def draw_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_BORDER, border_width=1.0):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(border_width)
        else:
            shape.line.fill.background()
        return shape

    # =========================================================================
    # SLIDE 1: COVER
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    # Background full box
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY_DARK
    bg1.line.fill.background()

    # Brand Pill
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(27.0), Cm(1.2), Cm(5.2), Cm(1.1))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    pill.line.color.rgb = C_TEAL
    pill.line.width = Pt(1.5)
    tf_pill = pill.text_frame
    tf_pill.text = "ISOOM 아이숨"
    tf_pill.paragraphs[0].alignment = PP_ALIGN.CENTER
    tf_pill.paragraphs[0].font.name = FONT_MAIN
    tf_pill.paragraphs[0].font.size = Pt(11)
    tf_pill.paragraphs[0].font.bold = True
    tf_pill.paragraphs[0].font.color.rgb = C_TEXT_WHITE

    # Title group
    tb1_sub = s1.shapes.add_textbox(Cm(1.69), Cm(5.8), Cm(20.0), Cm(0.8))
    tf1_sub = tb1_sub.text_frame
    p = tf1_sub.paragraphs[0]
    p.text = "소아병동을 지키는 의료 AI AGENTS"
    p.font.name = FONT_MAIN
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_TEAL

    tb1_main = s1.shapes.add_textbox(Cm(1.69), Cm(6.8), Cm(24.0), Cm(3.2))
    tf1_main = tb1_main.text_frame
    p1 = tf1_main.paragraphs[0]
    p1.text = "KTAS 응급 분류도 기반"
    p1.font.name = FONT_MAIN
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_WHITE
    p2 = tf1_main.add_paragraph()
    p2.text = "소아 환자 분류 서비스"
    p2.font.name = FONT_MAIN
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = C_TEXT_WHITE

    # Divider line
    line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1.69), Cm(11.2), Cm(20.0), Cm(0.04))
    line.fill.solid()
    line.fill.fore_color.rgb = C_TEAL
    line.line.fill.background()

    # Authors & Live Badges
    tb1_author = s1.shapes.add_textbox(Cm(1.69), Cm(11.6), Cm(24.0), Cm(1.5))
    tf1_author = tb1_author.text_frame
    p_auth = tf1_author.paragraphs[0]
    p_auth.text = "정영식 팀장 · 김동준 팀원  |  AI-Native Healthcare Project"
    p_auth.font.name = FONT_MAIN
    p_auth.font.size = Pt(13)
    p_auth.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    p_badge = tf1_author.add_paragraph()
    p_badge.text = "• Google Cloud Run Live  • 128 pytest Passed (100%)  • 50대 소아 임상 골든 케이스 검증 (언더트리아제 0%)"
    p_badge.font.name = FONT_MAIN
    p_badge.font.size = Pt(11)
    p_badge.font.color.rgb = C_EMERALD

    # Add Official App Icon on right
    if os.path.exists('images/aisum_official_app_icon.png'):
        s1.shapes.add_picture('images/aisum_official_app_icon.png', Cm(25.5), Cm(6.5), Cm(6.0), Cm(6.0))

    # =========================================================================
    # SLIDE 2: TABLE OF CONTENTS
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "발표 목차", "아이숨 핵심 프로젝트 발표 목차", "프로젝트 기획부터 15단계 엔지니어링 개발 로드맵, 백엔드 시각화 및 배포 성과까지의 흐름")

    toc_items = [
        ("01.", "개발 배경 및 문제 정의", "소아 응급실 뺑뺑이 사태와\n야간 의료 3대 구조적 모순"),
        ("02.", "데이터 분석 & 통계 실증", "9.4만 건 공공데이터 분석과\n경증 74% 쏠림 원인 규명"),
        ("03.", "15단계 개발 로드맵", "기획 ➔ 데이터셋 ➔ 백엔드 모듈화\n➔ AI 결합 ➔ 무중단 배포"),
        ("04.", "시스템 아키텍처 & 성과", "백엔드 로직 시각화 다이어그램,\n무중단 인프라 및 Cloud Run 배포")
    ]

    card_w = Cm(7.2)
    card_h = Cm(11.5)
    card_top = Cm(4.5)
    card_gap = Cm(0.8)

    for i, (num, t_text, d_text) in enumerate(toc_items):
        c_left = Cm(1.69) + i * (card_w + card_gap)
        card = draw_card(s2, c_left, card_top, card_w, card_h, C_CARD_BG, C_BORDER, 1.2)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.8)
        tf.margin_top = Cm(1.0)
        
        p_num = tf.paragraphs[0]
        p_num.text = num
        p_num.font.name = FONT_MAIN
        p_num.font.size = Pt(28)
        p_num.font.bold = True
        p_num.font.color.rgb = C_TEAL

        p_t = tf.add_paragraph()
        p_t.text = f"\n{t_text}"
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_DARK

        p_d = tf.add_paragraph()
        p_d.text = f"\n{d_text}"
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 3: PROBLEM DEFINITION (Roadmap 1 & 3)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "01. 개발 목적 및 사회적 배경", "대한민국 소아 응급의료 현장의 3대 구조적 모순", "소아청소년과 전문의 부재와 야간 경증 과밀화로 인한 골든타임 실종 문제를 해결하고자 시작되었습니다.")

    p_items = [
        ("야간 소아응급실 뺑뺑이 (골든타임 실종)", 
         "소아청소년과 전문의 및 야간 당직의 부재로 인한 진료 거부·제한 공지 속출",
         "• 대학병원·권역응급센터조차 당직의 부족으로 '소아 진료 불가' 공지 일상화\n• 보호자가 야간에 병원을 찾지 못해 여러 응급실을 전전하다 골든타임 소실\n• 비정형 공지사항에 기재되어 일반 포털 지도로는 진료 가능 여부 확인 불가",
         C_CORAL),
        ("대형 응급실 경증 환자 과밀화 (74.0%)", 
         "야간 1차 의원 부재로 단순 미열·경증 환아가 대형 응급실로 쏠리는 악순환",
         "• 야간 소아 응급실 내원 환아의 74%가 단순 미열·감기 등 경증 환자\n• 20시~24시 피크 시간대에 대기 환자 폭증 (평균 대기시간 3~5시간 소요)\n• 경증 환아의 응급실 점유로 인해 정작 중증 환아(KTAS 1~2) 처치 지연",
         C_AMBER),
        ("심야 처방약 조제 불가 사고 (조제 단절)", 
         "달빛어린이병원 진료 후 인근 약국 조기 마감에 따른 심야 조제 단절",
         "• 전국 156개 달빛어린이병원 반경 1km 이내 약국의 42.6%가 병원보다 일찍 마감\n• 진료를 어렵게 받고도 처방약을 조제하지 못해 새벽에 약국을 찾아 헤매는 사고 빈발\n• 병원 진료 시간과 약국 조제 시간의 미스매치가 시스템적으로 방치됨",
         C_TOSS_BLUE)
    ]

    c3_w = Cm(9.8)
    c3_h = Cm(12.0)
    c3_top = Cm(4.5)
    c3_gap = Cm(0.6)

    for i, (title, sub, bullets, accent) in enumerate(p_items):
        c_left = Cm(1.69) + i * (c3_w + c3_gap)
        card = draw_card(s3, c_left, c3_top, c3_w, c3_h, C_CARD_BG, C_BORDER, 1.2)
        
        # Accent top bar
        bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, c3_top, c3_w, Cm(0.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = accent
        bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.8)
        tf.margin_top = Cm(0.8)

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = accent

        p_s = tf.add_paragraph()
        p_s.text = f"\n{sub}\n"
        p_s.font.name = FONT_MAIN
        p_s.font.size = Pt(10)
        p_s.font.bold = True
        p_s.font.color.rgb = C_TEXT_DARK

        p_b = tf.add_paragraph()
        p_b.text = bullets
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 4: DATA ANALYSIS (Roadmap 2, 3, 5)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "02. 데이터 분석 & 통계 실증", "9.4만 건 공공데이터 실증 분석을 통해 발견한 핵심 문제점", "국립중앙의료원(NMC) E-Gen 실시간 병상과 심평원 전국 병의원·약국 마스터 데이터를 주피터 노트북으로 전수 분석했습니다.")

    # 3 Stat Cards on Top
    stat_w = Cm(9.8)
    stat_h = Cm(4.5)
    stat_top = Cm(4.2)
    stat_gap = Cm(0.6)

    stats = [
        ("74.0%", "응급실 소아 단순 경증 비율", "야간 내원 환자의 3/4이 비응급 경증 환자로 확인되어 응급실 마비의 주원인 규명", C_CORAL),
        ("4.2배 폭증", "20시~24시 심야 피크 쏠림", "소아과 문 닫는 20시 이후 특정 시간대에 환자가 집중되며 대기 3~5시간 발생", C_AMBER),
        ("-93.9%", "In-Memory Hash Diffing 절감", "5분 주기 실시간 병상 변동률이 5.8%에 불과함을 입증하여 DB 쓰기 비용 93.9% 절감", C_EMERALD)
    ]

    for i, (val, title, desc, col) in enumerate(stats):
        c_left = Cm(1.69) + i * (stat_w + stat_gap)
        card = draw_card(s4, c_left, stat_top, stat_w, stat_h, C_CARD_BG, C_BORDER, 1.2)
        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.8)
        tf.margin_top = Cm(0.6)

        p_v = tf.paragraphs[0]
        p_v.text = val
        p_v.font.name = FONT_MAIN
        p_v.font.size = Pt(28)
        p_v.font.bold = True
        p_v.font.color.rgb = col

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_DARK

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Bottom Full Card: Table / Findings
    bot_card = draw_card(s4, Cm(1.69), Cm(9.2), Cm(30.6), Cm(7.2), C_CARD_BG, C_BORDER, 1.2)
    tf_bot = bot_card.text_frame
    tf_bot.word_wrap = True
    tf_bot.margin_left = tf_bot.margin_right = Cm(1.0)
    tf_bot.margin_top = Cm(0.8)

    p_bh = tf_bot.paragraphs[0]
    p_bh.text = "주피터 노트북 1~5권 실증 분석을 통해 도출된 데이터 기반 결론"
    p_bh.font.name = FONT_MAIN
    p_bh.font.size = Pt(14)
    p_bh.font.bold = True
    p_bh.font.color.rgb = C_TEAL

    p_bd = tf_bot.add_paragraph()
    p_bd.text = (
        "\n1. [응급실 뺑뺑이의 본질 규명]: 단순 병상 부족이 아니라, '당직의 부재'와 '특정 시간대 경증 환자(74%)의 무분별한 쏠림'이 겹쳐 중증 환아 병동이 마비되는 현상임을 실측 증명.\n"
        "2. [조제 단절 사고 예방]: 달빛어린이병원 반경 1km 이내 약국의 42.6%가 조기 마감하므로, '병원 마감시간 + 30분 안전 마진'을 강제하는 1:1 페어링 알고리즘 도출.\n"
        "3. [키워드 RAG의 한계 확인]: 보호자의 비정형 증상 질의에 키워드 검색(BM25) RAG를 적용하면 유사도 0.0으로 엉뚱한 임상 지침을 주입해 환각이 발생하므로, 168개 소아 KTAS 지침을 LLM에 직접 주입(Direct Grounding)하는 방식으로 전환 결정."
    )
    p_bd.font.name = FONT_MAIN
    p_bd.font.size = Pt(10.5)
    p_bd.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 5: 2-TRACK SOLUTION & 5 PILLARS (Roadmap 4, 5)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "03. 해결 방향 & 핵심 솔루션", "야간·휴일 중증 병상 사수를 위한 2-트랙 경증 분리 시스템", "중증 응급 환아에게 병상을 양보하고 경증 환아는 달빛병원과 안심약국으로 신속히 분산 유도하는 5대 핵심 기술 기둥")

    # 5 Pillar Cards
    pillars = [
        ("0ms 2계층 안전 감시망", "26µs 정규식 인터셉터\n+ 복합 부정문 감별 엔진", "생후 100일 미만 고열, 경련 등 12대 Red Flag를 26µs 만에 즉각 차단하여 119 직행.\n'열은 나는데 경련은 없어요'와 같은 부정문을 감별하여 허위 119 경보 100% 방어.", C_CORAL),
        ("2-트랙 지능형 임상 라우팅", "소아 응급실 vs 달빛병원\n임상 맞춤 실시간 분기", "KTAS 1~3단계 중증은 소아전용 응급실 매칭, KTAS 4~5단계 경증은 1차 달빛어린이병원으로 분산 유도하여 응급실 74% 경증 과밀화 원천 해소.", C_TOSS_BLUE),
        ("+30분 마진 약국 페어링", "156개 달빛병원 1:1\n심야 안심약국 실시간 매칭", "달빛병원 진료 마감 시간보다 최소 30분 이상 늦게까지 영업하는 약국을 1:1 자동 페어링하여 진료 후 처방약 조제 불가 사고 완벽 방어.", C_EMERALD),
        ("In-Memory Hash Diffing", "클라우드 Firestore\nDB 쓰기 비용 93.9% 절감", "전국 415개 응급의료기관 병상 데이터를 5분 주기로 감시하되, MD5 해시 비교로 실제 변동된 5.8%만 DB에 반영하여 서버리스 FinOps 최적화.", C_PURPLE),
        ("119 구급대원 브리핑 카드", "30초 유선확인 대본 &\n본인확인 의무화 서류 안내", "구급대원 인계용 증상 브리핑 카드를 생성하고, 내원 전 소아 당직의 여부를 30초 만에 확인하는 통화 대본 및 2024년 5월 본인확인 서류 체크리스트 제공.", C_AMBER)
    ]

    p_w = Cm(5.8)
    p_h = Cm(11.8)
    p_top = Cm(4.5)
    p_gap = Cm(0.4)

    for i, (p_title, p_sub, p_desc, col) in enumerate(pillars):
        c_left = Cm(1.69) + i * (p_w + p_gap)
        card = draw_card(s5, c_left, p_top, p_w, p_h, C_CARD_BG, C_BORDER, 1.2)

        # Top indicator bar
        bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, p_top, p_w, Cm(0.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.5)
        tf.margin_top = Cm(0.7)

        p_t = tf.paragraphs[0]
        p_t.text = p_title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = col

        p_s = tf.add_paragraph()
        p_s.text = f"\n{p_sub}\n"
        p_s.font.name = FONT_MAIN
        p_s.font.size = Pt(9.5)
        p_s.font.bold = True
        p_s.font.color.rgb = C_TEXT_DARK

        p_d = tf.add_paragraph()
        p_d.text = p_desc
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(8.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 6: 15-STEP ROADMAP PART 1 (Steps 1~8)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "04. 15단계 E2E 엔지니어링 개발 로드맵 (Part 1)", "Step 1 ~ 8 : 문제 발견부터 데이터셋 구축 및 백엔드 모듈화까지", "실제 현장의 결함을 분석하고, 개발 거버넌스를 정립하여 파이썬 정규 백엔드 모듈로 체계화한 전반부 과정입니다.")

    r_steps_p1 = [
        ("Step 1", "사회적 이슈 포착", "소아 환자 응급실 뺑뺑이 및 야간 진료 제한 사태의 사회적 심각성 인식", C_CORAL),
        ("Step 2", "공공데이터 통계 분석", "NMC E-Gen 및 심평원 9.4만 건 공공데이터 수집 및 시간대별 상관관계 실증", C_AMBER),
        ("Step 3", "핵심 원인 규명", "당직의 부재와 20~24시 특정 시간대 단순 경증 환아 74% 쏠림 현상 확인", C_AMBER),
        ("Step 4", "2-트랙 분리 고안", "야간·휴일 중증 병상 사수를 위한 경증 분리 시스템 및 +30분 약국 페어링 착안", C_TEAL),
        ("Step 5", "목표 설정 및 실증", "주피터 노트북 1~5권으로 지리공간 쿼리, 해시 비교, 비정형 필터링 가설 검증 완료", C_TEAL),
        ("Step 6", "AI 규칙 & 거버넌스", "4대 불변 문서(Answer, Log, README, PLAN) 확립 및 Git NFD/NFC 협업 뼈대 구축", C_PURPLE),
        ("Step 7", "핵심 데이터셋 제작", "전국 156개 달빛병원, 2,028개 야간약국 페어링 매핑, 168개 소아 KTAS 지침 정제", C_PURPLE),
        ("Step 8", "백엔드 모듈화", "노트북 검증 알고리즘을 정규 백엔드 서비스(app/services, app/tools)로 패키지화", C_TOSS_BLUE)
    ]

    grid_w = Cm(7.2)
    grid_h = Cm(5.6)
    grid_left_start = Cm(1.69)
    grid_gap_x = Cm(0.6)
    grid_gap_y = Cm(0.6)
    row1_top = Cm(4.2)
    row2_top = Cm(10.4)

    for idx, (step_num, step_title, step_desc, col) in enumerate(r_steps_p1):
        col_idx = idx % 4
        row_top = row1_top if idx < 4 else row2_top
        c_left = grid_left_start + col_idx * (grid_w + grid_gap_x)

        card = draw_card(s6, c_left, row_top, grid_w, grid_h, C_CARD_BG, C_BORDER, 1.2)
        
        # Pill indicator
        pill = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left + Cm(0.5), row_top + Cm(0.5), Cm(2.2), Cm(0.7))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.fill.background()
        pill.text_frame.text = step_num
        pill.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        pill.text_frame.paragraphs[0].font.name = FONT_MAIN
        pill.text_frame.paragraphs[0].font.size = Pt(9.5)
        pill.text_frame.paragraphs[0].font.bold = True
        pill.text_frame.paragraphs[0].font.color.rgb = C_TEXT_WHITE

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.6)
        tf.margin_top = Cm(1.4)

        p_t = tf.paragraphs[0]
        p_t.text = step_title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_DARK

        p_d = tf.add_paragraph()
        p_d.text = f"\n{step_desc}"
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 7: 15-STEP ROADMAP PART 2 (Steps 9~15)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "05. 15단계 E2E 엔지니어링 개발 로드맵 (Part 2)", "Step 9 ~ 15 : AI 결합, 무중단 인프라, 프론트엔드 피봇부터 클라우드 배포까지", "백엔드에 AI와 FSM을 접목하고, 장애 방어 인프라 및 PWA 프론트엔드를 풀스택 연동하여 Cloud Run에 배포한 후반부 과정입니다.")

    r_steps_p2_top = [
        ("Step 9", "백엔드에 AI 결합", "Gemini 3.8 Flash 도입, 168개 KTAS 지침 Direct Grounding 주입 (키워드 RAG 전면 폐기)", C_PURPLE),
        ("Step 10", "에이전트 오케스트레이션", "Supervisor 6-State FSM 기반 3+1 멀티 에이전트(Triage/Matching/Logistics) 체계 완성", C_PURPLE),
        ("Step 11", "무중단 인프라 구축", "3-State 서킷 브레이커 & 3-Tier Multi-Storage Fallback (공공망 점검, Firebase 마비 대응)", C_EMERALD),
        ("Step 12", "프론트엔드 피봇 혁신", "Stitch MCP 연동 한계 폐기 ➔ 토스 TDS/모니모 레퍼런스 순수 Vanilla HTML5/CSS3 PWA 구축", C_TOSS_BLUE)
    ]

    r_steps_p2_bot = [
        ("Step 13", "풀스택 실시간 E2E 결합", "모듈화된 FastAPI 백엔드와 프론트엔드 6대 화면(input/result/detail 등) 실시간 연동 완성", C_TOSS_BLUE),
        ("Step 14", "AI 평가 (EVALS) 품질 검증", "50대 골든 케이스 실측, 128개 테스트 스위트 전수 통과, Red Flag 민감도 100%, 언더트리아제 0% 달성", C_CORAL),
        ("Step 15", "Cloud Run 프로덕션 배포", "Docker 경량화, GCP Secret Manager 5대 키 암호화 바인딩, gcloud CLI 기반 무중단 배포 및 라이브", C_TEAL)
    ]

    # Row 1 (4 items)
    for idx, (step_num, step_title, step_desc, col) in enumerate(r_steps_p2_top):
        c_left = grid_left_start + idx * (grid_w + grid_gap_x)
        card = draw_card(s7, c_left, row1_top, grid_w, grid_h, C_CARD_BG, C_BORDER, 1.2)
        
        pill = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left + Cm(0.5), row1_top + Cm(0.5), Cm(2.2), Cm(0.7))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.fill.background()
        pill.text_frame.text = step_num
        pill.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        pill.text_frame.paragraphs[0].font.name = FONT_MAIN
        pill.text_frame.paragraphs[0].font.size = Pt(9.5)
        pill.text_frame.paragraphs[0].font.bold = True
        pill.text_frame.paragraphs[0].font.color.rgb = C_TEXT_WHITE

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.6)
        tf.margin_top = Cm(1.4)

        p_t = tf.paragraphs[0]
        p_t.text = step_title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(12)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_DARK

        p_d = tf.add_paragraph()
        p_d.text = f"\n{step_desc}"
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = C_TEXT_MUTED

    # Row 2 (3 items, wider width)
    w_bot3 = Cm(9.8)
    gap_bot3 = Cm(0.6)
    for idx, (step_num, step_title, step_desc, col) in enumerate(r_steps_p2_bot):
        c_left = grid_left_start + idx * (w_bot3 + gap_bot3)
        card = draw_card(s7, c_left, row2_top, w_bot3, grid_h, C_CARD_BG, C_BORDER, 1.2)
        
        pill = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, c_left + Cm(0.6), row2_top + Cm(0.5), Cm(2.4), Cm(0.7))
        pill.fill.solid()
        pill.fill.fore_color.rgb = col
        pill.line.fill.background()
        pill.text_frame.text = step_num
        pill.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        pill.text_frame.paragraphs[0].font.name = FONT_MAIN
        pill.text_frame.paragraphs[0].font.size = Pt(9.5)
        pill.text_frame.paragraphs[0].font.bold = True
        pill.text_frame.paragraphs[0].font.color.rgb = C_TEXT_WHITE

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.8)
        tf.margin_top = Cm(1.4)

        p_t = tf.paragraphs[0]
        p_t.text = step_title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = C_TEXT_DARK

        p_d = tf.add_paragraph()
        p_d.text = f"\n{step_desc}"
        p_d.font.name = FONT_MAIN
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 8: BACKEND LOGIC ARCHITECTURE VISUALIZATION (USER KEY REQUEST)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    # Dark background for architecture slide
    bg8 = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg8.fill.solid()
    bg8.fill.fore_color.rgb = RGBColor(0x0B, 0x0F, 0x19)
    bg8.line.fill.background()

    add_header(s8, "06. 백엔드 시스템 로직 구조 시각화", "지능형 오케스트레이션 & 고가용성 데이터 파이프라인 아키텍처", "0ms 세이프티 가드레일 인터셉터, 6-State FSM 멀티 에이전트 및 3-Tier 무중단 스토리지 폴백 흐름도", is_dark=True)

    # Insert Generated Architecture Image
    arch_img_path = 'images/backend_logic_architecture.png'
    if os.path.exists(arch_img_path):
        s8.shapes.add_picture(arch_img_path, Cm(1.69), Cm(3.6), Cm(30.6), Cm(14.8))

    # =========================================================================
    # SLIDE 9: SERVICE PROCESS / 4-STEP USER JOURNEY
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "07. 서비스 프로세스 & 유저 저니", "문진 입력부터 응급실 이송·외래 조제까지 4단계 원스톱 파이프라인", "환아 보호자의 불안을 덜어주는 직관적인 단계별 가이드와 실시간 의료 지원 프로세스")

    steps_s9 = [
        ("1단계 : 스마트 원스톱 문진", "스마트 환아 입력", "• 0세~만18세 5대 연령 분류\n• 180도 부채꼴 인터랙티브 다이얼 체온계\n• 긴급한 상황을 위한 Web Speech STT 음성 입력\n• 이전 문진 기록 자동 연동 및 비증상 필터링", C_TEAL),
        ("2단계 : 0ms 가드레일 & KTAS", "0ms 감시 & 심층 추론", "• 26µs 정규식 인터셉터 12대 Red Flag 차단\n• 한국어 복합 부정문 감별 엔진 (오경보율 0%)\n• Gemini 3.8 Flash Thinking 168개 지침 완독\n• 의료법 제27조 불법 진단/투약 사후 소독 게이트웨이", C_PURPLE),
        ("3단계 : 2-트랙 맞춤 가이드", "임상 최적 맞춤 라우팅", "• Track A (중증 1~3단계): 소아응급실 병상(hv28) 실시간 랭킹 + 119 다이얼 직통 연동\n• Track B (경증 4~5단계): 전국 156개 달빛병원 LBS +30분 마진 안심약국 1:1 페어링\n• 불필요한 정보 배제로 응급실 과밀화 차단", C_CORAL),
        ("4단계 : 119 인계 브리핑 & 알림", "골든타임 현장 연계", "• 119 구급대원 인계용 응급 브리핑 카드\n• 병원 출발 전 소아 당직의 30초 유선확인 대본\n• 2024년 5월 본인확인 의무화 지참서류 체크리스트\n• 24시간 실시간 병상 변동 알림 센터 연동", C_EMERALD)
    ]

    s9_w = Cm(7.2)
    s9_h = Cm(11.8)
    s9_top = Cm(4.5)
    s9_gap = Cm(0.6)

    for i, (title, sub, bullets, col) in enumerate(steps_s9):
        c_left = Cm(1.69) + i * (s9_w + s9_gap)
        card = draw_card(s9, c_left, s9_top, s9_w, s9_h, C_CARD_BG, C_BORDER, 1.2)

        # Bar
        bar = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, s9_top, s9_w, Cm(0.2))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tf = card.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Cm(0.7)
        tf.margin_top = Cm(0.8)

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.name = FONT_MAIN
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = col

        p_s = tf.add_paragraph()
        p_s.text = f"\n{sub}\n"
        p_s.font.name = FONT_MAIN
        p_s.font.size = Pt(10.5)
        p_s.font.bold = True
        p_s.font.color.rgb = C_TEXT_DARK

        p_b = tf.add_paragraph()
        p_b.text = bullets
        p_b.font.name = FONT_MAIN
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = C_TEXT_MUTED

    # =========================================================================
    # SLIDE 10: ZERO-DOWNTIME INFRA & FRONTEND PIVOT (Roadmap 11, 12)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "08. 무중단 인프라 구축 & 프론트엔드 혁신", "외부 장애 방어 3-Tier Multi-Storage Fallback과 프론트엔드 피봇(Pivot) 스토리", "공공 API 마비나 Firebase 다운 상황에서도 100% 무중단 서비스를 제공하고, 디자인 피봇을 통해 최고 수준의 UI를 완성했습니다.")

    c10_w = Cm(14.9)
    c10_h = Cm(12.0)
    c10_top = Cm(4.5)

    # Left Card: Zero-Downtime Multi-Storage Fallback
    c_left10 = draw_card(s10, Cm(1.69), c10_top, c10_w, c10_h, C_CARD_BG, C_BORDER, 1.2)
    bar_l = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1.69), c10_top, c10_w, Cm(0.2))
    bar_l.fill.solid()
    bar_l.fill.fore_color.rgb = C_EMERALD
    bar_l.line.fill.background()

    tf_l = c_left10.text_frame
    tf_l.word_wrap = True
    tf_l.margin_left = tf_l.margin_right = Cm(0.9)
    tf_l.margin_top = Cm(0.8)

    p_lt = tf_l.paragraphs[0]
    p_lt.text = "⚡ 무중단 인프라 (3-State Circuit Breaker & 3-Tier Fallback)"
    p_lt.font.name = FONT_MAIN
    p_lt.font.size = Pt(13)
    p_lt.font.bold = True
    p_lt.font.color.rgb = C_EMERALD

    p_ld = tf_l.add_paragraph()
    p_ld.text = (
        "\n• [비동기 서킷 브레이커 (3-State FSM)]\n"
        "  공공데이터포털(E-Gen) API 점검 또는 500/504 장애 시, 3회 연속 실패 즉시 회로를 차단(OPEN)하여 사용자 대기 시간을 0ms로 단축.\n\n"
        "• [Tier 1 : In-Memory TTL Cache (0.05ms)]\n"
        "  5분 주기 실시간 병상 캐싱으로 공공 API 중복 호출 지연(400~1000ms) 방어.\n\n"
        "• [Tier 2 : Cloud Firestore Snapshot (25ms)]\n"
        "  In-Memory Hash Diffing으로 93.9% 비용을 절감하며 정상 수집된 최근 스냅샷 대체 안내.\n\n"
        "• [Tier 3 : Canonical JSON Masterset (< 1ms)]\n"
        "  인터넷 단절, 클라우드 DB 마비 등 최악의 재난 상황에서도 100% 로컬 불변 마스터셋으로 즉각 전환하여 전국 의료기관 안내 무중단 보장."
    )
    p_ld.font.name = FONT_MAIN
    p_ld.font.size = Pt(10)
    p_ld.font.color.rgb = C_TEXT_DARK

    # Right Card: Frontend Pivot Story
    c_right10 = draw_card(s10, Cm(17.39), c10_top, c10_w, c10_h, C_CARD_BG, C_BORDER, 1.2)
    bar_r = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(17.39), c10_top, c10_w, Cm(0.2))
    bar_r.fill.solid()
    bar_r.fill.fore_color.rgb = C_TOSS_BLUE
    bar_r.line.fill.background()

    tf_r = c_right10.text_frame
    tf_r.word_wrap = True
    tf_r.margin_left = tf_r.margin_right = Cm(0.9)
    tf_r.margin_top = Cm(0.8)

    p_rt = tf_r.paragraphs[0]
    p_rt.text = "🎨 프론트엔드 피봇 (시행착오 및 극복 혁신)"
    p_rt.font.name = FONT_MAIN
    p_rt.font.size = Pt(13)
    p_rt.font.bold = True
    p_rt.font.color.rgb = C_TOSS_BLUE

    p_rd = tf_r.add_paragraph()
    p_rd.text = (
        "\n• [시행착오 : Stitch MCP 자동 생성 연동 폐기]\n"
        "  초기에 Stitch 도구를 Antigravity MCP로 연동하여 UI를 자동 생성하려 했으나,\n"
        "  - 외부 CDN 라이브러리 강제 종속으로 오프라인 구동 불가\n"
        "  - 모바일 가상 키보드 팝업 시 화면이 찌그러지는 뷰포트 레이아웃 시프트 발생\n"
        "  - 이에 따라 자동 생성 방식을 과감히 전면 폐기하고 자체 개발로 전환 결정.\n\n"
        "• [극복 및 완성 : 토스 TDS & 모니모 디자인 시스템 이식]\n"
        "  - 외부 프레임워크 없는 100% 순수 Vanilla HTML5 & CSS3 웹앱 구축\n"
        "  - 첫 페이지 로딩 속도 0.1초 미만(초경량 최적화) 달성\n"
        "  - 야간에 어두운 방에서 아픈 아이를 안고 스마트폰을 켜는 부모의 눈부심 방지를 위해 토스 공식 TDS 다크 테마(#101012, #3182f6) 전역 이식\n"
        "  - PWA Service Worker v4 탑재로 앱처럼 홈 화면 설치 및 정적 자산 캐싱 지원."
    )
    p_rd.font.name = FONT_MAIN
    p_rd.font.size = Pt(10)
    p_rd.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 11: EVALS & CLOUD RUN DEPLOYMENT (Roadmap 14, 15)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "09. AI 평가 (EVALS) 품질 검증 & 클라우드 배포", "50대 골든 케이스 자동 평가기 실측 검증과 Google Cloud Run 실서버 프로덕션 무중단 배포", "철저한 임상 안전성 벤치마크 평가를 거쳐 엔터프라이즈 수준의 서버리스 클라우드 환경에 24시간 무중단 배포를 완료했습니다.")

    # Left Card: EVALS Benchmark
    c_left11 = draw_card(s11, Cm(1.69), c10_top, c10_w, c10_h, C_CARD_BG, C_BORDER, 1.2)
    bar_e = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(1.69), c10_top, c10_w, Cm(0.2))
    bar_e.fill.solid()
    bar_e.fill.fore_color.rgb = C_PURPLE
    bar_e.line.fill.background()

    tf_e = c_left11.text_frame
    tf_e.word_wrap = True
    tf_e.margin_left = tf_e.margin_right = Cm(0.9)
    tf_e.margin_top = Cm(0.8)

    p_et = tf_e.paragraphs[0]
    p_et.text = "🧪 AI 평가 (EVALS) 골든 테스트 시나리오 실측 검증"
    p_et.font.name = FONT_MAIN
    p_et.font.size = Pt(13)
    p_et.font.bold = True
    p_et.font.color.rgb = C_PURPLE

    p_ed = tf_e.add_paragraph()
    p_ed.text = (
        "\n• [50대 소아 임상 골든 케이스 벤치마크 평가]\n"
        "  대한소아응급의학회 지침 기반 50개 고난도 시나리오에 대한 자동 평가 엔진 구축.\n\n"
        "  - Red Flag 감지 민감도 : 100.0% (초응급 증상 누락 0건 달성)\n"
        "  - 언더트리아제 (Under-triage) 발생률 : 0.0% (중증을 경증으로 오판하는 사고 원천 차단)\n"
        "  - 복합 부정문 감별 오경보율 : 0.0% ('경련 없음' 안심 표현 100% 정상 판별)\n"
        "  - 평균 레이턴시 : 3.1초 (Gemini 3.8 Flash Thinking 기반 고속 추론)\n\n"
        "• [128개 pytest 단위/통합 테스트 전수 통과]\n"
        "  가드레일, FSM 상태 전이, Haversine 거리 계산, In-Memory 캐시, REST API 엔드포인트 전반에 걸친 128개 테스트 스위트 100% 패스 (무결점 회귀 방어)."
    )
    p_ed.font.name = FONT_MAIN
    p_ed.font.size = Pt(10)
    p_ed.font.color.rgb = C_TEXT_DARK

    # Right Card: Cloud Run Deployment
    c_right11 = draw_card(s11, Cm(17.39), c10_top, c10_w, c10_h, C_CARD_BG, C_BORDER, 1.2)
    bar_c = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE, Cm(17.39), c10_top, c10_w, Cm(0.2))
    bar_c.fill.solid()
    bar_c.fill.fore_color.rgb = C_TEAL
    bar_c.line.fill.background()

    tf_c = c_right11.text_frame
    tf_c.word_wrap = True
    tf_c.margin_left = tf_c.margin_right = Cm(0.9)
    tf_c.margin_top = Cm(0.8)

    p_ct = tf_c.paragraphs[0]
    p_ct.text = "☁️ gcloud CLI 기반 Google Cloud Run 프로덕션 무중단 배포"
    p_ct.font.name = FONT_MAIN
    p_ct.font.size = Pt(13)
    p_ct.font.bold = True
    p_ct.font.color.rgb = C_TEAL

    p_cd = tf_c.add_paragraph()
    p_cd.text = (
        "\n• [GCP Secret Manager 5대 핵심 비밀 키 암호화 연동]\n"
        "  코드 및 컨테이너 이미지에 비밀 키가 노출되지 않도록, Gemini API, 공공데이터 API, 카카오 REST API 키를 GCP Secret Manager에 암호화 보관하고 Cloud Run 실행 시 동적 주입.\n\n"
        "• [Docker 경량 슬림 컨테이너 아키텍처]\n"
        "  Python 3.11-slim 베이스 이미지 채택, 빌드 캐시 최적화 및 8080 포트 Uvicorn 비동기 서버 바인딩으로 컨테이너 콜드 스타트 최소화.\n\n"
        "• [Cloud Run 완전 관리형 서버리스 실서버 라이브]\n"
        "  리전: asia-northeast3 (서울 리전)\n  프로덕션 라이브 URL:\n  https://isoom-service-920380215419.asia-northeast3.run.app\n  24시간 실시간 무중단 서비스 및 자동 헬스체크 정상 가동 중."
    )
    p_cd.font.name = FONT_MAIN
    p_cd.font.size = Pt(10)
    p_cd.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 12: AS-IS vs TO-BE COMPARISON
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "10. 고도화 방안 비교 분석", "기존 의료 서비스 한계점(AS-IS)과 아이숨의 엔지니어링 개선 성과(TO-BE!)", "기존 룰베이스 지도 검색과 키워드 챗봇의 4대 한계를 엔지니어링과 AI를 통해 완전히 극복했습니다.")

    # Table or Dual Card Layout
    asis_w = Cm(14.9)
    asis_h = Cm(12.0)
    
    # Left AS-IS
    c_asis = draw_card(s12, Cm(1.69), c10_top, asis_w, asis_h, RGBColor(0xFE, 0xF2, 0xF2), C_CORAL, 1.2)
    tf_as = c_asis.text_frame
    tf_as.word_wrap = True
    tf_as.margin_left = tf_as.margin_right = Cm(0.9)
    tf_as.margin_top = Cm(0.8)

    p_at = tf_as.paragraphs[0]
    p_at.text = "❌ 기존 현황 및 한계점 (AS-IS)"
    p_at.font.name = FONT_MAIN
    p_at.font.size = Pt(14)
    p_at.font.bold = True
    p_at.font.color.rgb = C_CORAL

    p_ad = tf_as.add_paragraph()
    p_ad.text = (
        "\n1. 단순 지도 검색 및 비정형 정보 누락\n"
        "   일반 포털 지도는 야간 소청과 당직의 유무를 알 수 없으며, E-Gen 비정형 공지에 적힌 '소아 진료 불가' 메시지를 파싱하지 못해 환아 뺑뺑이 발생.\n\n"
        "2. 키워드 RAG 챗봇의 환각 및 임상 오분류\n"
        "   키워드 검색(BM25) RAG는 보호자의 일상 구어체 입력 시 유사도 0.0을 반환하며 엉뚱한 임상 청크를 주입하여 언더트리아제(위험 방치) 초래.\n\n"
        "3. 공공 API 장애 시 전체 서비스 중단 (SPOF)\n"
        "   공공데이터포털 서버 지연(400~1000ms)이나 점검 발생 시 웹 서비스 전체가 멈추는 단일 장애점(SPOF) 존재.\n\n"
        "4. 인근 약국 조기 마감으로 심야 조제 단절\n"
        "   달빛병원 근처 약국의 42.6%가 병원보다 일찍 문을 닫아, 진료를 받고도 약을 조제하지 못하는 현장 결함 방치."
    )
    p_ad.font.name = FONT_MAIN
    p_ad.font.size = Pt(10)
    p_ad.font.color.rgb = RGBColor(0x99, 0x1B, 0x1B)

    # Right TO-BE
    c_tobe = draw_card(s12, Cm(17.39), c10_top, asis_w, asis_h, RGBColor(0xF0, 0xFD, 0xF4), C_EMERALD, 1.2)
    tf_to = c_tobe.text_frame
    tf_to.word_wrap = True
    tf_to.margin_left = tf_to.margin_right = Cm(0.9)
    tf_to.margin_top = Cm(0.8)

    p_tt = tf_to.paragraphs[0]
    p_tt.text = "✅ 아이숨 고도화 엔지니어링 성과 (TO-BE!)"
    p_tt.font.name = FONT_MAIN
    p_tt.font.size = Pt(14)
    p_tt.font.bold = True
    p_tt.font.color.rgb = C_EMERALD

    p_td = tf_to.add_paragraph()
    p_td.text = (
        "\n1. E-Gen 실시간 병상 + 비정형 정규식 자동 필터링\n"
        "   소아 전용 병상(hv28) 실시간 추적 및 PEDIATRIC_BLOCK_PATTERN 정규식으로 '소아 불가' 공지 기관을 자동 배제하여 안전 병원만 직결.\n\n"
        "2. KTAS 168개 지침 Direct Grounding & 언더트리아제 0%\n"
        "   RAG를 폐기하고 Gemini 3.8 Flash에 KTAS 지침을 직접 주입하여 문장 전반부 안도성 표현을 완독 감별, 초응급 민감도 100% 달성.\n\n"
        "3. 3-State 서킷 브레이커 & 3-Tier 무중단 Fallback\n"
        "   L1 인메모리(0.05ms) -> L2 Firestore(25ms, Hash Diffing -93.9%) -> L3 로컬 JSON(1ms)으로 공공망 장애 시에도 100% 무중단 보장.\n\n"
        "4. 156개 달빛병원 + 30분 마진 안심약국 1:1 페어링\n"
        "   병원 진료 마감 시간보다 최소 30분 이상 늦게 닫는 안심약국을 1:1 페어링하여 심야 처방약 조제 불가 사고 원천 차단."
    )
    p_td.font.name = FONT_MAIN
    p_td.font.size = Pt(10)
    p_td.font.color.rgb = RGBColor(0x06, 0x5F, 0x46)

    # =========================================================================
    # SLIDE 13: CLOSING / Q&A
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    bg13 = s13.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg13.fill.solid()
    bg13.fill.fore_color.rgb = C_NAVY_DARK
    bg13.line.fill.background()

    # Brand Box
    pill13 = s13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Cm(13.4), Cm(5.0), Cm(7.1), Cm(1.6))
    pill13.fill.solid()
    pill13.fill.fore_color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    pill13.line.color.rgb = C_TEAL
    pill13.line.width = Pt(1.5)
    tf13_p = pill13.text_frame
    tf13_p.text = "ISOOM 아이숨"
    tf13_p.paragraphs[0].alignment = PP_ALIGN.CENTER
    tf13_p.paragraphs[0].font.name = FONT_MAIN
    tf13_p.paragraphs[0].font.size = Pt(13)
    tf13_p.paragraphs[0].font.bold = True
    tf13_p.paragraphs[0].font.color.rgb = C_TEXT_WHITE

    # Big Title
    tb13 = s13.shapes.add_textbox(Cm(1.69), Cm(7.5), Cm(30.5), Cm(4.0))
    tf13 = tb13.text_frame
    p13_1 = tf13.paragraphs[0]
    p13_1.alignment = PP_ALIGN.CENTER
    p13_1.text = "아이들이 숨쉬는 공간, ISOOM"
    p13_1.font.name = FONT_MAIN
    p13_1.font.size = Pt(34)
    p13_1.font.bold = True
    p13_1.font.color.rgb = C_TEXT_WHITE

    p13_2 = tf13.add_paragraph()
    p13_2.alignment = PP_ALIGN.CENTER
    p13_2.text = "소아 야간 의료의 공백을 기술과 데이터로 안전하게 메웁니다."
    p13_2.font.name = FONT_MAIN
    p13_2.font.size = Pt(16)
    p13_2.font.color.rgb = C_TEAL

    p13_3 = tf13.add_paragraph()
    p13_3.alignment = PP_ALIGN.CENTER
    p13_3.text = "\n경청해 주셔서 감사합니다.  |  질의응답 (Q&A)"
    p13_3.font.name = FONT_MAIN
    p13_3.font.size = Pt(18)
    p13_3.font.bold = True
    p13_3.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

    # Save to file
    out_filename = '아이숨(ISOOM) 중간프로젝트 발표.pptx'
    prs.save(out_filename)
    print(f"Successfully generated elevated PPT: {out_filename} (Total slides: {len(prs.slides)})")

if __name__ == '__main__':
    create_presentation()
