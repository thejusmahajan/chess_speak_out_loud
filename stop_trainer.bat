@echo off
title Stop Chess Speak Out Loud
setlocal

echo ========================================================
echo        Stopping Chess Speak Out Loud Services
echo ========================================================

echo Terminating backend, LC0, and frontend processes...
taskkill /F /FI "WINDOWTITLE eq Chess Backend (LC0)*" /T 2>nul
taskkill /F /FI "WINDOWTITLE eq Chess Frontend*" /T 2>nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Process -Name lc0 -ErrorAction SilentlyContinue | Stop-Process -Force; Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*cszero*' } | Stop-Process -Force; Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '*frontend*' -or $_.CommandLine -like '*vite*' } | Stop-Process -Force"

echo.
echo All trainer services stopped cleanly.
timeout /t 3
