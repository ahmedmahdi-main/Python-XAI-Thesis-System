import pathlib,json,hashlib
base=pathlib.Path(__file__).resolve().parent
rows=json.loads((base/'diagram_inventory.json').read_text(encoding='utf8'))
pdf=base/'ARABIC_TECHNICAL_BOOK_FIGURES_REVIEW_V5.pdf';html=base/'ARABIC_TECHNICAL_BOOK_FIGURES.html'
lines=['# جرد الأشكال في نسخة المراجعة','', 'الصور SVG مضمّنة في HTML، وترقيم الصفحات أدناه مستخرج من PDF V5. فُحصت الأشكال العشرة بصرياً في صفحاتها؛ الفحص لا يشمل كل صفحات الكتاب أو صحة جميع الادعاءات العلمية.','', '| الشكل | العنوان | مصدر Mermaid | SVG | صفحة PDF | SHA-256 لـ SVG |','|---:|---|---|---|---:|---|']
for r in rows:
 assert hashlib.sha256((base/r['svg']).read_bytes()).hexdigest()==r['sha256']
 lines.append(f"| {r['number']} | {r['title']} | [{r['mermaid_source']}]({r['mermaid_source']}) | [{r['svg']}]({r['svg']}) | {r['pdf_page']} | `{r['sha256']}` |")
lines += ['',f'بصمة HTML: `{hashlib.sha256(html.read_bytes()).hexdigest()}`.',f'بصمة PDF V5: `{hashlib.sha256(pdf.read_bytes()).hexdigest()}`.','','ملاحظة: نسخ PNG الأقدم لبعض الرسوم لا تمثل تعديلات SVG الأخيرة؛ تعتمد نسخة الكتاب على SVG فقط.','']
(base/'DIAGRAM_INVENTORY_AR.md').write_text('\n'.join(lines),encoding='utf8')
print('inventory:',len(rows),'figures')
