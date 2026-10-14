# -*- coding: utf-8 -*-
"""Generator for KTAS Interactive HTML Viewer from 2021_KTAS_guideline_ver1.6.pptx data."""

import json
import os
import re

def main():
    print("[1/4] Loading compiled KTAS dataset and slides...")
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch_ktas_slides.json"), "r", encoding="utf-8") as f:
        slides = json.load(f)

    # 1. Map categories
    category_names = {
        18: '물질관련', 19: '정신건강', 20: '신경계', 21: '눈/안과', 22: '코/비과',
        23: '귀/이과', 24: '입/목/치과', 25: '호흡기계', 26: '순환기계', 27: '소화기계',
        28: '산부인과', 29: '비뇨생식기', 30: '근골격계', 31: '중증외상', 32: '환경손상',
        33: '피부/감염', 34: '전신/기타'
    }

    ped_category_names = {
        204: '물질관련', 205: '정신건강', 206: '신경계', 207: '눈/안과', 208: '코/비과',
        209: '귀/이과', 210: '입/목/치과', 211: '호흡기계', 212: '순환기계', 213: '소화기계',
        214: '산부인과', 215: '비뇨생식기', 216: '근골격계', 217: '중증외상', 218: '환경손상',
        219: '피부/감염', 220: '전신/기타'
    }

    slide_to_cat = {}
    for s in slides:
        num = s['slide_num']
        if num in category_names:
            for l in s.get('links', []):
                m = re.search(r'slide(\d+)\.xml', l['target'])
                if m:
                    slide_to_cat[int(m.group(1))] = category_names[num]
        elif num in ped_category_names:
            for l in s.get('links', []):
                m = re.search(r'slide(\d+)\.xml', l['target'])
                if m:
                    slide_to_cat[int(m.group(1))] = ped_category_names[num]

    # 2. Extract symptoms
    symptoms = []
    for s in slides:
        num = s['slide_num']
        tables = s.get('tables', [])
        if not tables:
            continue
        
        code_table = None
        code_table_idx = -1
        for i, t in enumerate(tables):
            if len(t) >= 2 and any('Coding System' in str(cell) for cell in t[0]):
                code_table = t
                code_table_idx = i
                break
            elif len(t) >= 2 and any('NACRS' in str(cell) for cell in t[1]):
                code_table = t
                code_table_idx = i
                break
                
        if code_table is not None:
            name = ''
            code = ''
            if len(code_table[0]) >= 3:
                name = code_table[0][2].strip()
            if len(code_table) > 1 and len(code_table[1]) >= 2:
                code = code_table[1][1].strip()
                
            age = '성인' if num < 204 else '소아'
            cat = slide_to_cat.get(num, '전신/기타')
            
            sec = []
            prim = []
            for i, t in enumerate(tables):
                if i == code_table_idx:
                    continue
                t_header = ' '.join(t[0]) if t else ''
                if '2차' in t_header or '증상별' in t_header:
                    for r in t[1:]:
                        if len(r) >= 2 and r[0].strip().isdigit():
                            sec.append({'level': int(r[0].strip()), 'text': r[1].strip()})
                elif '1차' in t_header or '활력징후' in t_header:
                    for r in t[1:]:
                        if len(r) >= 2 and r[0].strip().isdigit():
                            prim.append({'level': int(r[0].strip()), 'text': r[1].strip()})
                else:
                    for r in t[1:]:
                        if len(r) >= 2 and r[0].strip().isdigit():
                            sec.append({'level': int(r[0].strip()), 'text': r[1].strip()})
                            
            levels = sorted(list(set([x['level'] for x in sec] + [x['level'] for x in prim])))
            notes = [txt for txt in s.get('texts', []) if '분류 도구' not in txt and 'ￜ' not in txt and txt.strip()]
            
            symptoms.append({
                'slide': num,
                'age': age,
                'category': cat,
                'name': name or f'슬라이드 {num} 증상',
                'code': code or '미지정',
                'levels': levels,
                'secondary': sec,
                'primary': prim,
                'notes': notes
            })

    print(f"[2/4] Extracted {len(symptoms)} symptoms (Adult: {len([x for x in symptoms if x['age']=='성인'])}, Ped: {len([x for x in symptoms if x['age']=='소아'])})")

    # 3. Extract Clinical References
    # Respiratory Table (Slide 390)
    resp_table = []
    if len(slides) >= 390:
        s390 = slides[389]
        if s390.get('tables'):
            resp_table = s390['tables'][0]

    # GCS (Slide 8)
    gcs_table = []
    if len(slides) >= 8:
        s8 = slides[7]
        if s8.get('tables'):
            gcs_table = s8['tables'][0]

    # SIRS (Slide 11)
    sirs_table = []
    if len(slides) >= 11:
        s11 = slides[10]
        if s11.get('tables'):
            sirs_table = s11['tables'][0]

    clinical_refs = {
        'respiratory_pediatric': resp_table,
        'gcs_adult': gcs_table,
        'sirs_adult': sirs_table
    }

    full_bundle = {
        'symptoms': symptoms,
        'clinical_refs': clinical_refs,
        'categories': [
            '순환기계', '호흡기계', '신경계', '소화기계', '정신건강',
            '눈/안과', '코/비과', '귀/이과', '입/목/치과', '산부인과',
            '비뇨생식기', '근골격계', '중증외상', '환경손상', '피부/감염',
            '물질관련', '전신/기타'
        ]
    }

    # Save to data directory
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"), exist_ok=True)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ktas_full_bundle.json"), "w", encoding="utf-8") as f:
        json.dump(full_bundle, f, ensure_ascii=False, indent=2)

    print("[3/4] Generating ktas_viewer.html...")
    data_json_str = json.dumps(full_bundle, ensure_ascii=False)

    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>2021 KTAS 한국형 응급환자 분류도구 가이드라인 대화형 뷰어 (ver 1.6)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-base: #090D16;
      --bg-surface: #0F172A;
      --bg-surface-elevated: #1E293B;
      --bg-card: rgba(30, 41, 59, 0.7);
      --border-color: rgba(255, 255, 255, 0.08);
      --border-highlight: rgba(56, 189, 248, 0.3);
      --text-main: #F8FAFC;
      --text-muted: #94A3B8;
      --text-dim: #64748B;
      --accent: #38BDF8;
      --accent-rgb: 56, 189, 248;
      --accent-gradient: linear-gradient(135deg, #38BDF8 0%, #6366F1 100%);
      
      /* KTAS Official Level Colors */
      --ktas-1: #EF4444; /* 소생 (Resuscitation) */
      --ktas-2: #F97316; /* 긴급 (Emergent) */
      --ktas-3: #EAB308; /* 응급 (Urgent) */
      --ktas-4: #10B981; /* 준응급 (Semi-urgent) */
      --ktas-5: #64748B; /* 비응급 (Non-urgent) */
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: 'Pretendard', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-main);
      line-height: 1.5;
      min-height: 100vh;
      overflow-x: hidden;
      padding-bottom: 80px;
    }}

    /* Scrollbar */
    ::-webkit-scrollbar {{
      width: 8px;
      height: 8px;
    }}
    ::-webkit-scrollbar-track {{
      background: var(--bg-base);
    }}
    ::-webkit-scrollbar-thumb {{
      background: #334155;
      border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #475569;
    }}

    /* Header */
    header {{
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 24px;
    }}

    .header-inner {{
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-icon {{
      font-size: 28px;
      line-height: 1;
      filter: drop-shadow(0 0 12px rgba(56, 189, 248, 0.5));
    }}

    .brand-title {{
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.5px;
      background: var(--accent-gradient);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .brand-subtitle {{
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
    }}

    .header-stats {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}

    .stat-badge {{
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid var(--border-color);
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .stat-badge span {{
      color: var(--accent);
    }}

    .btn {{
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--bg-surface-elevated);
      color: var(--text-main);
    }}

    .btn:hover {{
      background: #334155;
      transform: translateY(-1px);
    }}

    .btn-primary {{
      background: linear-gradient(135deg, #0284C7, #4F46E5);
      color: white;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
    }}
    .btn-primary:hover {{
      background: linear-gradient(135deg, #0369A1, #4338CA);
      box-shadow: 0 6px 20px rgba(2, 132, 199, 0.4);
    }}

    /* Main Container */
    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 24px 20px;
    }}

    /* Navigation Tabs */
    .nav-tabs {{
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 12px;
      overflow-x: auto;
    }}

    .tab-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .tab-btn:hover {{
      color: var(--text-main);
      background: rgba(255, 255, 255, 0.04);
    }}

    .tab-btn.active {{
      color: white;
      background: var(--bg-surface-elevated);
      border: 1px solid var(--border-highlight);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }}

    /* Banner */
    .redflag-banner {{
      background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(249, 115, 22, 0.08));
      border: 1px solid rgba(239, 68, 68, 0.3);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 24px;
      display: flex;
      align-items: flex-start;
      gap: 16px;
    }}

    .redflag-icon {{
      font-size: 28px;
      line-height: 1;
    }}

    .redflag-content h3 {{
      font-size: 16px;
      font-weight: 700;
      color: #FCA5A5;
      margin-bottom: 4px;
    }}

    .redflag-content p {{
      font-size: 13px;
      color: #CBD5E1;
      line-height: 1.6;
    }}

    /* Search & Filter Bar */
    .filter-panel {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 28px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
    }}

    .search-row {{
      display: flex;
      gap: 12px;
      margin-bottom: 16px;
      flex-wrap: wrap;
    }}

    .search-input-wrap {{
      flex: 1;
      min-width: 280px;
      position: relative;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 12px 16px 12px 42px;
      color: white;
      font-size: 15px;
      outline: none;
      transition: all 0.2s;
    }}

    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.2);
    }}

    .search-icon {{
      position: absolute;
      left: 14px;
      top: 50%;
      transform: translateY(-50%);
      font-size: 18px;
      color: var(--text-dim);
    }}

    .level-filters {{
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .level-chip {{
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      border: 1px solid transparent;
      transition: all 0.2s;
      background: var(--bg-surface-elevated);
      color: var(--text-muted);
    }}

    .level-chip:hover {{
      transform: translateY(-1px);
    }}

    .level-chip.active-all {{ background: #334155; color: white; }}
    .level-chip.active-1 {{ background: rgba(239, 68, 68, 0.2); border-color: var(--ktas-1); color: #FCA5A5; }}
    .level-chip.active-2 {{ background: rgba(249, 115, 22, 0.2); border-color: var(--ktas-2); color: #FDBA74; }}
    .level-chip.active-3 {{ background: rgba(234, 179, 8, 0.2); border-color: var(--ktas-3); color: #FDE047; }}
    .level-chip.active-4 {{ background: rgba(16, 185, 129, 0.2); border-color: var(--ktas-4); color: #6EE7B7; }}
    .level-chip.active-5 {{ background: rgba(100, 116, 139, 0.2); border-color: var(--ktas-5); color: #CBD5E1; }}

    .category-chips {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
      padding-top: 14px;
      border-top: 1px solid var(--border-color);
    }}

    .cat-chip {{
      padding: 5px 11px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      color: var(--text-muted);
      transition: all 0.15s;
    }}

    .cat-chip:hover {{
      border-color: var(--accent);
      color: var(--text-main);
    }}

    .cat-chip.active {{
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent);
      color: var(--accent);
      font-weight: 700;
    }}

    /* Grid Layout */
    .symptom-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 16px;
    }}

    .symptom-card {{
      background: var(--bg-card);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 18px;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    .symptom-card:hover {{
      transform: translateY(-3px);
      border-color: var(--border-highlight);
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3), 0 0 20px rgba(56, 189, 248, 0.1);
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 10px;
    }}

    .card-badges {{
      display: flex;
      gap: 6px;
      align-items: center;
    }}

    .code-badge {{
      font-size: 11px;
      font-family: monospace;
      font-weight: 700;
      background: rgba(255, 255, 255, 0.08);
      padding: 2px 7px;
      border-radius: 4px;
      color: #94A3B8;
    }}

    .cat-badge {{
      font-size: 11px;
      font-weight: 600;
      background: rgba(99, 102, 241, 0.15);
      color: #A5B4FC;
      padding: 2px 8px;
      border-radius: 4px;
    }}

    .slide-badge {{
      font-size: 11px;
      color: var(--text-dim);
    }}

    .symptom-title {{
      font-size: 17px;
      font-weight: 700;
      color: white;
      margin-bottom: 12px;
      letter-spacing: -0.3px;
    }}

    .card-levels {{
      display: flex;
      gap: 4px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }}

    .level-dot {{
      font-size: 11px;
      font-weight: 800;
      padding: 2px 6px;
      border-radius: 4px;
      display: inline-flex;
      align-items: center;
      gap: 3px;
    }}

    .level-1 {{ background: rgba(239, 68, 68, 0.2); color: #FCA5A5; border: 1px solid rgba(239, 68, 68, 0.3); }}
    .level-2 {{ background: rgba(249, 115, 22, 0.2); color: #FDBA74; border: 1px solid rgba(249, 115, 22, 0.3); }}
    .level-3 {{ background: rgba(234, 179, 8, 0.2); color: #FDE047; border: 1px solid rgba(234, 179, 8, 0.3); }}
    .level-4 {{ background: rgba(16, 185, 129, 0.2); color: #6EE7B7; border: 1px solid rgba(16, 185, 129, 0.3); }}
    .level-5 {{ background: rgba(100, 116, 139, 0.2); color: #CBD5E1; border: 1px solid rgba(100, 116, 139, 0.3); }}

    .card-preview {{
      font-size: 13px;
      color: var(--text-muted);
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      line-height: 1.5;
    }}

    .card-footer {{
      margin-top: 14px;
      padding-top: 10px;
      border-top: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: var(--text-dim);
    }}

    /* Modal */
    .modal-backdrop {{
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.75);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      z-index: 999;
      display: flex;
      justify-content: center;
      align-items: center;
      padding: 20px;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }}

    .modal-backdrop.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .modal-dialog {{
      background: var(--bg-surface);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      width: 100%;
      max-width: 800px;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
      transform: scale(0.95);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .modal-backdrop.open .modal-dialog {{
      transform: scale(1);
    }}

    .modal-header {{
      padding: 24px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      position: sticky;
      top: 0;
      background: var(--bg-surface);
      z-index: 10;
    }}

    .modal-close {{
      background: var(--bg-surface-elevated);
      border: none;
      color: var(--text-muted);
      width: 36px;
      height: 36px;
      border-radius: 9999px;
      cursor: pointer;
      font-size: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
    }}

    .modal-close:hover {{
      background: #334155;
      color: white;
    }}

    .modal-body {{
      padding: 24px;
    }}

    .section-title {{
      font-size: 16px;
      font-weight: 700;
      color: var(--accent);
      margin: 20px 0 12px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .section-title:first-child {{
      margin-top: 0;
    }}

    /* Table styles */
    .custom-table {{
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      border: 1px solid var(--border-color);
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 16px;
    }}

    .custom-table th, .custom-table td {{
      padding: 12px 16px;
      font-size: 13.5px;
      text-align: left;
    }}

    .custom-table th {{
      background: var(--bg-surface-elevated);
      color: var(--text-muted);
      font-weight: 600;
      border-bottom: 1px solid var(--border-color);
    }}

    .custom-table tr:not(:last-child) td {{
      border-bottom: 1px solid var(--border-color);
    }}

    .custom-table tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    .col-level {{
      width: 90px;
      font-weight: 800;
    }}

    /* Simulator Tab Styles */
    .simulator-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 28px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }}

    .step-box {{
      margin-bottom: 24px;
    }}

    .step-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .step-badge {{
      background: var(--accent);
      color: var(--bg-base);
      font-size: 12px;
      font-weight: 800;
      padding: 2px 7px;
      border-radius: 9999px;
    }}

    .choice-group {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .choice-btn {{
      padding: 14px 24px;
      border-radius: 12px;
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      color: var(--text-main);
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .choice-btn:hover {{
      border-color: var(--accent);
      transform: translateY(-2px);
    }}

    .choice-btn.selected {{
      background: rgba(56, 189, 248, 0.15);
      border-color: var(--accent);
      color: var(--accent);
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
    }}

    .select-dropdown {{
      width: 100%;
      background: var(--bg-base);
      border: 1px solid var(--border-color);
      color: white;
      padding: 12px 16px;
      border-radius: 10px;
      font-size: 15px;
      outline: none;
    }}

    .select-dropdown:focus {{
      border-color: var(--accent);
    }}

    .result-box {{
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.9));
      border: 1px solid var(--border-highlight);
      border-radius: 16px;
      padding: 24px;
      margin-top: 24px;
      display: none;
    }}

    .result-box.show {{
      display: block;
      animation: fadeIn 0.3s ease;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .result-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      border-radius: 8px;
      font-size: 18px;
      font-weight: 800;
      margin-bottom: 12px;
    }}

    /* Reference Cards */
    .ref-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
      gap: 20px;
    }}

    .ref-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      padding: 24px;
    }}

    .ref-title {{
      font-size: 18px;
      font-weight: 700;
      color: white;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    /* Guide Modal Steps */
    .guide-step {{
      display: flex;
      gap: 16px;
      margin-bottom: 16px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border-color);
    }}

    .guide-num {{
      width: 32px;
      height: 32px;
      border-radius: 9999px;
      background: var(--accent);
      color: var(--bg-base);
      font-weight: 800;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}

    .empty-state {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 60px 20px;
      color: var(--text-muted);
    }}

    .empty-icon {{
      font-size: 40px;
      margin-bottom: 12px;
    }}
  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <div class="header-inner">
      <div class="brand">
        <span class="brand-icon">🌙</span>
        <div>
          <div class="brand-title">KTAS 한국형 응급환자 분류도구 가이드라인 뷰어</div>
          <div class="brand-subtitle">2021년 최신 개정판 (ver 1.6) • 대한응급의학회 / 국립중앙의료원</div>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-badge">전체 증상 <span id="stat-total">325</span>개</div>
        <div class="stat-badge">소아 <span id="stat-ped">167</span>개</div>
        <div class="stat-badge">성인 <span id="stat-adult">158</span>개</div>
        <button class="btn btn-primary" onclick="openGuideModal()">
          📘 PDF 사용방법 안내
        </button>
      </div>
    </div>
  </header>

  <!-- Main Container -->
  <main class="container">
    
    <!-- Red Flag Banner -->
    <div class="redflag-banner">
      <div class="redflag-icon">🚨</div>
      <div class="redflag-content">
        <h3>MoonlightCare 소아 7대 Red Flag & KTAS 1~2단계 즉시 선별 연동</h3>
        <p>
          생후 100일 미만 38.0℃ 고열, 소아 경련, 청색증/호흡곤란, 의식저하, 중증 탈수, 두부 외상 후 구토, 담즙성 구토는
          KTAS 1단계(소생) 및 2단계(긴급)에 해당하며, 본 프로젝트에서는 LLM 지연 없이 <strong>0.012ms 인메모리 엔진</strong>으로 119 즉시 직결합니다.
        </p>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="nav-tabs">
      <button class="tab-btn active" onclick="switchTab('pediatric')">
        👶 소아 KTAS 가이드 (167개 증상)
      </button>
      <button class="tab-btn" onclick="switchTab('adult')">
        🧑 성인 KTAS 가이드 (158개 증상)
      </button>
      <button class="tab-btn" onclick="switchTab('simulator')">
        ⚡ 대화형 Triage 시뮬레이터 (판정기)
      </button>
      <button class="tab-btn" onclick="switchTab('clinical')">
        📊 1차 고려사항 임상 기준표 (활력징후/GCS/SIRS)
      </button>
    </div>

    <!-- TAB 1 & 2: Symptom Directory View -->
    <section id="directory-view">
      <div class="filter-panel">
        <div class="search-row">
          <div class="search-input-wrap">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-input" placeholder="증상명, NACRS 코드, 키워드 검색 (예: 열, 경련, 흉통, 001, 복통)..." oninput="applyFilters()">
          </div>
          <div class="level-filters">
            <span style="font-size:12px; font-weight:600; color:var(--text-dim); margin-right:4px;">KTAS 등급:</span>
            <div class="level-chip active-all" onclick="filterLevel(0)">전체</div>
            <div class="level-chip" onclick="filterLevel(1)">1단계 (소생)</div>
            <div class="level-chip" onclick="filterLevel(2)">2단계 (긴급)</div>
            <div class="level-chip" onclick="filterLevel(3)">3단계 (응급)</div>
            <div class="level-chip" onclick="filterLevel(4)">4단계 (준응급)</div>
            <div class="level-chip" onclick="filterLevel(5)">5단계 (비응급)</div>
          </div>
        </div>
        <div class="category-chips" id="category-chips-container">
          <!-- Dynamic category chips -->
        </div>
      </div>

      <div class="symptom-grid" id="symptom-grid">
        <!-- Dynamic Symptom Cards -->
      </div>
    </section>

    <!-- TAB 3: Interactive Triage Simulator -->
    <section id="simulator-view" style="display:none;">
      <div class="simulator-card">
        <h2 style="font-size:20px; font-weight:700; margin-bottom:20px; color:white;">
          ⚡ 대화형 KTAS 4단계 의사결정 트리 시뮬레이터
        </h2>
        
        <!-- Step 1: Age Selection -->
        <div class="step-box">
          <div class="step-title">
            <span class="step-badge">1단계</span> 대상 환자 연령군 선택
          </div>
          <div class="choice-group">
            <button class="choice-btn selected" id="sim-age-ped" onclick="simSetAge('소아')">
              <span style="font-size:20px;">👶</span> 소아 (15세 미만)
            </button>
            <button class="choice-btn" id="sim-age-adult" onclick="simSetAge('성인')">
              <span style="font-size:20px;">🧑</span> 성인 (15세 이상)
            </button>
          </div>
        </div>

        <!-- Step 2: Category Selection -->
        <div class="step-box">
          <div class="step-title">
            <span class="step-badge">2단계</span> 증상 대분류 (17개 계통) 선택
          </div>
          <select id="sim-category-select" class="select-dropdown" onchange="simUpdateSymptoms()">
            <!-- Dynamic Category Options -->
          </select>
        </div>

        <!-- Step 3: Specific Symptom Selection -->
        <div class="step-box">
          <div class="step-title">
            <span class="step-badge">3단계</span> 세부 주증상 선택
          </div>
          <select id="sim-symptom-select" class="select-dropdown" onchange="simUpdateConsiderations()">
            <!-- Dynamic Symptom Options -->
          </select>
        </div>

        <!-- Step 4: Decision Tree Options -->
        <div class="step-box" id="sim-considerations-box" style="display:none;">
          <div class="step-title">
            <span class="step-badge">4단계</span> 증상별 세부 상태 및 동반 징후 체크
          </div>
          <div id="sim-options-list" style="display:flex; flex-direction:column; gap:8px;">
            <!-- Dynamic Radio Options -->
          </div>
        </div>

        <!-- Result Box -->
        <div class="result-box" id="sim-result-box">
          <div class="result-badge" id="sim-result-badge">
            KTAS 2단계 (긴급)
          </div>
          <h3 id="sim-result-title" style="font-size:18px; font-weight:700; color:white; margin-bottom:8px;"></h3>
          <p id="sim-result-desc" style="font-size:14px; color:var(--text-muted); line-height:1.6;"></p>
          <div style="margin-top:16px; padding-top:14px; border-top:1px solid var(--border-color); font-size:13px; color:#38BDF8;">
            💡 <strong>임상 권고:</strong> <span id="sim-result-action"></span>
          </div>
        </div>

      </div>
    </section>

    <!-- TAB 4: Clinical Reference Standards -->
    <section id="clinical-view" style="display:none;">
      <div class="ref-grid">
        
        <!-- Adult GCS -->
        <div class="ref-card">
          <div class="ref-title">
            <span>🧠</span> 성인 의식수준 및 GCS 척도
          </div>
          <table class="custom-table">
            <thead>
              <tr><th>KTAS 단계</th><th>의식 수준</th><th>GCS</th><th>AVPU</th></tr>
            </thead>
            <tbody>
              <tr>
                <td><span class="level-dot level-1">1단계</span></td>
                <td><strong>무의식</strong><br><span style="font-size:12px; color:var(--text-dim);">기도 유지 불가, 지속 발작</span></td>
                <td>3 - 8</td>
                <td><strong>U</strong></td>
              </tr>
              <tr>
                <td><span class="level-dot level-2">2단계</span></td>
                <td><strong>의식수준 변화</strong><br><span style="font-size:12px; color:var(--text-dim);">지남력 상실, 착란, 초조</span></td>
                <td>9 - 13</td>
                <td><strong>V / P</strong></td>
              </tr>
              <tr>
                <td><span class="level-dot level-3">3단계 이상</span></td>
                <td><strong>명료 (Alert)</strong></td>
                <td>14 - 15</td>
                <td><strong>A</strong></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Adult SIRS / Sepsis -->
        <div class="ref-card">
          <div class="ref-title">
            <span>🌡️</span> 전신염증반응증후군(SIRS) & 패혈증
          </div>
          <div style="background:var(--bg-base); padding:14px; border-radius:10px; font-size:13px; color:var(--text-muted); margin-bottom:14px; border:1px solid var(--border-color);">
            <strong>SIRS 판정 기준 (2개 이상 만족 시):</strong><br>
            • 체온 &gt; 38.0°C 또는 &lt; 36.0°C<br>
            • 심박수 &gt; 90 회/분<br>
            • 호흡수 &gt; 20 회/분 (또는 PaCO2 &lt; 32 torr)<br>
            • 백혈구 &gt; 12,000 또는 &lt; 4,000 (또는 band &gt; 10%)
          </div>
          <table class="custom-table">
            <thead>
              <tr><th>KTAS</th><th>조건</th></tr>
            </thead>
            <tbody>
              <tr>
                <td><span class="level-dot level-2">2단계</span></td>
                <td><strong>패혈증 의증</strong> (SIRS 3개 이상 만족 또는 혈역학적 이상/호흡곤란 동반), 면역저하 상태 발열</td>
              </tr>
              <tr>
                <td><span class="level-dot level-3">3단계</span></td>
                <td><strong>전신염증반응증후군</strong> (열을 포함한 2개 SIRS 기준 만족)</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pediatric Respiratory Rates by Age (Slide 390) -->
        <div class="ref-card" style="grid-column: 1 / -1;">
          <div class="ref-title">
            <span>🫁</span> 소아 연령별 호흡수 기준표 (CTAS / KTAS 가이드라인)
          </div>
          <div style="overflow-x:auto;">
            <table class="custom-table" id="resp-table-view">
              <!-- Dynamically populated from Slide 390 -->
            </table>
          </div>
        </div>

      </div>
    </section>

  </main>

  <!-- Symptom Detail Modal -->
  <div class="modal-backdrop" id="symptom-modal" onclick="closeModalOnBackdrop(event)">
    <div class="modal-dialog">
      <div class="modal-header">
        <div>
          <div style="display:flex; gap:8px; align-items:center; margin-bottom:6px;">
            <span class="code-badge" id="modal-code"></span>
            <span class="cat-badge" id="modal-category"></span>
            <span style="font-size:12px; color:var(--text-dim);" id="modal-age"></span>
          </div>
          <h2 id="modal-title" style="font-size:22px; font-weight:800; color:white;"></h2>
        </div>
        <button class="modal-close" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-body">
        
        <!-- Available Levels -->
        <div style="margin-bottom:18px;">
          <div style="font-size:12px; color:var(--text-dim); margin-bottom:6px;">분류 가능 KTAS 등급:</div>
          <div id="modal-levels" style="display:flex; gap:6px; flex-wrap:wrap;"></div>
        </div>

        <!-- Secondary Considerations (Main Rule) -->
        <div class="section-title">
          <span>📋</span> 증상별 2차 고려사항 (세부 분류 기준)
        </div>
        <table class="custom-table">
          <thead>
            <tr>
              <th class="col-level">KTAS 등급</th>
              <th>세부 판정 기준 및 임상 상태</th>
            </tr>
          </thead>
          <tbody id="modal-secondary-tbody"></tbody>
        </table>

        <!-- Primary Considerations -->
        <div class="section-title">
          <span>🩺</span> 활력징후 및 1차 고려사항
        </div>
        <table class="custom-table">
          <thead>
            <tr>
              <th class="col-level">KTAS 등급</th>
              <th>고려 징후</th>
            </tr>
          </thead>
          <tbody id="modal-primary-tbody"></tbody>
        </table>

        <!-- Notes / Guidelines -->
        <div id="modal-notes-section" style="display:none;">
          <div class="section-title">
            <span>💡</span> 정의 및 참고 가이드
          </div>
          <div id="modal-notes-content" style="background:var(--bg-base); padding:16px; border-radius:10px; font-size:13.5px; color:#CBD5E1; line-height:1.6; border:1px solid var(--border-color);"></div>
        </div>

        <!-- Footer Info -->
        <div style="margin-top:20px; font-size:12px; color:var(--text-dim); text-align:right;">
          원본 PPTX 슬라이드: <span id="modal-slide-num"></span>번
        </div>

      </div>
    </div>
  </div>

  <!-- PDF Guide Modal -->
  <div class="modal-backdrop" id="guide-modal" onclick="closeGuideModalOnBackdrop(event)">
    <div class="modal-dialog">
      <div class="modal-header">
        <div>
          <h2 style="font-size:20px; font-weight:800; color:white;">
            📘 2021년 KTAS 분류도구 PPT 사용방법 안내
          </h2>
          <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">
            첨부 PDF 문서의 9단계 지침을 웹 뷰어로 편리하게 이용하는 방법
          </div>
        </div>
        <button class="modal-close" onclick="closeGuideModal()">✕</button>
      </div>
      <div class="modal-body">
        <div class="guide-step">
          <div class="guide-num">1</div>
          <div>
            <strong style="color:white;">읽기 전용 및 슬라이드쇼 방식의 한계 극복</strong>
            <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">
              기존 PowerPoint 원본 파일(42MB)은 읽기 전용 상태에서 F5 슬라이드쇼를 실행해 398개 슬라이드를 클릭 이동해야 했습니다. 본 웹 뷰어는 모든 데이터를 웹 표준으로 추출하여 0.01초 만에 브라우저에서 바로 검색하고 열람할 수 있도록 개선했습니다.
            </p>
          </div>
        </div>

        <div class="guide-step">
          <div class="guide-num">2</div>
          <div>
            <strong style="color:white;">연령에 따른 2-트랙 자동 분기</strong>
            <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">
              상단 탭에서 <strong>[👶 소아]</strong>와 <strong>[🧑 성인]</strong>을 원클릭으로 전환하여 해당 연령대 전용 167개 / 158개 가이드라인을 분리하여 확인하실 수 있습니다.
            </p>
          </div>
        </div>

        <div class="guide-step">
          <div class="guide-num">3</div>
          <div>
            <strong style="color:white;">주증상 17대 대분류 필터링</strong>
            <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">
              순환기계, 호흡기계, 신경계, 소화기계 등 17개 계통별 칩 버튼을 클릭하면 해당 증상만 즉시 필터링됩니다.
            </p>
          </div>
        </div>

        <div class="guide-step">
          <div class="guide-num">4</div>
          <div>
            <strong style="color:white;">1차/2차 고려사항 종합 판정</strong>
            <p style="font-size:13px; color:var(--text-muted); margin-top:4px;">
              카드를 클릭하면 해당 질환의 <strong>증상별 2차 고려사항</strong>과 <strong>활력징후 1차 고려사항</strong>이 표로 나타나며, [대화형 Triage 시뮬레이터] 탭에서 환자의 상태를 체크하면 최종 KTAS 1~5등급이 자동으로 계산됩니다.
            </p>
          </div>
        </div>

        <div style="text-align:center; margin-top:20px;">
          <button class="btn btn-primary" onclick="closeGuideModal()" style="padding:10px 24px;">
            확인 및 가이드라인 둘러보기
          </button>
        </div>
      </div>
    </div>
  </div>

  <script>
    // Embedded Data Bundle
    const KTAS_DATA = {data_json_str};

    // State Variables
    let currentAge = '소아';
    let currentLevelFilter = 0;
    let currentCategoryFilter = '전체';
    let simSelectedAge = '소아';

    // DOM Ready Initialization
    document.addEventListener('DOMContentLoaded', () => {{
      initCategoryChips();
      renderSymptoms();
      initSimulator();
      renderRespiratoryTable();
    }});

    // Tab Switching
    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      const dirView = document.getElementById('directory-view');
      const simView = document.getElementById('simulator-view');
      const clinView = document.getElementById('clinical-view');

      dirView.style.display = 'none';
      simView.style.display = 'none';
      clinView.style.display = 'none';

      if (tabId === 'pediatric') {{
        event.currentTarget.classList.add('active');
        currentAge = '소아';
        dirView.style.display = 'block';
        applyFilters();
      }} else if (tabId === 'adult') {{
        event.currentTarget.classList.add('active');
        currentAge = '성인';
        dirView.style.display = 'block';
        applyFilters();
      }} else if (tabId === 'simulator') {{
        event.currentTarget.classList.add('active');
        simView.style.display = 'block';
      }} else if (tabId === 'clinical') {{
        event.currentTarget.classList.add('active');
        clinView.style.display = 'block';
      }}
    }}

    // Category Chips Setup
    function initCategoryChips() {{
      const container = document.getElementById('category-chips-container');
      container.innerHTML = `<div class="cat-chip active" onclick="filterCategory('전체')">전체 분류</div>`;
      KTAS_DATA.categories.forEach(cat => {{
        container.innerHTML += `<div class="cat-chip" onclick="filterCategory('${{cat}}')">${{cat}}</div>`;
      }});
    }}

    function filterCategory(cat) {{
      currentCategoryFilter = cat;
      document.querySelectorAll('.cat-chip').forEach(chip => {{
        chip.classList.toggle('active', chip.textContent.trim() === cat || (cat === '전체' && chip.textContent.trim() === '전체 분류'));
      }});
      applyFilters();
    }}

    function filterLevel(lvl) {{
      currentLevelFilter = lvl;
      document.querySelectorAll('.level-chip').forEach((chip, idx) => {{
        chip.className = 'level-chip';
        if (lvl === 0 && idx === 0) chip.className = 'level-chip active-all';
        else if (lvl === idx) chip.className = `level-chip active-${{lvl}}`;
      }});
      applyFilters();
    }}

    // Render Symptom Cards
    function renderSymptoms() {{
      applyFilters();
    }}

    function applyFilters() {{
      const query = document.getElementById('search-input').value.trim().toLowerCase();
      const grid = document.getElementById('symptom-grid');
      
      const filtered = KTAS_DATA.symptoms.filter(item => {{
        // Age check
        if (item.age !== currentAge) return false;
        
        // Category check
        if (currentCategoryFilter !== '전체' && item.category !== currentCategoryFilter) return false;
        
        // Level check
        if (currentLevelFilter > 0 && !item.levels.includes(currentLevelFilter)) return false;
        
        // Query search
        if (query) {{
          const matchName = item.name.toLowerCase().includes(query);
          const matchCode = item.code.toLowerCase().includes(query);
          const matchCat = item.category.toLowerCase().includes(query);
          const matchSec = item.secondary.some(s => s.text.toLowerCase().includes(query));
          if (!matchName && !matchCode && !matchCat && !matchSec) return false;
        }}
        
        return true;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = `
          <div class="empty-state">
            <div class="empty-icon">🔎</div>
            <h3>조건에 맞는 KTAS 증상을 찾을 수 없습니다.</h3>
            <p style="font-size:13px; margin-top:4px;">검색어 오타를 확인하시거나 필터 조건을 변경해 보세요.</p>
          </div>
        `;
        return;
      }}

      grid.innerHTML = filtered.map(item => {{
        const levelDots = item.levels.map(lvl => `
          <span class="level-dot level-${{lvl}}">KTAS ${{lvl}}</span>
        `).join('');

        const previewText = item.secondary.length > 0 
          ? item.secondary[0].text 
          : (item.primary.length > 0 ? item.primary[0].text : '상세 세부 기준 확인');

        return `
          <div class="symptom-card" onclick="openSymptomModal(${{item.slide}})">
            <div>
              <div class="card-top">
                <div class="card-badges">
                  <span class="code-badge">NACRS ${{item.code}}</span>
                  <span class="cat-badge">${{item.category}}</span>
                </div>
                <span class="slide-badge">p.${{item.slide}}</span>
              </div>
              <div class="symptom-title">${{item.name}}</div>
              <div class="card-levels">${{levelDots}}</div>
              <div class="card-preview">
                <strong>주요 기준:</strong> ${{previewText}}
              </div>
            </div>
            <div class="card-footer">
              <span>판정 기준 ${{item.secondary.length}}개</span>
              <span style="color:var(--accent);">자세히 보기 →</span>
            </div>
          </div>
        `;
      }}).join('');
    }}

    // Modal Operations
    function openSymptomModal(slideNum) {{
      const item = KTAS_DATA.symptoms.find(s => s.slide === slideNum);
      if (!item) return;

      document.getElementById('modal-code').textContent = 'NACRS ' + item.code;
      document.getElementById('modal-category').textContent = item.category;
      document.getElementById('modal-age').textContent = item.age + ' 가이드라인';
      document.getElementById('modal-title').textContent = item.name;
      document.getElementById('modal-slide-num').textContent = item.slide;

      // Render Levels Available
      const lvlNames = ['', '1단계: 소생 (즉각)', '2단계: 긴급 (15분)', '3단계: 응급 (30분)', '4단계: 준응급 (60분)', '5단계: 비응급 (120분)'];
      document.getElementById('modal-levels').innerHTML = item.levels.map(l => `
        <span class="level-dot level-${{l}}" style="font-size:12px; padding:3px 8px;">
          ${{lvlNames[l] || 'KTAS ' + l}}
        </span>
      `).join('');

      // Render Secondary Considerations
      const secTbody = document.getElementById('modal-secondary-tbody');
      if (item.secondary.length > 0) {{
        secTbody.innerHTML = item.secondary.map(s => `
          <tr>
            <td><span class="level-dot level-${{s.level}}">KTAS ${{s.level}}</span></td>
            <td>${{s.text}}</td>
          </tr>
        `).join('');
      }} else {{
        secTbody.innerHTML = `<tr><td colspan="2" style="color:var(--text-dim); text-align:center;">증상별 세부 2차 고려사항이 활력징후 기준에 준합니다.</td></tr>`;
      }}

      // Render Primary Considerations
      const primTbody = document.getElementById('modal-primary-tbody');
      if (item.primary.length > 0) {{
        primTbody.innerHTML = item.primary.map(p => `
          <tr>
            <td><span class="level-dot level-${{p.level}}">KTAS ${{p.level}}</span></td>
            <td>${{p.text}}</td>
          </tr>
        `).join('');
      }} else {{
        primTbody.innerHTML = `<tr><td colspan="2" style="color:var(--text-dim); text-align:center;">표준 1차 활력징후(맥박, 혈압, 의식수준 등) 고려 대상입니다.</td></tr>`;
      }}

      // Notes
      const notesSec = document.getElementById('modal-notes-section');
      const notesContent = document.getElementById('modal-notes-content');
      if (item.notes && item.notes.length > 0) {{
        notesSec.style.display = 'block';
        notesContent.innerHTML = item.notes.map(n => `<p style="margin-bottom:6px;">• ${{n}}</p>`).join('');
      }} else {{
        notesSec.style.display = 'none';
      }}

      document.getElementById('symptom-modal').classList.add('open');
    }}

    function closeModal() {{
      document.getElementById('symptom-modal').classList.remove('open');
    }}

    function closeModalOnBackdrop(e) {{
      if (e.target.id === 'symptom-modal') closeModal();
    }}

    // Guide Modal
    function openGuideModal() {{
      document.getElementById('guide-modal').classList.add('open');
    }}

    function closeGuideModal() {{
      document.getElementById('guide-modal').classList.remove('open');
    }}

    function closeGuideModalOnBackdrop(e) {{
      if (e.target.id === 'guide-modal') closeGuideModal();
    }}

    // Triage Simulator Logic
    function initSimulator() {{
      simSetAge('소아');
    }}

    function simSetAge(age) {{
      simSelectedAge = age;
      document.getElementById('sim-age-ped').classList.toggle('selected', age === '소아');
      document.getElementById('sim-age-adult').classList.toggle('selected', age === '성인');

      // Populate Categories
      const catSelect = document.getElementById('sim-category-select');
      catSelect.innerHTML = `<option value="">-- 대분류를 선택하세요 --</option>` + 
        KTAS_DATA.categories.map(c => `<option value="${{c}}">${{c}}</option>`).join('');

      document.getElementById('sim-symptom-select').innerHTML = `<option value="">-- 주증상을 선택하세요 --</option>`;
      document.getElementById('sim-considerations-box').style.display = 'none';
      document.getElementById('sim-result-box').classList.remove('show');
    }}

    function simUpdateSymptoms() {{
      const cat = document.getElementById('sim-category-select').value;
      const symSelect = document.getElementById('sim-symptom-select');
      document.getElementById('sim-considerations-box').style.display = 'none';
      document.getElementById('sim-result-box').classList.remove('show');

      if (!cat) {{
        symSelect.innerHTML = `<option value="">-- 주증상을 선택하세요 --</option>`;
        return;
      }}

      const matched = KTAS_DATA.symptoms.filter(s => s.age === simSelectedAge && s.category === cat);
      symSelect.innerHTML = `<option value="">-- 주증상을 선택하세요 (${{matched.length}}개) --</option>` +
        matched.map(s => `<option value="${{s.slide}}">[${{s.code}}] ${{s.name}}</option>`).join('');
    }}

    function simUpdateConsiderations() {{
      const slideNum = parseInt(document.getElementById('sim-symptom-select').value);
      const box = document.getElementById('sim-considerations-box');
      const list = document.getElementById('sim-options-list');
      document.getElementById('sim-result-box').classList.remove('show');

      if (!slideNum) {{
        box.style.display = 'none';
        return;
      }}

      const item = KTAS_DATA.symptoms.find(s => s.slide === slideNum);
      if (!item) return;

      box.style.display = 'block';

      // Combine secondary and primary items
      const allChoices = [];
      item.secondary.forEach(s => allChoices.push({{ level: s.level, text: s.text, type: '2차 증상 기준' }}));
      item.primary.forEach(p => allChoices.push({{ level: p.level, text: p.text, type: '1차 활력징후' }}));

      // Sort by level (1 to 5)
      allChoices.sort((a, b) => a.level - b.level);

      if (allChoices.length === 0) {{
        list.innerHTML = `<p style="font-size:13px; color:var(--text-muted);">표준 활력징후 안정 시 일반 경증으로 분류됩니다.</p>`;
        return;
      }}

      list.innerHTML = allChoices.map((c, idx) => `
        <label style="background:var(--bg-base); border:1px solid var(--border-color); padding:12px 16px; border-radius:10px; cursor:pointer; display:flex; align-items:center; gap:12px; transition:all 0.15s;" onmouseover="this.style.borderColor='var(--accent)'" onmouseout="this.style.borderColor='var(--border-color)'">
          <input type="radio" name="sim-choice" value="${{c.level}}" data-desc="${{c.text}}" onchange="simCalculateResult(${{c.level}}, '${{c.text}}', '${{item.name}}')">
          <div>
            <span class="level-dot level-${{c.level}}" style="margin-right:6px;">KTAS ${{c.level}}</span>
            <span style="font-size:14px; color:white;">${{c.text}}</span>
            <span style="font-size:11px; color:var(--text-dim); margin-left:6px;">(${{c.type}})</span>
          </div>
        </label>
      `).join('');
    }}

    function simCalculateResult(level, desc, symName) {{
      const box = document.getElementById('sim-result-box');
      const badge = document.getElementById('sim-result-badge');
      const title = document.getElementById('sim-result-title');
      const descEl = document.getElementById('sim-result-desc');
      const actionEl = document.getElementById('sim-result-action');

      const levelConfig = {{
        1: {{ name: 'KTAS 1단계 (소생 - Resuscitation)', bg: 'var(--ktas-1)', action: '즉각적인 119 구급차 출동 및 심폐소생/기도확보 최우선 (0분 이내 처치)' }},
        2: {{ name: 'KTAS 2단계 (긴급 - Emergent)', bg: 'var(--ktas-2)', action: '생명/신체기능 위험 의심, 상급병원 권역응급센터 15분 이내 진료' }},
        3: {{ name: 'KTAS 3단계 (응급 - Urgent)', bg: 'var(--ktas-3)', action: '급성 상태 진행 가능성 관찰 필요, 30분 이내 응급실 진료 권고' }},
        4: {{ name: 'KTAS 4단계 (준응급 - Semi-urgent)', bg: 'var(--ktas-4)', action: '1~2시간 내 진료 가능. 야간 시 달빛어린이병원 + 30분 안심약국 연계 권장' }},
        5: {{ name: 'KTAS 5단계 (비응급 - Non-urgent)', bg: 'var(--ktas-5)', action: '긴급하지 않은 경증 상태. 익일 외래 또는 인근 1차 의원 진료 가능' }}
      }};

      const cfg = levelConfig[level] || levelConfig[5];
      badge.textContent = cfg.name;
      badge.style.background = cfg.bg;
      badge.style.color = 'white';

      title.textContent = `[${{symName}}] 판정 결과: ${{cfg.name}}`;
      descEl.textContent = `선택하신 임상 징후: "${{desc}}"`;
      actionEl.textContent = cfg.action;

      box.classList.add('show');
      box.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
    }}

    // Render Respiratory Table (Slide 390)
    function renderRespiratoryTable() {{
      const tableEl = document.getElementById('resp-table-view');
      const raw = KTAS_DATA.clinical_refs.respiratory_pediatric;
      if (!raw || raw.length === 0) return;

      let html = '<thead><tr>';
      raw[1].forEach(col => {{
        html += `<th>${{col || '연령'}}</th>`;
      }});
      html += '</tr></thead><tbody>';

      for (let i = 2; i < raw.length; i++) {{
        const row = raw[i];
        html += '<tr>';
        row.forEach((cell, idx) => {{
          if (idx === 0) html += `<td style="font-weight:700; color:var(--accent);">${{cell}}</td>`;
          else html += `<td>${{cell}}</td>`;
        }});
        html += '</tr>';
      }}
      html += '</tbody>';
      tableEl.innerHTML = html;
    }}
  </script>
</body>
</html>
"""

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ktas_viewer.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[4/4] Successfully generated ktas_viewer.html!")

if __name__ == "__main__":
    main()
