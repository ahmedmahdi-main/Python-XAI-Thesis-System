from pathlib import Path
import json,math,hashlib
import pymupdf
base=Path(__file__).resolve().parent;pdf=base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf';doc=pymupdf.open(pdf);out=base/'page_audit_contact_sheets';out.mkdir(exist_ok=True)
rows=[]
for i,page in enumerate(doc):
 words=page.get_text('words'); size=page.rect; outside=[]
 for w in words:
  x0,y0,x1,y1,txt,*_=w
  if x0 < -0.5 or y0 < -0.5 or x1 > size.width+0.5 or y1 > size.height+0.5: outside.append({'text':txt,'box':[round(x0,1),round(y0,1),round(x1,1),round(y1,1)]})
 footer=[w[4] for w in words if w[1]>size.height-40 and w[4].strip().isdigit()]
 rows.append({'page':i+1,'word_count':len(words),'text_characters':len(page.get_text()),'footer_numbers':footer,'footer_expected_found':str(i+1) in footer,'outside_words':outside,'low_text':len(words)<20})
pack=pymupdf.open(); cols=4; per=20; cw=200; ch=290
for start in range(0,len(doc),per):
 sheet=pack.new_page(width=cols*cw,height=5*ch)
 for offset in range(min(per,len(doc)-start)):
  n=start+offset; c=offset%cols;r=offset//cols
  sheet.draw_rect(pymupdf.Rect(c*cw,r*ch,(c+1)*cw,(r+1)*ch),color=(.7,.7,.7),width=.4)
  sheet.insert_text((c*cw+4,r*ch+11),f'{n+1}',fontsize=9)
  sheet.show_pdf_page(pymupdf.Rect(c*cw+4,r*ch+16,(c+1)*cw-4,(r+1)*ch-4),doc,n,keep_proportion=True)
 pack[-1].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3),alpha=False).save(str(out/f'sheet_{start//per+1:02}.png'))
summary={'pdf':'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf','sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':len(doc),'footer_number_missing':[r['page'] for r in rows if not r['footer_expected_found']],'low_text_pages':[r['page'] for r in rows if r['low_text']],'under_60_word_candidates':[r['page'] for r in rows if r['word_count']<60],'outside_word_pages':[r['page'] for r in rows if r['outside_words']],'contact_sheets':len(pack),'limitations':'word boxes and text extraction cannot establish visual clipping, reading order, shape, vector diagram completeness or semantic correctness; low text can be intentional.'}
(base/'page_quality_audit.json').write_text(json.dumps({'summary':summary,'pages':rows},ensure_ascii=False,indent=2),encoding='utf8')
lines=['# تدقيق صفحات PDF: آلي ومراجعة بصرية غير مكتملة','',f"الملف: `{summary['pdf']}`؛ SHA-256: `{summary['sha256']}`؛ عدد الصفحات: {len(doc)}.",'',f"- عدم العثور آلياً على رقم الصفحة المتوقع في تذييل النص: {summary['footer_number_missing'] or 'لا شيء'}.",f"- صفحات أقل من 20 كلمة مستخرجة: {summary['low_text_pages'] or 'لا شيء'}؛ قد تكون رسوماً أو صفحات مقصودة.",f"- صفحات تتضمن مربعات كلمات خارج حدود الصفحة بأكثر من نصف نقطة: {summary['outside_word_pages'] or 'لا شيء'}.",f"- أُنشئت {len(pack)} لوحة اتصال لمراجعة توزيع الصفحات؛ لا تكفي الصور المصغرة لفحص كل كلمة أو تشكيل الحروف.",'','هذه اختبارات إرشادية على النص المستخرج ومربعاته، ولا تثبت سلامة ترتيب RTL أو الخطوط أو قص داخل الصفحة أو جودة الجداول والمعادلات. المراجعة البصرية الكاملة لكل صفحة على مقياس مقروء لم تكتمل.','', '| الصفحة | كلمات مستخرجة | رقم التذييل | مربعات خارجية | أقل من 20 كلمة |','|---:|---:|---|---:|---|']
lines[5:5]=[f"- مرشح قليل النص بأقل من 60 كلمة، ويحتاج مراجعة السياق والرسوم: {summary['under_60_word_candidates']}.",'- ملاحظة نشر مؤكدة بفحص الصفحة 63 بحجم مقروء: فهرس الشيفرة يضغط أعمدة المسار وعدد الأسطر ويجزئ كلماتها؛ يلزم إصلاح الجدول وإعادة بناء نسخة مراجعة وفحصها.','- الصفحة 110 مثال لصفحة قليلة المحتوى بسبب توزيع النص وفاصل القسم؛ يلزم تقييم بقية المرشحات، وبعضها غلاف أو شكل.']
for r in rows:lines.append(f"| {r['page']} | {r['word_count']} | {'موجود' if r['footer_expected_found'] else 'غير متحقق'} | {len(r['outside_words'])} | {'نعم' if r['low_text'] else 'لا'} |")
(base/'PAGE_QUALITY_AUDIT_AR.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps(summary,ensure_ascii=False))

