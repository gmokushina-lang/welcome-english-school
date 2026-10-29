"""Build the editor's text catalogue without loading a preview iframe."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent / 'dist' / 'v2'
source = (ROOT / 'index.html').read_text(encoding='utf-8')
translations = json.loads(re.search(r'const translations=(\{.*?\});const records=\[\]', source, re.S).group(1))

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.texts = []

    def handle_starttag(self, tag, attrs):
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.stack.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if data.strip():
            self.texts.append((data, tuple(self.stack)))

def classes(ancestors, name):
    return any(name in (attrs.get('class') or '').split() for _, attrs in ancestors)

def tags(ancestors, names):
    return any(tag in names for tag, _ in ancestors)

parser = Parser()
parser.feed(source)
records = []
included = set()
for i, (text, ancestors) in enumerate(parser.texts):
    translated = text.strip() in translations and not tags(ancestors, {'script', 'style'}) and not any(tag == 'blockquote' and attrs.get('lang') == 'en' for tag, attrs in ancestors)
    root = tags(ancestors, {'section', 'header'}) or classes(ancestors, 'hero-content')
    excluded = tags(ancestors, {'dialog', 'footer'}) or classes(ancestors, 'version') or classes(ancestors, 'review-controls')
    if translated and root and not excluded:
        records.append((text, text.replace(text.strip(), translations[text.strip()], 1), ancestors))
        included.add(i)
for i, (text, ancestors) in enumerate(parser.texts):
    root = tags(ancestors, {'section'}) or classes(ancestors, 'hero-content')
    excluded = tags(ancestors, {'script', 'style', 'dialog'}) or classes(ancestors, 'review-controls')
    if i not in included and root and not excluded and re.search('[a-zA-Zа-яА-Я]', text):
        records.append((text, text, ancestors))

counts = {}
schema = []
for ru, en, ancestors in records:
    value = 2166136261
    for char in ru.strip():
        code = ord(char)
        if code > 0xffff:
            code = 0xd800 + ((code - 0x10000) >> 10)
        value = ((value ^ code) * 16777619) & 0xffffffff
    base = 't' + format(value, 'x')
    counts[base] = counts.get(base, 0) + 1
    section = next((attrs.get('id', '') for tag, attrs in reversed(ancestors) if tag == 'section'), '') or 'header'
    schema.append(dict(id=f'{base}_{counts[base]}', section=section, ru=ru.strip(), en=en.strip()))
(ROOT / 'content-schema.json').write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Built {len(schema)} editable text fields')
