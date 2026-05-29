---
name: analytics-automation
description: Build a complete analytics automation project from scratch. Use this skill whenever the user wants to automate data collection, reporting, dashboards, email alerts, or any combination of these. Triggers include: "build me an automation", "automate my spreadsheet", "create a dashboard for my data", "set up email alerts for my metrics", "build an analytics platform", "I want to track X automatically", "create a report from my database", or any request involving recurring data tasks, business intelligence, or automated reporting. Also use when the user wants to apply the analytics pipeline pattern to a new scenario — even if they don't use technical terms. This skill covers the full pipeline: data source → Python scripts → Excel report → AI analysis → email alerts → interactive dashboard → one click launcher.
---

# Analytics Automation Skill

This skill builds complete analytics automation projects following a proven pipeline pattern. Every project uses the same structure — only the data source, metrics, and thresholds change.

---

## The Pipeline Pattern

Every project follows this exact sequence:

```
Data Source → Process → Excel Report → AI Analysis → Alerts → Dashboard → Launcher
```

| Phase | What gets built | Script name convention |
|-------|----------------|----------------------|
| 1 | Database or data connection | `build_[project]_db.py` |
| 2 | Business metric queries | `query_[project].py` |
| 3 | Excel report generator | `generate_[project]_report.py` |
| 4 | AI executive summary | `ai_[project]_summary.py` |
| 5 | Email alerts | `[project]_alerts.py` |
| 6 | Interactive dashboard | `[project]_dashboard.py` |
| 7 | One click launcher | `run_[project].bat` |

Not every project needs all 7 phases. Ask the user which phases they want or build all by default.

---

## Step 1 — Gather Requirements

Before writing any code ask the user for:

**Data source** — what kind of data are we working with?
- Excel file (ask for column layout and which sheet)
- Existing database (ask for table names and structure)
- API (ask for the API name and what data it returns)
- Website (ask for the URL and what data to pull)
- Build from scratch (we generate fake realistic data)

**Metrics** — what does the user want to track?
- Ask: "What are the 3-5 most important numbers you want to see?"
- Examples: revenue, churn, ticket volume, prices, headlines

**Alert thresholds** — when should something trigger an email?
- Ask: "What would make you worried if you saw it?"
- Examples: price drops below X, churn above Y%, tickets above Z

**Email destination** — who receives alerts?
- Default: Mailtrap (for testing — free, no real email needed)
- Production: ask for real email address and provider

**Output preferences** — what do they want at the end?
- Excel report, dashboard, AI summary, email alerts, or all of the above

**Folder name** — what should the project folder be called?

---

## Step 2 — Set Up Project Folder

Tell the user to create a new folder for this project. Every project gets its own folder. Remind them:
- Keep all scripts and data files in the same folder
- The batch file launcher requires this to work correctly
- Name it something descriptive like "Sales Tracker" or "Fund Monitor"

---

## Step 3 — Build Each Phase

### Phase 1 — Data Source

**If SQLite database:**
- Create tables with `CREATE TABLE IF NOT EXISTS`
- Use `AUTOINCREMENT` primary keys
- Link tables with foreign keys where relevant
- Fill with realistic fake data if building from scratch
- Confirm with record counts after building

**If Excel file:**
- Read the INSTRUCTIONS.md for column mapping requirements
- Use `openpyxl` to read existing files
- Identify header row, data start row, and key columns

**If API:**
- Install required library with pip
- Store API key as a variable at the top of the script
- Always include error handling for failed API calls

**Key libraries:**
```
sqlite3     — built into Python, no install needed
openpyxl    — pip install openpyxl
requests    — pip install requests
yfinance    — pip install yfinance
groq        — pip install groq
```

### Phase 2 — Queries and Metrics

Write SQL or data processing logic that produces:
- Summary numbers (totals, counts, averages)
- Breakdowns (by category, region, plan, date)
- Rankings (top 5 products, worst performing items)
- Trend data (daily, weekly, monthly)

Always print results to terminal with clean formatting so user can verify data before connecting to Excel.

### Phase 3 — Excel Report

Use `openpyxl` to build professional reports:

**Standard color palette:**
```python
dark_blue  = "1F3864"   # headers and titles
mid_blue   = "2E75B6"   # section headers
light_blue = "DCE6F1"   # alternating rows
green      = "70AD47"   # positive metrics
red        = "C00000"   # negative metrics / alerts
orange     = "ED7D31"   # warnings
yellow     = "FFF2CC"   # flagged rows
white      = "FFFFFF"
```

**Smart color coding rule:**
- Metrics that exceed bad thresholds → red automatically
- Metrics within good range → green automatically
- Never hardcode colors for metric values — always calculate

