import hashlib, json, pathlib, re
base=pathlib.Path(__file__).resolve().parent
root=base.parents[1]
rows=json.loads((base/'inventory.json').read_text(encoding='utf-8'))
manifest={} 
for filename in ('dashboard_batch_manifest.json','data_batch_manifest.json','sources_batch_manifest.json','models_train_batch_manifest.json','explain_batch_manifest.json','explain_pipeline_manifest.json','evaluation_batch_manifest.json','validation_core_manifest.json','validation_report_manifest.json','report_storage_manifest.json','entry_seed_manifest.json','plots_orchestration_manifest.json','tests_batch_manifest.json','launch_helpers_manifest.json','wizard_manifest.json','replay_smoke_manifest.json','packaging_docs_manifest.json','deployment_tests_manifest.json','verification_scripts_manifest.json'):
    manifest.update(json.loads((base/filename).read_text(encoding='utf-8')))
old={'src/xai_finance/data/split.py':{1,4,5,6,7,8,9},'src/xai_finance/models/baselines.py':{1,4,5}}
covered={**old}
for path,entry in manifest.items():
    raw=(root/path).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==entry['sha256'], f'changed source: {path}'
    lines=raw.decode('utf-8').splitlines()
    doc=(base/entry['document']).read_text(encoding='utf-8')
    blocks=re.findall(r'```python\n(.*?)\n```',doc,re.S)
    assert len(blocks)==len(entry['ranges']), path
    line_set=set()
    for (start,end),quote in zip(entry['ranges'],blocks):
        assert quote=='\n'.join(lines[start-1:end]),f'quote mismatch: {path}:{start}-{end}'
        line_set.update(range(start,end+1))
    covered[path]=line_set

def ranges(values):
    values=sorted(values)
    if not values: return '—'
    groups=[]; start=last=values[0]
    for n in values[1:]:
        if n==last+1: last=n
        else:
            groups.append(str(start) if start==last else f'{start}–{last}'); start=last=n
    groups.append(str(start) if start==last else f'{start}–{last}')
    return ', '.join(groups)
count=done=0; complete=[]; missing=[]
for row in rows:
    path=row['path']; required=set(row['meaningful_token_start_lines']); present=covered.get(path,set()); gap=required-present
    count+=len(required); done+=len(required & present)
    if not gap and path in covered: complete.append(path)
    else: missing.append((path,gap))
text=['# تقرير التغطية المؤقت','', 'النطاق: main.py ومجلدات dashboard وsrc وscripts وtests. تستبعد البيئات ونسخ المصدر المولّدة تحت artifacts؛ يلزم البت في سكربتات artifacts/deployment المستقلة. ملفات batch والإعدادات ليست في المقام.','',f'- الجرد: {len(rows)} ملفاً، {sum(r["physical_lines"] for r in rows)} سطراً فعلياً؛ الأسطر التنفيذية التقريبية: {sum(r["executable_lines_approx"] for r in rows)}.',f'- مقياس بدايات رموز Python غير التعليقات: {done} من {count} ({100*done/count:.2f}%). لا يحسب كل أسطر السلاسل متعددة الأسطر، ولا يقيس جودة الشرح الأكاديمي.',f'- صفحات يدوية تغطي جميع بدايات الرموز في الجرد: {len(complete)}؛ ملفات فيها فجوات: {len(missing)}.','- يتحقق هذا التدقيق من بصمات المصدر واقتباسات جميع دفعات manifest المشمولة آلياً؛ تدقق stamp_source_versions.py بصمات صفحات الشرح مقابل الجرد وتدرجها في الصفحات. تدقق أداة verify_legacy_quotes.py اقتباسات الصفحتين الأقدم وبصمتيهما؛ شغّلها مع هذا التدقيق.','- المراجعة الأكاديمية: تفسيرات الصفحات روجعت يدوياً مقابل المصدر؛ لم يختبر تشغيل الواجهة، ولم تُراجع الشروح مراجعة مستقلة. لا يدل التطابق النصي على صحة التفسير.','','## الملفات المغطاة بمقياس بدايات الرموز','']+['- `'+p+'`' for p in complete]+['','## الفجوات: أرقام أسطر بدايات الرموز غير المشروحة','', 'النطاقات تجمع الأسطر المتتالية فقط؛ التعليقات والأسطر الفارغة وأسطر استمرار السلاسل لا تدخل هذا المقياس.','']+[f'- `{p}`: {ranges(gap)}' for p,gap in missing]+['','المطلوب أيضاً: تدقيق الاقتباسات والتفسير لجميع الصفحات، وفصل تغطية الأكواد عن الجودة، وإكمال الفصول والرسوم والأمثلة الفعلية والاختبارات والنشر وأسئلة الدفاع والتقرير القابل للطباعة. لا يجوز ادعاء اكتمال 100%.','']
text += ['', '## نطاق موسع مستقل', '', 'وُجد سكربتان من شيفرة المشروع تحت artifacts/deployment خارج جرد 77: initial_check.py وverify_final_release.py. تدقق verify_deployment_extra.py بصمتيهما واقتباساتهما و57 بداية رمز فيهما؛ معهما يصبح النطاق الموسع 79 ملفاً و3267 بداية رمز عند نجاح جميع التدقيقات. لا يشمل ذلك نسخ المصدر المحفوظة أو سكربتات توليد وتدقيق هذا التوثيق. هذه الأرقام لا تثبت اكتمال الشرح الأكاديمي أو دقة النتائج.', '']
(base/'COVERAGE_AR.md').write_text('\n'.join(text),encoding='utf-8')
print(f'{len(complete)} files, {done}/{count} = {100*done/count:.2f}%; {len(missing)} files with gaps; quoted blocks verified: {sum(len(e["ranges"]) for e in manifest.values())}')






















