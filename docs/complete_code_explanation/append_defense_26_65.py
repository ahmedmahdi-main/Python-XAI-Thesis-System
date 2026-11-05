import pathlib
base=pathlib.Path(__file__).resolve().parent
p=base/'11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md'; text=p.read_text(encoding='utf8')
assert '## 25.' in text and '## 26.' not in text
rows=[line.split('|') for line in (base/'defense_items_26_65.txt').read_text(encoding='utf8').splitlines() if line.strip()]
assert len(rows)==40 and all(len(r)==6 for r in rows)
out=[]
for i,(q,answer,detail,ref,why,follow) in enumerate(rows,26):
 out += [f'## {i}. {q}','',f'**الإجابة المختصرة:** {answer}','','**التفسير:** '+detail,'',f'**الدليل:** [{ref}]({ref}).','','**لماذا يهم؟** '+why,'','**سؤال متابعة:** '+follow,'']
text=text.replace('**الحالة: 25 سؤالاً؛ الهدف 100 على الأقل، والوثيقة غير مكتملة.**','**الحالة: 65 سؤالاً؛ الهدف 100 على الأقل، والوثيقة غير مكتملة.**')
p.write_text(text+'\n'+'\n'.join(out),encoding='utf8')
print('added',len(rows),'total',25+len(rows))
