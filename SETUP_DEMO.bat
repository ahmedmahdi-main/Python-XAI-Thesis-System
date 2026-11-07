@echo off
setlocal
cd /d "%~dp0"
title Mohammad XAI - CPU Setup Wizard
if exist ".demo_venv\Scripts\python.exe" (
  ".demo_venv\Scripts\python.exe" scripts\demo_wizard.py setup %*
  goto finished
)
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" scripts\demo_wizard.py setup %*
  goto finished
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3.12 -c "import sys; assert sys.version_info[:2] == (3,12)" >nul 2>nul
  if not errorlevel 1 (
    py -3.12 scripts\demo_wizard.py setup %*
    goto finished
  )
)
where python >nul 2>nul
if not errorlevel 1 (
  python scripts\bootstrap_cpu.py %*
  goto finished
)
echo Python 3.12 x64 was not found. Install it for your user, then run SETUP_DEMO.bat again.
exit /b 1
:finished
set "demo_result=%errorlevel%"
if not "%demo_result%"=="0" echo Setup failed. See the message above and .demo_runtime\logs.
if /i not "%XAI_DEMO_NO_PAUSE%"=="1" pause
exit /b %demo_result%
