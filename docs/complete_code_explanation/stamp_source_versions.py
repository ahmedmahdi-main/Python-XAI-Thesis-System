import hashlib,json,pathlib
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
rows={r['path']:r for r in json.loads((base/'inventory.json').read_text(encoding='utf-8'))}
entries={}
for p in base.glob('*manifest.json'):
 try: data=json.loads(p.read_text(encoding='utf-8'))
 except (ValueError, OSError): continue
 for source,entry in data.items():
  if source in rows and isinstance(entry,dict) and 'document' in entry and 'sha256' in entry: entries[source]=entry
for source,doc in [('src/xai_finance/data/split.py','line_by_line/src_xai_finance_data_split.py.md'),('src/xai_finance/models/baselines.py','line_by_line/src_xai_finance_models_baselines.py.md')]: entries[source]={'document':doc,'sha256':rows[source]['sha256']}
for source,entry in entries.items():
 digest=hashlib.sha256((root/source).read_bytes()).hexdigest(); assert digest==entry['sha256']==rows[source]['sha256'],source
 path=base/entry['document']; content=path.read_text(encoding='utf-8'); marker=f'بصمة المصدر SHA-256: `{digest}`.'
 if marker not in content:
  head,rest=content.split('\n',1); path.write_text(head+'\n\n'+marker+'\n'+rest,encoding='utf-8')
 assert marker in path.read_text(encoding='utf-8')
print('source versions verified and recorded:',len(entries))

