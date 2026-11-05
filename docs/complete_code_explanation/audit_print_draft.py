import pathlib,re
from html.parser import HTMLParser
base=pathlib.Path(__file__).resolve().parent; p=base/'ARABIC_TECHNICAL_BOOK_DRAFT.html'
class Audit(HTMLParser):
 def __init__(self): super().__init__(); self.html_rtl=False; self.sections=[]; self.pre=0; self.mermaid=0; self.missing=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='html': self.html_rtl=a.get('dir')=='rtl' and a.get('lang')=='ar'
  if tag=='section': self.sections.append(a.get('id'))
  if tag=='pre': self.pre+=1
  if tag=='code' and a.get('class')=='language-mermaid': self.mermaid+=1
x=Audit(); text=p.read_text(encoding='utf8'); x.feed(text)
assert x.html_rtl and 'charset="utf-8"' in text and 'direction:ltr' in text
assert sum(1 for i in x.sections if i and i.startswith('source-'))==81
assert sum(1 for i in x.sections if i and i.startswith('chapter-'))==14
assert x.mermaid>=10
print('HTML structural check: RTL document; LTR code CSS; 14 chapters; 81 source pages; Mermaid code blocks:',x.mermaid,'pre blocks:',x.pre)
print('No rendering, page break, font shaping, page-number or Mermaid-parser validation performed.')
