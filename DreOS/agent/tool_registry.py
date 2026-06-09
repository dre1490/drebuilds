# tool_registry.py
# DreOS Phase 12 — Step 1
# Wraps all DreOS modules as callable tools for the autonomous agent
# Location: DreOS\agent\tool_registry.py

import sys
import os
import json
import sqlite3
import smtplib
import subprocess
from email.mime.text import MIMEText
from datetime import datetime

# ── Path setup — lets us import from modules\ and agent\ ──────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODULES_DIR = os.path.join(BASE_DIR, "modules")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DATA_DIR = os.path.join(BASE_DIR, "data")

sys.path.insert(0, MODULES_DIR)
sys.path.insert(0, BASE_DIR)

# ── Load credentials ───────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_EMAIL = "1490dre@gmail.com"


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 1 — get_market_data
# Runs market_pulse.py and returns the latest prices for all 25 assets
# ══════════════════════════════════════════════════════════════════════════════
def get_market_data() -> dict:
    """
    Fetches current prices for all 25 tracked assets.
    Returns a dict with asset symbols as keys and price data as values.
    """
    try:
        script_path = os.path.join(MODULES_DIR, "market_pulse.py")
        subprocess.run([sys.executable, script_path], cwd=BASE_DIR, check=True)

        market_path = os.path.join(OUTPUTS_DIR, "market_data.json")
        with open(market_path, "r") as f:
            data = json.load(f)

        print("[tool_registry] ✅ get_market_data — loaded market_data.json")
        return {"status": "success", "data": data}

    except Exception as e:
        print(f"[tool_registry] ❌ get_market_data failed: {e}")
        return {"status": "error", "message": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 2 — get_news
# Runs weather_news.py and returns headlines + weather
# ══════════════════════════════════════════════════════════════════════════════
def get_news() -> dict:
    """
    Fetches today's top headlines and weather summary.
    Returns a dict with articles list and weather conditions.
    """
    try:
        script_path = os.path.join(MODULES_DIR, "weather_news.py")
        subprocess.run([sys.executable, script_path], cwd=BASE_DIR, check=True)

        context_path = os.path.join(OUTPUTS_DIR, "context_data.json")
        with open(context_path, "r") as f:
            data = json.load(f)

        print("[tool_registry] ✅ get_news — loaded context_data.json")
        return {"status": "success", "data": data}

    except Exception as e:
        print(f"[tool_registry] ❌ get_news failed: {e}")
        return {"status": "error", "message": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 3 — get_history
# Queries price_history.db for a specific ticker's recent history
# ══════════════════════════════════════════════════════════════════════════════
def get_history(ticker: str, days: int = 7) -> dict:
    """
    Pulls the last N days of price history for a given ticker from SQLite.
    Args:
        ticker: Asset symbol e.g. 'AAPL', 'BTC', 'VFIAX'
        days:   How many days back to look (default 7)
    Returns a dict with ticker, history list, and basic trend stats.
    """
    try:
        db_path = os.path.join(DATA_DIR, "price_history.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date, price, volume
            FROM price_history
            WHERE ticker = ?
            ORDER BY date DESC
            LIMIT ?
        """, (ticker.upper(), days))

        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return {"status": "no_data", "ticker": ticker, "message": f"No history found for {ticker}"}

        history = [{"date": r[0], "price": r[1], "volume": r[2]} for r in rows]

        # Basic trend: compare first and last price in the window
        latest_price = history[0]["price"]
        oldest_price = history[-1]["price"]
        change_pct = ((latest_price - oldest_price) / oldest_price) * 100 if oldest_price else 0

        print(f"[tool_registry] ✅ get_history — {ticker} | {len(history)} records | {change_pct:.2f}% trend")
        return {
            "status": "success",
            "ticker": ticker,
            "days": days,
            "history": history,
            "latest_price": latest_price,
            "change_pct": round(change_pct, 2),
            "trend": "up" if change_pct > 0 else "down"
        }

    except Exception as e:
        print(f"[tool_registry] ❌ get_history failed for {ticker}: {e}")
        return {"status": "error", "ticker": ticker, "message": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 4 — get_jira_status
# Runs jira_tracker.py and returns open tickets from the KAN board
# ══════════════════════════════════════════════════════════════════════════════
def get_jira_status() -> dict:
    """
    Fetches current Jira ticket status from the KAN board.
    Returns a dict with open, in-progress, and done ticket counts + details.
    """
    try:
        script_path = os.path.join(MODULES_DIR, "jira_tracker.py")
        subprocess.run([sys.executable, script_path], cwd=BASE_DIR, check=True)

        jira_path = os.path.join(OUTPUTS_DIR, "jira_data.json")
        with open(jira_path, "r") as f:
            data = json.load(f)

        print("[tool_registry] ✅ get_jira_status — loaded jira_data.json")
        return {"status": "success", "data": data}

    except Exception as e:
        print(f"[tool_registry] ❌ get_jira_status failed: {e}")
        return {"status": "error", "message": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 5 — get_figma_status
# Runs figma_status.py and returns recent file activity
# ══════════════════════════════════════════════════════════════════════════════
def get_figma_status() -> dict:
    """
    Checks Figma file activity for the DreOS design file.
    Returns last modified time and recent changes.
    """
    try:
        script_path = os.path.join(MODULES_DIR, "figma_status.py")
        subprocess.run([sys.executable, script_path], cwd=BASE_DIR, check=True)

        figma_path = os.path.join(OUTPUTS_DIR, "figma_data.json")
        with open(figma_path, "r") as f:
            data = json.load(f)

        print("[tool_registry] ✅ get_figma_status — loaded figma_data.json")
        return {"status": "success", "data": data}

    except Exception as e:
        print(f"[tool_registry] ❌ get_figma_status failed: {e}")
        return {"status": "error", "message": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 6 — check_price_spike
# Checks if any asset has moved more than a threshold % since yesterday
# ══════════════════════════════════════════════════════════════════════════════
def check_price_spike(threshold_pct: float = 5.0) -> dict:
    """
    Scans all tracked assets for price moves exceeding the threshold.
    Args:
        threshold_pct: Alert if price moved more than this % (default 5.0)
    Returns a list of assets that triggered the threshold.
    """
    try:
        db_path = os.path.join(DATA_DIR, "price_history.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get last 2 days for each ticker
        cursor.execute("""
            SELECT ticker, date, price
            FROM price_history
            WHERE date >= date('now', '-2 days')
            ORDER BY ticker, date DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        # Group by ticker
        ticker_prices = {}
        for ticker, date, price in rows:
            if ticker not in ticker_prices:
                ticker_prices[ticker] = []
            ticker_prices[ticker].append((date, price))

        spikes = []
        for ticker, prices in ticker_prices.items():
            if len(prices) >= 2:
                latest = prices[0][1]
                previous = prices[1][1]
                change_pct = ((latest - previous) / previous) * 100 if previous else 0
                if abs(change_pct) >= threshold_pct:
                    spikes.append({
                        "ticker": ticker,
                        "latest_price": latest,
                        "previous_price": previous,
                        "change_pct": round(change_pct, 2),
                        "direction": "🔺 UP" if change_pct > 0 else "🔻 DOWN"
                    })

        print(f"[tool_registry] ✅ check_price_spike — {len(spikes)} spike(s) found above {threshold_pct}%")
        return {
            "status": "success",
            "threshold_pct": threshold_pct,
            "spike_count": len(spikes),
            "spikes": spikes
        }

    except Exception as e:
        print(f"[tool_registry] ❌ check_price_spike failed: {e}")
        return {"status": "error", "message": str(e)}


# ══════════════════════════════════════════════════════════════════════════════
# TOOL 7 — send_alert
# Prints to terminal AND sends a Gmail alert email
# ══════════════════════════════════════════════════════════════════════════════
def send_alert(message: str, subject: str = "DreOS Agent Alert") -> dict:
    """
    Sends an alert via terminal print and Gmail email.
    Args:
        message: The alert body text
        subject: Email subject line (default: 'DreOS Agent Alert')
    Returns status of both delivery methods.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {message}"

    # ── Terminal output ────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"🚨 DREOS ALERT — {timestamp}")
    print("="*60)
    print(message)
    print("="*60 + "\n")

    # ── Gmail delivery ─────────────────────────────────────────────────────────
    email_status = "not_attempted"
    if GMAIL_USER and GMAIL_APP_PASSWORD:
        try:
            msg = MIMEText(full_message)
            msg["Subject"] = subject
            msg["From"] = GMAIL_USER
            msg["To"] = ALERT_EMAIL

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_USER, ALERT_EMAIL, msg.as_string())

            email_status = "sent"
            print(f"[tool_registry] ✅ send_alert — email sent to {ALERT_EMAIL}")

        except Exception as e:
            email_status = f"failed: {e}"
            print(f"[tool_registry] ❌ send_alert email failed: {e}")
    else:
        email_status = "no_credentials"
        print("[tool_registry] ⚠️  send_alert — GMAIL_USER or GMAIL_APP_PASSWORD not set in .env")

    return {
        "status": "success",
        "terminal": "printed",
        "email": email_status,
        "timestamp": timestamp
    }


# ══════════════════════════════════════════════════════════════════════════════
# TOOL REGISTRY — the master list Groq will see
# This is what gets passed to the autonomous agent as available tools
# ══════════════════════════════════════════════════════════════════════════════
TOOL_REGISTRY = {
    "get_market_data": {
        "function": get_market_data,
        "description": "Fetch current prices for all 25 tracked assets (stocks, crypto, funds)",
        "parameters": {}
    },
    "get_news": {
        "function": get_news,
        "description": "Fetch today's top news headlines and weather summary",
        "parameters": {}
    },
    "get_history": {
        "function": get_history,
        "description": "Get recent price history for a specific ticker from the database",
        "parameters": {
            "ticker": "Asset symbol e.g. AAPL, BTC, VFIAX (required)",
            "days": "Number of days to look back, default 7 (optional)"
        }
    },
    "get_jira_status": {
        "function": get_jira_status,
        "description": "Get current status of all Jira tickets on the KAN board",
        "parameters": {}
    },
    "get_figma_status": {
        "function": get_figma_status,
        "description": "Check recent activity on the DreOS Figma design file",
        "parameters": {}
    },
    "check_price_spike": {
        "function": check_price_spike,
        "description": "Scan all assets for price moves above a threshold percentage",
        "parameters": {
            "threshold_pct": "Alert threshold percentage, default 5.0 (optional)"
        }
    },
    "send_alert": {
        "function": send_alert,
        "description": "Send an alert to terminal and Gmail email",
        "parameters": {
            "message": "The alert message body (required)",
            "subject": "Email subject line, default 'DreOS Agent Alert' (optional)"
        }
    }
}


# ══════════════════════════════════════════════════════════════════════════════
# TOOL DISPATCHER — called by the agent to execute any tool by name
# ══════════════════════════════════════════════════════════════════════════════
def dispatch_tool(tool_name: str, params: dict = None) -> dict:
    """
    Executes a tool from the registry by name with optional parameters.
    Args:
        tool_name: Name of the tool to run (must match TOOL_REGISTRY key)
        params:    Dict of keyword arguments to pass to the tool function
    Returns the tool's output dict.
    """
    if tool_name not in TOOL_REGISTRY:
        available = list(TOOL_REGISTRY.keys())
        return {"status": "error", "message": f"Unknown tool '{tool_name}'. Available: {available}"}

    tool = TOOL_REGISTRY[tool_name]
    fn = tool["function"]
    params = params or {}

    print(f"[tool_registry] 🔧 dispatching → {tool_name}({params})")

    try:
        result = fn(**params)
        return result
    except TypeError as e:
        return {"status": "error", "message": f"Bad params for {tool_name}: {e}"}


# ══════════════════════════════════════════════════════════════════════════════
# QUICK TEST — run this file directly to verify all tools load
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "="*60)
    print("DreOS Tool Registry — Phase 12 Step 1")
    print("="*60)
    print(f"\n{len(TOOL_REGISTRY)} tools registered:\n")
    for name, info in TOOL_REGISTRY.items():
        params = list(info["parameters"].keys())
        param_str = f"({', '.join(params)})" if params else "(no params)"
        print(f"  ✅ {name}{param_str}")
        print(f"     {info['description']}\n")

    print("="*60)
    print("Tool registry loaded successfully. Ready for Phase 12 Step 2.")
    print("="*60 + "\n")