**Report structure:**
1. Title row — dark blue, company name and report type
2. Subtitle row — mid blue, date and data source
3. Blank spacer row
4. Section headers — mid blue with emoji label
5. Column headers — dark blue with white text
6. Data rows — alternating light blue and white

**Always name the file with today's date:**
```python
REPORT_FILE = f"report_{date.today().strftime('%Y-%m-%d')}.xlsx"
```

### Phase 4 — AI Executive Summary

Use Groq API with model `llama-3.3-70b-versatile`:

```python
from groq import Groq
client = Groq(api_key=API_KEY)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)
summary = response.choices[0].message.content
```

**Prompt structure — always include:**
1. Role assignment — "You are the [role] at [company]"
2. Task — "Write a [type] summary for [audience]"
3. Required sections — numbered list of exactly what to include
4. Tone guidance — professional, direct, data backed
5. The data — organized and clearly labeled

**Save output as dated text file:**
```python
with open(f"ai_summary_{date.today().strftime('%Y-%m-%d')}.txt", "w") as f:
    f.write(summary)
```

### Phase 5 — Email Alerts

Use Mailtrap for testing by default:
```python
SMTP_HOST     = "sandbox.smtp.mailtrap.io"
SMTP_PORT     = 2525
SMTP_USERNAME = "[user's mailtrap username]"
SMTP_PASSWORD = "[user's mailtrap password]"
```

**Two severity levels — always use both:**
- `alerts = []` — Critical issues, immediate action required 🔴
- `warnings = []` — Watch closely, may need attention 🟡
- `clear = []` — Within normal range ✅

**Alert email must include:**
- Business snapshot at top (key numbers)
- Critical section with metric, current value, threshold, and action message
- Warning section same format
- Clean list of metrics that are fine
- Footer with automation system signature

**Only send email if `alerts` or `warnings` is not empty.**

### Phase 6 — Interactive Dashboard

Use `plotly` with `make_subplots`:

```python
pip install plotly
pip install pandas
```

**Standard chart types by data:**
- Proportions → Pie chart
- Comparisons → Bar chart (vertical)
- Rankings → Bar chart (horizontal)
- Trends over time → Bar or line chart
- Detailed data → Table

**Always add a KPI banner:**
```python
fig.add_annotation(
    text=f"KPI 1: {val1}   |   KPI 2: {val2}   |   KPI 3: {val3}",
    xref="paper", yref="paper",
    x=0.5, y=1.04,
    showarrow=False,
    font=dict(size=13, color="white"),
    bgcolor="#1F3864",
    borderpad=8
)
```

**Always open in browser automatically:**
```python
import webbrowser, os
fig.write_html("dashboard.html")
webbrowser.open(f"file:///{os.path.abspath('dashboard.html')}")
```

### Phase 7 — One Click Launcher

Windows batch file that runs all scripts in sequence:

```batch
@echo off
echo.
echo ========================================
echo   [PROJECT NAME] - Analytics Platform
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Generating report...
python generate_report.py

echo.
echo [2/4] Running AI summary...
python ai_summary.py

echo.
echo [3/4] Checking alerts...
python alerts.py

echo.
echo [4/4] Opening dashboard...
python dashboard.py

echo.
echo Press any key to close...
pause > nul
```

The `cd /d "%~dp0"` line is critical — it navigates to the folder where the batch file lives automatically so scripts always find their data files.

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Library not installed | `pip install [library name]` |
| `Permission denied: file.xlsx` | Excel file is open | Close Excel then rerun |
| `Path not found` | Wrong folder in terminal | Use `cd` to navigate, wrap folder names with spaces in quotes |
| `Model decommissioned` | Groq model retired | Change to `llama-3.3-70b-versatile` |
| `API Error 400` | Bad API key | Check key was pasted correctly with no extra spaces |
| `FileNotFoundError` | Script and data in different folders | Move all files to the same folder |

---

## Portability Rules

These rules make every project reusable and transferable:

1. **One folder per project** — all scripts, data files, and outputs live together
2. **Date in output filenames** — never overwrite old reports
3. **API keys at the top** — clearly labeled, easy to swap
4. **Email settings at the top** — one section to update when going to production
5. **Thresholds clearly labeled** — easy to adjust without reading the whole script
6. **Comments on every section** — future user (including you) can understand it

---

## Read INSTRUCTIONS.md for:
- How to change the email destination to a real inbox
- How to connect to an existing Excel file instead of a database
- How to get API keys for Mailtrap, Groq, NewsAPI, and yfinance
- How to schedule the launcher to run automatically on Windows
- Troubleshooting guide for the most common issues
