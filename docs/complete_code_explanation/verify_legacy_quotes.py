import json,hashlib,pathlib,re
base=pathlib.Path(__file__).resolve().parent; root=base.parents[1]
rows={r['path']:r for r in json.loads((base/'inventory.json').read_text(encoding='utf-8'))}
items={
 'src/xai_finance/data/split.py':('line_by_line/src_xai_finance_data_split.py.md',{1:'import numpy as np',4:'def chronological_indices(count: int) -> dict[str, np.ndarray]:',5:'if count < 30:',6:'raise ValueError("Too few aligned samples for chronological train/validation/test")',7:'train_end = int(0.8 * count)',8:'validation_end = train_end + int(0.1 * count)',9:'return {"train": np.arange(train_end), "validation": np.arange(train_end, validation_end), "test": np.arange(validation_end, count)}'}),
 'src/xai_finance/models/baselines.py':('line_by_line/src_xai_finance_models_baselines.py.md',{1:'import numpy as np',4:'def persistence(current_close: np.ndarray) -> np.ndarray:',5:'return np.asarray(current_close, dtype=float).copy()'})}
for path,(doc,quotes) in items.items():
 raw=(root/path).read_bytes(); assert hashlib.sha256(raw).hexdigest()==rows[path]['sha256']; lines=raw.decode('utf-8').splitlines(); content=(base/doc).read_text(encoding='utf-8')
 for n,q in quotes.items():
  assert lines[n-1].strip()==q, f'{path}:{n} source mismatch'
  assert '`'+q+'`' in content, f'{path}:{n} documentation mismatch'
print('verified old quotes and inventory hashes:',sum(len(q) for _,q in items.values()),'lines')
