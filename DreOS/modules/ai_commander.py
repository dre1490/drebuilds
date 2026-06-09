"""
DreOS — AI Commander Module
Phase 6: Read all module outputs and write your morning brief

Data sources: All JSON files in outputs/ folder
AI: Groq (llama-3.3-70b-versatile)

Output:
- outputs/morning_brief.txt   (conversational summary)
- outputs/brief_data.json     (structured data for dashboard/PDF)

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: python modules/ai_commander.py
"""

import json
import os
from datetime import datetime, date
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------
# SETTINGS
# -----------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("\n🤖 DreOS AI Commander — Building your morning brief...\n")

client = Groq(api_key=GROQ_API_KEY)

# -----------------------------------------
# STEP 1 — Load all JSON files
# Read every note left on the desk
# -----------------------------------------
print("  📂 Loading module outputs...")

def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"    ⚠️  {filepath} not found — run the module first")
        return {}
    except Exception as e:
        print(f"    ❌ Error loading {filepath}: {str(e)}")
        return {}

market_data  = load_json("outputs/market_data.json")
context_data = load_json("outputs/context_data.json")
jira_data    = load_json("outputs/jira_data.json")
figma_data   = load_json("outputs/figma_data.json")
history_data = load_json("outputs/history_data.json")

print(f"    ✅ Market data: {len(market_data.get('big_5_stocks', []))} stocks loaded")
print(f"    ✅ Weather: {context_data.get('weather', {}).get('current', {}).get('temperature', 'N/A')}°F")
print(f"    ✅ News: {len(context_data.get('news', {}).get('ai_headlines', []))} AI + {len(context_data.get('news', {}).get('finance_headlines', []))} finance headlines")
print(f"    ✅ Jira: {jira_data.get('summary', {}).get('pct_complete', 0)}% complete")
print(f"    ✅ Figma: {figma_data.get('summary', {}).get('activity_status', 'Unknown')}")
print(f"    ✅ History: {history_data.get('days_of_history', 0)} days tracked")

# -----------------------------------------
# STEP 2 — Build the data brief
# Organize everything into a clear summary
# the AI can read and understand
# -----------------------------------------
today = date.today().strftime("%A, %B %d, %Y")

# Market summary
market_summary = market_data.get("summary", {})
big_5          = market_data.get("big_5_stocks", [])
potential      = market_data.get("potential_stocks", [])
cryptos        = market_data.get("major_cryptos", [])
tokens         = market_data.get("potential_tokens", [])
funds          = market_data.get("mutual_funds", [])

big_5_str    = "\n".join([f"  {s['ticker']}: ${s['price']:,.2f} ({s['change_pct']:+.2f}%)" for s in big_5 if s.get('price')])
potential_str= "\n".join([f"  {s['ticker']}: ${s['price']:,.2f} ({s['change_pct']:+.2f}%)" for s in potential if s.get('price')])
crypto_str   = "\n".join([f"  {s['ticker']}: ${s['price']:,.2f} ({s['change_pct']:+.2f}%)" for s in cryptos if s.get('price')])
token_str    = "\n".join([f"  {s['ticker']}: ${s['price']:,.2f} ({s['change_pct']:+.2f}%)" for s in tokens if s.get('price')])
funds_str    = "\n".join([f"  {s['ticker']}: ${s['price']:,.2f}" for s in funds if s.get('price')])

# Weather summary
weather      = context_data.get("weather", {}).get("current", {})
forecast     = context_data.get("weather", {}).get("forecast", [])
forecast_str = "\n".join([f"  {f['date']}: {f['low']}°F - {f['high']}°F, {f['description']}" for f in forecast])

# News summary
ai_news      = context_data.get("news", {}).get("ai_headlines", [])
fin_news     = context_data.get("news", {}).get("finance_headlines", [])
ai_str       = "\n".join([f"  - {h['source']}: {h['title']}" for h in ai_news])
fin_str      = "\n".join([f"  - {h['source']}: {h['title']}" for h in fin_news])

# Jira summary
jira_summary = jira_data.get("summary", {})
in_progress  = [t for t in jira_data.get("tickets", []) if t["status"].lower() == "in progress"]
todo         = [t for t in jira_data.get("tickets", []) if t["status"].lower() == "to do"]

# Figma summary
figma_summary = figma_data.get("summary", {})

# Historical trend context
days_of_history = history_data.get("days_of_history", 0)
top_gainers_7d  = history_data.get("top_gainers_7d", [])
top_losers_7d   = history_data.get("top_losers_7d", [])
hist_summary    = history_data.get("summary", {})

# Build trend strings for assets that have history
trends          = history_data.get("trends", [])
trend_map       = {t["ticker"]: t for t in trends}

def trend_str(ticker):
    t = trend_map.get(ticker, {})
    parts = []
    if t.get("change_7d") is not None:
        parts.append(f"7d: {t['change_7d']:+.1f}%")
    if t.get("change_30d") is not None:
        parts.append(f"30d: {t['change_30d']:+.1f}%")
    if t.get("change_90d") is not None:
        parts.append(f"90d: {t['change_90d']:+.1f}%")
    return f"({', '.join(parts)})" if parts else "(building history...)"

