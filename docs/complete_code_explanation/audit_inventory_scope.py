import pathlib,json,hashlib,collections
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
rows=json.loads((base/'inventory.json').read_text(encoding='utf8')); indexed={r['path']:r for r in rows}
missing=[]; changed=[]
for path,row in indexed.items():
 p=root/path
 if not p.is_file(): missing.append(path)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=row['sha256']: changed.append(path)
active={'main.py'} | {p.relative_to(root).as_posix() for d in ('dashboard','src','scripts','tests') for p in (root/d).rglob('*.py') if '__pycache__' not in p.parts}
extras=set(p.relative_to(root).as_posix() for p in (root/'artifacts/deployment').rglob('*.py'))
covered_docs=collections.defaultdict(list); counts=collections.Counter()
for manifest in base.glob('*manifest.json'):
 try: data=json.loads(manifest.read_text(encoding='utf8'))
 except (OSError,ValueError): continue
 if not isinstance(data,dict): continue
 for source,entry in data.items():
  if isinstance(entry,dict) and 'document' in entry and source in indexed: counts[source]+=1; covered_docs[entry['document']].append(source)
legacy={'src/xai_finance/data/split.py','src/xai_finance/models/baselines.py'}
empty=[r['path'] for r in rows if r['physical_lines']==0]
print('inventory files',len(rows),'nonempty',len(rows)-len(empty),'empty',len(empty))
print('source missing',missing,'source hash mismatch',changed)
print('active outside inventory',sorted(active-set(indexed)),'inventory missing from active',sorted(set(indexed)-active))
print('deployment Python outside inventory',sorted(extras-set(indexed)))
print('source duplicated in manifests',[k for k,v in counts.items() if v>1])
print('document mapped to multiple sources',{k:v for k,v in covered_docs.items() if len(v)>1})
print('inventory entries without manifest or legacy',sorted(set(indexed)-set(counts)-legacy))
assert not (missing or changed or active-set(indexed) or set(indexed)-active)
assert not [k for k,v in counts.items() if v>1]
assert not (set(indexed)-set(counts)-legacy)
