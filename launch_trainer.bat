@echo off
title Chess Speak Out Loud Launcher
setlocal enabledelayedexpansion

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo ========================================================
echo        Launching Chess Speak Out Loud Trainer
echo ========================================================

:: 1. Start backend if not already responsive
echo [1/3] Starting Backend (LC0 + BT3 attention)...
start "Chess Backend (LC0)" /min "C:\Users\Admin\miniconda3\envs\cszero\python.exe" -m uvicorn backend.app:app --port 8000

:: 2. Start frontend dev server
echo [2/3] Starting React Frontend...
cd /d "%PROJECT_DIR%frontend"
start "Chess Frontend" /min cmd /c "npm run dev"

cd /d "%PROJECT_DIR%"

:: 3. Wait and open browser
echo [3/3] Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:5173 ...
start http://localhost:5173

echo.
echo ========================================================
echo App launched at http://localhost:5173
echo Backend running on http://127.0.0.1:8000
echo.
echo To shut down all services, double-click 'stop_trainer.bat'
echo or the 'Stop Chess Trainer' shortcut on your Desktop.
echo ========================================================
timeout /t 4
