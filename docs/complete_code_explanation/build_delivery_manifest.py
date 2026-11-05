from pathlib import Path
import hashlib,json
base=Path(__file__).resolve().parent
exclude={'mermaid_tool','node_modules','.npm-cache'}
mds=[p for p in base.rglob('*.md') if p.name!='DELIVERY_MANIFEST_AR.md' and not any(x in exclude or x.startswith('edge_') for x in p.relative_to(base).parts)]
other=[base/'ARABIC_TECHNICAL_BOOK_FIGURES.html',base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf',base/'ARABIC_TECHNICAL_BOOK_PROOF.pdf',base/'ARABIC_TECHNICAL_BOOK_LAYOUT_REVIEW.html',base/'ARABIC_TECHNICAL_BOOK_CARD_REVIEW.html',base/'ARABIC_TECHNICAL_BOOK_CARD_REVIEW.pdf',base/'ARABIC_TECHNICAL_BOOK_CARD_REVIEW_V2.html',base/'ARABIC_TECHNICAL_BOOK_CARD_REVIEW_V2.pdf',base/'INDEX_LAYOUT_PROOF.html',base/'INDEX_LAYOUT_PROOF.pdf',base/'INDEX_CARD_PROOF.html',base/'INDEX_CARD_PROOF.pdf',base/'BIDI_FOCUSED_PROOF.html',base/'BIDI_FOCUSED_PROOF.pdf',base/'diagram_inventory.json',base/'page_quality_audit.json',base/'page_quality_card_review_v2.json',base/'question_audit_matrix.json']+sorted((base/'mermaid_rendered').glob('*.svg'))+sorted((base/'mermaid_rendered').glob('*.mmd'))
other += [base/'BIDI_FOCUSED_PROOF_V2.html',base/'BIDI_FOCUSED_PROOF_V2.pdf']
other += [base/'ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.html',base/'ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.pdf',base/'scientific_review_v3_page_audit.json']
files=sorted(set(mds+other));assert all(p.is_file() for p in files)
rows=[]
for p in files:
 rel=p.relative_to(base).as_posix();digest=hashlib.sha256(p.read_bytes()).hexdigest()
 if rel=='ARABIC_TECHNICAL_BOOK_FIGURES.html': status='10 SVG مدمجة؛ فحص بنيوي وروابط داخلية؛ نسخة مراجعة علمية.'
 elif rel.endswith('FIGURES_REVIEW_V5.pdf'): status='283 صفحة؛ فُحصت الأشكال وعينات صفحات؛ جدول الصفحة 63 ضيق ويحتاج تصحيحاً؛ ليس نهائياً.'
 elif rel.endswith('LAYOUT_REVIEW.html'): status='نسخة مراجعة بتعديل تجريبي لأعمدة الفهرس؛ لم تُفحص طباعتها، وليست نهائية.'
 elif 'CARD_REVIEW_V2' in rel: status='نسخة مراجعة 282 صفحة في PDF؛ فحص آلي كامل وعينات مرئية للفهرس؛ المراجعة العلمية والبصرية الشاملة معلقة.'
 elif 'CARD_REVIEW' in rel: status='نسخة مراجعة سابقة لتصحيح عرض __init__؛ ليست نهائية.'
 elif 'INDEX_CARD_PROOF' in rel: status='إثبات مستقل لتخطيط البطاقات؛ فُحصت صفحتا PDF بصرياً.'
 elif 'INDEX_LAYOUT_PROOF' in rel: status='إثبات جدولي سابق؛ استمر تجزؤ بعض المسارات.'
 elif 'BIDI_FOCUSED_PROOF' in rel: status='إثبات فصل 06؛ فحص بصري للتواريخ والمسار، ولا يثبت سلامة بقية الكتاب.'
 elif 'SCIENTIFIC_REVIEW_V3' in rel: status='نسخة مراجعة 284 صفحة في PDF؛ فحص آلي و16 صفحة مرئية والأشكال العشرة؛ ليست نهائية.'
 elif rel.endswith('PROOF.pdf'): status='نسخة إثبات أقدم محفوظة؛ لا تحتوي الأشكال المدمجة الحالية.'
 elif rel.startswith('mermaid_rendered/') and rel.endswith('.svg'): status='SVG مُحلل ومضمن؛ فحص بصري في PDF V5.'
 elif rel.startswith('line_by_line/'): status='اقتباس وبصمة مدققان آلياً وفق النطاق؛ الجودة العلمية تحتاج مراجعة شاملة.'
 elif rel=='11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md': status='100 سؤال؛ فحص شكلي ومراجعة موجهة غير شاملة للمعنى والأدلة.'
 elif rel=='SCIENTIFIC_REVIEW_AR.md': status='سجل مراجعة مؤلف جزئية؛ ليس تحكيماً خارجياً.'
 elif rel=='02_PROJECT_ARCHITECTURE_AR.md': status='10 مخططات حُللت ومُثلت في PDF؛ المسارات تلخيصية.'
 else: status='ملف موثق؛ لا تعني سلامة الرابط اكتمال المراجعة الأكاديمية.'
 rows.append({'path':rel,'bytes':p.stat().st_size,'sha256':digest,'validation_status':status})
manifest={'status':'REVIEW_COPY_NOT_FINAL_ACADEMIC_APPROVAL','scope':'ملفات Markdown للمؤلف وصور Mermaid SVG ومصادرها وHTML وPDF المحددة؛ يستبعد ملفات الأدوات والاعتمادات والملفات الشخصية وفهرسي التسليم نفسيهما.','html':'ARABIC_TECHNICAL_BOOK_FIGURES.html','pdf':'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf','pdf_pages':283,'figures':10,'figures_visual_inspected':10,'figure_pages':[5,6,7,8,9,10,10,11,12,13],'toc_named_chapters_checked':14,'raw_mermaid_patterns_found':False,'sampled_other_pages':'1,2,17,19,22,142,283','full_pdf_page_review':False,'question_count':100,'question_scientific_review':'partial; no external expert review','source_coverage':'3210/3210 token starts in original 77, plus 57/57 in 2 additional scripts; 7 original files empty','notes':['الكتاب يتضمن لقطة سجل المراجعة حتى وقت البناء؛ نتائج فحص V5 اللاحقة مسجلة في الملف الخارجي.','المخططات مدمجة داخل HTML لكن بعض إحالات الأدلة تشير إلى ملفات محلية خارج HTML.','صور PNG القديمة ليست مرجع الرسوم المعدلة؛ الاعتماد على SVG.'],'artifacts':rows}
manifest['latest_review_html']='ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.html'
manifest['latest_review_pdf']='ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.pdf'
manifest['latest_review_pages']=284
manifest['latest_review_note']='فحص آلي لكل الصفحات ومعاينة 16 صفحة والأشكال العشرة؛ المراجعة العلمية والبصرية الشاملة غير مكتملة.'
(base/'delivery_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# سجل تسليم نسخة المراجعة','', '**الحالة: نسخة مراجعة وليست اعتماداً علمياً نهائياً.** فُحصت الأشكال العشرة بصرياً وعينات من صفحات الكتاب، بينما المراجعة الدلالية والعلمية لجميع الأسئلة والفصول وفحص جميع صفحات الطباعة لم يكتمل. لم تُعد تجارب أو تُعدّل الأدلة البحثية.','', '- HTML وPDF وصفحاتهما وبصمات SVG مدرجة أدناه؛ الرسوم مدمجة في HTML، وبعض روابط الأدلة المحلية تتطلب ملفات المشروع.','- الصفحة العلمية المضمنة في الكتاب لقطة عند البناء؛ نتيجة فحص V5 اللاحقة في سجل المراجعة الخارجي.','- `audit_figure_book_v5.py` دقق وجود 10 SVG ومطابقة الهاش وغياب أنماط Mermaid المحددة و14 وجهة فصل.','','| الملف | SHA-256 | حالة التحقق |','|---|---|---|']
lines.insert(4,'- أحدث نسخة مراجعة هي `ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.html` و`ARABIC_TECHNICAL_BOOK_SCIENTIFIC_REVIEW_V3.pdf` (284 صفحة). فُحصت الأشكال العشرة و16 صفحة بصرياً؛ المراجعة الشاملة غير مكتملة.')
lines += [f"| [{r['path']}]({r['path']}) | `{r['sha256']}` | {r['validation_status']} |" for r in rows]
lines += ['', 'يغطي السجل Markdown للمؤلف وSVG ومصادرها والملفات المختارة أعلاه، ويستبعد أدوات البناء والاعتمادات وملفات المتصفح والفهرس نفسه وJSON الخاص به.','']
(base/'DELIVERY_MANIFEST_AR.md').write_text('\n'.join(lines),encoding='utf8')
print('manifested',len(rows),'files; HTML',hashlib.sha256((base/manifest['html']).read_bytes()).hexdigest(),'PDF',hashlib.sha256((base/manifest['pdf']).read_bytes()).hexdigest())
