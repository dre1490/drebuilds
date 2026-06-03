"""
DreOS — The Agent
Phase 9: Intelligent orchestrator that responds to natural language

The agent reads your cached JSON data and answers questions
conversationally. It can also trigger module refreshes on demand.

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: python agent/dreos_agent.py
4. Type any question and press Enter
5. Type 'exit' to quit
"""

import json
import os
import subprocess
from datetime import datetime, date
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client       = Groq(api_key=GROQ_API_KEY)

# -----------------------------------------
# LOAD ALL CACHED DATA
# Agent reads from JSON files — no re-fetching
# unless you specifically ask for a refresh
# -----------------------------------------
def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def load_all_data():
    return {
        "market":  load_json("outputs/market_data.json"),
        "context": load_json("outputs/context_data.json"),
        "jira":    load_json("outputs/jira_data.json"),
        "figma":   load_json("outputs/figma_data.json"),
        "brief":   load_json("outputs/brief_data.json"),
    }

# -----------------------------------------
# RUN A SPECIFIC MODULE
# Agent can trigger refreshes on demand
# -----------------------------------------
def run_module(module_name):
    modules = {
        "market":    "modules/market_pulse.py",
        "news":      "modules/weather_news.py",
        "weather":   "modules/weather_news.py",
        "jira":      "modules/jira_tracker.py",
        "figma":     "modules/figma_status.py",
        "brief":     "modules/ai_commander.py",
        "dashboard": "modules/dashboard.py",
        "pdf":       "modules/pdf_report.py",
        "email":     "modules/email_delivery.py",
        "all":       None
    }

    if module_name == "all":
        print("\n  🔄 Running full DreOS platform...\n")
        subprocess.run(["run_dreos.bat"], shell=True)
        return "Full platform refresh complete."

    script = modules.get(module_name)
    if script:
        print(f"\n  🔄 Running {script}...\n")
        result = subprocess.run(["python", script], capture_output=True, text=True)
        if result.returncode == 0:
            return f"{module_name.title()} module refreshed successfully."
        else:
            return f"Error running {module_name}: {result.stderr[:200]}"
    return f"Unknown module: {module_name}"

# -----------------------------------------
# BUILD CONTEXT FOR AI
# Summarize all data into a brief for the AI
# -----------------------------------------
def build_context(data):
    market   = data.get("market", {})
    context  = data.get("context", {})
    jira     = data.get("jira", {})
    figma    = data.get("figma", {})
    brief    = data.get("brief", {})

    big_5    = market.get("big_5_stocks", [])
    cryptos  = market.get("major_cryptos", [])
    potential= market.get("potential_stocks", [])
    tokens   = market.get("potential_tokens", [])
    funds    = market.get("mutual_funds", [])
    mkt_sum  = market.get("summary", {})

    weather  = context.get("weather", {}).get("current", {})
    forecast = context.get("weather", {}).get("forecast", [])
    ai_news  = context.get("news", {}).get("ai_headlines", [])
    fin_news = context.get("news", {}).get("finance_headlines", [])

    jira_sum = jira.get("summary", {})
    tickets  = jira.get("tickets", [])
    figma_sum= figma.get("summary", {})

    last_brief = brief.get("brief", "No brief available yet.")

    stocks_str  = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in big_5 if s.get('price')])
    pot_str     = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in potential if s.get('price')])
    crypto_str  = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in cryptos if s.get('price')])
    token_str   = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in tokens if s.get('price')])
    funds_str   = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f}" for s in funds if s.get('price')])
    forecast_str= "\n".join([f"{f['date']}: {f['low']}°F-{f['high']}°F {f['description']}" for f in forecast])
    ai_str      = "\n".join([f"- {h['source']}: {h['title']}" for h in ai_news])
    fin_str     = "\n".join([f"- {h['source']}: {h['title']}" for h in fin_news])
    tickets_str = "\n".join([f"{t['key']} [{t['status']}]: {t['summary']}" for t in tickets])

    return f"""
CURRENT DATA SNAPSHOT — {datetime.now().strftime("%Y-%m-%d %H:%M")}

BIG 5 STOCKS:
{stocks_str}

POTENTIAL STOCKS:
{pot_str}

MAJOR CRYPTOS:
{crypto_str}

POTENTIAL TOKENS:
{token_str}

MUTUAL FUNDS:
{funds_str}

MARKET SUMMARY:
Top Gainer: {mkt_sum.get('top_gainer','N/A')}
Top Loser: {mkt_sum.get('top_loser','N/A')}
Gainers: {mkt_sum.get('gainers',0)} | Losers: {mkt_sum.get('losers',0)}

WEATHER — Bedford NH:
Current: {weather.get('temperature')}°F — {weather.get('description')}
Wind: {weather.get('wind_mph')} mph
Forecast:
{forecast_str}

AI HEADLINES:
{ai_str}

FINANCE HEADLINES:
{fin_str}

DREOS PROJECT STATUS:
Progress: {jira_sum.get('pct_complete',0)}% ({jira_sum.get('done',0)}/{jira_sum.get('total_tickets',0)} phases)
Current: {jira_sum.get('current_phase','N/A')}
Next: {jira_sum.get('next_phase','N/A')}

ALL TICKETS:
{tickets_str}

FIGMA:
{figma_sum.get('activity_status','N/A')} — last modified {figma.get('file',{}).get('last_modified','N/A')}

LAST MORNING BRIEF:
{last_brief[:500]}
"""

