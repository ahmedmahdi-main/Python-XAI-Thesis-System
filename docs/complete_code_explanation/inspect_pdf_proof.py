import fitz
from pathlib import Path
p=Path('docs/complete_code_explanation/ARABIC_TECHNICAL_BOOK_PROOF.pdf')
d=fitz.open(p)
print('pages',len(d))
for i in [0,len(d)//2,len(d)-1]:
 d[i].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(str(p.parent/f'proof_page_{i+1:04}.png'))
 print('page',i+1,'text_chars',len(d[i].get_text()))
