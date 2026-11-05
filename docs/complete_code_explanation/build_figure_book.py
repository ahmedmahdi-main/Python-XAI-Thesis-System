from pathlib import Path
import base64, hashlib, html, json, os, re, sys
from urllib.parse import urlsplit, urlunsplit, quote
from xml.etree import ElementTree
from markdown_it import MarkdownIt
from markdown_it.token import Token
base=Path(__file__).resolve().parent
names=['01_SYSTEM_OVERVIEW_AR.md','02_PROJECT_ARCHITECTURE_AR.md','03_DATA_PIPELINE_AR.md','04_MACHINE_LEARNING_MODELS_AR.md','05_LSTM_DEEP_EXPLANATION_AR.md','06_SHAP_LIME_EXPLANATION_AR.md','07_EVALUATION_AND_RESULTS_AR.md','08_STREAMLIT_DASHBOARD_AR.md','09_TESTS_AND_DEPLOYMENT_AR.md','10_SCIENTIFIC_LIMITATIONS_AR.md','11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md','12_CODE_INDEX_AR.md','SCIENTIFIC_REVIEW_AR.md','COVERAGE_AR.md']
chapters=[base/n for n in names]; pages=sorted((base/'line_by_line').glob('*.md'))
architecture=chapters[1].read_text(encoding='utf-8-sig')
titles=re.findall(r'^##\s+(\d+)\.\s+(.+)$',architecture,re.M)
blocks=re.findall(r'```mermaid\s*\n(.*?)\n```',architecture,re.S)
assert len(titles)==len(blocks)==10
inventory=[]
for i,((number,title),block) in enumerate(zip(titles,blocks),1):
 assert int(number)==i
 folder=base/'mermaid_rendered'; source=folder/f'diagram_{i:02}.mmd'; image=folder/f'diagram_{i:02}.svg'
 assert source.read_text(encoding='utf8').strip()==block.strip(),f'stale diagram source {i}'
 raw=image.read_bytes(); root=ElementTree.fromstring(raw); assert root.tag.endswith('svg') and root.attrib.get('viewBox')
 inventory.append({'number':i,'title':title,'caption':f'الشكل ({i}): {title}','source_markdown':'02_PROJECT_ARCHITECTURE_AR.md','mermaid_source':source.relative_to(base).as_posix(),'svg':image.relative_to(base).as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'data':base64.b64encode(raw).decode('ascii')})
md=MarkdownIt('commonmark',{'html':False}).enable('table')
iso_date=re.compile(r'(?<![\w\d])\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})?)?(?![\w\d])')
def isolate_inline(children):
 result=[]
 for child in children:
  if child.type=='text':
   pos=0
   for match in iso_date.finditer(child.content):
    if match.start()>pos:
     t=Token('text','',0);t.content=child.content[pos:match.start()];result.append(t)
    t=Token('html_inline','',0);t.content='<bdi dir="ltr">'+html.escape(match.group())+'</bdi>';result.append(t);pos=match.end()
   if pos:
    if pos<len(child.content):
     t=Token('text','',0);t.content=child.content[pos:];result.append(t)
    continue
  path_prefixes=('src/','artifacts/','data/','docs/','scripts/','configs/','dashboard/','.demo_venv/','../')
  is_path=child.content.startswith(path_prefixes) or bool(re.fullmatch(r'(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.(?:py|json|csv|npz|md|yaml|yml|html|pdf)(?::\d+)?',child.content))
  if child.type=='code_inline' and is_path and '\n' not in child.content:
   # WBR adds a line-break opportunity after each separator without changing text.
   t=Token('html_inline','',0);t.content='<code class="inline-path" dir="ltr">'+html.escape(child.content).replace('/','/<wbr>')+'</code>';result.append(t);continue
  result.append(child)
 return result
