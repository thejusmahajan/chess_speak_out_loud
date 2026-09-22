@echo off
title Goethe B2 Exam Simulator Launcher
setlocal

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo ====================================================================
echo        Goethe-Zertifikat B2 Prüfungssimulator & AI Trainer
echo ====================================================================
echo.
echo Starting Goethe B2 Simulator on port 8020...
start "Goethe B2 Simulator" "C:\Users\Admin\miniconda3\envs\cszero\python.exe" -m uvicorn app:app --port 8020

timeout /t 3 /nobreak >nul

echo Opening browser at http://127.0.0.1:8020/ ...
start http://127.0.0.1:8020/

echo.
echo ====================================================================
echo Goethe B2 Simulator is running at http://127.0.0.1:8020/
echo To stop, double-click 'stop_b2_trainer.bat'.
echo ====================================================================
timeout /t 3
