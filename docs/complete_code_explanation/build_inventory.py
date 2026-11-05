import ast, dis, hashlib, json, pathlib, tokenize
from io import BytesIO
root = pathlib.Path(__file__).resolve().parents[2]
out = pathlib.Path(__file__).resolve().parent
paths = [root/'main.py'] + sorted(p for d in ('dashboard','src','scripts','tests') for p in (root/d).rglob('*.py') if '__pycache__' not in p.parts)
def code_lines(code):
    lines = {line for _, line in dis.findlinestarts(code) if line is not None and line > 0}
    for item in code.co_consts:
        if isinstance(item, type(code)):
            lines |= code_lines(item)
    return lines
rows=[]
for path in paths:
    raw=path.read_bytes(); source=tokenize.detect_encoding(BytesIO(raw).readline)[0]; text=raw.decode(source); tree=ast.parse(text, filename=str(path))
    symbols=[]; imports=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            symbols.append({'kind':'class' if isinstance(node,ast.ClassDef) else 'function','name':node.name,'line':node.lineno,'end_line':node.end_lineno})
        elif isinstance(node,ast.Import): imports.extend(a.name for a in node.names)
        elif isinstance(node,ast.ImportFrom): imports.append('.'*node.level+(node.module or ''))
    meaningful=sorted({t.start[0] for t in tokenize.tokenize(BytesIO(raw).readline) if t.type not in (tokenize.ENCODING,tokenize.ENDMARKER,tokenize.NL,tokenize.NEWLINE,tokenize.INDENT,tokenize.DEDENT,tokenize.COMMENT)})
    rows.append({'path':path.relative_to(root).as_posix(),'physical_lines':len(text.splitlines()),'executable_lines_approx':len(code_lines(compile(text,str(path),'exec'))),'meaningful_token_start_lines':meaningful,'sha256':hashlib.sha256(raw).hexdigest(),'symbols':sorted(symbols,key=lambda x:x['line']),'imports':sorted(set(imports))})
(out/'inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# فهرس آلي أولي للشيفرة','', 'يشمل main.py ومجلدات dashboard وsrc وscripts وtests. تستبعد نسخ artifacts المحفوظة ومخرجات البناء والبيئات. هذا جرد نحوي آلي وليس دليلاً على اكتمال الشرح. عدد الأسطر القابلة للتنفيذ تقريبي من أرقام أسطر bytecode وقد يتغير حسب إصدار Python. الأسطر ذات الرموز تحتسب بداية الرمز فقط ولا تكفي وحدها لإثبات التغطية.','', '| المسار | الأسطر الفعلية | تنفيذية تقريبية | الأصناف والدوال (الاسم:السطر) | الواردات |','|---|---:|---:|---|---|']
for row in rows:
    syms=', '.join(f"{s['name']}:{s['line']}" for s in row['symbols']) or '—'
    lines.append(f"| `{row['path']}` | {row['physical_lines']} | {row['executable_lines_approx']} | {syms} | {', '.join(row['imports']) or '—'} |")
lines += ['',f"المجموع: {len(rows)} ملفاً؛ {sum(r['physical_lines'] for r in rows)} سطراً فعلياً؛ {sum(r['executable_lines_approx'] for r in rows)} سطراً تنفيذياً تقريبياً.",'','لا يستخرج هذا الجرد آلياً المسؤوليات أو نقاط الدخول أو الملفات المقروءة والمكتوبة؛ تحتاج إلى فحص يدوي. أرقام الدوال المتداخلة تظهر أيضاً، ولا يثبت الاستيراد تنفيذ المسار وقت التشغيل.']
(out/'12_CODE_INDEX_AR.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(len(rows),sum(r['physical_lines'] for r in rows),sum(r['executable_lines_approx'] for r in rows))

