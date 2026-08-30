@echo off
title Stop Knowledge Trainer
setlocal

echo ========================================================
echo        Stopping Knowledge Trainer Server
echo ========================================================

taskkill /F /FI "WINDOWTITLE eq Knowledge Trainer*" /T 2>nul
taskkill /F /FI "WINDOWTITLE eq Timetable Daemon*" /T 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*trainer.app:app*' } | Stop-Process -Force"

echo.
echo Knowledge Trainer stopped.
timeout /t 2
