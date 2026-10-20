import pptx

prs = pptx.Presentation('아이숨(ISOOM) 중간프로젝트 발표.pptx')

with open('scratch/pptx_dump.txt', 'w', encoding='utf-8') as out:
    out.write(f"Slide count: {len(prs.slides)}\n")
    out.write(f"Slide dimensions: {prs.slide_width} x {prs.slide_height} (EMU)\n\n")

    for idx, slide in enumerate(prs.slides):
        out.write(f"\n==================== SLIDE {idx+1} ====================\n")
        for s_idx, shape in enumerate(slide.shapes):
            shape_type = shape.shape_type
            name = shape.name
            left_pt = shape.left / 914400.0 * 2.54 if shape.left else 0 # cm
            top_pt = shape.top / 914400.0 * 2.54 if shape.top else 0
            w_pt = shape.width / 914400.0 * 2.54 if shape.width else 0
            h_pt = shape.height / 914400.0 * 2.54 if shape.height else 0

            out.write(f"--- Shape {s_idx} ({name}, type={shape_type}): pos=({left_pt:.2f}cm, {top_pt:.2f}cm), size=({w_pt:.2f}cm x {h_pt:.2f}cm) ---\n")
            if shape.has_text_frame:
                for p_idx, paragraph in enumerate(shape.text_frame.paragraphs):
                    text = paragraph.text.strip()
                    if text:
                        font_size = paragraph.font.size.pt if paragraph.font.size else "inherit"
                        font_bold = paragraph.font.bold
                        out.write(f"  [P{p_idx}] (size={font_size}, bold={font_bold}): {text}\n")
            elif shape.has_table:
                out.write(f"  [TABLE] rows={len(shape.table.rows)}, cols={len(shape.table.columns)}\n")
                for r in shape.table.rows:
                    row_vals = [cell.text.strip().replace('\n', ' ') for cell in r.cells]
                    out.write(f"    {' | '.join(row_vals)}\n")
