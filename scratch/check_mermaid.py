with open('README.md', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'```mermaid\n(.*?)```', text, re.DOTALL)
with open('scratch/mermaid_out.txt', 'w', encoding='utf-8') as out:
    out.write(f"Total mermaid diagrams: {len(matches)}\n")
    for i, m in enumerate(matches):
        out.write(f"\n==================== MERMAID {i+1} ====================\n")
        out.write(m)
