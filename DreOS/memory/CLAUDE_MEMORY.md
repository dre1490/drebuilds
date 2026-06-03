# DreOS — Claude Memory File
# Last updated: May 2026
# Read this file at the start of every Cowork session

---

## Who I Am

Name: Dre
Primary computer: HP Windows laptop
Username on machine: eliza
GitHub: github.com/dre1490
Portfolio URL (in progress): drebuilds.io
Primary email: 1490dre@gmail.com
Location: East Providence, Rhode Island / Bedford NH area

---

## My Skill Level

- Python: Beginner-intermediate — learning through building
- SQL: Some background, actively improving
- AI/Automation: Building rapidly through project based learning
- Terminal: Comfortable with cd, dir, pip, python commands
- GitHub: Recently set up, learning version control

---

## How I Like to Work

- Step by step explanations at every phase
- Simple language — avoid jargon unless explained
- Learn by doing — build real things, not just tutorials
- Files first at the top of every response
- Remind me of credential protocol every time a new key is created
- Conversational tone — like a colleague, not a textbook

---

## Credential Protocol — ALWAYS FOLLOW THIS

Every new API key or credential must:
1. Be added to MY_CREDENTIALS.txt immediately
2. Be added to the project .env file
3. Be referenced in scripts with os.getenv() — never hardcoded
4. Be protected by .gitignore — never pushed to GitHub

Credential vault location:
C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\MY_CREDENTIALS.txt

---

## Folder Structure

Base folder:
C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\

GitHub repository (drebuilds):
C:\Users\eliza\OneDrive\Desktop\OneDrive\Documents\Dre AI practice file\drebuilds\

Projects inside drebuilds:
- Horizon Capital Fund Tracker\     — fund price automation
- Pulse research exercise\          — news headline logger
- SQL project\                      — Vertex Solutions customer DB
- NovaTech Analytics\               — full BI platform
- Dre Grocery tracker\              — weekly grocery PDF report
- analytics-automation-skill\       — reusable skill for analytics projects
- credential-cleanup\               — skill for cleaning credentials before GitHub push
- DreOS\                            — capstone project (currently building)

DreOS folder structure (being built):
DreOS\
├── modules\        — individual data fetching scripts
├── agent\          — the orchestration brain
├── skills\         — Cowork slash command files
├── memory\         — this file and other context files
├── outputs\        — generated reports, PDFs, dashboards
├── portfolio\      — drebuilds.io website files
└── .env            — credentials (never pushed to GitHub)

---

## My Projects — Status

| Project | Status | Location |
|---------|--------|----------|
| Horizon Capital Fund Tracker | Complete | drebuilds/Horizon Capital Fund Tracker |
| Pulse Research News Logger | Complete | drebuilds/Pulse research exercise |
| Vertex Solutions Customer DB | Complete | drebuilds/SQL project |
| NovaTech Analytics Platform | Complete | drebuilds/NovaTech Analytics |
| Weekly Grocery Tracker | Complete | drebuilds/Dre Grocery tracker |
| DreOS Personal Intelligence Hub | In Progress | drebuilds/DreOS |

---

## DreOS — Current Build Status

Track via Jira: My Operations Team Dre (KAN board)
Figma file: https://www.figma.com/design/bZbfXpqt2KdzmlVmH6qXBe/DreOS-Portfolio-Design-Assets

| Phase | Ticket | Status |
|-------|--------|--------|
| Phase 0 — GitHub, Jira, Figma Setup | KAN-4 | Done |
| Phase 1 — Memory File + Google Sheets | KAN-5 | In Progress |
| Phase 2 — Market Pulse Module | KAN-6 | To Do |
| Phase 3 — Weather and News Module | KAN-7 | To Do |
| Phase 4 — Jira Project Tracker | KAN-8 | To Do |
| Phase 5 — Figma Design Status | KAN-9 | To Do |
| Phase 6 — AI Commander | KAN-10 | To Do |
| Phase 7 — Master Dashboard + PDF | KAN-11 | To Do |
| Phase 8 — Email + Launcher | KAN-12 | To Do |
| Phase 9 — The Agent | KAN-13 | To Do |
| Phase 10 — Cowork Skill + Dispatch | KAN-14 | To Do |
| Phase 11 — Portfolio Website | KAN-15 | To Do |

---

## DreOS — Data Sources

| Source | What it tracks | Module |
|--------|---------------|--------|
| yfinance | AAPL, MSFT, GOOGL, AMZN, NVDA, PLTR, AMD, META, RIVN, TSLA | Market Pulse |
| yfinance | VFIAX, FCNTX, TRBCX, AGTHX, SWTSX | Market Pulse |
| Crypto API | BTC, ETH, BNB, SOL, XRP, MATIC, ARB, LINK, UNI, AAVE | Market Pulse |
| NewsAPI | AI and finance headlines | News Module |
| Weather API | Bedford NH daily forecast | Weather Module |
| Google Sheets | Personal tasks, deadlines, progress | Task Board |
| Jira | DreOS phase tickets | Project Tracker |
| Figma | Portfolio design file activity | Design Status |

---

## Tools and Accounts

| Tool | Account | Purpose |
|------|---------|---------|
| GitHub | dre1490 | Code backup and portfolio hosting |
| Groq | 1490dre@gmail.com | AI API for analysis and content |
| Mailtrap | 1490dre@gmail.com | Fake email inbox for testing |
| NewsAPI | 1490dre@gmail.com | News headlines |
| Jira | 1490dre@gmail.com | Project tracking |
| Figma | 1490dre@gmail.com | Design assets |
| Mailtrap SMTP | sandbox.smtp.mailtrap.io port 2525 | Test email sending |
| Gmail SMTP | smtp.gmail.com port 587 | Real email sending |

---

## Libraries Installed

pip install openpyxl plotly pandas requests groq reportlab python-dotenv yfinance

---

## Agent Preferences

- Tone: Conversational — like a colleague giving me a rundown
- Morning brief format: PDF email + live dashboard + Cowork summary
- Alert style: Flag problems clearly, keep wins brief
- Task board: Tasks with deadlines and progress tracking over time

---

## Portfolio Website

URL: drebuilds.io
Host: GitHub Pages (free)
Languages: English and Spanish (toggle button)
Style: Professional, bold, visual — corporate feel
Sections: About, Projects, Skills, Contact
Contact: Email link + LinkedIn + social media
Audience: Hiring managers, clients, collaborators, developers
Positioning: AI automation + finance tools + full stack range

---

## Notes for Claude

- When I say CONTINUE pick up from where we left off in DreOS build
- Always put downloadable files at the top of responses
- Remind me of credential protocol every time a new key is created
- Update this memory file whenever something significant changes
- Check Jira phase status before starting any DreOS work session
- Keep explanations simple — I learn by doing, not by reading walls of text
