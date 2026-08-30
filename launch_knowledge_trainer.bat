@echo off
title Knowledge Trainer Launcher
setlocal

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo ========================================================
echo        Launching Knowledge Trainer (Study Cards)
echo ========================================================

echo Starting the 24/7 timetable daemon...
start "Timetable Daemon" /min "C:\Users\Admin\miniconda3\envs\cszero\python.exe" -X utf8 -m trainer.schedule_daemon

echo Starting Knowledge Trainer server on port 8010...
start "Knowledge Trainer" /min "C:\Users\Admin\miniconda3\envs\cszero\python.exe" -m uvicorn trainer.app:app --port 8010

timeout /t 2 /nobreak >nul

echo Opening browser at http://127.0.0.1:8010/ ...
start http://127.0.0.1:8010/

echo.
echo ========================================================
echo Knowledge Trainer is running at http://127.0.0.1:8010/
echo To stop, double-click 'stop_knowledge_trainer.bat'.
echo ========================================================
timeout /t 3
