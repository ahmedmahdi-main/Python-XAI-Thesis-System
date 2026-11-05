import pathlib,hashlib,json,re,tokenize
from io import BytesIO
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]; data=json.loads((base/'deployment_extra_sources.json').read_text(encoding='utf8'))
for name,e in data.items():
 raw=(root/name).read_bytes(); assert hashlib.sha256(raw).hexdigest()==e['sha256']; lines=raw.decode('utf8').splitlines(); blocks=re.findall(r'```python\n(.*?)\n```',(base/e['document']).read_text(encoding='utf8'),re.S); assert len(blocks)==len(e['ranges'])
 covered=set()
 for (a,b),block in zip(e['ranges'],blocks): assert block=='\n'.join(lines[a-1:b]); covered.update(range(a,b+1))
 starts={t.start[0] for t in tokenize.tokenize(BytesIO(raw).readline) if t.type not in (tokenize.ENCODING,tokenize.ENDMARKER,tokenize.NL,tokenize.NEWLINE,tokenize.INDENT,tokenize.DEDENT,tokenize.COMMENT)}
 assert starts<=covered, (name,starts-covered)
 print(name,'physical',len(lines),'token starts',len(starts),'verified')
