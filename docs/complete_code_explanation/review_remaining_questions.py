from pathlib import Path
import re
s=Path('docs/complete_code_explanation/11_DEFENSE_QUESTIONS_AND_ANSWERS_AR.md').read_text(encoding='utf8')
blocks=re.split(r'(?=^## \d+\. )',s,flags=re.M)[1:]
for n in [41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100]:
 m=re.search(r'(?s)^(## .+?)\n\n\*\*الإجابة المختصرة:\*\* (.*?)\n\n\*\*التفسير:\*\* (.*?)\n\n\*\*الدليل:',blocks[n-1]); assert m,n
 print(m.group(1)+'\n'+m.group(2)+' '+m.group(3)+'\n')
