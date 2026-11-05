from pathlib import Path
from html.parser import HTMLParser
import base64
import hashlib
import json
import re
import sys
from urllib.parse import urlsplit
import pymupdf
sys.path.append(str(Path(__file__).resolve().parents[2] / '.demo_venv/Lib/site-packages'))
from markdown_it import MarkdownIt

base = Path(__file__).resolve().parent
html_path = base / 'ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.html'
pdf_path = base / 'ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.pdf'
document = html_path.read_text(encoding='utf8')
pdf = pymupdf.open(pdf_path)

class Collector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.fragments = []
        self.blocks = []
        self.in_pre = False
        self.current = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'a' and attrs.get('href', '').startswith('#'):
            self.fragments.append(attrs['href'][1:])
        if tag == 'pre':
            self.in_pre = True
            self.current = []
    def handle_endtag(self, tag):
        if tag == 'pre':
            self.blocks.append(''.join(self.current))
            self.in_pre = False
    def handle_data(self, data):
        if self.in_pre:
            self.current.append(data)

collector = Collector()
collector.feed(document)
chapters = [base / n for n in ['01_SYSTEM_OVERVIEW_AR.md','02_PROJECT_ARCHITECTURE_AR.md','03_DATA_PIPELINE_AR.md','04_MACHINE_LEARNING_MODELS_AR.md','05_LSTM_DEEP_EXPLANATION_AR.md','06_SHAP_LIME_EXPLANATION_AR.md','07_EVALUATION_AND_RESULTS_AR.md','08_STREAMLIT_DASHBOARD_AR.md','09_TESTS_AND_DEPLOYMENT_AR.md','10_SCIENTIFIC_LIMITATIONS_AR.md','11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md','12_CODE_INDEX_AR.md','SCIENTIFIC_REVIEW_AR.md','COVERAGE_AR.md']]
pages = sorted((base / 'line_by_line').glob('*.md'))
parser = MarkdownIt('commonmark', {'html': False}).enable('table')
fences = []
for page in chapters + pages:
    for token in parser.parse(page.read_text(encoding='utf-8-sig')):
        if token.type == 'fence' and token.info.strip().split(' ')[0] != 'mermaid':
            fences.append(token.content)
assert collector.blocks == fences, f'Code block mismatch: HTML {len(collector.blocks)}, source {len(fences)}'
inventory = json.loads((base / 'diagram_inventory.json').read_text(encoding='utf8'))
images = re.findall(r'data:image/svg\+xml;base64,([^\"]+)', document)
assert len(images) == len(inventory) == 10
assert all(hashlib.sha256(base64.b64decode(image)).hexdigest() == row['sha256'] for image, row in zip(images, inventory))
assert 'language-mermaid' not in document
missing_fragments = sorted(set(collector.fragments) - collector.ids)
assert not missing_fragments, missing_fragments
names = pdf.resolve_names()
missing_chapters = [f'chapter-{i}' for i in range(14) if f'chapter-{i}' not in names]
assert not missing_chapters, missing_chapters
figures = {str(i): [j + 1 for j, page in enumerate(pdf) if f'[FIG-{i:02}]' in page.get_text()] for i in range(1, 11)}
assert all(len(where) == 1 for where in figures.values()), figures
visual_samples = {1, 2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 19, 21, 65, 170, 284}
rows = []
for index, page in enumerate(pdf):
    words = page.get_text('words')
    footer = [word[4] for word in words if word[1] > page.rect.height - 40 and word[4].strip().isdigit()]
    outside = [word[4] for word in words if word[0] < -.5 or word[1] < -.5 or word[2] > page.rect.width + .5 or word[3] > page.rect.height + .5]
    rows.append({'page': index + 1, 'words': len(words), 'footer_ok': str(index + 1) in footer, 'outside_words': outside, 'visual_status': 'SAMPLED' if index + 1 in visual_samples else 'NOT_INSPECTED'})
summary = {'pdf': pdf_path.name, 'pdf_sha256': hashlib.sha256(pdf_path.read_bytes()).hexdigest(), 'html': html_path.name, 'html_sha256': hashlib.sha256(html_path.read_bytes()).hexdigest(), 'pages': len(pdf), 'figures': figures, 'svg_hashes_match': 10, 'code_fences_match': len(fences), 'missing_fragments': missing_fragments, 'missing_chapters': missing_chapters, 'footer_missing': [r['page'] for r in rows if not r['footer_ok']], 'outside_word_pages': [r['page'] for r in rows if r['outside_words']], 'under_60_words': [r['page'] for r in rows if r['words'] < 60], 'limitations': 'Automated checks do not verify semantic links, image clipping, Arabic shaping, visual reading order or page-level appearance.'}
(base / 'scientific_review_v3_page_audit.json').write_text(json.dumps({'summary': summary, 'pages': rows}, ensure_ascii=False, indent=2), encoding='utf8')
lines = ['# تدقيق آلي لنسخة المراجعة العلمية V3', '', f"الملف `{summary['pdf']}`، بصمة SHA-256 `{summary['pdf_sha256']}`، عدد الصفحات {len(pdf)}.", '', f"- طابقت بصمات SVG العشرة؛ علامات الأشكال في الصفحات {figures}.", f"- طابقت {len(fences)} كتلة شيفرة نصوص Markdown؛ لا يعني ذلك مراجعة كل اقتباس أو فحص شكلها بصرياً.", f"- أهداف روابط HTML الداخلية ووجهات فصول PDF الأربعة عشر موجودة. أرقام التذييل الغائبة: {summary['footer_missing']}; مربعات الكلمات خارج الصفحة: {summary['outside_word_pages']}.", f"- مرشحات أقل من 60 كلمة: {summary['under_60_words']}. تحتاج معاينة فردية؛ الرسوم قد تفسر قلة النص.", '', 'هذه فحوص بنيوية لا تثبت تشكيل العربية أو عدم القص داخل الصفحة أو المعنى العلمي. عُوينت 16 صفحة من V3 على نحو مستقل كما في [السجل المرئي](PAGE_VISUAL_SCIENTIFIC_REVIEW_V3_AR.md)؛ لا تُنقل نتائج V2 إلى V3.', '', '| الصفحة | كلمات مستخرجة | رقم التذييل | مربعات خارج الصفحة | مراجعة بصرية |', '|---:|---:|---|---:|---|']
for row in rows:
    lines.append(f"| {row['page']} | {row['words']} | {'موجود' if row['footer_ok'] else 'غير متحقق'} | {len(row['outside_words'])} | {'معاينة عينة' if row['visual_status'] == 'SAMPLED' else 'لم تفحص فردياً'} |")
(base / 'PAGE_QUALITY_SCIENTIFIC_REVIEW_V3_AR.md').write_text('\n'.join(lines) + '\n', encoding='utf8')
print(json.dumps(summary, ensure_ascii=False))
