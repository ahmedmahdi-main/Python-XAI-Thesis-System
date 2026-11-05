from pathlib import Path
import json

base = Path(__file__).resolve().parent
data = json.loads((base / 'page_quality_card_review_v2.json').read_text(encoding='utf8'))
lines = [
    '# تدقيق صفحات نسخة البطاقات V2 — مراجعة غير مكتملة',
    '',
    f"الملف `{data['pdf']}`؛ بصمة SHA-256 `{data['sha256']}`؛ عدد الصفحات {data['pages']}.",
    '',
    'الفحص الآلي لكل الصفحات وجد رقم التذييل المتوقع ولم يجد مربعات كلمات خارج الصفحة، ووجد مسارات الفهرس 77 كاملة في النص المستخرج. لا يثبت ذلك سلامة العرض أو عدم القص داخل الصفحة.',
    '',
    f"الصفحات المرشحة لقلة المحتوى بأقل من 60 كلمة مستخرجة: {data['under_60']}؛ قد تتضمن غلافاً أو رسماً ويجب فحصها بصرياً.",
    '',
    'فُحصت 35 صفحة بالحجم المقروء، بينها جميع المرشحات الـ31 منخفضة الكلمات. تفاصيل المعايير في [الدفعة الأولى](PAGE_VISUAL_BATCH_01_AR.md) و[الثانية](PAGE_VISUAL_BATCH_02_AR.md) و[الثالثة](PAGE_VISUAL_BATCH_03_AR.md) و[الرابعة](PAGE_VISUAL_BATCH_04_AR.md) و[الخامسة](PAGE_VISUAL_BATCH_05_AR.md). الصفحات 19 و63–65 و282 تحتاج إلى سجل تفصيلي. لم تُفحص الصفحات الأخرى فردياً في V2.',
    '',
    '| الصفحة | الكلمات المستخرجة | رقم التذييل | مربعات خارج الصفحة | فحص بصري | الحالة |',
    '|---:|---:|---|---:|---|---|',
]
for row in data['pages_data']:
    n = row['page']
    inspected = n in (1, 5, 8, 19, 21, 26, 28, 63, 64, 65, 82, 83, 85, 107, 109, 138, 147, 160, 168, 172, 173, 184, 186, 187, 191, 194, 197, 202, 216, 231, 232, 240, 241, 273, 282)
    # Even inspected samples require a complete per-criterion page review.
    lines.append(f"| {n} | {row['words']} | {'موجود' if row['footer'] else 'غير متحقق'} | {len(row['outside'])} | {'نعم، مراجعة عينة' if inspected else 'لا'} | UNRESOLVED |")
(base / 'PAGE_QUALITY_CARD_REVIEW_V2_AR.md').write_text('\n'.join(lines) + '\n', encoding='utf8')
print('pages', len(data['pages_data']), 'sampled', 35, 'all-page review incomplete')
