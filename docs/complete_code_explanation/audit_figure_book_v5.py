from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import base64,hashlib,json,re
import pymupdf
base=Path(__file__).resolve().parent;htmlpath=base/'ARABIC_TECHNICAL_BOOK_FIGURES.html';pdfpath=base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf';rows=json.loads((base/'diagram_inventory.json').read_text(encoding='utf8'))
class Inspect(HTMLParser):
 def __init__(self): super().__init__();self.ids=set();self.anchors=[];self.images=[];self.figures=0;self.rtl=False
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.add(a['id'])
  if t=='html':self.rtl=a.get('dir')=='rtl' and a.get('lang')=='ar'
  if t=='a' and a.get('href','').startswith('#'):self.anchors.append(a['href'][1:])
  if t=='img':self.images.append(a.get('src',''))
  if t=='figure' and a.get('class')=='architecture-figure':self.figures+=1
h=htmlpath.read_text(encoding='utf8');x=Inspect();x.feed(h)
assert x.rtl and x.figures==10 and len(x.images)==10 and len(rows)==10
assert not (set(x.anchors)-x.ids),set(x.anchors)-x.ids
for i,(src,row) in enumerate(zip(x.images,rows),1):
 assert src.startswith('data:image/svg+xml;base64,')
 svg=base64.b64decode(src.split(',',1)[1],validate=True)
 assert hashlib.sha256(svg).hexdigest()==row['sha256']==hashlib.sha256((base/row['svg']).read_bytes()).hexdigest()
 assert row['number']==i
for needle in ['flowchart TD','flowchart LR','graph TD','sequenceDiagram','language-mermaid']:
 assert needle not in h,needle
d=pymupdf.open(pdfpath);text='\n'.join(p.get_text() for p in d)
for needle in ['flowchart TD','flowchart LR','graph TD','sequenceDiagram']:assert needle not in text,needle
for row in rows:
 marker=f'FIG-{row["number"]:02}';hits=[i+1 for i,p in enumerate(d) if p.search_for(marker)]
 assert hits==[row['pdf_page']],(marker,hits,row['pdf_page'])
toclinks=d[1].get_links();chapterlinks=[l for l in toclinks if l.get('nameddest','').startswith('chapter-')]
assert {l['nameddest'] for l in chapterlinks}=={f'chapter-{i}' for i in range(14)} and all(0<=l['page']<len(d) for l in chapterlinks)
print('HTML: 10 embedded SVG match hashes; local fragment targets exist; no raw Mermaid patterns')
print('PDF: 10 unique figure markers match inventory pages; 14 named chapter destinations resolve; pages',len(d))
print('Visual page inspection remains a human review; scientific completeness is separate.')

