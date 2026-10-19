from html.parser import HTMLParser

class Validator(HTMLParser):
    pass

try:
    with open('frontend/templates/emergency_guide_symptoms.html', 'r', encoding='utf-8') as f:
        content = f.read()
    v = Validator()
    v.feed(content)
    print("VALIDATION SUCCESS: HTML Parser parsed the whole file without exceptions!")
    print(f"File size: {len(content)} characters, {len(content.splitlines())} lines")
except Exception as e:
    print(f"VALIDATION ERROR: {e}")
