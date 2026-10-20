import re

with open('frontend/templates/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

scripts = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', text)
print('Scripts in index.html:')
for s in scripts:
    print(' -', s)

with open('frontend/templates/hospital_detail.html', 'r', encoding='utf-8') as f:
    text_h = f.read()

scripts_h = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', text_h)
print('\nScripts in hospital_detail.html:')
for s in scripts_h:
    print(' -', s)

with open('frontend/templates/pharmacy_detail.html', 'r', encoding='utf-8') as f:
    text_p = f.read()

scripts_p = re.findall(r'<script[^>]*src=[\'"]([^\'"]+)[\'"]', text_p)
print('\nScripts in pharmacy_detail.html:')
for s in scripts_p:
    print(' -', s)
