@echo off
echo.
echo ========================================
echo   HORIZON CAPITAL - Daily Fund Updater
echo ========================================
echo.

cd /d "%~dp0"

python update_tracker.py

echo.
echo Press any key to close...
pause > nul
