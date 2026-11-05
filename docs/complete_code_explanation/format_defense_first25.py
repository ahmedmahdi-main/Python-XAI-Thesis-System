import pathlib,re
base=pathlib.Path(__file__).resolve().parent;p=base/'11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md';text=p.read_text(encoding='utf8')
parts=re.split(r'(?=^## \d+\. )',text,flags=re.M)
for i in range(1,26):
 part=parts[i]; match=re.search(r'\*\*الإجابة:\*\* (.+)',part); assert match
 answer=match.group(1); concise=re.split(r'(?<=[.؛؟])\s+',answer,maxsplit=1)[0]
 parts[i]=part.replace(match.group(0),'**الإجابة المختصرة:** '+concise+'\n\n**التفسير:** '+answer,1)
p.write_text(''.join(parts),encoding='utf8')
