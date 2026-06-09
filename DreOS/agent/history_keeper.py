"""
DreOS — History Keeper Agent
Step 1: Receives handoff from Market Pulse and stores historical prices

This is Agent 2 in the DreOS multi-agent system.
Agent 1 (Market Pulse) fetches live data and saves market_data.json
Agent 2 (History Keeper) reads that file and stores it in a database

Why two agents instead of one?
- Market Pulse specializes in fetching — fast, focused, replaceable
- History Keeper specializes in storing and analyzing — separate concern
- If Market Pulse fails History Keeper isn't affected
- Each agent can be upgraded independently

Output:
- DreOS/data/price_history.db  (SQLite database)
- outputs/history_data.json    (trends for AI Commander)

HOW TO RUN:
1. Run market_pulse.py first (Agent 1)
2. Run: python agent/history_keeper.py
"""

import sqlite3
import json
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv

load_dotenv()

print("\n📚 DreOS History Keeper — Agent 2\n")
print("  Receiving handoff from Market Pulse (Agent 1)...")

# -----------------------------------------
# STEP 1 — Check for Agent 1 handoff
# History Keeper only runs after Market Pulse
# This is the agent communication pattern
# -----------------------------------------
MARKET_DATA_FILE = "outputs/market_data.json"

if not os.path.exists(MARKET_DATA_FILE):
    print(f"  ❌ No handoff detected — market_data.json not found")
    print(f"  Run market_pulse.py first then retry")
    exit()

with open(MARKET_DATA_FILE, "r") as f:
    market_data = json.load(f)

timestamp = market_data.get("timestamp", "unknown")
print(f"  ✅ Handoff received — data from {timestamp}")

# -----------------------------------------
# STEP 2 — Set up the historical database
# Different from previous SQLite databases
# This is a TIME SERIES database — data grows
# every day as new prices come in
# -----------------------------------------
os.makedirs("data", exist_ok=True)
DB_FILE = "data/price_history.db"

conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables if they don't exist yet
cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_history (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        date         TEXT NOT NULL,
        ticker       TEXT NOT NULL,
        name         TEXT NOT NULL,
        asset_class  TEXT NOT NULL,
        price        REAL,
        change_pct   REAL,
        volume       REAL,
        timestamp    TEXT NOT NULL,
        UNIQUE(date, ticker)
    )
""")

# Metadata table — tracks when agent last ran
cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_runs (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        run_date    TEXT NOT NULL,
        assets_stored INTEGER,
        status      TEXT,
        timestamp   TEXT NOT NULL
    )
""")

conn.commit()
print(f"  ✅ Database ready: {DB_FILE}")

# -----------------------------------------
# STEP 3 — Store today's prices
# Combines all asset classes into one table
# UNIQUE(date, ticker) prevents duplicates
# if agent runs twice in one day
# -----------------------------------------
print(f"\n  💾 Storing today's prices...")

today      = date.today().strftime("%Y-%m-%d")
stored     = 0
skipped    = 0
errors     = 0

# Map asset classes to their data
asset_classes = {
    "stock":  market_data.get("big_5_stocks", []) + market_data.get("potential_stocks", []),
    "fund":   market_data.get("mutual_funds", []),
    "crypto": market_data.get("major_cryptos", []) + market_data.get("potential_tokens", [])
}