gainers_7d_str = "\n".join([f"  {g['ticker']}: {g['change_7d']:+.2f}%" for g in top_gainers_7d]) if top_gainers_7d else "  Not enough history yet"
losers_7d_str  = "\n".join([f"  {l['ticker']}: {l['change_7d']:+.2f}%" for l in top_losers_7d]) if top_losers_7d else "  Not enough history yet"

data_brief = f"""
Date: {today}

MARKET DATA (with {days_of_history} days of historical context):
Big 5 Stocks:
{chr(10).join([f"  {s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}% today) {trend_str(s['ticker'])}" for s in big_5 if s.get('price')])}

Potential Stocks:
{chr(10).join([f"  {s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}% today) {trend_str(s['ticker'])}" for s in potential if s.get('price')])}

Major Cryptos:
{chr(10).join([f"  {s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}% today) {trend_str(s['ticker'])}" for s in cryptos if s.get('price')])}

Potential Tokens:
{chr(10).join([f"  {s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}% today) {trend_str(s['ticker'])}" for s in tokens if s.get('price')])}

Mutual Funds:
{funds_str}

Market Summary: {market_summary.get('gainers', 0)} gainers, {market_summary.get('losers', 0)} losers today
Top Gainer Today: {market_summary.get('top_gainer', 'N/A')}
Top Loser Today: {market_summary.get('top_loser', 'N/A')}

7-Day Top Performers:
{gainers_7d_str}

7-Day Underperformers:
{losers_7d_str}

WEATHER — Bedford NH:
Current: {weather.get('temperature')}°F — {weather.get('description')}
Wind: {weather.get('wind_mph')} mph
3 Day Forecast:
{forecast_str}

AI HEADLINES:
{ai_str}

FINANCE HEADLINES:
{fin_str}

DREOOS PROJECT STATUS:
Progress: {jira_summary.get('pct_complete', 0)}% complete ({jira_summary.get('done', 0)}/{jira_summary.get('total_tickets', 0)} phases)
Currently working on: {jira_summary.get('current_phase', 'N/A')}
Up next: {jira_summary.get('next_phase', 'N/A')}

FIGMA DESIGN FILE:
File: {figma_data.get('file', {}).get('name', 'N/A')}
Status: {figma_summary.get('activity_status', 'N/A')}
Last modified: {figma_data.get('file', {}).get('last_modified', 'N/A')}
"""

# -----------------------------------------
# STEP 3 — Send to Groq AI
# Give it a clear role, specific sections,
# and a conversational tone — like a colleague
# -----------------------------------------
print("\n  🧠 Sending to Groq AI...")

prompt = f"""
You are DreOS — Dre's personal AI assistant and analyst.
Your job is to give Dre his morning briefing in a conversational,
collegial tone — like a smart colleague who has already done the
research and is giving you the highlights over coffee.

You now have {days_of_history} days of historical price data.
{"Use the trend data (7d, 30d, 90d) to add context beyond just today's moves." if days_of_history > 1 else "Historical data is just starting to build — focus on today's moves for now."}

Write a morning brief covering these four sections:

1. GOOD MORNING
   One friendly sentence greeting Dre and mentioning today's date and weather.
   If it's raining or cold mention it naturally.

2. MARKET PULSE
   Talk through the market like a colleague would — don't just list numbers.
   Highlight the biggest movers today and {"connect them to recent trends where relevant. If something is up today AND up over 7 days that's a stronger signal — say so." if days_of_history > 6 else "note any standout moves."}
   Mention both stocks and crypto. Keep it to 4-5 sentences.

3. WHAT'S IN THE NEWS
   Pick the 2-3 most interesting or relevant headlines and briefly explain
   why they matter. Connect any news to market movements if relevant.
   Keep it conversational — 3-4 sentences.

4. PROJECT UPDATE
   Give a quick DreOS build status update. Mention progress percentage,
   what's currently being worked on, and what's coming next.
   One sentence on the Figma file status. Keep it brief and encouraging.

Tone rules:
- Talk like a smart colleague, not a robot or a formal report
- Use "you" not "the user"
- Be specific with numbers but don't just list them — weave them into sentences
- Keep the whole brief under 350 words
- End with one sentence of encouragement about the day ahead

Here is all the data:
{data_brief}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}]
)

brief = response.choices[0].message.content.strip()

# -----------------------------------------
# STEP 4 — Display and save
# -----------------------------------------
print("\n" + "="*60)
print("  DREOS — MORNING BRIEF")
print("="*60)
print(brief)
print("="*60)

# Save as text file
os.makedirs("outputs", exist_ok=True)
brief_file = f"outputs/morning_brief_{date.today().strftime('%Y-%m-%d')}.txt"
with open(brief_file, "w") as f:
    f.write(f"DreOS Morning Brief — {today}\n")
    f.write("="*60 + "\n\n")
    f.write(brief)

# Save structured data for dashboard and PDF
brief_data = {
    "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    "date":         today,
    "brief":        brief,
    "market":       market_data,
    "weather":      context_data.get("weather", {}),
    "news":         context_data.get("news", {}),
    "jira":         jira_data.get("summary", {}),
    "figma":        figma_data.get("summary", {}),
    "history":      history_data.get("summary", {})
}

with open("outputs/brief_data.json", "w") as f:
    json.dump(brief_data, f, indent=2)

print(f"\n  💾 Brief saved as: {brief_file}")
print(f"  💾 Data saved as: outputs/brief_data.json\n")
