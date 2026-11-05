import pathlib,re,collections
base=pathlib.Path(__file__).resolve().parent; p=base/'11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md'; text=p.read_text(encoding='utf8'); blocks=re.split(r'(?=^## \d+\. )',text,flags=re.M)[1:]
heads=[re.match(r'## (\d+)\. (.+)',b).groups() for b in blocks]
assert [int(n) for n,_ in heads]==list(range(1,101))
assert len({q.strip() for _,q in heads})==100
for (n,q),b in zip(heads,blocks):
 for label in ('**الإجابة المختصرة:**','**التفسير:**','**الدليل:**','**لماذا يهم؟**','**سؤال متابعة:**'): assert label in b,(n,label)
 for target in re.findall(r'\]\(([^)]+)\)',b):
  path=target.split('#')[0]; assert not path or (base/path).exists(),(n,target)
print('100 sequential questions, exact duplicate titles: 0, required fields present, local evidence files exist')
print('Semantic overlap, adequacy of evidence, technical accuracy and line references require manual review.')
