@echo off
REM run_agent.bat
REM DreOS Phase 12 — Step 4
REM Launches the autonomous agent monitor in the background
REM Location: DreOS\run_agent.bat

title DreOS Autonomous Agent

echo.
echo ============================================================
echo   DreOS Autonomous Agent — Phase 12
echo   %date% %time%
echo ============================================================
echo.

REM Navigate to DreOS root
cd /d "C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\drebuilds\DreOS"

echo [1/3] Starting autonomous agent monitor...
echo.

REM Option 1 — Run once (single check, then exit)
REM python agent\monitor.py

REM Option 2 — Run continuously (checks every 30 min, runs in new window)
start "DreOS Monitor" cmd /k "cd /d "C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\drebuilds\DreOS" && python agent\monitor.py --continuous"

echo [2/3] Monitor launched in separate window
echo.

REM Also launch the Flask web app if not already running
echo [3/3] Starting Flask web app at localhost:5000...
start "DreOS Web App" cmd /k "cd /d "C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\drebuilds\DreOS" && python app.py"
start "" "http://localhost:5000"

echo.
echo ============================================================
echo   DreOS Agent is running!
echo.
echo   Monitor:  Check the DreOS Monitor window
echo   Web app:  http://localhost:5000
echo   Logs:     outputs\monitor_log.json
echo             outputs\agent_log.json
echo ============================================================
echo.
pause
