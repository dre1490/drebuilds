"""
DreOS — Flask Web Application
Turns DreOS into a proper web application accessible from any browser

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: pip install flask
4. Run: python app.py
5. Open browser and go to: http://localhost:5000

Routes:
- /              Main dashboard
- /api/brief     Returns morning data as JSON
- /api/market    Returns market data as JSON
- /run           Triggers a fresh DreOS run
- /history       Shows price history charts
"""

from flask import Flask, jsonify, render_template_string, request
import json
import os
import subprocess
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# -----------------------------------------
# HELPER — Load JSON files
# -----------------------------------------
def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {}

def load_all_data():
    return {
        "market":  load_json("outputs/market_data.json"),
        "context": load_json("outputs/context_data.json"),
        "jira":    load_json("outputs/jira_data.json"),
        "figma":   load_json("outputs/figma_data.json"),
        "history": load_json("outputs/history_data.json"),
        "brief":   load_json("outputs/brief_data.json"),
    }

# -----------------------------------------
# DASHBOARD TEMPLATE
# This is the HTML that Flask serves
# Notice it uses {{ }} to insert Python data
# That's called templating — dynamic HTML
# -----------------------------------------
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="300">
<title>DreOS — Live Dashboard</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#080c14; color:#e2e8f0; }

.header { background:#1F3864; padding:16px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #2E75B6; }
.header h1 { color:white; font-size:20px; letter-spacing:2px; }
.header .meta { color:#aac4e0; font-size:12px; text-align:right; }

.kpi-bar { background:#1a2535; padding:10px 24px; display:flex; gap:16px; flex-wrap:wrap; border-bottom:1px solid #2a3a4a; }
.kpi { background:#1F3864; padding:8px 16px; border-radius:6px; text-align:center; min-width:130px; }
.kpi-label { font-size:9px; color:#aac4e0; text-transform:uppercase; letter-spacing:1px; }
.kpi-value { font-size:15px; font-weight:bold; color:white; margin-top:2px; }
.green { color:#70AD47; } .red { color:#C00000; } .blue { color:#00d4ff; }

.grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; padding:16px 24px; }
.grid-wide { display:grid; grid-template-columns:1fr 1fr; gap:12px; padding:0 24px 16px; }
.card { background:#1a2535; border-radius:8px; padding:14px; border:1px solid #2a3a4a; }
.card-title { font-size:10px; text-transform:uppercase; letter-spacing:1px; color:#2E75B6; margin-bottom:10px; font-weight:bold; }

table { width:100%; border-collapse:collapse; font-size:12px; }
th { text-align:left; padding:4px 6px; color:#aac4e0; font-size:10px; border-bottom:1px solid #2a3a4a; }
td { padding:4px 6px; border-bottom:1px solid #1f2f3f; }
tr:hover { background:#1f2f3f; }

.news-item { margin-bottom:8px; padding-bottom:8px; border-bottom:1px solid #2a3a4a; }
.news-source { font-size:9px; color:#aac4e0; display:block; margin-bottom:2px; }
.news-title { font-size:11px; color:#cce0ff; text-decoration:none; line-height:1.4; }
.news-title:hover { color:white; }

.progress-bg { background:#0f1923; border-radius:8px; height:10px; margin:6px 0; }
.progress-fill { height:10px; border-radius:8px; background:linear-gradient(90deg,#2E75B6,#70AD47); }

.btn { display:inline-block; padding:10px 20px; border-radius:6px; text-decoration:none; font-size:12px; font-weight:bold; letter-spacing:1px; cursor:pointer; border:none; margin:4px; transition:all 0.2s; }
.btn-primary { background:#00d4ff; color:#080c14; }
.btn-primary:hover { background:white; }
.btn-secondary { background:#1a2535; color:#aac4e0; border:1px solid #2a3a4a; }
.btn-secondary:hover { border-color:#00d4ff; color:#00d4ff; }
.btn-danger { background:#C00000; color:white; }

.brief-text { font-size:12px; line-height:1.8; color:#cce0ff; }
.weather-temp { font-size:32px; font-weight:bold; color:white; }
.forecast-row { display:flex; gap:6px; margin-top:10px; }
.forecast-day { flex:1; background:#0f1923; border-radius:6px; padding:6px; text-align:center; font-size:10px; }
.forecast-date { color:#aac4e0; }
.forecast-desc { color:white; margin:3px 0; }
.forecast-temp { color:#FFC000; }

.status-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }
.dot-green { background:#70AD47; }
.dot-red { background:#C00000; }

footer { background:#1F3864; padding:12px 24px; text-align:center; color:#aac4e0; font-size:11px; border-top:1px solid #2a3a4a; }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>⚡ DreOS LIVE DASHBOARD</h1>
    <div style="color:#aac4e0;font-size:11px;">Personal Intelligence Hub</div>
  </div>
  <div class="meta">
    {{ date }}<br>
    Last updated: {{ timestamp }}<br>
    <span style="color:#00d4ff;">● LIVE</span>
    <span style="color:#aac4e0;font-size:10px;"> — refreshes every 5 min</span>
  </div>
</div>

<div class="kpi-bar">
  <div class="kpi">
    <div class="kpi-label">Top Gainer</div>
    <div class="kpi-value green">{{ top_gainer }}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Top Loser</div>
    <div class="kpi-value red">{{ top_loser }}</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Gainers / Losers</div>
    <div class="kpi-value blue">{{ gainers }} ▲ / {{ losers }} ▼</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">DreOS Progress</div>
    <div class="kpi-value blue">{{ jira_pct }}% Complete</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">History</div>
    <div class="kpi-value blue">{{ days_history }} Days</div>
  </div>
  <div class="kpi">
    <div class="kpi-label">Actions</div>
    <div>
      <a href="/run" class="btn btn-primary">▶ RUN</a>
      <a href="/api/brief" class="btn btn-secondary">API</a>
    </div>
  </div>
</div>

<div class="grid">
  <!-- Big 5 Stocks -->
  <div class="card">
    <div class="card-title">📊 Big 5 Stocks</div>
    <table>
      <tr><th>Ticker</th><th>Price</th><th>Today</th></tr>
      {% for s in big_5 %}
      <tr>
        <td><strong>{{ s.ticker }}</strong></td>
        <td>${{ "{:,.2f}".format(s.price) }}</td>
        <td style="color:{{ '#70AD47' if s.change_pct >= 0 else '#C00000' }}">
          {{ "▲" if s.change_pct >= 0 else "▼" }} {{ "{:.2f}".format(s.change_pct|abs) }}%
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <!-- Potential Stocks -->
  <div class="card">
    <div class="card-title">🚀 Potential Stocks</div>
    <table>
      <tr><th>Ticker</th><th>Price</th><th>Today</th></tr>
      {% for s in potential %}
      <tr>
        <td><strong>{{ s.ticker }}</strong></td>
        <td>${{ "{:,.2f}".format(s.price) }}</td>
        <td style="color:{{ '#70AD47' if s.change_pct >= 0 else '#C00000' }}">
          {{ "▲" if s.change_pct >= 0 else "▼" }} {{ "{:.2f}".format(s.change_pct|abs) }}%
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <!-- Major Cryptos -->
  <div class="card">
    <div class="card-title">🪙 Major Cryptos</div>
    <table>
      <tr><th>Token</th><th>Price</th><th>24h</th></tr>
      {% for s in cryptos %}
      <tr>
        <td><strong>{{ s.ticker }}</strong></td>
        <td>${{ "{:,.2f}".format(s.price) }}</td>
        <td style="color:{{ '#70AD47' if s.change_pct >= 0 else '#C00000' }}">
          {{ "▲" if s.change_pct >= 0 else "▼" }} {{ "{:.2f}".format(s.change_pct|abs) }}%
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <!-- Potential Tokens -->
  <div class="card">
    <div class="card-title">⚡ Potential Tokens</div>
    <table>
      <tr><th>Token</th><th>Price</th><th>24h</th></tr>
      {% for s in tokens %}
      <tr>
        <td><strong>{{ s.ticker }}</strong></td>
        <td>${{ "{:,.2f}".format(s.price) }}</td>
        <td style="color:{{ '#70AD47' if s.change_pct >= 0 else '#C00000' }}">
          {{ "▲" if s.change_pct >= 0 else "▼" }} {{ "{:.2f}".format(s.change_pct|abs) }}%
        </td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <!-- Mutual Funds -->
  <div class="card">
    <div class="card-title">📈 Mutual Funds</div>
    <table>
      <tr><th>Ticker</th><th>Fund</th><th>NAV</th></tr>
      {% for s in funds %}
      <tr>
        <td><strong>{{ s.ticker }}</strong></td>
        <td style="font-size:10px;">{{ s.name[:20] }}</td>
        <td>${{ "{:,.2f}".format(s.price) }}</td>
      </tr>
      {% endfor %}
    </table>
  </div>

  <!-- Weather -->
  <div class="card">
    <div class="card-title">🌤️ Weather — Bedford NH</div>
    <div style="display:flex;justify-content:space-between;align-items:center;">
      <div>
        <div class="weather-temp">{{ current_weather.temperature }}°F</div>
        <div style="color:#aac4e0;font-size:12px;">{{ current_weather.description }}</div>
      </div>
      <div style="text-align:right;font-size:11px;color:#aac4e0;">
        💨 {{ current_weather.wind_mph }} mph<br>
        🌧️ {{ current_weather.precip_in }} in
      </div>
    </div>
    <div class="forecast-row">
      {% for f in forecast %}
      <div class="forecast-day">
        <div class="forecast-date">{{ f.date[5:] }}</div>
        <div class="forecast-desc">{{ f.description[:12] }}</div>
        <div class="forecast-temp">{{ f.low }}°-{{ f.high }}°F</div>
      </div>
      {% endfor %}
    </div>
  </div>
</div>

<div class="grid-wide">
  <!-- News -->
  <div class="card">
    <div class="card-title">📰 AI & Finance Headlines</div>
    <div style="margin-bottom:10px;">
      <div style="font-size:9px;color:#2E75B6;margin-bottom:6px;font-weight:bold;">🤖 AI NEWS</div>
      {% for h in ai_news %}
      <div class="news-item">
        <span class="news-source">{{ h.source }}</span>
        <a href="{{ h.url }}" target="_blank" class="news-title">{{ h.title[:80] }}...</a>
      </div>
      {% endfor %}
    </div>
    <div>
      <div style="font-size:9px;color:#2E75B6;margin-bottom:6px;font-weight:bold;">💰 FINANCE NEWS</div>
      {% for h in fin_news %}
      <div class="news-item">
        <span class="news-source">{{ h.source }}</span>
        <a href="{{ h.url }}" target="_blank" class="news-title">{{ h.title[:80] }}...</a>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- Right column -->
  <div style="display:flex;flex-direction:column;gap:12px;">

    <!-- AI Brief -->
    <div class="card">
      <div class="card-title">🤖 AI Morning Brief</div>
      <div class="brief-text">{{ brief_text[:400] }}...</div>
    </div>

    <!-- Project Status -->
    <div class="card">
      <div class="card-title">🎯 DreOS Project Status</div>
      <div style="font-size:11px;display:flex;justify-content:space-between;margin-bottom:4px;">
        <span>Phase Progress</span>
        <span>{{ jira_done }}/{{ jira_total }} complete</span>
      </div>
      <div class="progress-bg">
        <div class="progress-fill" style="width:{{ jira_pct }}%"></div>
      </div>
      <div style="font-size:11px;margin-top:8px;">
        <div style="color:#aac4e0;">🔄 <span style="color:white;">{{ current_phase[:45] }}</span></div>
        <div style="color:#aac4e0;margin-top:3px;">⏭️ <span style="color:white;">{{ next_phase[:45] }}</span></div>
      </div>
      <div style="margin-top:10px;padding-top:10px;border-top:1px solid #2a3a4a;font-size:11px;">
        <span class="status-dot {{ 'dot-green' if figma_active else 'dot-red' }}"></span>
        Figma: {{ figma_status }}
      </div>
    </div>

  </div>
</div>

<footer>
  ⚡ DreOS Personal Intelligence Hub &nbsp;|&nbsp;
  <a href="/api/brief" style="color:#00d4ff;">API</a> &nbsp;|&nbsp;
  <a href="/history" style="color:#00d4ff;">History</a> &nbsp;|&nbsp;
  <a href="/run" style="color:#00d4ff;">Run DreOS</a> &nbsp;|&nbsp;
  drebuilds.io
</footer>

</body>
</html>
"""

# -----------------------------------------
# ROUTES
# Each route is a URL that Flask handles
# The @ symbol is called a decorator —
# it connects the URL to the function below it
# -----------------------------------------

# Route 1 — Main Dashboard
# URL: http://localhost:5000/
@app.route("/")
def dashboard():
    data    = load_all_data()
    market  = data["market"]
    context = data["context"]
    jira    = data["jira"]
    figma   = data["figma"]
    history = data["history"]
    brief   = data["brief"]

    # Extract data for template
    big_5    = [s for s in market.get("big_5_stocks", []) if s.get("price")]
    potential= [s for s in market.get("potential_stocks", []) if s.get("price")]
    cryptos  = [s for s in market.get("major_cryptos", []) if s.get("price")]
    tokens   = [s for s in market.get("potential_tokens", []) if s.get("price")]
    funds    = [s for s in market.get("mutual_funds", []) if s.get("price")]

    mkt_sum         = market.get("summary", {})
    current_weather = context.get("weather", {}).get("current", {})
    forecast        = context.get("weather", {}).get("forecast", [])
    ai_news         = context.get("news", {}).get("ai_headlines", [])[:4]
    fin_news        = context.get("news", {}).get("finance_headlines", [])[:4]
    jira_sum        = jira.get("summary", {})
    figma_sum       = figma.get("summary", {})

    return render_template_string(DASHBOARD_TEMPLATE,
        date         = brief.get("date", date.today().strftime("%A, %B %d, %Y")),
        timestamp    = market.get("timestamp", "Not yet run"),
        top_gainer   = mkt_sum.get("top_gainer", "N/A"),
        top_loser    = mkt_sum.get("top_loser", "N/A"),
        gainers      = mkt_sum.get("gainers", 0),
        losers       = mkt_sum.get("losers", 0),
        jira_pct     = jira_sum.get("pct_complete", 0),
        jira_done    = jira_sum.get("done", 0),
        jira_total   = jira_sum.get("total_tickets", 0),
        current_phase= jira_sum.get("current_phase", "N/A"),
        next_phase   = jira_sum.get("next_phase", "N/A"),
        days_history = history.get("days_of_history", 0),
        big_5        = big_5,
        potential    = potential,
        cryptos      = cryptos,
        tokens       = tokens,
        funds        = funds,
        current_weather = type('obj', (object,), current_weather)(),
        forecast     = [type('obj', (object,), f)() for f in forecast],
        ai_news      = [type('obj', (object,), h)() for h in ai_news],
        fin_news     = [type('obj', (object,), h)() for h in fin_news],
        brief_text   = brief.get("brief", "Run DreOS to generate a brief."),
        figma_status = figma_sum.get("activity_status", "Unknown"),
        figma_active = figma_sum.get("recently_updated", False),
    )

# Route 2 — API endpoint
# URL: http://localhost:5000/api/brief
# Returns all DreOS data as JSON
# This is what other apps can query
@app.route("/api/brief")
def api_brief():
    data = load_all_data()
    return jsonify({
        "status":    "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "market":    data["market"].get("summary", {}),
        "weather":   data["context"].get("weather", {}).get("current", {}),
        "jira":      data["jira"].get("summary", {}),
        "history":   data["history"].get("summary", {}),
        "brief":     data["brief"].get("brief", "")
    })

# Route 3 — Market data only
# URL: http://localhost:5000/api/market
@app.route("/api/market")
def api_market():
    data = load_all_data()
    return jsonify(data["market"])

# Route 4 — Trigger a fresh DreOS run
# URL: http://localhost:5000/run
@app.route("/run")
def run_dreos():
    try:
        print("🔄 DreOS triggered from web interface...")
        subprocess.Popen(["python", "modules/market_pulse.py"])
        return jsonify({
            "status":  "triggered",
            "message": "DreOS market pulse is running. Refresh dashboard in 30 seconds.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Route 5 — History page
# URL: http://localhost:5000/history
@app.route("/history")
def history_page():
    data    = load_all_data()
    history = data["history"]
    trends  = history.get("trends", [])
    summary = history.get("summary", {})

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <title>DreOS — Price History</title>
    <style>
    body {{ font-family:'Segoe UI',sans-serif; background:#080c14; color:#e2e8f0; padding:24px; }}
    h1 {{ color:#00d4ff; margin-bottom:8px; }}
    .sub {{ color:#aac4e0; font-size:13px; margin-bottom:24px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th {{ text-align:left; padding:8px; background:#1F3864; color:white; }}
    td {{ padding:8px; border-bottom:1px solid #1a2535; }}
    tr:hover {{ background:#1a2535; }}
    .green {{ color:#70AD47; }} .red {{ color:#C00000; }} .gray {{ color:#64748b; }}
    a {{ color:#00d4ff; text-decoration:none; }}
    </style>
    </head>
    <body>
    <h1>📈 DreOS Price History</h1>
    <div class="sub">
        {summary.get('days_of_history', 0)} days tracked &nbsp;|&nbsp;
        Best 7d: {summary.get('best_7d', 'Building...')} &nbsp;|&nbsp;
        Worst 7d: {summary.get('worst_7d', 'Building...')} &nbsp;|&nbsp;
        <a href="/">← Back to Dashboard</a>
    </div>
    <table>
        <tr>
            <th>Ticker</th><th>Asset Class</th><th>Current Price</th>
            <th>7 Day</th><th>30 Day</th><th>90 Day</th>
        </tr>
    """

    for t in trends:
        def fmt(val):
            if val is None:
                return '<span class="gray">—</span>'
            color = 'green' if val >= 0 else 'red'
            arrow = '▲' if val >= 0 else '▼'
            return f'<span class="{color}">{arrow}{abs(val):.2f}%</span>'

        html += f"""
        <tr>
            <td><strong>{t['ticker']}</strong></td>
            <td>{t['asset_class']}</td>
            <td>${t['price']:,.2f}</td>
            <td>{fmt(t.get('change_7d'))}</td>
            <td>{fmt(t.get('change_30d'))}</td>
            <td>{fmt(t.get('change_90d'))}</td>
        </tr>"""

    html += "</table></body></html>"
    return html

# -----------------------------------------
# START THE SERVER
# debug=True means it reloads automatically
# when you save changes to the file
# -----------------------------------------
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  ⚡ DreOS Flask Web Application")
    print("="*50)
    print("  Dashboard:  http://localhost:5000")
    print("  API:        http://localhost:5000/api/brief")
    print("  Market:     http://localhost:5000/api/market")
    print("  History:    http://localhost:5000/history")
    print("  Run DreOS:  http://localhost:5000/run")
    print("="*50)
    print("  Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)
