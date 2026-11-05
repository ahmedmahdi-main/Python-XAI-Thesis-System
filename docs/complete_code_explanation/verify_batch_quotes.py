import hashlib,json,pathlib,re
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
manifest=json.loads((base/'batch_files_manifest.json').read_text(encoding='utf8'))
for path,e in manifest.items():
 raw=(root/path).read_bytes(); assert hashlib.sha256(raw).hexdigest()==e['sha256'],path
 lines=raw.decode('utf8').splitlines(); doc=(base/e['document']).read_text(encoding='utf8'); blocks=re.findall(r'```bat\n(.*?)\n```',doc,re.S); assert len(blocks)==len(e['ranges']),path
 for (a,b),block in zip(e['ranges'],blocks): assert block=='\n'.join(lines[a-1:b]),(path,a,b)
print('verified',len(manifest),'batch files and',sum(len(e['ranges']) for e in manifest.values()),'quoted blocks')
