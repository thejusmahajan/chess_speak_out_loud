@echo off
title Timetable Daemon
setlocal

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo ========================================================
echo         Knowledge Trainer - Timetable Daemon
echo ========================================================
echo.
echo Runs 24/7 and announces every block boundary:
echo   - 5 minutes before a session ENDS   : silent banner
echo   - 5 minutes before a session STARTS : banner + ALARM
echo   - 03:00 wake-up                     : alarm on the hour
echo.
echo Schedule lives in trainer\content\timetable.json - edit it
echo and the daemon reloads it by itself, no restart needed.
echo.
echo Close this window (or press Ctrl+C) to stop.
echo ========================================================
echo.

"C:\Users\Admin\miniconda3\envs\cszero\python.exe" -X utf8 -m trainer.schedule_daemon %*
