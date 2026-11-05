# مخططات بنية النظام ومساراته

هذه المخططات مستخلصة من الشيفرة المشار إليها أسفل كل رسم. نجح Mermaid CLI 11.4.2، المثبت في مجلد معزول للتوثيق، في تحليل الرسوم العشرة وتصديرها إلى SVG في `mermaid_rendered/`؛ بعض نسخ PNG الأقدم لا تعكس تعديلات تخطيط SVG الأخيرة. فُحصت المخططات العشرة بصرياً داخل نسخة PDF للمراجعة، وأعيد ترتيب بعض التسميات لتحسين قراءتها؛ تبقى المراجعة العلمية الشاملة لبقية الكتاب. نجاح التحليل لا يثبت صحة المخططات العلمية. الأسهم تلخص الاعتماد أو التسلسل ولا تعني تنفيذ كل خطوة عند عرض لوحة Streamlit.

## 1. البنية العامة

```mermaid
flowchart TD
    A[لقطات موثقة] --> B[سمات ونوافذ]
    B --> C[تدريب واختيار]
    C --> D[تنبؤات الاختبار]
    C --> E[SHAP و LIME]
    D --> F[آثار محفوظة]
    E --> F
    F --> G[واجهة Streamlit]
```

المصدر: `pipelines/train.py`, `pipelines/explain.py`, `dashboard/app.py`.

## 2. معالجة البيانات

```mermaid
flowchart TD
    A[تحميل لقطة وبصمة] --> B[التحقق من التواريخ والقيم]
    B --> C[بناء السمات الماضية]
    C --> D[حذف الصفوف الناقصة]
    D --> E[نافذة حتى الأصل]
    E --> F[هدف الرصد التالي]
    F --> G[تقسيم زمني]
```

المصدر: `io/data_sources.py`, `data/validate.py`, `data/features.py`, `data/windows.py`. الهدف هو الصف التالي بعد تكوين السمات؛ مطابقة الرصد الخام التالي في اللقطات المحفوظة موضوع تدقيق مستقل.

## 3. هندسة السمات

```mermaid
flowchart LR
    P[سلسلة الإغلاق] --> SMA[متوسطات 5 و 20]
    P --> EMA[EMA 12 و 26 و MACD]
    P --> RSI[RSI 14]
    P --> R[عوائد وتقلب وزخم]
    P --> BB[Bollinger من نافذة 20]
    O[OHLCV يومي] --> A[تعديل الأسعار ولوغاريتم الحجم]
```

المصدر: `data/features.py`. تُطبق سمات OHLCV على التردد اليومي فقط.

## 4. التدريب

```mermaid
flowchart TD
    W[النوافذ] --> T[تدريب فقط]
    W --> V[تحقق]
    T --> SK[مرشحو sklearn]
    T --> L[LSTM ومعايير تدريب]
    V --> S["اختيار بالتحقق<br/>RMSE / MSE"]
    SK --> S
    L --> S
    S --> M[نماذج محفوظة]
```

المصدر: `models/sklearn_models.py`, `models/lstm_model.py`, `pipelines/train.py`.

## 5. LSTM المنفذ

```mermaid
flowchart TD
    X["المدخل<br/>B × T × F"] --> L["طبقة واحدة<br/>LSTM, H"]
    L --> S["خرج السلسلة<br/>B × T × H"]
    S --> LAST[آخر خطوة زمنية]
    LAST --> D[Dropout]
    D --> O[Linear إلى قيمة واحدة]
    O --> Y["عكس معيار الهدف<br/>predict"]
```

المصدر: `models/lstm_model.py:16–25,36–45`. لا تظهر الخلايا الداخلية كطبقات إضافية.

## 6. التنبؤ والتقييم

```mermaid
flowchart LR
    T[نوافذ الاختبار] --> M[النماذج الأربعة]
    C[الإغلاق الحالي] --> P[Persistence]
    M --> E[مقاييس بوحدات الهدف]
    P --> E
    A[الهدف الفعلي] --> E
    E --> O[تنبؤات ومقاييس محفوظة]
```

المصدر: `pipelines/train.py:89–107`, `evaluate/metrics.py`.

## 7. SHAP وLIME

```mermaid
flowchart TD
    TR[نوافذ التدريب] --> BG[خلفية SHAP]
    TR --> LT[مرجع LIME]
    TE[عينات اختبار محددة] --> SH[SHAP]
    TE --> LI[LIME]
    BG --> SH
    LT --> LI
    M[نموذج محفوظ] --> SH
    M --> LI
    SH --> Q[فحص الجمع والاستقرار]
    LI --> Q2["خطأ البديل المحلي<br/>R² الجوار"]
```

المصدر: `pipelines/explain.py`, `explain/shap_explain.py`, `explain/lime_explain.py`.

## 8. Streamlit

```mermaid
flowchart TD
    S[اختيار تشغيل محفوظ وأصل] --> A[قراءة التدقيق والتنبؤات]
    A --> T[ثمانية تبويبات]
    T --> F[مقارنة وتنبؤات محفوظة]
    T --> X[SHAP وLIME محفوظان]
    T --> R[تحقق ومطابقة الرسالة]
```

المصدر: `dashboard/app.py:179–205`. لا يستدعي الرسم تدريباً أو inference حياً.

## 9. التحقق العلمي

```mermaid
flowchart TD
    O[التجربة المجمدة] --> A[تدقيق المحاذاة والمعايير]
    O --> W[نوافذ محفوظة]
    W --> F[هدف فرق أو عائد]
    F --> V["تقسيم ثابت أو<br/>Walk-forward"]
    V --> P[تنبؤات ومراجع ساذجة]
    P --> B["مقاييس وعدم يقين<br/>Block bootstrap"]
    B --> R[تقرير استكشافي]
```

المصدر: `validation/audit.py`, `validation/design.py`, `validation/experiments.py`, `validation/statistics.py`. هذه التجارب السابقة لا تُعاد في إعداد التوثيق.

## 10. النشر المحلي CPU

```mermaid
flowchart TD
    Z[استخراج الحزمة] --> I[SETUP_DEMO]
    I --> V[فحص النسخة والآثار]
    V --> W[بيئة منفصلة وعجلات CPU]
    W --> C[فحوص الإعداد]
    C --> S[START_DEMO]
    S --> L[خادم localhost]
    L --> B[متصفح محلي]
```

المصدر: `SETUP_DEMO.bat`, `START_DEMO.bat`, `scripts/demo_wizard.py`. التثبيت يعمل دون شبكة فقط عند توفر حزمة العجلات اللازمة؛ Python نفسه غير مرفق بحسب README.
