"""
DreOS — Master Dashboard
Phase 7a: Interactive browser dashboard showing all morning data

Data source: outputs/brief_data.json

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: pip install plotly
4. Run: python modules/dashboard.py
"""

import json
import os
import webbrowser
from datetime import date
from dotenv import load_dotenv

load_dotenv()

print("\n📊 DreOS Master Dashboard — Building...\n")

# -----------------------------------------
# LOAD DATA
# -----------------------------------------
def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"  ❌ {filepath} not found — run ai_commander.py first")
        exit()

brief_data = load_json("outputs/brief_data.json")

market     = brief_data.get("market", {})
weather    = brief_data.get("weather", {})
news       = brief_data.get("news", {})
jira       = brief_data.get("jira", {})
figma      = brief_data.get("figma", {})
brief_text = brief_data.get("brief", "")
today      = brief_data.get("date", date.today().strftime("%A, %B %d, %Y"))

# Extract market data
big_5        = market.get("big_5_stocks", [])
potential    = market.get("potential_stocks", [])
cryptos      = market.get("major_cryptos", [])
tokens       = market.get("potential_tokens", [])
funds        = market.get("mutual_funds", [])
mkt_summary  = market.get("summary", {})

# Colors
DARK_BLUE  = "#1F3864"
MID_BLUE   = "#2E75B6"
GREEN      = "#70AD47"
RED        = "#C00000"
ORANGE     = "#ED7D31"
YELLOW     = "#FFC000"
WHITE      = "#FFFFFF"
LIGHT_GRAY = "#F5F5F5"

# -----------------------------------------
# BUILD HTML DASHBOARD
# Pure HTML/CSS/JS — no plotly needed
# More flexible for this layout
# -----------------------------------------
print("  🎨 Building dashboard layout...")

# Build stock rows
def stock_rows(stocks):
    rows = ""
    for s in stocks:
        if not s.get("price"):
            continue
        color  = GREEN if s["change_pct"] >= 0 else RED
        arrow  = "▲" if s["change_pct"] >= 0 else "▼"
        rows += f"""
        <tr>
            <td><strong>{s['ticker']}</strong></td>
            <td>{s['name']}</td>
            <td>${s['price']:,.2f}</td>
            <td style="color:{color}">{arrow} {abs(s['change_pct']):.2f}%</td>
        </tr>"""
    return rows

# Build news items
def news_items(headlines, emoji):
    items = ""
    for h in headlines[:5]:
        items += f"""
        <div class="news-item">
            <span class="news-source">{emoji} {h['source']}</span>
            <a href="{h['url']}" target="_blank" class="news-title">{h['title']}</a>
        </div>"""
    return items

# Weather forecast
forecast    = weather.get("forecast", [])
current_w   = weather.get("current", {})
forecast_html = ""
for f in forecast:
    forecast_html += f"""
    <div class="forecast-day">
        <div class="forecast-date">{f['date']}</div>
        <div class="forecast-desc">{f['description']}</div>
        <div class="forecast-temps">{f['low']}° — {f['high']}°F</div>
    </div>"""

# Progress bar
pct_complete  = jira.get("pct_complete", 0)
done          = jira.get("done", 0)
total_tickets = jira.get("total_tickets", 0)
current_phase = jira.get("current_phase", "N/A")
next_phase    = jira.get("next_phase", "N/A")

