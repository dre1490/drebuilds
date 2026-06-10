# DreOS — Claude Memory File
# Last updated: June 9, 2026
# Read this file at the start of every Cowork session

---

## Who I Am

Name: Dre
Computer: HP Windows laptop, username: eliza
GitHub: github.com/dre1490 — repo: drebuilds
Portfolio: dre1490.github.io/drebuilds
Email: 1490dre@gmail.com
Location: Goffstown, NH 03045
LinkedIn: linkedin.com/in/andres-onoa-49a73794
Target roles: AI Engineer / AI Project Manager (entry level, breaking in)

---

## How I Like to Work

- Step by step, simple language, no jargon unless explained
- Files at the top of every response
- Learn by doing — build real things
- Remind me of credential protocol every time a new key is created
- Conversational tone — like a colleague

---

## Credential Protocol — ALWAYS FOLLOW

Every new API key or credential:
1. Add to MY_CREDENTIALS.txt
2. Add to project .env file
3. Reference with os.getenv() — never hardcode
4. Protected by .gitignore — never on GitHub

Vault: C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\MY_CREDENTIALS.txt

---

## Git Workflow — Use This Every Session

Always use Git to track progress. Standard workflow:

```
cd "OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\drebuilds"
git status                         # see what changed
git add .                          # stage all changes
git commit -m "describe what changed"   # save snapshot
git push                           # push to GitHub
```

Before any major change — create a branch:
```
git checkout -b feature/branch-name   # create and switch to branch
git checkout main                      # go back to main
git merge feature/branch-name         # merge branch into main
```

Run credential cleanup before every push:
- Use Cowork: "Clean credentials in my drebuilds folder"
- Or use credential-cleanup/SKILL.md

Commit message conventions:
- feat: new feature added
- fix: bug fixed
- update: existing code improved
- style: visual/UI changes
- docs: documentation updated

---

## Folder Structure

Base: C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\
GitHub repo: ...Dre AI practice file\drebuilds\

Projects in drebuilds:
- Horizon Capital Fund Tracker\
- Pulse research exercise\
- SQL project\
- NovaTech Analytics\
- Dre Grocery tracker\
- analytics-automation-skill\
- credential-cleanup\
- DreOS\

DreOS structure:
DreOS\
├── modules\          — market_pulse, weather_news, jira_tracker, figma_status
│                       ai_commander, dashboard, pdf_report, email_delivery
├── agent\            — dreos_agent.py, history_keeper.py
│                       tool_registry.py, autonomous_agent.py, monitor.py
├── skills\           — dreos_skill.md
├── memory\           — CLAUDE_MEMORY.md (this file)
├── outputs\          — all JSON files, reports, agent_log.json, monitor_log.json
├── data\             — price_history.db (growing daily)
├── portfolio\        — index.html (also at drebuilds root)
├── app.py            — Flask web application (Version 2 — fintech redesign)
├── run_dreos.bat     — full DreOS launcher
├── run_agent.bat     — autonomous agent launcher (Phase 12)
├── .env              — credentials (never on GitHub)
└── error_log.txt

---

## Completed Projects

| Project | Status | Key tech |
|---------|--------|---------|
| Horizon Capital Fund Tracker | Complete | yfinance, openpyxl, Plotly, SMTP |
| Pulse Research News Logger | Complete | NewsAPI, openpyxl |
| Vertex Solutions Customer DB | Complete | SQLite, SQL, Groq, Plotly |
| NovaTech Analytics Platform | Complete | SQLite, Groq, Plotly, openpyxl |
| Weekly Grocery Tracker | Complete | reportlab, Groq, Gmail SMTP |
| DreOS Personal Intelligence Hub | Active | All of the above + Flask + autonomous agent |

---

## DreOS Current State

### Modules (run in sequence via run_dreos.bat)
- market_pulse.py — fetches 25 assets (stocks, crypto, funds)
- history_keeper.py — stores prices in SQLite, calculates trends
- weather_news.py — Open-Meteo weather + NewsAPI headlines
- jira_tracker.py — reads Jira KAN board
- figma_status.py — checks Figma file activity
- ai_commander.py — reads all JSON, writes AI brief (uses history_data.json)
- dashboard.py — builds static HTML dashboard
- pdf_report.py — generates PDF
- email_delivery.py — sends to 1490dre@gmail.com

