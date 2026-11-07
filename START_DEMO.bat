@echo off
setlocal
cd /d "%~dp0"
title Mohammad XAI - CPU Dashboard
if not exist ".demo_venv\Scripts\python.exe" (
  echo Run SETUP_DEMO.bat first to prepare this computer.
  if /i not "%XAI_DEMO_NO_PAUSE%"=="1" pause
  exit /b 1
)
if /i "%~1"=="stop" goto stop_server
".demo_venv\Scripts\python.exe" scripts\demo_wizard.py start %*
goto finished
:stop_server
".demo_venv\Scripts\python.exe" scripts\demo_wizard.py stop
:finished
set "demo_result=%errorlevel%"
if not "%demo_result%"=="0" if /i not "%XAI_DEMO_NO_PAUSE%"=="1" pause
exit /b %demo_result%
