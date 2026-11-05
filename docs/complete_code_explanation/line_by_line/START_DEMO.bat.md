# شرح `START_DEMO.bat`

بصمة المصدر SHA-256: `f129e483d502a52bc8a7996397051670c7bf3c33ccdfd8b96750f37fc5f8f9d6`.

لا ينفذ هذا الشرح ملفات التشغيل.

## الأسطر 1–4

```bat
@echo off
setlocal
cd /d "%~dp0"
title Mohammad XAI - CPU Dashboard
```

يعزل البيئة ويحدد مجلد batch وعنوان نافذة العرض ويخفي الأوامر.

## الأسطر 5–9

```bat
if not exist ".demo_venv\Scripts\python.exe" (
  echo Run SETUP_DEMO.bat first to prepare this computer.
  if /i not "%XAI_DEMO_NO_PAUSE%"=="1" pause
  exit /b 1
)
```

يتحقق من وجود مفسر .demo_venv، ويعرض تعليمات الإعداد ويتوقف اختيارياً ويخرج برمز 1 إن غاب.

## الأسطر 10–14

```bat
if /i "%~1"=="stop" goto stop_server
".demo_venv\Scripts\python.exe" scripts\demo_wizard.py start %*
goto finished
:stop_server
".demo_venv\Scripts\python.exe" scripts\demo_wizard.py stop
```

إن كان الوسيط الأول stop ينتقل إلى الفرع المعني؛ وإلا ينفذ wizard start مع جميع الوسائط ثم ينتقل إلى finished. فرع stop يستدعي wizard stop دون تمرير بقية الوسائط.

## الأسطر 15–18

```bat
:finished
set "demo_result=%errorlevel%"
if not "%demo_result%"=="0" if /i not "%XAI_DEMO_NO_PAUSE%"=="1" pause
exit /b %demo_result%
```

يحفظ رمز الخروج ويتوقف اختيارياً عند الفشل فقط ثم يعيده للبيئة المستدعية.