### Autonomous Agent (Phase 12 — complete)
- tool_registry.py — wraps 7 modules as callable tools with dispatch_tool()
- autonomous_agent.py — ReAct reasoning loop using Groq tool calling
- monitor.py — proactive monitor, runs 3 checks every 30 min, alerts via terminal + Gmail
- run_agent.bat — launches monitor + Flask in separate windows

### Key agent details
- Model: llama-3.3-70b-versatile (llama3-70b-8192 is decommissioned — never use it)
- Modules are top-level scripts with no run() function — call via subprocess.run()
- dispatch_tool() is the single entry point for all tool calls
- agent_log.json — reasoning trace saved after every run
- monitor_log.json — monitor run history (last 100 runs)
- Alert threshold: 5% price move triggers terminal print + Gmail

### Flask Web App (app.py) — Version 2 Fintech Redesign
URL: localhost:5000

Routes:
- / — main dashboard
- /chat — dual mode AI chat interface
- /api/brief — returns morning data as JSON
- /api/market — returns full market data as JSON
- /api/chart/<ticker> — returns 30 day price history for line charts
- /history — price history table with 7/30/90 day trends
- /run — triggers market pulse refresh

Dashboard features (redesigned June 2026):
- Modern fintech UI — Inter font, gradient header, dark cards
- Sticky header with live pulse indicator
- KPI strip with pill buttons
- 6 asset cards: Big 5, Potential Stocks, Crypto, Tokens, Funds, Weather
- 📊 Chart toggle on each stock/crypto card
- 30 day SVG line charts with hover crosshair + tooltip
- Live price display on hover — updates header stats
- Real data when available, simulated when building history
- Project Switcher — tabs for all 6 projects with phase tracking
- AI Morning Brief card
- Live headlines — AI + Finance side by side
- Compact weather card with 3 day forecast
- Agent button — purple/blue gradient glow

Chat interface (/chat):
- Quick Mode ⚡ — fast answers from cached JSON (~2 seconds)
- Deep Mode 🔍 — uses autonomous agent with live tool calls (~15-30 seconds)
- Shows which tools were used in Deep Mode responses
- Different suggestion buttons per mode
- Purple theme for Deep Mode, blue for Quick Mode

### Data files (outputs/)
- market_data.json — 25 asset prices
- context_data.json — weather + news
- jira_data.json — project tickets
- figma_data.json — design status
- history_data.json — trend analysis (7/30/90 day)
- brief_data.json — full brief data
- morning_brief_YYYY-MM-DD.txt — AI written brief
- agent_log.json — autonomous agent reasoning trace
- monitor_log.json — proactive monitor run history

### Database (data/)
- price_history.db — growing daily, 90 day target
- Tables: price_history (date, ticker, name, asset_class, price, change_pct, volume), agent_runs

---

## DreOS Assets Tracked

Big 5 Stocks: AAPL, MSFT, GOOGL, AMZN, NVDA
Potential Stocks: PLTR, AMD, META, RIVN, TSLA
Mutual Funds: VFIAX, FCNTX, TRBCX, AGTHX, SWTSX
Major Cryptos: BTC, ETH, BNB, SOL, XRP
Potential Tokens: POL, ARB, LINK, UNI, AAVE

---

## Connectors Active

| Service | Credentials in .env | Purpose |
|---------|-------------------|---------|
| Groq | GROQ_API_KEY | AI analysis and brief writing |
| NewsAPI | NEWSAPI_KEY | Headlines |
| Gmail | GMAIL_APP_PASSWORD, GMAIL_USER | Email delivery |
| Mailtrap | MAILTRAP_USERNAME/PASSWORD | Test emails |
| Jira | JIRA_API_TOKEN, JIRA_EMAIL, JIRA_DOMAIN | Project tracking |
| Figma | FIGMA_API_TOKEN | Design status |
| Google Sheets | Sheet ID: 1WHCUYT2hr2JJJofquQabE6sfXS-aQyUapmaw7wL2Fq8 | Task board |