for asset_class, assets in asset_classes.items():
    for asset in assets:
        ticker = asset.get("ticker")
        name   = asset.get("name", ticker)
        price  = asset.get("price")
        change = asset.get("change_pct", 0)

        if not price:
            errors += 1
            continue

        try:
            cursor.execute("""
                INSERT OR IGNORE INTO price_history
                (date, ticker, name, asset_class, price, change_pct, volume, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (today, ticker, name, asset_class, price, change, 0, timestamp))

            if cursor.rowcount > 0:
                stored += 1
            else:
                skipped += 1

        except Exception as e:
            errors += 1
            print(f"    ❌ Error storing {ticker}: {str(e)}")

conn.commit()
print(f"  ✅ Stored: {stored} | Skipped (already exists): {skipped} | Errors: {errors}")

# -----------------------------------------
# STEP 4 — TREND ANALYSIS
# This is where History Keeper adds value
# beyond just storing data
# Calculate performance over time periods
# -----------------------------------------
print(f"\n  📈 Calculating trends...")

def get_price_on_date(cursor, ticker, target_date):
    cursor.execute("""
        SELECT price FROM price_history
        WHERE ticker = ? AND date <= ?
        ORDER BY date DESC LIMIT 1
    """, (ticker, target_date))
    row = cursor.fetchone()
    return row[0] if row else None

def calc_change(current, historical):
    if current and historical and historical != 0:
        return round((current - historical) / historical * 100, 2)
    return None

# Date ranges for trend analysis
today_dt    = date.today()
day_7_ago   = (today_dt - timedelta(days=7)).strftime("%Y-%m-%d")
day_30_ago  = (today_dt - timedelta(days=30)).strftime("%Y-%m-%d")
day_90_ago  = (today_dt - timedelta(days=90)).strftime("%Y-%m-%d")

# Get all tickers
cursor.execute("SELECT DISTINCT ticker, name, asset_class FROM price_history")
all_tickers = cursor.fetchall()

trends      = []
top_gainers = []
top_losers  = []

for ticker, name, asset_class in all_tickers:
    # Get current price
    cursor.execute("""
        SELECT price FROM price_history
        WHERE ticker = ? ORDER BY date DESC LIMIT 1
    """, (ticker,))
    current_row   = cursor.fetchone()
    current_price = current_row[0] if current_row else None

    if not current_price:
        continue

    # Calculate performance over different periods
    price_7d  = get_price_on_date(cursor, ticker, day_7_ago)
    price_30d = get_price_on_date(cursor, ticker, day_30_ago)
    price_90d = get_price_on_date(cursor, ticker, day_90_ago)

    change_7d  = calc_change(current_price, price_7d)
    change_30d = calc_change(current_price, price_30d)
    change_90d = calc_change(current_price, price_90d)

    trend = {
        "ticker":      ticker,
        "name":        name,
        "asset_class": asset_class,
        "price":       current_price,
        "change_7d":   change_7d,
        "change_30d":  change_30d,
        "change_90d":  change_90d,
    }
    trends.append(trend)

    # Track top gainers and losers by 7 day performance
    if change_7d is not None:
        top_gainers.append((ticker, change_7d, current_price))
        top_losers.append((ticker, change_7d, current_price))

# Sort gainers and losers
top_gainers = sorted(top_gainers, key=lambda x: x[1], reverse=True)[:5]
top_losers  = sorted(top_losers,  key=lambda x: x[1])[:5]

# -----------------------------------------
# STEP 5 — How many days of history do we have
# -----------------------------------------
cursor.execute("SELECT COUNT(DISTINCT date) FROM price_history")
days_of_history = cursor.fetchone()[0]

cursor.execute("SELECT MIN(date), MAX(date) FROM price_history")
date_range = cursor.fetchone()

print(f"  ✅ {days_of_history} days of history ({date_range[0]} to {date_range[1]})")

if len(top_gainers) > 0:
    print(f"\n  🏆 7-Day Top Performers:")
    for ticker, chg, price in top_gainers[:3]:
        print(f"    {ticker}: {chg:+.2f}%")

if len(top_losers) > 0:
    print(f"\n  📉 7-Day Underperformers:")
    for ticker, chg, price in top_losers[:3]:
        print(f"    {ticker}: {chg:+.2f}%")

# -----------------------------------------
# STEP 6 — Save history_data.json
# This is the handoff TO the AI Commander
# Agent 2 completes its work and signals
# Agent 3 (AI Commander) can now proceed
# -----------------------------------------
os.makedirs("outputs", exist_ok=True)

history_output = {
    "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M"),
    "days_of_history": days_of_history,
    "date_range":      {"start": date_range[0], "end": date_range[1]},
    "trends":          trends,
    "top_gainers_7d":  [{"ticker": t, "change_7d": c, "price": p} for t,c,p in top_gainers],
    "top_losers_7d":   [{"ticker": t, "change_7d": c, "price": p} for t,c,p in top_losers],
    "summary": {
        "total_assets":    len(trends),
        "days_of_history": days_of_history,
        "best_7d":         f"{top_gainers[0][0]} {top_gainers[0][1]:+.2f}%" if top_gainers else "N/A",
        "worst_7d":        f"{top_losers[0][0]} {top_losers[0][1]:+.2f}%" if top_losers else "N/A",
    }
}

with open("outputs/history_data.json", "w") as f:
    json.dump(history_output, f, indent=2)

# Log this run
cursor.execute("""
    INSERT INTO agent_runs (run_date, assets_stored, status, timestamp)
    VALUES (?, ?, ?, ?)
""", (today, stored, "success", datetime.now().strftime("%Y-%m-%d %H:%M")))
conn.commit()
conn.close()

print(f"\n{'='*55}")
print(f"  ✅ History Keeper complete — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  📊 {days_of_history} days tracked | {len(trends)} assets analyzed")
print(f"  💾 Saved to: outputs/history_data.json")
print(f"  🗄️  Database: data/price_history.db")
print(f"  ➡️  Signaling AI Commander — handoff ready")
print(f"{'='*55}\n")
