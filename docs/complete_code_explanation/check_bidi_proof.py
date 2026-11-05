from html.parser import HTMLParser
from pathlib import Path
import re
import sys

base = Path(__file__).resolve().parent
source = (base / '06_SHAP_LIME_EXPLANATION_AR.md').read_text(encoding='utf8')
proof = (base / (sys.argv[1] if len(sys.argv) > 1 else 'BIDI_FOCUSED_PROOF.html')).read_text(encoding='utf8')

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = False
    def handle_starttag(self, tag, attrs):
        if tag in ('style', 'script'):
            self.hidden = True
    def handle_endtag(self, tag):
        if tag in ('style', 'script'):
            self.hidden = False
    def handle_data(self, value):
        if not self.hidden:
            self.parts.append(value)

extractor = TextExtractor()
extractor.feed(proof)
plain = ''.join(extractor.parts)
dates = set(re.findall(r'(?<!\d)\d{4}-\d{2}-\d{2}(?!\d)', source))
paths = [value for value in re.findall(r'`([^`\n]+)`', source) if '/' in value]
missing_dates = [value for value in dates if value not in plain]
missing_paths = [value for value in paths if value not in plain]
assert not missing_dates, missing_dates
assert not missing_paths, missing_paths
assert '<bdi dir="ltr">2024-11-29</bdi>' in proof
assert 'explanations/<wbr>quality.json' in proof
print(f'dates preserved {len(dates)}; inline paths preserved {len(paths)}; sample isolation and separator break present')
print('This focused check does not establish correct rendering of all chapters, dates, numerical expressions or code blocks.')
