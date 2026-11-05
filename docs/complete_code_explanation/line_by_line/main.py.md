# شرح `main.py`

بصمة المصدر SHA-256: `bd298e28fe24d362920cf792a09e9efc052c72d110f2e9b5dd17c85bd6abd061`.

نقطة الدخول إلى العرض المحلي. لا تتلقى معاملات دوال ولا تقرأ بيانات بحثية مباشرة؛ تمرر التنفيذ إلى dashboard/app.py. الاستدعاء المتوقع من Streamlit موثق في رأس الملف.

كل مقطع مقتبس آلياً من الملف المحدد؛ الأسطر الفارغة للفصل والتنسيق. التفسير من مراجعة المصدر ولا يمثل اختبار تشغيل للواجهة.

## الأسطر 1–4

```python
"""Stable Streamlit entry point for the original saved-evidence dashboard.

Run with ``python -m streamlit run main.py`` or START_DEMO.bat.
"""
```

سلسلة التوثيق تعرّف هذا الملف نقطة دخول ثابتة وتذكر أمر Streamlit وملف التشغيل؛ لا تنفذ الأمر بنفسها.

## الأسطر 6–7

```python
from pathlib import Path
import runpy
```

يستورد Path من المكتبة القياسية لبناء مسار مستقل عن مجلد العمل، وrunpy لتشغيل ملف Python آخر.

## الأسطر 10–11

```python
if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "dashboard" / "app.py"), run_name="__main__")
```

يفحص شرط __main__ ما إذا كان الملف منفذاً كنقطة دخول. إذا تحقق، يبني المسار المطلق من مكان الملف إلى dashboard/app.py ويشغله عبر run_path مع run_name="__main__"، فيُفعّل شرط الدخول في الملف الهدف. لا يعيد قيمة؛ أخطاء قراءة الملف أو تنفيذه تنتشر إلى المستدعي.