# KPI values
top_gainer = mkt_summary.get("top_gainer", "N/A")
top_loser  = mkt_summary.get("top_loser", "N/A")
gainers    = mkt_summary.get("gainers", 0)
losers     = mkt_summary.get("losers", 0)

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DreOS Morning Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', sans-serif; background: #0f1923; color: #e0e0e0; }}

  .header {{ background: {DARK_BLUE}; padding: 20px 30px; display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid {MID_BLUE}; }}
  .header h1 {{ color: white; font-size: 24px; letter-spacing: 2px; }}
  .header .date {{ color: #aac4e0; font-size: 14px; }}

  .kpi-bar {{ background: #1a2535; padding: 12px 30px; display: flex; gap: 20px; border-bottom: 1px solid #2a3a4a; flex-wrap: wrap; }}
  .kpi {{ background: {DARK_BLUE}; padding: 8px 16px; border-radius: 6px; text-align: center; min-width: 140px; }}
  .kpi-label {{ font-size: 10px; color: #aac4e0; text-transform: uppercase; letter-spacing: 1px; }}
  .kpi-value {{ font-size: 16px; font-weight: bold; color: white; margin-top: 2px; }}
  .kpi-value.green {{ color: {GREEN}; }}
  .kpi-value.red {{ color: {RED}; }}
  .kpi-value.orange {{ color: {ORANGE}; }}

  .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; padding: 20px 30px; }}
  .grid-wide {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 0 30px 20px; }}
  .card {{ background: #1a2535; border-radius: 10px; padding: 16px; border: 1px solid #2a3a4a; }}
  .card-title {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: {MID_BLUE}; margin-bottom: 12px; font-weight: bold; }}

  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ text-align: left; padding: 6px 8px; color: #aac4e0; font-size: 11px; border-bottom: 1px solid #2a3a4a; }}
  td {{ padding: 5px 8px; border-bottom: 1px solid #1f2f3f; }}
  tr:hover {{ background: #1f2f3f; }}

  .news-item {{ margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid #2a3a4a; }}
  .news-source {{ font-size: 10px; color: #aac4e0; display: block; margin-bottom: 3px; }}
  .news-title {{ font-size: 12px; color: #cce0ff; text-decoration: none; line-height: 1.4; }}
  .news-title:hover {{ color: white; }}

  .weather-current {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
  .weather-temp {{ font-size: 36px; font-weight: bold; color: white; }}
  .weather-desc {{ font-size: 14px; color: #aac4e0; }}
  .forecast-row {{ display: flex; gap: 8px; }}
  .forecast-day {{ flex: 1; background: #0f1923; border-radius: 6px; padding: 8px; text-align: center; }}
  .forecast-date {{ font-size: 10px; color: #aac4e0; }}
  .forecast-desc {{ font-size: 11px; color: white; margin: 4px 0; }}
  .forecast-temps {{ font-size: 12px; color: {YELLOW}; }}

  .progress-bar-bg {{ background: #0f1923; border-radius: 10px; height: 12px; margin: 8px 0; }}
  .progress-bar-fill {{ background: linear-gradient(90deg, {MID_BLUE}, {GREEN}); border-radius: 10px; height: 12px; width: {pct_complete}%; }}
  .progress-label {{ display: flex; justify-content: space-between; font-size: 11px; color: #aac4e0; }}

  .brief-text {{ font-size: 13px; line-height: 1.8; color: #cce0ff; white-space: pre-wrap; }}

  .figma-status {{ display: flex; align-items: center; gap: 8px; margin-top: 8px; }}
  .status-dot {{ width: 10px; height: 10px; border-radius: 50%; background: {GREEN}; }}
  .status-dot.inactive {{ background: {RED}; }}
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>⚡ DreOS MORNING DASHBOARD</h1>
    <div class="date">Personal Intelligence Hub — {today}</div>
  </div>
  <div style="text-align:right; color:#aac4e0; font-size:13px;">
    🌡️ {current_w.get('temperature')}°F &nbsp;|&nbsp;
    {current_w.get('description')} &nbsp;|&nbsp;
    💨 {current_w.get('wind_mph')} mph
  </div>
</div>

<div class="kpi-bar">
  <div class="kpi">
    <div class="kpi-label">Top Gainer</div>
    <div class="kpi-value green">{top_gainer}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Top Loser</div>
    <div class="kpi-value red">{top_loser}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Gainers / Losers</div>
    <div class="kpi-value orange">{gainers} ▲ / {losers} ▼</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">DreOS Progress</div>
    <div class="kpi-value orange">{pct_complete}% Complete</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Figma Status</div>
    <div class="kpi-value green">{figma.get('activity_status', 'N/A')[:20]}</div>
  </div>
</div>

<div class="grid">
  <!-- Big 5 Stocks -->
  <div class="card">
    <div class="card-title">📊 Big 5 Stocks</div>
    <table>
      <tr><th>Ticker</th><th>Name</th><th>Price</th><th>Change</th></tr>
      {stock_rows(big_5)}
    </table>
  </div>

  <!-- Potential Stocks -->
  <div class="card">
    <div class="card-title">🚀 Potential Stocks</div>
    <table>
      <tr><th>Ticker</th><th>Name</th><th>Price</th><th>Change</th></tr>
      {stock_rows(potential)}
    </table>
  </div>

  <!-- Crypto -->
  <div class="card">
    <div class="card-title">🪙 Major Cryptos</div>
    <table>
      <tr><th>Token</th><th>Name</th><th>Price</th><th>24h</th></tr>
      {stock_rows(cryptos)}
    </table>
  </div>

  <!-- Potential Tokens -->
  <div class="card">
    <div class="card-title">⚡ Potential Tokens</div>
    <table>
      <tr><th>Token</th><th>Name</th><th>Price</th><th>24h</th></tr>
      {stock_rows(tokens)}
    </table>
  </div>

  <!-- Mutual Funds -->
  <div class="card">
    <div class="card-title">📈 Mutual Funds</div>
    <table>
      <tr><th>Ticker</th><th>Fund</th><th>NAV</th></tr>
      {stock_rows(funds)}
    </table>
  </div>

  <!-- Weather -->
  <div class="card">
    <div class="card-title">🌤️ Weather — Bedford NH</div>
    <div class="weather-current">
      <div>
        <div class="weather-temp">{current_w.get('temperature')}°F</div>
        <div class="weather-desc">{current_w.get('description')}</div>
      </div>
      <div style="text-align:right; font-size:12px; color:#aac4e0;">
        💨 {current_w.get('wind_mph')} mph<br>
        🌧️ {current_w.get('precip_in')} in
      </div>
    </div>
    <div class="forecast-row">
      {forecast_html}
    </div>
  </div>
</div>

<div class="grid-wide">
  <!-- News -->
  <div class="card">
    <div class="card-title">📰 AI & Finance Headlines</div>
    <div style="margin-bottom:12px;">
      <div style="font-size:11px; color:{MID_BLUE}; margin-bottom:6px;">🤖 AI NEWS</div>
      {news_items(news.get('ai_headlines', []), '🤖')}
    </div>
    <div>
      <div style="font-size:11px; color:{MID_BLUE}; margin-bottom:6px;">💰 FINANCE NEWS</div>
      {news_items(news.get('finance_headlines', []), '💰')}
    </div>
  </div>

  <!-- Project Status + Brief -->
  <div class="card">
    <div class="card-title">🎯 DreOS Project Status</div>
    <div class="progress-label">
      <span>Phase Progress</span>
      <span>{done}/{total_tickets} phases complete</span>
    </div>
    <div class="progress-bar-bg">
      <div class="progress-bar-fill"></div>
    </div>
    <div style="font-size:12px; margin-top:8px;">
      <div style="color:#aac4e0;">🔄 Current: <span style="color:white;">{current_phase[:50]}</span></div>
      <div style="color:#aac4e0; margin-top:4px;">⏭️ Next: <span style="color:white;">{next_phase[:50]}</span></div>
    </div>
    <div style="margin-top:12px; padding-top:12px; border-top:1px solid #2a3a4a;">
      <div class="card-title">🎨 Figma Design File</div>
      <div class="figma-status">
        <div class="status-dot {'inactive' if not figma.get('recently_updated') else ''}"></div>
        <span style="font-size:12px;">{figma.get('activity_status', 'N/A')}</span>
      </div>
    </div>
    <div style="margin-top:12px; padding-top:12px; border-top:1px solid #2a3a4a;">
      <div class="card-title">🤖 AI Morning Brief</div>
      <div class="brief-text">{brief_text[:500]}...</div>
    </div>
  </div>
</div>

</body>
</html>"""

# Save and open
os.makedirs("outputs", exist_ok=True)
dashboard_file = "outputs/dreos_dashboard.html"
with open(dashboard_file, "w", encoding="utf-8") as f:
    f.write(html)

print(f"  ✅ Dashboard built successfully!")
print(f"  🌐 Opening in browser...")
webbrowser.open(f"file:///{os.path.abspath(dashboard_file)}")

print(f"\n{'='*50}")
print(f"  💾 Saved to: {dashboard_file}")
print(f"{'='*50}\n")
