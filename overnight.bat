@echo off
rem Overnight training build: starts a fresh backend (picks up latest code),
rem then runs scripts\overnight_run.py. See data\training\overnight_report.md
rem in the morning.
cd /d "%~dp0"

set PY=C:\Users\Admin\miniconda3\envs\cszero\python.exe

netstat -ano | findstr "LISTENING" | findstr ":8000" >nul
if %errorlevel%==0 (
    echo.
    echo A backend is already running on port 8000. Close that window first
    echo ^(it may be running old code without the clk filter^), then rerun
    echo this script.
    pause
    exit /b 1
)

if not exist data\training mkdir data\training

echo Starting backend (log: data\training\backend_overnight.log)...
start "cszero-backend (overnight)" cmd /c "%PY% -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 > data\training\backend_overnight.log 2>&1"

echo Starting overnight runner (log: data\training\overnight_run.log)...
echo LEAVE THIS WINDOW OPEN overnight. Report: data\training\overnight_report.md
"%PY%" scripts\overnight_run.py --games 693
pause