def render(page):
 tokens=md.parse(page.read_text(encoding='utf-8-sig')); figure_count=0
 for token in tokens:
  if token.type=='fence' and token.info.strip().split(' ')[0]=='mermaid':
   figure_count+=1
   if page.name=='02_PROJECT_ARCHITECTURE_AR.md':
    figure=inventory[figure_count-1]; assert token.content.strip()==blocks[figure_count-1].strip()
    title=html.escape(figure['title']); caption=html.escape(figure['caption']); n=figure['number']
    token.type='html_block'; token.tag=''; token.content=f'<figure class="architecture-figure" id="figure-{n:02}"><img src="data:image/svg+xml;base64,{figure["data"]}" alt="{title}"><figcaption>{caption} <span dir="ltr">[FIG-{n:02}]</span></figcaption></figure>\n'
   else:
    assert page.name in {'01_SYSTEM_OVERVIEW_AR.md','05_LSTM_DEEP_EXPLANATION_AR.md'},page
    n=1 if page.name.startswith('01_') else 5
    token.type='html_block';token.tag='';token.content=f'<p>انظر <a href="#figure-{n:02}">الشكل ({n}) في فصل المعمارية</a>.</p>\n'
  if token.children:
   token.children=isolate_inline(token.children)
  for child in token.children or []:
   if child.type=='link_open':
    href=child.attrGet('href') or ''; part=urlsplit(href)
    if part.path and not part.scheme and not part.netloc:
     dest=(page.parent/part.path).resolve();rel=os.path.relpath(dest,base).replace('\\','/')
     child.attrSet('href',urlunsplit(('', '', quote(rel,safe='/'),part.query,part.fragment)))
 if page.name=='02_PROJECT_ARCHITECTURE_AR.md': assert figure_count==10
 rendered=md.renderer.render(tokens,md.options,{})
 if page.name=='12_CODE_INDEX_AR.md':
  # Use a full-width path for each source instead of five competing table columns.
  table=re.search(r'<table>\s*<thead>.*?</thead>\s*<tbody>(.*?)</tbody>\s*</table>',rendered,re.S)
  assert table, 'source index table missing'
  records=re.findall(r'<tr>(.*?)</tr>',table.group(1),re.S)
  cards=[]
  for record in records:
   cells=re.findall(r'<td(?:\s+[^>]*)?>(.*?)</td>',record,re.S)
   assert len(cells)==5, 'unexpected index columns'
   path,physical,executable,symbols,imports=cells
   # Markdown interprets the underscores in the Python name as emphasis.
   symbols=symbols.replace('<strong>init</strong>','__init__')
   cards.append('<article class="index-card"><div class="index-path" dir="ltr">'+path+'</div><p>الأسطر الفعلية: '+physical+'؛ التنفيذية التقريبية: '+executable+'</p><p>الأصناف والدوال (الاسم:السطر): <span dir="ltr">'+symbols+'</span></p><p>الواردات: <span dir="ltr">'+imports+'</span></p></article>')
  assert len(cards)==77, 'unexpected source index record count'
  rendered=rendered[:table.start()]+'\n'.join(cards)+rendered[table.end():]
 return re.sub(r'(<h[1-6]>الأسطر )([0-9]+–[0-9]+)(</h[1-6]>)', r'\1<bdi dir="ltr">\2</bdi>\3', rendered)
