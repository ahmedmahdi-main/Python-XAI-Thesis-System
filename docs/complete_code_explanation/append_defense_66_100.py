import pathlib
base=pathlib.Path(__file__).resolve().parent; p=base/'11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md'; text=p.read_text(encoding='utf8')
assert '## 65.' in text and '## 66.' not in text
rows=[line.split('|') for line in (base/'defense_items_66_100.txt').read_text(encoding='utf8').splitlines() if line.strip()]
assert len(rows)==35 and all(len(r)==6 for r in rows),len(rows)
out=[]
for i,(q,answer,detail,ref,why,follow) in enumerate(rows,66):
 out += [f'## {i}. {q}','','**الإجابة المختصرة:** '+answer,'','**التفسير:** '+detail,'',f'**الدليل:** [{ref}]({ref}).','','**لماذا يهم؟** '+why,'','**سؤال متابعة:** '+follow,'']
text=text.replace('**الحالة: 65 سؤالاً؛ الهدف 100 على الأقل، والوثيقة غير مكتملة.**','**الحالة: 100 سؤال؛ تحتاج المجموعة إلى مراجعة علمية وتحريرية نهائية شاملة.**')
p.write_text(text+'\n'+'\n'.join(out),encoding='utf8'); print('added',len(rows),'total',25+40+len(rows))
