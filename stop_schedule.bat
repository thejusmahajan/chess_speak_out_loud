@echo off
title Stop Timetable Daemon
setlocal

echo ========================================================
echo        Stopping the Timetable Daemon
echo ========================================================

taskkill /F /FI "WINDOWTITLE eq Timetable Daemon*" /T 2>nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-CimInstance Win32_Process -Filter \"Name like '%%python%%'\" | Where-Object { $_.CommandLine -like '*trainer.schedule_daemon*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"

echo.
echo Timetable daemon stopped.
timeout /t 2
