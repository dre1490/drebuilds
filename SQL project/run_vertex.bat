@echo off
echo.
echo ========================================
echo   VERTEX SOLUTIONS - Weekly Workflow
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Generating report and checking alerts...
python generate_report_with_alerts.py

echo.
echo [2/3] Running AI analysis...
python ai_analyst.py

echo.
echo [3/3] Opening dashboard...
python vertex_dashboard.py

echo.
echo Press any key to close...
pause > nul
