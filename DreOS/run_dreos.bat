@echo off
echo.
echo ============================================================
echo   ⚡  DreOS — PERSONAL INTELLIGENCE HUB
echo   Multi-Agent Morning Brief System
echo ============================================================
echo.

cd /d "%~dp0"

echo [AGENT 1] Market Pulse — Fetching 25 live assets...
python modules/market_pulse.py
if %errorlevel% neq 0 (
    echo ERROR in market_pulse.py — check error_log.txt
)

echo.
echo [AGENT 2] History Keeper — Storing prices and analyzing trends...
python agent/history_keeper.py
if %errorlevel% neq 0 (
    echo ERROR in history_keeper.py — check error_log.txt
)

echo.
echo [AGENT 3] Weather + News — Fetching context data...
python modules/weather_news.py
if %errorlevel% neq 0 (
    echo ERROR in weather_news.py — check error_log.txt
)

echo.
echo [AGENT 4] Jira Tracker — Checking project status...
python modules/jira_tracker.py
if %errorlevel% neq 0 (
    echo ERROR in jira_tracker.py — check error_log.txt
)

echo.
echo [AGENT 5] Figma Status — Checking design files...
python modules/figma_status.py
if %errorlevel% neq 0 (
    echo ERROR in figma_status.py — check error_log.txt
)

echo.
echo [AGENT 6] AI Commander — Writing morning brief...
python modules/ai_commander.py
if %errorlevel% neq 0 (
    echo ERROR in ai_commander.py — check error_log.txt
)

echo.
echo [AGENT 7] PDF + Email — Generating and delivering report...
python modules/pdf_report.py
python modules/email_delivery.py

echo.
echo ============================================================
echo   ✅  All agents complete — launching Flask dashboard...
echo ============================================================
echo.
echo   Dashboard will open at: http://localhost:5000
echo   Press Ctrl+C in this window to stop the server
echo.

start "" http://localhost:5000
python app.py

