from pathlib import Path
import pymupdf,re,json,hashlib
base=Path('docs/complete_code_explanation'); pdf=base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V4.pdf';html=base/'ARABIC_TECHNICAL_BOOK_FIGURES.html';d=pymupdf.open(pdf); data=html.read_text(encoding='utf8'); text='\n'.join(p.get_text() for p in d)
for needle in ['flowchart TD','flowchart LR','graph TD','sequenceDiagram']:
 print(repr(needle),'PDF occurrences',text.count(needle),'HTML occurrences',data.count(needle))
print('HTML embedded SVG',data.count('data:image/svg+xml;base64,'),'Mermaid code class',data.count('language-mermaid'))
links=d[1].get_links();print('ToC pdf links',len(links),'internal',sum(x.get('kind')==pymupdf.LINK_GOTO for x in links))
print('hash HTML',hashlib.sha256(html.read_bytes()).hexdigest());print('hash PDF',hashlib.sha256(pdf.read_bytes()).hexdigest());print('pages',len(d))