# -----------------------------------------
# DETECT INTENT
# Check if user wants to run a module
# -----------------------------------------
def detect_refresh_intent(question):
    q = question.lower()
    if any(w in q for w in ["refresh market", "update market", "run market", "fetch prices"]):
        return "market"
    if any(w in q for w in ["refresh news", "update news", "latest news", "refresh weather", "update weather"]):
        return "weather"
    if any(w in q for w in ["refresh jira", "update jira", "check jira", "update tickets"]):
        return "jira"
    if any(w in q for w in ["refresh figma", "check figma", "update figma"]):
        return "figma"
    if any(w in q for w in ["run brief", "new brief", "morning brief", "refresh brief"]):
        return "brief"
    if any(w in q for w in ["open dashboard", "show dashboard", "launch dashboard"]):
        return "dashboard"
    if any(w in q for w in ["send email", "email me", "email report"]):
        return "email"
    if any(w in q for w in ["run everything", "full refresh", "run all", "full update"]):
        return "all"
    return None

# -----------------------------------------
# MAIN AGENT LOOP
# Runs continuously until you type 'exit'
# -----------------------------------------
print("\n" + "="*60)
print("  ⚡  DreOS AGENT — Personal Intelligence Assistant")
print("="*60)
print("  Ask me anything about your markets, weather, news,")
print("  or project status. Type 'exit' to quit.")
print("="*60 + "\n")

# Load data once at startup
data = load_all_data()
data_timestamp = data.get("market", {}).get("timestamp", "unknown")
print(f"  📂 Data loaded — last updated: {data_timestamp}")
print(f"  💡 Tip: Say 'refresh market' or 'run everything' to fetch fresh data\n")

while True:
    try:
        user_input = input("  You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "bye", "close"]:
            print("\n  DreOS: See you tomorrow. Have a great day! 👋\n")
            break

        # Check if user wants to run a module
        refresh_intent = detect_refresh_intent(user_input)
        if refresh_intent:
            result = run_module(refresh_intent)
            # Reload data after refresh
            data   = load_all_data()
            print(f"\n  DreOS: {result} Data reloaded.\n")
            continue

        # Build context and ask Groq
        context  = build_context(data)
        today    = date.today().strftime("%A, %B %d, %Y")

        prompt   = f"""
You are DreOS — Dre's personal AI assistant and analyst.
You have access to Dre's current financial and productivity data.
Answer conversationally — like a smart colleague, not a formal report.
Be specific with numbers. Keep answers concise — 2-4 sentences unless more detail is needed.
Today is {today}.

Current data:
{context}

Dre's question: {user_input}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.choices[0].message.content.strip()
        print(f"\n  DreOS: {answer}\n")

    except KeyboardInterrupt:
        print("\n\n  DreOS: Closing agent. Have a great day! 👋\n")
        break
    except Exception as e:
        print(f"\n  DreOS: Something went wrong — {str(e)}\n")
        with open("error_log.txt", "a") as log:
            log.write(f"\n[{datetime.now()}] Agent error: {str(e)}\n")
