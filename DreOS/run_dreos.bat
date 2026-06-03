@echo off
echo.
echo ============================================================
echo   ⚡  DreOS — PERSONAL INTELLIGENCE HUB
echo   Morning Brief System
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/6] Fetching market data — 25 assets...
python modules/market_pulse.py
if %errorlevel% neq 0 (
    echo ERROR in market_pulse.py — check error_log.txt
)

echo.
echo [2/6] Fetching weather and news...
python modules/weather_news.py
if %errorlevel% neq 0 (
    echo ERROR in weather_news.py — check error_log.txt
)

echo.
echo [3/6] Checking Jira project status...
python modules/jira_tracker.py
if %errorlevel% neq 0 (
    echo ERROR in jira_tracker.py — check error_log.txt
)

echo.
echo [4/6] Checking Figma design status...
python modules/figma_status.py
if %errorlevel% neq 0 (
    echo ERROR in figma_status.py — check error_log.txt
)

echo.
echo [5/6] Building AI morning brief...
python modules/ai_commander.py
if %errorlevel% neq 0 (
    echo ERROR in ai_commander.py — check error_log.txt
)

echo.
echo [6/6] Generating dashboard, PDF and sending email...
python modules/dashboard.py
python modules/pdf_report.py
python modules/email_delivery.py

echo.
echo ============================================================
echo   ✅  DreOS Complete — Check your Gmail and browser!
echo ============================================================
echo.
echo Press any key to close...
pause > nul
