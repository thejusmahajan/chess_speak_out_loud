@echo off
title Stop Goethe B2 Trainer
setlocal

echo ========================================================
echo        Stopping Goethe B2 Simulator Server (Port 8020)
echo ========================================================

taskkill /F /FI "WINDOWTITLE eq Goethe B2 Simulator*" /T 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetTCPConnection -LocalPort 8020 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"

echo.
echo Goethe B2 Simulator stopped.
timeout /t 2
