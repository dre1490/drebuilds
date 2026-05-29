# Analytics Automation Skill — Instructions Manual

Everything you need to know to use, customize, and deploy any project built with this skill.

---

## Table of Contents

1. What this skill builds
2. Before you start — required setup
3. How to get your API keys
4. How to change the email destination
5. How to connect to an existing Excel file
6. How to schedule automatic runs on Windows
7. How to add a new project from scratch
8. Folder structure rules
9. Troubleshooting guide
10. Glossary of terms

---

## 1. What This Skill Builds

Every project built with this skill follows the same 7 phase pipeline:

| Phase | What it does | Output |
|-------|-------------|--------|
| 1 | Connects to your data source | Database or data connection |
| 2 | Pulls business metrics | Terminal printout to verify |
| 3 | Generates Excel report | Dated .xlsx file |
| 4 | Writes AI executive summary | Dated .txt file |
| 5 | Sends email alerts | Mailtrap or real inbox |
| 6 | Builds interactive dashboard | Browser based .html file |
| 7 | One click launcher | .bat file |

You don't need all 7 phases for every project. Tell Claude which ones you want.

---

## 2. Before You Start — Required Setup

These things must be in place before running any project:

**Python installed**
- Download from https://www.python.org/downloads
- During install check the box that says "Add Python to PATH"
- Verify by opening terminal and typing: `python --version`

**Terminal navigation basics**
- `cd FolderName` — move into a folder
- `cd ..` — go back one level
- `dir` — list everything in current folder
- Wrap folder names with spaces in quotes: `cd "My Folder Name"`

**Core libraries installed** (one time, works for all projects)
```
pip install openpyxl
pip install plotly
pip install pandas
pip install requests
pip install groq
```

**One folder per project**
- Create a dedicated folder for each project
- All scripts and data files must live in the same folder
- The launcher batch file will not work if files are in different folders

---

## 3. How to Get Your API Keys

### Mailtrap (fake email inbox for testing)
1. Go to https://mailtrap.io
2. Sign up free — no credit card needed
3. Click Sandboxes in the left sidebar
4. Click My Sandbox
5. Click SMTP Settings
6. Select Python from the integration dropdown
7. Copy Host, Port, Username, and Password

### Groq (free AI API)
1. Go to https://console.groq.com
2. Sign up free — no credit card needed
3. Click API Keys in the left sidebar
4. Click Create API Key
5. Name it anything and copy the key — starts with `gsk_`
6. Use model: `llama-3.3-70b-versatile`

### NewsAPI (free news headlines)
1. Go to https://newsapi.org
2. Click Get API Key
3. Sign up free
4. Copy your key from the dashboard
5. Free tier: 100 requests per day

### Yahoo Finance / yfinance (free stock and fund prices)
- No API key needed
- Just install the library: `pip install yfinance`
- Free with no limits for personal use

---

## 4. How to Change the Email Destination

### For testing (Mailtrap)
Every alert script has this section at the top:
```python
SMTP_HOST     = "sandbox.smtp.mailtrap.io"
SMTP_PORT     = 2525
SMTP_USERNAME = "your_username"
SMTP_PASSWORD = "your_password"
EMAIL_FROM    = "alerts@yourcompany.com"
EMAIL_TO      = "recipient@yourcompany.com"
```
Change `EMAIL_TO` to any email address — Mailtrap will catch it in your fake inbox.

### For production (real Gmail)
Replace the settings above with:
```python
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SMTP_USERNAME = "your.gmail@gmail.com"
SMTP_PASSWORD = "your_app_password"
EMAIL_FROM    = "your.gmail@gmail.com"
EMAIL_TO      = "recipient@anyemail.com"
```

**Important:** For Gmail you need an App Password, not your regular password:
1. Go to https://myaccount.google.com
2. Click Security
3. Enable 2 Step Verification if not already on
4. Go to https://myaccount.google.com/apppasswords
5. Create a password named after your project
6. Copy the 16 character password Google shows you
7. Use that as `SMTP_PASSWORD` — you only see it once

### For production (Outlook / company email)
```python
SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587
```
Username and password are your regular Outlook credentials.

---

## 5. How to Connect to an Existing Excel File

When you have a real Excel file instead of a database, tell Claude:

- The file name and location
- Which sheet the data is on
- Which row the headers are on
- Which row the data starts on
- Which columns hold which information

Example:
> "My Excel file is called fund_tracker.xlsx, data is on Sheet1, headers on row 3, data starts row 4, fund names in column A, prices in column C"

Claude will build the script around your exact layout using openpyxl:
```python
from openpyxl import load_workbook
wb = load_workbook("your_file.xlsx")
ws = wb["Sheet1"]

# Read a specific cell
value = ws.cell(row=4, column=3).value

# Write to a specific cell
ws.cell(row=4, column=3, value=new_price)
wb.save("your_file.xlsx")
```

**Important:** Always close the Excel file before running a script that writes to it. Open files cause a Permission Denied error.

---

## 6. How to Schedule Automatic Runs on Windows

Use Windows Task Scheduler to run your launcher automatically:

1. Press Windows key + S, type Task Scheduler, open it
2. Click Create Basic Task on the right
3. Name it after your project, click Next
4. Select Daily, click Next
5. Set the time you want it to run, click Next
6. Select Start a Program, click Next
7. Click Browse and select your .bat launcher file
8. Click Next then Finish

