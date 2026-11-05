from pathlib import Path
import json,re
import pymupdf
base=Path(__file__).resolve().parent; pdf=base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf'; d=pymupdf.open(pdf); out=base/'figure_pdf_inspection_v5';out.mkdir(exist_ok=True)
items=json.loads((base/'diagram_inventory.json').read_text(encoding='utf8'))
for row in items:
 marker=f'FIG-{row["number"]:02}'; matches=[(i,p.search_for(marker)) for i,p in enumerate(d) if p.search_for(marker)]
 print(marker,'matches',[(i+1,len(r)) for i,r in matches])
 assert len(matches)==1 and len(matches[0][1])==1
 i,rects=matches[0]; row['pdf_page']=i+1
 d[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(str(out/f'figure_{row["number"]:02}_page.png'))
for name,i in [('cover',0),('contents',1),('middle',len(d)//2),('end',len(d)-1)]:
 d[i].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3),alpha=False).save(str(out/f'{name}_page.png'));print(name,i+1)
(base/'diagram_inventory.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
print('total_pages',len(d))




