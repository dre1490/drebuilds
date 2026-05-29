@echo off
echo.
echo ========================================
echo   PULSE RESEARCH - Daily News Logger
echo ========================================
echo.

cd /d "%~dp0"

python update_news_tracker.py

echo.
echo Press any key to close...
pause > nul
