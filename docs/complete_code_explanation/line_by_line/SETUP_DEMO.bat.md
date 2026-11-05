# شرح `SETUP_DEMO.bat`

بصمة المصدر SHA-256: `19ef858e28246181b180df9b96ccb071f96e2133338f99266f67316c218813db`.

لا ينفذ هذا الشرح ملفات التشغيل.

## الأسطر 1–4

```bat
@echo off
setlocal
cd /d "%~dp0"
title Mohammad XAI - CPU Setup Wizard
```

يخفي عرض الأوامر ويعزل متغيرات البيئة ويغير القرص والمجلد إلى موقع batch ويحدد عنوان النافذة.

## الأسطر 5–8

```bat
if exist ".demo_venv\Scripts\python.exe" (
  ".demo_venv\Scripts\python.exe" scripts\demo_wizard.py setup %*
  goto finished
)
```

إذا وجد Python داخل .demo_venv يشغل wizard setup مع جميع الوسائط %* ثم ينتقل إلى finished.

## الأسطر 9–12

```bat
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" scripts\demo_wizard.py setup %*
  goto finished
)
```

وإلا إن وجد Python في .venv يشغل الإعداد به وينتقل إلى النهاية؛ مجرد وجود الملف لا يضمن سلامة البيئة.

## الأسطر 13–20

```bat
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 -c "import sys; assert sys.version_info[:2] == (3,12)" >nul 2>nul
  if not errorlevel 1 (
    py -3.12 scripts\demo_wizard.py setup %*
    goto finished
  )
)
```

يبحث عن py دون إظهار الخرج، ثم يتحقق من Python 3.12 ويشغل wizard عبره إن توفر. فحص الإصدار هنا لا يتحقق صراحة من معمارية 64 بت.

## الأسطر 21–27

```bat
where python >nul 2>nul
if not errorlevel 1 (
  python scripts\bootstrap_cpu.py %*
  goto finished
)
echo Python 3.12 x64 was not found. Install it for your user, then run SETUP_DEMO.bat again.
exit /b 1
```

إن وجد python في PATH يستدعي bootstrap_cpu للبحث عن إصدار مناسب؛ وإلا يعرض تعليمات وينهي برمز 1.

## الأسطر 28–32

```bat
:finished
set "demo_result=%errorlevel%"
if not "%demo_result%"=="0" echo Setup failed. See the message above and .demo_runtime\logs.
if /i not "%XAI_DEMO_NO_PAUSE%"=="1" pause
exit /b %demo_result%
```

label finished يحفظ errorlevel ويعرض رسالة عند الفشل، ويتوقف للقراءة ما لم يُضبط XAI_DEMO_NO_PAUSE=1، ثم يعيد رمز النتيجة.
