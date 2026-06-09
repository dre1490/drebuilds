# monitor.py
# DreOS Phase 12 — Step 3
# Proactive monitor — runs on a schedule, alerts without being asked
# Location: DreOS\agent\monitor.py

import os
import sys
import json
import time
from datetime import datetime

# ── Path setup ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
sys.path.insert(0, os.path.join(BASE_DIR, "agent"))

from tool_registry import dispatch_tool

# ── Config ─────────────────────────────────────────────────────────────────────
CHECK_INTERVAL_MINUTES = 30       # how often to run checks
PRICE_SPIKE_THRESHOLD  = 5.0      # alert if any asset moves more than this %
MONITOR_LOG_PATH       = os.path.join(OUTPUTS_DIR, "monitor_log.json")


# ══════════════════════════════════════════════════════════════════════════════
# LOGGING — saves every monitor run to monitor_log.json
# ══════════════════════════════════════════════════════════════════════════════
def log_monitor_run(checks: list, alerts_sent: int):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "checks_run": len(checks),
        "alerts_sent": alerts_sent,
        "checks": checks
    }

    # Load existing log or start fresh
    if os.path.exists(MONITOR_LOG_PATH):
        with open(MONITOR_LOG_PATH, "r") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    else:
        log = []

    log.append(entry)

    # Keep last 100 runs only
    if len(log) > 100:
        log = log[-100:]

    with open(MONITOR_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

    print(f"[monitor] 📝 run logged → outputs/monitor_log.json")


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 1 — Price Spikes
# Scans all 25 assets for moves above the threshold
# ══════════════════════════════════════════════════════════════════════════════
def check_price_spikes() -> dict:
    print(f"[monitor] 🔍 Checking for price spikes above {PRICE_SPIKE_THRESHOLD}%...")

    result = dispatch_tool("check_price_spike", {"threshold_pct": PRICE_SPIKE_THRESHOLD})

    if result["status"] == "error":
        return {"check": "price_spikes", "status": "error", "message": result["message"]}

    spikes = result.get("spikes", [])

    if spikes:
        # Build alert message
        lines = [f"🚨 DreOS Price Alert — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
        lines.append(f"{len(spikes)} asset(s) moved more than {PRICE_SPIKE_THRESHOLD}%:\n")
        for s in spikes:
            lines.append(f"  {s['direction']} {s['ticker']}: {s['change_pct']:+.2f}% (${s['latest_price']:,.2f})")

        message = "\n".join(lines)

        dispatch_tool("send_alert", {
            "message": message,
            "subject": f"DreOS Alert — {len(spikes)} Price Spike(s) Detected"
        })

        return {"check": "price_spikes", "status": "alerted", "spike_count": len(spikes), "spikes": spikes}

    print(f"[monitor] ✅ No price spikes detected")
    return {"check": "price_spikes", "status": "clear", "spike_count": 0}


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 2 — Market Pulse + News Cross-reference
# Fetches fresh prices and top headlines, flags if any tracked ticker
# appears in the news alongside a significant price move
# ══════════════════════════════════════════════════════════════════════════════
def check_news_market_crossref() -> dict:
    print("[monitor] 🔍 Cross-referencing market data with news headlines...")

    # Get fresh market data
    market_result = dispatch_tool("get_market_data", {})
    if market_result["status"] == "error":
        return {"check": "news_crossref", "status": "error", "message": market_result["message"]}

    # Get news
    news_result = dispatch_tool("get_news", {})
    if news_result["status"] == "error":
        return {"check": "news_crossref", "status": "error", "message": news_result["message"]}

    # Pull all tracked tickers
    data = market_result["data"]
    all_assets = (
        data.get("big_5_stocks", []) +
        data.get("potential_stocks", []) +
        data.get("major_cryptos", []) +
        data.get("potential_tokens", [])
    )

    # Build a set of tickers and company names to search for in headlines
    tracked = {}
    for asset in all_assets:
        ticker = asset.get("ticker", "")
        name = asset.get("name", "")
        change = asset.get("change_pct", 0) or 0
        if ticker:
            tracked[ticker.upper()] = {"name": name, "change_pct": change}

    # Scan headlines for ticker/name mentions
    articles = news_result["data"].get("articles", [])
    hits = []

    for article in articles:
        title = article.get("title", "").upper()
        for ticker, info in tracked.items():
            name_upper = info["name"].upper()
            if ticker in title or (len(name_upper) > 3 and name_upper in title):
                hits.append({
                    "ticker": ticker,
                    "change_pct": info["change_pct"],
                    "headline": article.get("title", ""),
                    "source": article.get("source", "")
                })

    if hits:
        lines = [f"📰 DreOS News Alert — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
        lines.append(f"{len(hits)} tracked asset(s) in today's headlines:\n")
        for h in hits:
            change_str = f"{h['change_pct']:+.2f}%" if h['change_pct'] else "n/a"
            lines.append(f"  • {h['ticker']} ({change_str}) — {h['headline']} [{h['source']}]")

        message = "\n".join(lines)

        dispatch_tool("send_alert", {
            "message": message,
            "subject": f"DreOS News Alert — {len(hits)} Ticker(s) in Headlines"
        })

        return {"check": "news_crossref", "status": "alerted", "hit_count": len(hits), "hits": hits}

    print("[monitor] ✅ No tracked tickers in today's headlines")
    return {"check": "news_crossref", "status": "clear", "hit_count": 0}


# ══════════════════════════════════════════════════════════════════════════════
# CHECK 3 — Jira Overdue Tickets
# Flags any in-progress tickets that haven't moved recently
# ══════════════════════════════════════════════════════════════════════════════
def check_jira_overdue() -> dict:
    print("[monitor] 🔍 Checking Jira for stalled tickets...")

    result = dispatch_tool("get_jira_status", {})
    if result["status"] == "error":
        return {"check": "jira_overdue", "status": "error", "message": result["message"]}

    data = result["data"]
    issues = data.get("issues", [])

    # Flag anything that's In Progress
    in_progress = [i for i in issues if "progress" in i.get("status", "").lower()]

    if in_progress:
        lines = [f"📋 DreOS Jira Alert — {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
        lines.append(f"{len(in_progress)} ticket(s) currently In Progress:\n")
        for ticket in in_progress:
            lines.append(f"  • {ticket.get('key', '?')} — {ticket.get('summary', 'No summary')}")

        message = "\n".join(lines)

        dispatch_tool("send_alert", {
            "message": message,
            "subject": f"DreOS Jira Update — {len(in_progress)} Ticket(s) In Progress"
        })

        return {"check": "jira_overdue", "status": "alerted", "in_progress_count": len(in_progress)}

    print("[monitor] ✅ No stalled Jira tickets")
    return {"check": "jira_overdue", "status": "clear"}


# ══════════════════════════════════════════════════════════════════════════════
# SINGLE RUN — executes all 3 checks once
# ══════════════════════════════════════════════════════════════════════════════
def run_once():
    print("\n" + "="*60)
    print(f"🤖 DreOS Monitor — Running checks")
    print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    checks = []
    alerts_sent = 0

    # Run all checks
    r1 = check_price_spikes()
    checks.append(r1)
    if r1.get("status") == "alerted":
        alerts_sent += 1

    r2 = check_news_market_crossref()
    checks.append(r2)
    if r2.get("status") == "alerted":
        alerts_sent += 1

    r3 = check_jira_overdue()
    checks.append(r3)
    if r3.get("status") == "alerted":
        alerts_sent += 1

    # Summary
    print(f"\n[monitor] ✅ All checks complete — {alerts_sent} alert(s) sent")
    log_monitor_run(checks, alerts_sent)

    return checks


# ══════════════════════════════════════════════════════════════════════════════
# CONTINUOUS LOOP — runs every CHECK_INTERVAL_MINUTES
# ══════════════════════════════════════════════════════════════════════════════
def run_continuous():
    print("\n" + "="*60)
    print(f"🤖 DreOS Monitor — Continuous Mode")
    print(f"⏱  Checking every {CHECK_INTERVAL_MINUTES} minutes")
    print(f"🛑  Press Ctrl+C to stop")
    print("="*60)

    while True:
        try:
            run_once()
            next_check = datetime.now().strftime('%H:%M')
            print(f"\n[monitor] 💤 Sleeping {CHECK_INTERVAL_MINUTES} min — next check at {next_check}")
            time.sleep(CHECK_INTERVAL_MINUTES * 60)

        except KeyboardInterrupt:
            print("\n[monitor] 🛑 Monitor stopped by user")
            break
        except Exception as e:
            print(f"\n[monitor] ❌ Unexpected error: {e}")
            print(f"[monitor] 🔄 Retrying in 5 minutes...")
            time.sleep(300)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# Run once:       python monitor.py
# Run continuous: python monitor.py --continuous
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    if "--continuous" in sys.argv:
        run_continuous()
    else:
        run_once()