Jira domain: 1490dre.atlassian.net
Jira project: KAN (My Operations Team Dre)
Figma file: bZbfXpqt2KdzmlVmH6qXBe

---

## DreOS Jira Tickets

KAN-4  Phase 0 — GitHub, Jira, Figma Setup — Done
KAN-5  Phase 1 — Memory + Google Sheets — Done
KAN-6  Phase 2 — Market Pulse — Done
KAN-7  Phase 3 — Weather + News — Done
KAN-8  Phase 4 — Jira Tracker — Done
KAN-9  Phase 5 — Figma Status — Done
KAN-10 Phase 6 — AI Commander — Done
KAN-11 Phase 7 — Dashboard + PDF — Done
KAN-12 Phase 8 — Email + Launcher — Done
KAN-13 Phase 9 — The Agent — Done
KAN-14 Phase 10 — Cowork Skill + Dispatch — Done
KAN-15 Phase 11 — Portfolio Website — Done
KAN-16 Phase 12 — Autonomous Agent — Done
KAN-17 Phase 13 — Portfolio Case Studies — Done

---

## What's Been Learned

Authentication: No auth (CoinGecko), API key (NewsAPI), Basic Auth (Jira), Bearer token (Figma)
Data patterns: JSON handoff, time series database, multi-agent orchestration
Web: Flask routes, templates, API endpoints, SVG charts, hover interactions
Dev ops: GitHub, git CLI, .env, .gitignore, credential cleanup skill
AI: Groq integration, role prompting, structured output, agent loops, ReAct pattern, tool calling
Agent patterns: tool registry, dispatcher, ReAct loop, proactive monitoring, scheduled checks
Frontend: Fintech UI design, SVG line charts, CSS animations, JavaScript hover events

---

## Roadmap — Next Steps

When CONTINUE is typed, pick up here in order:

1. Phase 14 — Cloud deployment
   Deploy market_pulse + weather_news + app.py to Render
   Keep Jira/Figma/Gmail LOCAL for privacy
   Credentials via Render environment variables
   Two trigger modes: scheduled + webhook
   Status: ON HOLD — security concerns about credentials on third party servers

2. Phase 15 — Monetization
   Small business automation, freelance, consulting

3. Phone access to agent
   Option A: Flask route that triggers agent when visited in browser
   Option B: Telegram bot — text it from phone, get DreOS data back

4. Git practice
   Dre wants to use Git more actively — branch per feature, commit after every session

---

## Portfolio Website

URL: dre1490.github.io/drebuilds
File: drebuilds\index.html (Version 3 — dark editorial hybrid)
Custom domain target: drebuilds.io (not yet purchased)
Host: GitHub Pages
Style: Dark bg, Fraunces serif headlines, red accents, monospace labels
Sections: Hero, DreOS flagship, 6 case studies, skills, contact
Target audience: AI Engineer / AI PM hiring managers
Last updated: June 2026 (Phase 13)

---

## Agent Preferences

Tone: Conversational — like a colleague
Morning brief format: PDF email + Flask dashboard + Cowork summary
Brief sections: Good morning, Market Pulse, News, Project Update

---

## Skills Library

analytics-automation/SKILL.md — builds full analytics projects
credential-cleanup/SKILL.md — sanitizes before GitHub push
DreOS/skills/dreos_skill.md — triggers DreOS via Cowork

---

## Notes for Claude

- Files at top of every response
- Remind credential protocol every new key
- Update this file when significant changes happen
- Keep explanations simple — learn by doing
- Never use model llama3-70b-8192 — it is decommissioned. Always use llama-3.3-70b-versatile
- DreOS modules have no run() function — always call via subprocess.run([sys.executable, script_path], cwd=BASE_DIR, check=True)
- Encourage Git commits after every meaningful session
- When CONTINUE is typed — Phase 14 cloud deployment or Git practice first based on what Dre wants