**To set an end date:**
1. Find the task in Task Scheduler Library
2. Right click → Properties
3. Click the Triggers tab
4. Click Edit
5. Check the Expire box and set the end date
6. Click OK

**Important:** Your computer must be on and not asleep at the scheduled time for the task to run.

---

## 7. How to Add a New Project From Scratch

Tell Claude:

> "I want to build a new analytics automation project. I'm tracking [what you track] from [your data source]. The most important metrics are [list them]. I want an alert if [describe the conditions]. Send alerts to [email]. Call the project [name]."

Claude will ask follow up questions then build all phases automatically following this skill.

---

## 8. Folder Structure Rules

Every project must follow this structure:

```
Project Folder Name/
├── data_file.db          (or .xlsx if using Excel)
├── build_db.py           (Phase 1 — only if using database)
├── query_data.py         (Phase 2)
├── generate_report.py    (Phase 3)
├── ai_summary.py         (Phase 4)
├── alerts.py             (Phase 5)
├── dashboard.py          (Phase 6)
├── run_project.bat       (Phase 7 — launcher)
├── dashboard.html        (auto generated by dashboard.py)
└── outputs/              (optional — for dated reports)
    ├── report_2026-05-20.xlsx
    ├── report_2026-05-21.xlsx
    └── ai_summary_2026-05-20.txt
```

**Rules:**
- Never mix files from two different projects in the same folder
- Never move a script out of its project folder — the launcher uses relative paths
- The .bat file must be in the same folder as the scripts it runs

---

## 9. Troubleshooting Guide

### "pip is not recognized"
Python is not installed or not added to PATH.
Fix: Reinstall Python from python.org and check "Add Python to PATH" during install.

### "ModuleNotFoundError: No module named X"
A required library is not installed.
Fix: Run `pip install X` where X is the module name shown in the error.

### "Permission denied: filename.xlsx"
The Excel file is open in Excel while the script tries to write to it.
Fix: Close the Excel file completely then run the script again.

### "The system cannot find the path specified"
Terminal is not in the right folder, or the folder name has a typo.
Fix: Use `dir` to see what folders exist, then `cd "Exact Folder Name"` with quotes.

### "Model decommissioned" (Groq error)
The AI model you specified has been retired by Groq.
Fix: Change the model to `llama-3.3-70b-versatile` in your script.

### "Bad Request 400" (API error)
Your API key is wrong or has extra spaces.
Fix: Re-copy the key from your account dashboard and paste it fresh.

### Dashboard opens but shows no data
The script ran but couldn't find the database or Excel file.
Fix: Make sure the data file is in the same folder as the script.

### Batch file runs but closes immediately
There is an error in one of the scripts it calls.
Fix: Run each script individually in terminal to find which one has the error.

---

## 10. Glossary of Terms

**API (Application Programming Interface)**
A messenger that lets two programs talk to each other. Your script sends a request and gets data back. Think of it like a waiter taking your order to the kitchen.

**API Key**
A unique password that identifies your account when making API requests. Treat it like a password — don't share it publicly.

**Batch File (.bat)**
A Windows file containing a list of commands that run in sequence when you double click it. Used to launch all project scripts in one click.

**Churn Rate**
The percentage of customers who cancel their subscription in a given period. Industry benchmark for SaaS is 5-7%. Above 10% is a serious problem.

**Dashboard**
An interactive visual display of your key metrics. Built with Plotly and opens in your browser as an HTML file.

**Database**
An organized collection of data stored in tables. SQLite stores the entire database as a single file on your computer — no server needed.

**Foreign Key**
A field in one database table that links to a record in another table. Allows tables to be connected and queried together.

**Groq**
A free AI API service that gives access to large language models. Used to generate written analysis from your data automatically.

**JSON**
A structured data format that APIs use to send information back. Looks like organized lists and labels that Python can read and process.

**Mailtrap**
A fake email inbox used for testing. Catches all emails your script sends without delivering them to real inboxes.

**MRR (Monthly Recurring Revenue)**
The total guaranteed monthly income from all active subscriptions. The most important metric in any subscription based business.

**openpyxl**
A Python library for reading and writing Excel files. Used to build and update .xlsx files from scripts.

**PATH**
A Windows setting that tells the terminal where to find programs like Python. "Add Python to PATH" during install makes terminal commands like `python` and `pip` work from any folder.

**Plotly**
A Python library for building interactive charts and dashboards that open in your browser.

**Prompt Engineering**
The practice of writing clear, structured instructions for an AI model to get better and more consistent outputs. Includes role assignment, specific sections, tone guidance, and example formats.

**SaaS (Software as a Service)**
A business model where customers pay a recurring subscription to use software. Examples: Netflix, Spotify, Salesforce.

**SQLite**
A lightweight database that lives as a single .db file on your computer. No server or installation required beyond the built in Python sqlite3 library.

**SMTP**
The protocol used to send emails programmatically. Your script connects to an SMTP server (Gmail, Mailtrap, Outlook) to deliver alert emails.

**Threshold**
A limit that triggers an alert when crossed. Example: send an alert if churn rate goes above 7%.
