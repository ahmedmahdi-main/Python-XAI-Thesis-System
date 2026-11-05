import pymupdf
from pathlib import Path
base=Path('docs/complete_code_explanation'); d=pymupdf.open(base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V3.pdf')
for needle in ['tanh','502.862','mean(|','squeeze(-1)']:
 hits=[i for i,p in enumerate(d) if needle in p.get_text()]
 print(needle,[i+1 for i in hits[:8]])
 if hits:
  i=hits[0];d[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(str(base/'figure_pdf_inspection_v3'/('equation_'+str(i+1)+'.png')))
