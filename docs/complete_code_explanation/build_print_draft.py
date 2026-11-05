from pathlib import Path
import html, os
from urllib.parse import urlsplit, urlunsplit, quote
from markdown_it import MarkdownIt
base=Path(__file__).resolve().parent
names=['01_SYSTEM_OVERVIEW_AR.md','02_PROJECT_ARCHITECTURE_AR.md','03_DATA_PIPELINE_AR.md','04_MACHINE_LEARNING_MODELS_AR.md','05_LSTM_DEEP_EXPLANATION_AR.md','06_SHAP_LIME_EXPLANATION_AR.md','07_EVALUATION_AND_RESULTS_AR.md','08_STREAMLIT_DASHBOARD_AR.md','09_TESTS_AND_DEPLOYMENT_AR.md','10_SCIENTIFIC_LIMITATIONS_AR.md','11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md','12_CODE_INDEX_AR.md','SCIENTIFIC_REVIEW_AR.md','COVERAGE_AR.md']
chapters=[base/n for n in names]; pages=sorted((base/'line_by_line').glob('*.md')); assert all(p.is_file() for p in chapters)
md=MarkdownIt('commonmark',{'html':False}).enable('table')
def render(page):
 tokens=md.parse(page.read_text(encoding='utf-8-sig'))
 for token in tokens:
  for child in token.children or []:
   if child.type=='link_open':
    href=child.attrGet('href') or ''; part=urlsplit(href)
    if part.path and not part.scheme and not part.netloc:
     dest=(page.parent/part.path).resolve(); rel=os.path.relpath(dest,base).replace('\\','/')
     child.attrSet('href',urlunsplit(('', '', quote(rel,safe='/'),part.query,part.fragment)))
 return md.renderer.render(tokens,md.options,{})
css=' @page{size:A4;margin:18mm 16mm;@bottom-center{content:counter(page)}} body{font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:#172331;line-height:1.8;max-width:1050px;margin:auto} h1,h2,h3{color:#174564;line-height:1.35;break-after:avoid} .cover{min-height:80vh;display:flex;flex-direction:column;justify-content:center;text-align:center;break-after:page}.warning{border:2px solid #a44;padding:1em;background:#fff4ef}.chapter{break-before:page} pre{direction:ltr;text-align:left;white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f7;padding:.6em;border:1px solid #ddd;font:9pt Consolas,monospace;unicode-bidi:embed}code{direction:ltr;unicode-bidi:isolate;font-family:Consolas,monospace}table{border-collapse:collapse;width:100%;font-size:9pt}th,td{border:1px solid #aaa;padding:.25em;vertical-align:top;overflow-wrap:anywhere}tr{break-inside:avoid}a{color:#124f7b}.source{direction:ltr;text-align:left;font-size:9pt;overflow-wrap:anywhere}@media print{body{max-width:none}a{color:inherit;text-decoration:none}pre{font-size:8pt}}'
parts=['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>دليل نظام التنبؤ المالي المفسر</title><style>'+css+'</style></head><body><section class="cover"><h1>نظام التنبؤ المالي القابل للتفسير</h1><h2>دليل دراسة تقني لرسالة الماجستير</h2><p>محمد صالح — Python XAI Thesis System</p><div class="warning"><strong>مسودة مراجعة وليست نسخة تسليم نهائية.</strong><br>لم تُستكمل المراجعة العلمية لجميع الادعاءات، ولم تُفحص مخططات Mermaid بمحلل؛ تظهر المخططات كنصوص مصدرية. لم تُفحص الطباعة أو أرقام الصفحات بصرياً.</div></section><nav><h1>فهرس المحتويات</h1><ol>']
for i,page in enumerate(chapters):
 title=next((s[2:].strip() for s in page.read_text(encoding='utf-8-sig').splitlines() if s.startswith('# ')),page.stem)
 parts.append(f'<li><a href="#chapter-{i}">{html.escape(title)}</a></li>')
parts.append('<li><a href="#code-appendix">ملحق الشروح السطرية</a></li></ol></nav>')
for i,page in enumerate(chapters): parts.append(f'<section class="chapter" id="chapter-{i}"><p class="source">{html.escape(page.name)}</p>{render(page)}</section>')
parts.append('<section class="chapter" id="code-appendix"><h1>ملحق الشروح السطرية</h1><p>كل قسم يحتفظ بمسار المصدر وبصمته وأرقام الأسطر الموثقة؛ يعتمد اكتمال المعنى على المراجعة العلمية المنفصلة.</p></section>')
for i,page in enumerate(pages): parts.append(f'<section class="chapter" id="source-{i}">{render(page)}</section>')
parts.append('</body></html>'); out=base/'ARABIC_TECHNICAL_BOOK_DRAFT.html'; out.write_text('\n'.join(parts),encoding='utf8')
print('draft:',out,'chapters:',len(chapters),'source pages:',len(pages),'bytes:',out.stat().st_size)
