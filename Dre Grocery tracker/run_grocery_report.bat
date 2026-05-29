@echo off
echo.
echo ================================================
echo   WEEKLY GROCERY REPORT
echo   Market Basket vs Hannaford
echo ================================================
echo.

cd /d "%~dp0"

echo [1/3] Fetching latest prices...
python fetch_prices.py

echo.
echo [2/3] Generating PDF report...
python generate_grocery_report.py

echo.
echo [3/3] Emailing report to 1490dre@gmail.com...
python email_report.py

echo.
echo ================================================
echo   Done! Check your Gmail inbox.
echo ================================================
echo.
echo Press any key to close...
pause > nul
