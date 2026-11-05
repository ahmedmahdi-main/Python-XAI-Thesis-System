from pathlib import Path
import pymupdf
base=Path('docs/complete_code_explanation');d=pymupdf.open(base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf'); out=base/'figure_pdf_inspection_v5'
for label,needle in [('lstm','tanh'),('metrics','mean(|'),('lime','502.862')]:
 hits=[i for i,p in enumerate(d) if needle in p.get_text()];assert hits,(label,needle)
 i=hits[0];d[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(str(out/(label+'_page.png')));print(label,i+1)

