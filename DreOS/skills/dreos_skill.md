---
name: dreos
description: Run the DreOS Personal Intelligence Hub. Use this skill when the user says /dreos, "run DreOS", "morning brief", "run my intelligence hub", "start DreOS", or any variation. This skill triggers the full DreOS platform — fetching market data, weather, news, Jira status, Figma status, building the AI brief, generating the dashboard and PDF, and emailing the report.
---

# DreOS Skill — Personal Intelligence Hub

This skill runs Dre's complete morning intelligence platform from a single command in Cowork.

---

## Trigger Phrases

Any of these trigger this skill:
- `/dreos`
- "run DreOS"
- "morning brief"
- "run my intelligence hub"
- "start my morning brief"
- "run the platform"
- "DreOS go"

---

## What This Skill Does

Runs the full DreOS platform in this sequence:

1. Fetches live prices for 25 assets (stocks, crypto, funds)
2. Pulls Bedford NH weather and top headlines
3. Checks Jira project status
4. Checks Figma design file activity
5. Generates AI morning brief
6. Builds interactive dashboard
7. Generates PDF report
8. Emails everything to 1490dre@gmail.com

---

## Execution Instructions

### Step 1 — Navigate to DreOS folder
```
cd "C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\drebuilds\DreOS"
```

### Step 2 — Run the launcher
```
run_dreos.bat
```

### Step 3 — Confirm completion
After the batch file completes tell Dre:
- How many assets were fetched
- Top market gainer and loser
- Current weather in Bedford NH
- DreOS project progress percentage
- Confirmation that email was sent to 1490dre@gmail.com

---

## Module Commands (Individual Runs)

If Dre asks to run a specific module only:

| Request | Command |
|---------|---------|
| "refresh market" / "update prices" | `python modules/market_pulse.py` |
| "refresh news" / "latest headlines" | `python modules/weather_news.py` |
| "check Jira" / "project status" | `python modules/jira_tracker.py` |
| "check Figma" | `python modules/figma_status.py` |
| "new brief" / "write brief" | `python modules/ai_commander.py` |
| "open dashboard" | `python modules/dashboard.py` |
| "generate PDF" | `python modules/pdf_report.py` |
| "send email" / "email me" | `python modules/email_delivery.py` |
| "run agent" / "ask DreOS" | `python agent/dreos_agent.py` |

---

## Agent Mode

If Dre wants to ask questions about his data instead of running a full refresh:

```
python agent/dreos_agent.py
```

The agent runs in a continuous loop — Dre types questions and gets conversational answers. Remind him to type 'exit' to close the agent.

---

## Error Handling

If any module fails:
1. Check `error_log.txt` in the DreOS root folder
2. Report the specific error to Dre
3. Suggest running the failed module individually to isolate the issue
4. Other modules can still run even if one fails

---

## Credential Reminder

If credentials need updating:
- Real keys live in `MY_CREDENTIALS.txt` (outside drebuilds folder)
- Project credentials live in `DreOS/.env`
- Never hardcode credentials in scripts
- Never push `.env` to GitHub

---

## Context

- Owner: Dre
- Computer: HP Windows laptop, username eliza
- DreOS folder: `C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\drebuilds\DreOS`
- Memory file: `DreOS/memory/CLAUDE_MEMORY.md`
- GitHub: github.com/dre1490/drebuilds
- Portfolio: drebuilds.io (in progress)
- Email: 1490dre@gmail.com
- Tone: Conversational — like a colleague

---

## Related Skills
- credential-cleanup — run before pushing to GitHub
- analytics-automation — for building new analytics projects