css=' @page{size:A4;margin:18mm 16mm;@bottom-center{content:counter(page)}} body{font-family:"Segoe UI",Tahoma,Arial,sans-serif;color:#172331;line-height:1.8;max-width:1050px;margin:auto}h1,h2,h3{color:#174564;line-height:1.35;break-after:avoid}.cover{min-height:80vh;display:flex;flex-direction:column;justify-content:center;text-align:center;break-after:page}.warning{border:2px solid #a44;padding:1em;background:#fff4ef}.chapter{break-before:page}pre{direction:ltr;text-align:left;white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f7;padding:.6em;border:1px solid #ddd;font:9pt Consolas,monospace;unicode-bidi:embed}code{direction:ltr;unicode-bidi:isolate;font-family:Consolas,monospace;overflow-wrap:anywhere;word-break:break-word}table{border-collapse:collapse;width:100%;font-size:9pt}th,td{border:1px solid #aaa;padding:.25em;vertical-align:top;overflow-wrap:anywhere}tr{break-inside:avoid}a{color:#124f7b}.source{direction:ltr;text-align:left;font-size:9pt;overflow-wrap:anywhere}.architecture-figure{break-inside:avoid;page-break-inside:avoid;text-align:center;margin:12mm auto;max-width:100%}.architecture-figure img{display:block;max-width:100%;max-height:170mm;width:auto;height:auto;margin:auto;object-fit:contain}.architecture-figure figcaption{margin-top:4mm;font-weight:bold;direction:rtl;break-inside:avoid}@media print{body{max-width:none}a{color:inherit;text-decoration:none}pre{font-size:8pt}}'
css += '#chapter-11 table{table-layout:fixed}#chapter-11 th:nth-child(1),#chapter-11 td:nth-child(1){width:23%}#chapter-11 th:nth-child(2),#chapter-11 td:nth-child(2),#chapter-11 th:nth-child(3),#chapter-11 td:nth-child(3){width:8%}#chapter-11 th:nth-child(4),#chapter-11 td:nth-child(4){width:31%}#chapter-11 th:nth-child(5),#chapter-11 td:nth-child(5){width:30%}'
css += '.index-card{border:1px solid #aaa;padding:3mm;margin:3mm 0;break-inside:avoid;font-size:9pt}.index-card p{margin:1mm 0}.index-path{direction:ltr;text-align:left;font-family:Consolas,monospace;font-size:9pt;overflow-wrap:normal;word-break:normal}.index-path code{overflow-wrap:normal;word-break:normal}'
css += 'bdi,.inline-path{unicode-bidi:isolate}.inline-path{direction:ltr;word-break:normal;overflow-wrap:anywhere}'
if len(sys.argv)==3 and sys.argv[1]=='--proof':
 proof=base/Path(sys.argv[2]).name
 if proof.exists(): raise SystemExit('Refusing to overwrite proof')
 proof.write_text('<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><style>'+css+'</style></head><body>'+render(base/'06_SHAP_LIME_EXPLANATION_AR.md')+'</body></html>',encoding='utf8')
 print('focused proof',proof.name);sys.exit(0)
parts=['<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>دليل نظام التنبؤ المالي المفسر</title><style>'+css+'</style></head><body><section class="cover"><h1>نظام التنبؤ المالي القابل للتفسير</h1><h2>دليل دراسة تقني لرسالة الماجستير</h2><p>محمد صالح — Python XAI Thesis System</p><div class="warning"><strong>نسخة مراجعة؛ الاعتماد العلمي والتحريري لم يكتمل.</strong><br>تُعرض مخططات المعمارية كصور مدمجة؛ تخضع الصفحات والأسئلة والمراجع للمراجعة العلمية والمرئية.</div></section><nav><h1>فهرس المحتويات</h1><ol>']
for i,page in enumerate(chapters):
 title=next((s[2:].strip() for s in page.read_text(encoding='utf-8-sig').splitlines() if s.startswith('# ')),page.stem)
 parts.append(f'<li><a href="#chapter-{i}">{html.escape(title)}</a></li>')
parts.append('<li><a href="#code-appendix">ملحق الشروح السطرية</a></li></ol></nav>')
for i,page in enumerate(chapters): parts.append(f'<section class="chapter" id="chapter-{i}"><p class="source">{html.escape(page.name)}</p>{render(page)}</section>')
parts.append('<section class="chapter" id="code-appendix"><h1>ملحق الشروح السطرية</h1><p>كل قسم يحتفظ بمسار المصدر وبصمته وأرقام الأسطر الموثقة؛ يعتمد اكتمال المعنى على المراجعة العلمية المنفصلة.</p></section>')
for i,page in enumerate(pages): parts.append(f'<section class="chapter" id="source-{i}">{render(page)}</section>')
parts.append('</body></html>'); doc='\n'.join(parts)
assert doc.count('<figure class="architecture-figure"')==10 and 'language-mermaid' not in doc
assert not re.search(r'(?m)^\s*(?:flowchart\s+(?:TD|LR)|graph\s+TD|sequenceDiagram)\s*$',doc)
if len(sys.argv)!=2 or Path(sys.argv[1]).name != sys.argv[1]:
 raise SystemExit('Supply one new HTML filename in the documentation directory; existing snapshots are preserved.')
out=base/sys.argv[1]
if out.exists():
 raise SystemExit(f'Refusing to overwrite existing book snapshot: {out.name}')
out.write_text(doc,encoding='utf8')
for row in inventory: del row['data']
print('HTML',out.name,'figures',len(inventory),'sections',len(pages),'bytes',out.stat().st_size)
