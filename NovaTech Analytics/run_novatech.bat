@echo off
echo.
echo ================================================
echo   NOVATECH ANALYTICS PLATFORM
echo   Full Business Intelligence Suite
echo ================================================
echo.

cd /d "%~dp0"

echo [1/4] Generating Excel report...
python generate_novatech_report.py

echo.
echo [2/4] Running AI executive summary...
python ai_executive_summary.py

echo.
echo [3/4] Checking alerts and sending notifications...
python novatech_alerts.py

echo.
echo [4/4] Opening interactive dashboard...
python novatech_dashboard.py

echo.
echo ================================================
echo   NOVATECH ANALYTICS — Complete
echo ================================================
echo.
echo Press any key to close...
pause > nul
