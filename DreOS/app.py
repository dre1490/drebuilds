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

from flask import Flask, jsonify, render_template_string, request, session
import json
import os
import subprocess
from datetime import datetime, date
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
app.secret_key = "dreos-secret-key-2026"

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
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root {
  --bg:#0a0e1a; --surface:#111827; --card:#141d2e; --border:#1e293b;
  --accent:#3b82f6; --accent2:#10b981; --accent3:#f59e0b;
  --red:#ef4444; --green:#10b981; --purple:#8b5cf6;
  --text:#e2e8f0; --muted:#64748b; --white:#ffffff;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }
a { text-decoration:none; }

.header { background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%); padding:0 28px; height:60px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border); position:sticky; top:0; z-index:100; }
.logo { display:flex; align-items:center; gap:10px; }
.logo-icon { width:32px; height:32px; background:linear-gradient(135deg,#3b82f6,#8b5cf6); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:16px; }
.logo-text { font-family:'Space Mono',monospace; font-size:14px; font-weight:700; color:var(--white); letter-spacing:2px; }
.logo-sub { font-size:10px; color:var(--muted); letter-spacing:1px; }
.header-right { display:flex; align-items:center; gap:10px; }
.live-badge { display:flex; align-items:center; gap:6px; background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.3); padding:4px 10px; border-radius:20px; font-size:11px; color:var(--green); }
.live-dot { width:6px; height:6px; background:var(--green); border-radius:50%; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
.header-meta { font-size:10px; color:var(--muted); text-align:right; line-height:1.6; }
.nav-btn { padding:6px 14px; border-radius:6px; font-size:12px; font-weight:600; transition:all 0.2s; cursor:pointer; border:none; }
.nav-btn-primary { background:var(--accent); color:white; }
.nav-btn-primary:hover { background:#2563eb; }
.nav-btn-ghost { background:transparent; border:1px solid var(--border); color:var(--muted); }
.nav-btn-ghost:hover { border-color:var(--accent); color:var(--accent); }
.nav-btn-agent { background:linear-gradient(135deg,#7c3aed,#3b82f6); color:white; box-shadow:0 0 12px rgba(124,58,237,0.4); }
.nav-btn-agent:hover { box-shadow:0 0 20px rgba(124,58,237,0.7); transform:translateY(-1px); }

.kpi-strip { background:var(--surface); padding:10px 28px; display:flex; gap:8px; flex-wrap:wrap; border-bottom:1px solid var(--border); align-items:center; }
.kpi-pill { display:flex; align-items:center; gap:8px; background:var(--card); border:1px solid var(--border); border-radius:8px; padding:7px 12px; transition:border-color 0.2s; }
.kpi-pill:hover { border-color:var(--accent); }
.kpi-label { font-size:9px; color:var(--muted); text-transform:uppercase; letter-spacing:1px; white-space:nowrap; }
.kpi-val { font-size:13px; font-weight:700; white-space:nowrap; }
.kpi-div { width:1px; height:20px; background:var(--border); margin:0 2px; }
.green{color:var(--green)} .red{color:var(--red)} .blue{color:var(--accent)} .amber{color:var(--accent3)} .purple{color:var(--purple)}

.main { padding:18px 28px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }
.main-wide { padding:0 28px 18px; display:grid; grid-template-columns:1.2fr 0.8fr; gap:12px; }

.card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:14px; transition:border-color 0.2s,box-shadow 0.2s; }
.card:hover { border-color:rgba(59,130,246,0.3); box-shadow:0 4px 20px rgba(0,0,0,0.3); }
.card-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:11px; }
.card-title { font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; color:var(--muted); }
.card-badge { font-size:9px; padding:2px 8px; border-radius:10px; font-weight:600; letter-spacing:0.5px; }
.badge-blue   { background:rgba(59,130,246,0.15); color:#60a5fa; border:1px solid rgba(59,130,246,0.3); }
.badge-green  { background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3); }
.badge-amber  { background:rgba(245,158,11,0.15);  color:#fbbf24; border:1px solid rgba(245,158,11,0.3); }
.badge-purple { background:rgba(139,92,246,0.15);  color:#a78bfa; border:1px solid rgba(139,92,246,0.3); }

table { width:100%; border-collapse:collapse; }
th { font-size:9px; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; padding:5px 6px; border-bottom:1px solid var(--border); text-align:left; }
td { padding:6px 6px; border-bottom:1px solid rgba(30,41,59,0.5); font-size:12px; }
tr:last-child td { border-bottom:none; }
tr:hover td { background:rgba(59,130,246,0.05); }
.ticker-cell { font-weight:700; font-family:'Space Mono',monospace; font-size:11px; }
.price-cell  { font-weight:600; color:var(--white); }
.change-up   { color:var(--green); font-weight:600; font-size:11px; }
.change-down { color:var(--red);   font-weight:600; font-size:11px; }

.news-item { padding:7px 0; border-bottom:1px solid rgba(30,41,59,0.5); }
.news-item:last-child { border-bottom:none; padding-bottom:0; }
.news-source { font-size:9px; color:var(--muted); text-transform:uppercase; letter-spacing:0.5px; margin-bottom:2px; }
.news-link { font-size:11px; color:#93c5fd; line-height:1.5; display:block; }
.news-link:hover { color:white; }

.weather-temp { font-size:40px; font-weight:300; color:var(--white); line-height:1; }
.weather-desc { font-size:12px; color:var(--muted); margin-top:3px; }
.forecast-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:5px; margin-top:10px; }
.forecast-item { background:rgba(0,0,0,0.2); border:1px solid var(--border); border-radius:7px; padding:7px; text-align:center; }
.f-date { font-size:9px; color:var(--muted); margin-bottom:3px; }
.f-desc { font-size:10px; color:var(--text); margin-bottom:3px; }
.f-temp { font-size:10px; font-weight:600; color:var(--accent3); }

.brief-text { font-size:12px; line-height:1.9; color:#cbd5e1; }

.project-tabs { display:flex; gap:5px; margin-bottom:10px; flex-wrap:wrap; }
.proj-tab { padding:3px 10px; border-radius:20px; font-size:10px; font-weight:600; cursor:pointer; border:1px solid var(--border); color:var(--muted); background:transparent; transition:all 0.2s; }
.proj-tab:hover { border-color:var(--accent); color:var(--accent); }
.proj-tab.active { background:var(--accent); color:white; border-color:var(--accent); }
.project-view { display:none; }
.project-view.active { display:block; }
.proj-phase { display:flex; align-items:center; gap:7px; padding:4px 0; border-bottom:1px solid rgba(30,41,59,0.4); font-size:11px; }
.proj-phase:last-child { border-bottom:none; }
.phase-dot { width:7px; height:7px; border-radius:50%; flex-shrink:0; }
.phase-done     { background:var(--green); }
.phase-progress { background:var(--accent); box-shadow:0 0 6px var(--accent); }
.phase-todo     { background:var(--border); }
.phase-name { flex:1; color:var(--text); }
.phase-status { font-size:9px; padding:1px 6px; border-radius:10px; font-weight:600; }
.status-done     { background:rgba(16,185,129,0.15); color:#34d399; }
.status-progress { background:rgba(59,130,246,0.15); color:#60a5fa; }
.status-todo     { background:rgba(100,116,139,0.15); color:#94a3b8; }
.progress-track { background:rgba(0,0,0,0.3); border-radius:4px; height:5px; margin:6px 0 4px; overflow:hidden; }
.progress-fill-ft { height:100%; border-radius:4px; background:linear-gradient(90deg,var(--accent),var(--accent2)); }
.chart-view { display:none; }
.chart-view.active { display:block; }
.table-view.hidden { display:none; }
.chart-toggle { background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.3); color:#60a5fa; padding:2px 8px; border-radius:10px; font-size:9px; font-weight:600; cursor:pointer; transition:all 0.2s; }
.chart-toggle:hover { background:rgba(59,130,246,0.3); }
.chart-toggle.active { background:rgba(59,130,246,0.4); color:white; }
.line-chart-wrap { position:relative; width:100%; height:130px; margin-top:6px; }
.line-chart-wrap svg { width:100%; height:100%; }
.chart-labels { display:flex; justify-content:space-between; font-size:8px; color:var(--muted); margin-top:2px; padding:0 2px; }
.chart-stats { display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; }
.chart-stat-val { font-size:13px; font-weight:700; color:var(--white); }
.chart-stat-lbl { font-size:9px; color:var(--muted); }
.chart-loading { display:flex; align-items:center; justify-content:center; height:130px; color:var(--muted); font-size:11px; }
.figma-row { display:flex; align-items:center; gap:8px; padding:7px 0; font-size:11px; color:var(--muted); border-top:1px solid var(--border); margin-top:7px; }

footer { background:var(--surface); border-top:1px solid var(--border); padding:11px 28px; display:flex; justify-content:space-between; align-items:center; font-size:11px; color:var(--muted); }
.footer-links { display:flex; gap:14px; }
.footer-links a { color:var(--muted); transition:color 0.2s; }
.footer-links a:hover { color:var(--accent); }
</style>
</head>
<body>

<div class="header">
  <div class="logo">
    <div class="logo-icon">⚡</div>
    <div>
      <div class="logo-text">DreOS</div>
      <div class="logo-sub">PERSONAL INTELLIGENCE HUB</div>
    </div>
  </div>
  <div class="header-right">
    <div class="live-badge"><div class="live-dot"></div>LIVE</div>
    <div class="header-meta">{{ date }}<br>Updated: {{ timestamp }}</div>
    <a href="/run" class="nav-btn nav-btn-primary">▶ Run</a>
    <a href="/chat" class="nav-btn nav-btn-agent">🤖 Agent</a>
    <a href="/history" class="nav-btn nav-btn-ghost">📈 History</a>
    <a href="/api/brief" class="nav-btn nav-btn-ghost">API</a>
  </div>
</div>

<div class="kpi-strip">
  <div class="kpi-pill"><div class="kpi-label">Top Gainer</div><div class="kpi-val green">{{ top_gainer }}</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-pill"><div class="kpi-label">Top Loser</div><div class="kpi-val red">{{ top_loser }}</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-pill"><div class="kpi-label">Market</div><div class="kpi-val blue">{{ gainers }}▲ {{ losers }}▼</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-pill"><div class="kpi-label">DreOS</div><div class="kpi-val amber">{{ jira_pct }}% Built</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-pill"><div class="kpi-label">History</div><div class="kpi-val purple">{{ days_history }}d</div></div>
  <div class="kpi-div"></div>
  <div class="kpi-pill"><div class="kpi-label">Weather</div><div class="kpi-val blue">{{ current_weather.temperature }}°F</div></div>
</div>

<div class="main">
  <div class="card">
    <div class="card-header"><div class="card-title">Big 5 Stocks</div><div style="display:flex;gap:6px;align-items:center;"><span class="card-badge badge-blue">S&P</span><button class="chart-toggle" onclick="toggleChart('big5')">📊 Chart</button></div></div>
    <div id="big5-table" class="table-view"><table><tr><th>Ticker</th><th>Price</th><th>Change</th></tr>
    {% for s in big_5 %}<tr><td class="ticker-cell">{{ s.ticker }}</td><td class="price-cell">${{ "{:,.2f}".format(s.price) }}</td><td class="{{ 'change-up' if s.change_pct >= 0 else 'change-down' }}">{{ "▲" if s.change_pct >= 0 else "▼" }}{{ "{:.2f}".format(s.change_pct|abs) }}%</td></tr>{% endfor %}</table></div>
    <div id="big5-chart" class="chart-view">
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px;">{% for s in big_5 %}<button onclick="loadChart('big5-svg','{{ s.ticker }}',{{ s.change_pct }})" style="padding:2px 8px;border-radius:10px;border:1px solid var(--border);background:transparent;color:var(--muted);font-size:10px;cursor:pointer;font-family:'Space Mono',monospace;" onmouseover="this.style.borderColor='#3b82f6'" onmouseout="this.style.borderColor='#1e293b'">{{ s.ticker }}</button>{% endfor %}</div>
      <div id="big5-svg" class="chart-loading">Click a ticker to view chart</div>
    </div>
  </div>
  <div class="card">
    <div class="card-header"><div class="card-title">Potential Stocks</div><div style="display:flex;gap:6px;align-items:center;"><span class="card-badge badge-amber">WATCH</span><button class="chart-toggle" onclick="toggleChart('potential')">📊 Chart</button></div></div>
    <div id="potential-table" class="table-view"><table><tr><th>Ticker</th><th>Price</th><th>Change</th></tr>
    {% for s in potential %}<tr><td class="ticker-cell">{{ s.ticker }}</td><td class="price-cell">${{ "{:,.2f}".format(s.price) }}</td><td class="{{ 'change-up' if s.change_pct >= 0 else 'change-down' }}">{{ "▲" if s.change_pct >= 0 else "▼" }}{{ "{:.2f}".format(s.change_pct|abs) }}%</td></tr>{% endfor %}</table></div>
    <div id="potential-chart" class="chart-view">
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px;">{% for s in potential %}<button onclick="loadChart('potential-svg','{{ s.ticker }}',{{ s.change_pct }})" style="padding:2px 8px;border-radius:10px;border:1px solid var(--border);background:transparent;color:var(--muted);font-size:10px;cursor:pointer;font-family:'Space Mono',monospace;" onmouseover="this.style.borderColor='#3b82f6'" onmouseout="this.style.borderColor='#1e293b'">{{ s.ticker }}</button>{% endfor %}</div>
      <div id="potential-svg" class="chart-loading">Click a ticker to view chart</div>
    </div>
  </div>
  <div class="card">
    <div class="card-header"><div class="card-title">Major Crypto</div><div style="display:flex;gap:6px;align-items:center;"><span class="card-badge badge-purple">24H</span><button class="chart-toggle" onclick="toggleChart('crypto')">📊 Chart</button></div></div>
    <div id="crypto-table" class="table-view"><table><tr><th>Token</th><th>Price</th><th>24h</th></tr>
    {% for s in cryptos %}<tr><td class="ticker-cell">{{ s.ticker }}</td><td class="price-cell">${{ "{:,.2f}".format(s.price) }}</td><td class="{{ 'change-up' if s.change_pct >= 0 else 'change-down' }}">{{ "▲" if s.change_pct >= 0 else "▼" }}{{ "{:.2f}".format(s.change_pct|abs) }}%</td></tr>{% endfor %}</table></div>
    <div id="crypto-chart" class="chart-view">
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px;">{% for s in cryptos %}<button onclick="loadChart('crypto-svg','{{ s.ticker }}',{{ s.change_pct }})" style="padding:2px 8px;border-radius:10px;border:1px solid var(--border);background:transparent;color:var(--muted);font-size:10px;cursor:pointer;font-family:'Space Mono',monospace;" onmouseover="this.style.borderColor='#3b82f6'" onmouseout="this.style.borderColor='#1e293b'">{{ s.ticker }}</button>{% endfor %}</div>
      <div id="crypto-svg" class="chart-loading">Click a ticker to view chart</div>
    </div>
  </div>
  <div class="card">
    <div class="card-header"><div class="card-title">Potential Tokens</div><span class="card-badge badge-purple">DEFI</span></div>
    <table><tr><th>Token</th><th>Price</th><th>24h</th></tr>
    {% for s in tokens %}<tr><td class="ticker-cell">{{ s.ticker }}</td><td class="price-cell">${{ "{:,.2f}".format(s.price) }}</td><td class="{{ 'change-up' if s.change_pct >= 0 else 'change-down' }}">{{ "▲" if s.change_pct >= 0 else "▼" }}{{ "{:.2f}".format(s.change_pct|abs) }}%</td></tr>{% endfor %}</table>
  </div>
  <div class="card">
    <div class="card-header"><div class="card-title">Mutual Funds</div><span class="card-badge badge-green">NAV</span></div>
    <table><tr><th>Ticker</th><th>Fund</th><th>NAV</th></tr>
    {% for s in funds %}<tr><td class="ticker-cell">{{ s.ticker }}</td><td style="font-size:10px;color:var(--muted);">{{ s.name[:18] }}</td><td class="price-cell">${{ "{:,.2f}".format(s.price) }}</td></tr>{% endfor %}</table>
  </div>
  <div class="card" style="display:flex;flex-direction:column;justify-content:space-between;">
    <div class="card-header" style="margin-bottom:6px;"><div class="card-title">Weather — Bedford NH</div><span class="card-badge badge-blue">3D</span></div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
      <div style="display:flex;align-items:baseline;gap:6px;">
        <span style="font-size:22px;font-weight:400;color:var(--white);">{{ current_weather.temperature }}°F</span>
        <span style="font-size:10px;color:var(--muted);">{{ current_weather.description[:12] }}</span>
      </div>
      <span style="font-size:10px;color:var(--muted);">💨 {{ current_weather.wind_mph }}mph</span>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px;">
      {% for f in forecast %}<div style="background:rgba(0,0,0,0.25);border:1px solid var(--border);border-radius:5px;padding:4px;text-align:center;"><div style="font-size:8px;color:var(--muted);">{{ f.date[5:] }}</div><div style="font-size:8px;color:var(--text);margin:1px 0;">{{ f.description[:7] }}</div><div style="font-size:9px;font-weight:600;color:var(--accent3);">{{ f.low }}°–{{ f.high }}°</div></div>{% endfor %}
    </div>
  </div>
</div>

<div class="main-wide">
  <div style="display:flex;flex-direction:column;gap:12px;">
    <div class="card">
      <div class="card-header"><div class="card-title">AI Morning Brief</div><span class="card-badge badge-purple">GROQ</span></div>
      <div class="brief-text">{{ brief_text[:450] }}...</div>
    </div>
    <div class="card">
      <div class="card-header"><div class="card-title">Headlines</div><span class="card-badge badge-blue">LIVE</span></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;">
        <div>
          <div style="font-size:9px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">🤖 AI</div>
          {% for h in ai_news %}<div class="news-item"><div class="news-source">{{ h.source }}</div><a href="{{ h.url }}" target="_blank" class="news-link">{{ h.title[:65] }}...</a></div>{% endfor %}
        </div>
        <div>
          <div style="font-size:9px;font-weight:700;color:var(--accent2);text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">💰 Finance</div>
          {% for h in fin_news %}<div class="news-item"><div class="news-source">{{ h.source }}</div><a href="{{ h.url }}" target="_blank" class="news-link">{{ h.title[:65] }}...</a></div>{% endfor %}
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-header"><div class="card-title">Project Tracker</div><span class="card-badge badge-amber">ALL PROJECTS</span></div>
    <div class="project-tabs">
      <button class="proj-tab active" onclick="showProject('dreos',this)">DreOS</button>
      <button class="proj-tab" onclick="showProject('horizon',this)">Horizon</button>
      <button class="proj-tab" onclick="showProject('novatech',this)">NovaTech</button>
      <button class="proj-tab" onclick="showProject('vertex',this)">Vertex</button>
      <button class="proj-tab" onclick="showProject('pulse',this)">Pulse</button>
      <button class="proj-tab" onclick="showProject('grocery',this)">Grocery</button>
    </div>

    <div class="project-view active" id="proj-dreos">
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="font-size:11px;color:var(--muted);">{{ jira_done }}/{{ jira_total }} phases</span><span style="font-size:13px;font-weight:700;color:var(--accent);">{{ jira_pct }}%</span></div>
      <div class="progress-track"><div class="progress-fill-ft" style="width:{{ jira_pct }}%"></div></div>
      <div style="margin-top:8px;">
        {% set phases = [('Phase 0 — GitHub + Jira + Figma','done'),('Phase 1 — Memory + Google Sheets','done'),('Phase 2 — Market Pulse','done'),('Phase 3 — Weather + News','done'),('Phase 4 — Jira Tracker','done'),('Phase 5 — Figma Status','done'),('Phase 6 — AI Commander','done'),('Phase 7 — Dashboard + PDF','done'),('Phase 8 — Email + Launcher','done'),('Phase 9 — The Agent','done'),('Phase 10 — Cowork + Dispatch','done'),('Phase 11 — Portfolio Website','done'),('Phase 12 — Autonomous Agent','done'),('Phase 13 — Portfolio Case Studies','todo'),('Phase 14 — Cloud Deployment','todo'),('Phase 15 — Monetization','todo')] %}
        {% for name,status in phases %}
        <div class="proj-phase">
          <div class="phase-dot {{ 'phase-done' if status=='done' else 'phase-progress' if status=='progress' else 'phase-todo' }}"></div>
          <div class="phase-name">{{ name }}</div>
          <span class="phase-status {{ 'status-done' if status=='done' else 'status-progress' if status=='progress' else 'status-todo' }}">{{ 'Done' if status=='done' else 'Active' if status=='progress' else 'Planned' }}</span>
        </div>
        {% endfor %}
      </div>
      <div class="figma-row">
        <div style="width:7px;height:7px;border-radius:50%;background:{{ '#10b981' if figma_active else '#ef4444' }};"></div>
        <span>Figma: {{ figma_status }}</span>
        <span style="margin-left:auto;color:var(--accent);font-size:10px;">{{ current_phase[:35] }}</span>
      </div>
    </div>

    {% set other_projects = [
      ('horizon','Horizon Capital Fund Tracker','100','4/4',[('Live fund price fetching (yfinance)','done'),('Excel automation (openpyxl)','done'),('Email alerts + Mailtrap','done'),('Interactive dashboard (Plotly)','done')],'Python · yfinance · openpyxl · Plotly'),
      ('novatech','NovaTech Analytics Platform','100','7/7',[('SQLite database — 3 connected tables','done'),('7 business metric queries','done'),('Professional Excel report','done'),('AI executive summary (Groq)','done'),('Email alerts — Critical/Warning','done'),('9-chart interactive dashboard','done'),('One click launcher','done')],'Python · SQLite · Groq · Plotly · openpyxl'),
      ('vertex','Vertex Solutions Customer DB','100','5/5',[('Customer database (SQLite)','done'),('SQL business queries','done'),('Automated weekly report','done'),('Email alerts + AI analysis','done'),('4-chart dashboard','done')],'Python · SQLite · Groq · Plotly'),
      ('pulse','Pulse Research News Logger','100','3/3',[('NewsAPI direct integration','done'),('Growing Excel headline log','done'),('One click batch launcher','done')],'Python · NewsAPI · openpyxl · REST API'),
      ('grocery','Weekly Grocery Tracker','100','4/4',[('Grocery price database (SQLite)','done'),('AI price estimation (Groq)','done'),('Professional PDF report','done'),('Gmail delivery every Friday','done')],'Python · Groq · reportlab · Gmail SMTP'),
    ] %}

    {% for pid,pname,pct,phases_label,phases,tech in other_projects %}
    <div class="project-view" id="proj-{{ pid }}">
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="font-size:11px;color:var(--muted);">{{ phases_label }} phases</span><span style="font-size:13px;font-weight:700;color:var(--green);">{{ pct }}%</span></div>
      <div class="progress-track"><div class="progress-fill-ft" style="width:{{ pct }}%"></div></div>
      <div style="margin-top:8px;">
        {% for name,status in phases %}
        <div class="proj-phase">
          <div class="phase-dot phase-done"></div>
          <div class="phase-name">{{ name }}</div>
          <span class="phase-status status-done">Done</span>
        </div>
        {% endfor %}
      </div>
      <div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border);font-size:10px;color:var(--muted);">{{ tech }}</div>
    </div>
    {% endfor %}
  </div>
</div>

<footer>
  <div style="display:flex;align-items:center;gap:8px;">
    <div class="logo-icon" style="width:20px;height:20px;font-size:10px;">⚡</div>
    <span style="font-family:'Space Mono',monospace;font-size:11px;color:var(--muted);">DreOS — drebuilds.io</span>
  </div>
  <div class="footer-links">
    <a href="/chat">🤖 Agent</a>
    <a href="/history">📈 History</a>
    <a href="/api/brief">API</a>
    <a href="/run">▶ Run</a>
  </div>
  <div style="font-size:10px;color:var(--muted);">Auto-refreshes every 5 min</div>
</footer>

<script>
function toggleChart(id) {
  var table = document.getElementById(id + '-table');
  var chart = document.getElementById(id + '-chart');
  var btn   = event.target;
  if (chart.classList.contains('active')) {
    chart.classList.remove('active');
    table.classList.remove('hidden');
    btn.classList.remove('active');
  } else {
    chart.classList.add('active');
    table.classList.add('hidden');
    btn.classList.add('active');
  }
}

function showProject(id, el) {
  document.querySelectorAll('.project-view').forEach(function(v){ v.classList.remove('active'); });
  document.querySelectorAll('.proj-tab').forEach(function(t){ t.classList.remove('active'); });
  document.getElementById('proj-' + id).classList.add('active');
  el.classList.add('active');
}

async function loadChart(containerId, ticker, changePct) {
  var container = document.getElementById(containerId);
  container.innerHTML = '<div class="chart-loading">Loading ' + ticker + '...</div>';
  try {
    var res  = await fetch('/api/chart/' + ticker);
    var json = await res.json();
    var data = json.data;
    if (!data || data.length < 2) {
      container.innerHTML = '<div class="chart-loading">Not enough data for ' + ticker + '</div>';
      return;
    }

    var prices = data.map(function(d){ return d.price; });
    var dates  = data.map(function(d){ return d.date; });
    var minP   = Math.min.apply(null, prices);
    var maxP   = Math.max.apply(null, prices);
    var range  = maxP - minP || 1;
    var W = 400, H = 130, PAD = 10;
    var xStep = (W - PAD*2) / (prices.length - 1);
    var color  = changePct >= 0 ? '#10b981' : '#ef4444';
    var gradId = 'grad' + ticker.replace(/[^a-zA-Z0-9]/g,'');

    var pts = prices.map(function(p, i) {
      return {
        x: PAD + i * xStep,
        y: PAD + (1 - (p - minP) / range) * (H - PAD*2),
        price: p,
        date: dates[i]
      };
    });

    var pathD = pts.map(function(pt,i){ return (i===0?'M':'L')+pt.x.toFixed(1)+','+pt.y.toFixed(1); }).join(' ');
    var areaD = 'M'+pts[0].x.toFixed(1)+','+H+' '+pts.map(function(pt){ return 'L'+pt.x.toFixed(1)+','+pt.y.toFixed(1); }).join(' ')+' L'+pts[pts.length-1].x.toFixed(1)+','+H+' Z';

    var lastPrice  = prices[prices.length-1];
    var firstPrice = prices[0];
    var pctChange  = ((lastPrice-firstPrice)/firstPrice*100).toFixed(2);
    var arrow  = pctChange >= 0 ? '&#9650;' : '&#9660;';
    var pColor = pctChange >= 0 ? '#10b981' : '#ef4444';

    var fmtPrice = function(p) {
      if (p >= 1000) return '$' + Math.round(p).toString().replace(/\B(?=(\d{3})+(?!\d))/g,',');
      if (p >= 1) return '$' + p.toFixed(2);
      return '$' + p.toFixed(4);
    };

    var svgId      = containerId + '-svg-el';
    var crossId    = containerId + '-cross';
    var dotId      = containerId + '-dot';
    var tooltipId  = containerId + '-tip';
    var statValId  = containerId + '-statval';
    var statLblId  = containerId + '-statlbl';
    var statChgId  = containerId + '-statchg';

    container.innerHTML =
      '<div class="chart-stats">' +
        '<div>' +
          '<div class="chart-stat-lbl" id="' + statLblId + '">' + ticker + ' &mdash; 30 Day</div>' +
          '<div class="chart-stat-val" id="' + statValId + '">' + fmtPrice(lastPrice) + '</div>' +
        '</div>' +
        '<div style="text-align:right">' +
          '<div class="chart-stat-lbl">Period change</div>' +
          '<div id="' + statChgId + '" style="color:' + pColor + ';font-size:13px;font-weight:700;">' + arrow + Math.abs(pctChange) + '%</div>' +
        '</div>' +
      '</div>' +
      '<div class="line-chart-wrap" id="' + containerId + '-wrap" style="cursor:crosshair;">' +
        '<svg id="' + svgId + '" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;">' +
          '<defs>' +
            '<linearGradient id="' + gradId + '" x1="0" y1="0" x2="0" y2="1">' +
              '<stop offset="0%" stop-color="' + color + '" stop-opacity="0.25"/>' +
              '<stop offset="100%" stop-color="' + color + '" stop-opacity="0.02"/>' +
            '</linearGradient>' +
          '</defs>' +
          '<path d="' + areaD + '" fill="url(#' + gradId + ')"/>' +
          '<path d="' + pathD + '" fill="none" stroke="' + color + '" stroke-width="2" stroke-linejoin="round"/>' +
          '<line id="' + crossId + '" x1="0" y1="0" x2="0" y2="' + H + '" stroke="rgba(255,255,255,0.25)" stroke-width="1" stroke-dasharray="3,3" visibility="hidden"/>' +
          '<circle id="' + dotId + '" cx="0" cy="0" r="4" fill="' + color + '" stroke="#fff" stroke-width="1.5" visibility="hidden"/>' +
        '</svg>' +
        '<div id="' + tooltipId + '" style="position:absolute;background:#1e293b;border:1px solid #334155;border-radius:6px;padding:5px 9px;font-size:10px;color:#e2e8f0;pointer-events:none;display:none;white-space:nowrap;z-index:10;"></div>' +
      '</div>' +
      '<div class="chart-labels">' +
        '<span>' + dates[0].slice(5) + '</span>' +
        '<span>' + dates[Math.floor(dates.length/2)].slice(5) + '</span>' +
        '<span>' + dates[dates.length-1].slice(5) + '</span>' +
      '</div>' +
      '<div style="font-size:9px;color:#64748b;text-align:right;margin-top:2px;">' +
        (json.source === 'real' ? '&#9679; Real data' : '&#9675; Simulated') +
      '</div>';

    // Attach hover interactions
    var wrap    = document.getElementById(containerId + '-wrap');
    var svgEl   = document.getElementById(svgId);
    var cross   = document.getElementById(crossId);
    var dot     = document.getElementById(dotId);
    var tooltip = document.getElementById(tooltipId);
    var statVal = document.getElementById(statValId);
    var statLbl = document.getElementById(statLblId);
    var statChg = document.getElementById(statChgId);

    wrap.addEventListener('mousemove', function(e) {
      var rect   = svgEl.getBoundingClientRect();
      var mouseX = e.clientX - rect.left;
      var pctX   = mouseX / rect.width;
      var svgX   = PAD + pctX * (W - PAD*2);

      // Find nearest data point
      var idx = Math.round((svgX - PAD) / xStep);
      idx = Math.max(0, Math.min(pts.length-1, idx));
      var pt = pts[idx];

      // Move crosshair and dot
      cross.setAttribute('x1', pt.x.toFixed(1));
      cross.setAttribute('x2', pt.x.toFixed(1));
      cross.setAttribute('visibility', 'visible');
      dot.setAttribute('cx', pt.x.toFixed(1));
      dot.setAttribute('cy', pt.y.toFixed(1));
      dot.setAttribute('visibility', 'visible');

      // Update stat display
      statVal.textContent = fmtPrice(pt.price);
      statLbl.textContent = ticker + ' — ' + pt.date;
      var dayChg = ((pt.price - firstPrice)/firstPrice*100).toFixed(2);
      var dColor = dayChg >= 0 ? '#10b981' : '#ef4444';
      statChg.style.color = dColor;
      statChg.innerHTML = (dayChg >= 0 ? '&#9650;' : '&#9660;') + Math.abs(dayChg) + '% from start';

      // Position tooltip
      var tipX = e.clientX - wrap.getBoundingClientRect().left + 10;
      var tipY = e.clientY - wrap.getBoundingClientRect().top - 30;
      if (tipX + 140 > wrap.offsetWidth) tipX -= 150;
      tooltip.style.left = tipX + 'px';
      tooltip.style.top  = tipY + 'px';
      tooltip.style.display = 'block';
      tooltip.innerHTML = '<strong>' + fmtPrice(pt.price) + '</strong> &nbsp; ' + pt.date;
    });

    wrap.addEventListener('mouseleave', function() {
      cross.setAttribute('visibility', 'hidden');
      dot.setAttribute('visibility', 'hidden');
      tooltip.style.display = 'none';
      statVal.textContent = fmtPrice(lastPrice);
      statLbl.textContent = ticker + ' — 30 Day';
      statChg.style.color = pColor;
      statChg.innerHTML = arrow + Math.abs(pctChange) + '%';
    });

  } catch(e) {
    container.innerHTML = '<div class="chart-loading">Error: ' + e.message + '</div>';
  }
}
</script>

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


# Route — Chart data API
# URL: http://localhost:5000/api/chart/<ticker>
# Returns price history for a ticker as JSON for line charts
@app.route("/api/chart/<ticker>")
def chart_data(ticker):
    import sqlite3
    import random
    import math
    from datetime import datetime, timedelta

    ticker = ticker.upper()
    today  = datetime.now()
    days   = 30

    # Try to get real data from price_history.db first
    real_data = []
    try:
        db_path = os.path.join(os.path.dirname(__file__), "data", "price_history.db")
        if os.path.exists(db_path):
            conn   = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT date, price FROM price_history
                WHERE ticker = ?
                ORDER BY date ASC
                LIMIT 90
            """, (ticker,))
            rows = cursor.fetchall()
            conn.close()
            real_data = [{"date": r[0], "price": r[1]} for r in rows if r[1]]
    except:
        pass

    # If we have enough real data use it
    if len(real_data) >= 5:
        return jsonify({"ticker": ticker, "data": real_data, "source": "real"})

    # Otherwise simulate realistic price history
    # Get current price from market data if available
    market = load_json("outputs/market_data.json")
    current_price = None

    for category in ["big_5_stocks", "potential_stocks", "major_cryptos", "potential_tokens", "mutual_funds"]:
        for asset in market.get(category, []):
            if asset.get("ticker") == ticker:
                current_price = asset.get("price")
                break
        if current_price:
            break

    if not current_price:
        return jsonify({"ticker": ticker, "data": [], "source": "none"})

    # Generate 30 days of simulated history ending at current price
    # Uses realistic random walk with slight trend
    random.seed(hash(ticker) % 10000)  # consistent seed per ticker
    volatility = 0.015 if ticker in ["BTC","ETH","SOL","BNB","XRP"] else 0.008
    if ticker in ["POL","ARB","LINK","UNI","AAVE"]:
        volatility = 0.025

    prices = [current_price]
    for i in range(days - 1):
        change = random.gauss(0, volatility)
        prices.insert(0, prices[0] / (1 + change))

    data = []
    for i, price in enumerate(prices):
        day = today - timedelta(days=(days - 1 - i))
        data.append({
            "date":  day.strftime("%Y-%m-%d"),
            "price": round(price, 2)
        })

    return jsonify({"ticker": ticker, "data": data, "source": "simulated"})

# -----------------------------------------
# CHAT TEMPLATE
# -----------------------------------------
CHAT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DreOS — Agent Chat</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#080c14; color:#e2e8f0; height:100vh; display:flex; flex-direction:column; }

.header { background:#1F3864; padding:14px 24px; display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #2E75B6; flex-shrink:0; }
.header h1 { color:white; font-size:18px; letter-spacing:2px; }
.header-right { display:flex; align-items:center; gap:16px; }
.header a { color:#00d4ff; text-decoration:none; font-size:12px; }

/* MODE TOGGLE */
.mode-toggle { display:flex; background:#0d1520; border:1px solid #2a3a4a; border-radius:8px; overflow:hidden; }
.mode-btn { padding:7px 16px; font-size:11px; font-weight:bold; letter-spacing:1px; cursor:pointer; border:none; transition:all 0.2s; text-transform:uppercase; }
.mode-btn.quick { background:transparent; color:#aac4e0; }
.mode-btn.deep  { background:transparent; color:#aac4e0; }
.mode-btn.active-quick { background:#2E75B6; color:white; }
.mode-btn.active-deep  { background:#7c3aed; color:white; }

.mode-indicator { font-size:10px; padding:3px 10px; border-radius:20px; font-weight:bold; letter-spacing:1px; }
.mode-indicator.quick { background:rgba(46,117,182,0.2); color:#2E75B6; border:1px solid #2E75B6; }
.mode-indicator.deep  { background:rgba(124,58,237,0.2); color:#a78bfa; border:1px solid #7c3aed; }

.chat-container { flex:1; overflow-y:auto; padding:20px 24px; display:flex; flex-direction:column; gap:14px; }

.message { display:flex; gap:12px; max-width:82%; }
.message.user { align-self:flex-end; flex-direction:row-reverse; }
.message.dreos { align-self:flex-start; }

.avatar { width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:15px; flex-shrink:0; }
.avatar.dreos-av { background:#1F3864; border:2px solid #00d4ff; }
.avatar.user-av  { background:#2E75B6; }
.avatar.deep-av  { background:#1F3864; border:2px solid #7c3aed; }

.bubble { padding:11px 15px; border-radius:12px; font-size:13px; line-height:1.75; max-width:100%; }
.bubble.dreos-bubble { background:#1a2535; border:1px solid #2a3a4a; border-top-left-radius:4px; color:#e2e8f0; }
.bubble.user-bubble  { background:#2E75B6; border-top-right-radius:4px; color:white; }
.bubble.deep-bubble  { background:#1a1535; border:1px solid #4c1d95; border-top-left-radius:4px; color:#e2e8f0; }
.bubble.typing { color:#64748b; font-style:italic; }

.tools-used { margin-top:8px; padding-top:8px; border-top:1px solid #2a3a4a; font-size:10px; color:#64748b; }
.tool-tag { display:inline-block; background:#0d1520; border:1px solid #2a3a4a; color:#7c3aed; padding:2px 8px; border-radius:10px; font-size:10px; margin:2px; }

.suggestions { display:flex; gap:8px; flex-wrap:wrap; padding:4px 24px 10px; }
.suggestion { background:#1a2535; border:1px solid #2a3a4a; color:#aac4e0; padding:5px 12px; border-radius:20px; font-size:11px; cursor:pointer; transition:all 0.2s; }
.suggestion:hover { border-color:#00d4ff; color:#00d4ff; }
.suggestion.deep-sug { border-color:#4c1d95; color:#a78bfa; }
.suggestion.deep-sug:hover { border-color:#7c3aed; color:#c4b5fd; }

.input-area { background:#1a2535; border-top:1px solid #2a3a4a; padding:14px 24px; display:flex; gap:10px; flex-shrink:0; align-items:center; }
.chat-input { flex:1; background:#0d1520; border:1px solid #2a3a4a; color:#e2e8f0; padding:11px 16px; border-radius:8px; font-size:13px; font-family:'Segoe UI',sans-serif; outline:none; transition:border-color 0.2s; }
.chat-input:focus { border-color:#00d4ff; }
.chat-input.deep-mode { border-color:#4c1d95; }
.chat-input.deep-mode:focus { border-color:#7c3aed; }
.send-btn { color:#080c14; border:none; padding:11px 22px; border-radius:8px; font-size:13px; font-weight:bold; cursor:pointer; transition:all 0.2s; letter-spacing:1px; white-space:nowrap; }
.send-btn.quick-send { background:#00d4ff; }
.send-btn.quick-send:hover { background:white; }
.send-btn.deep-send  { background:#7c3aed; color:white; }
.send-btn.deep-send:hover  { background:#a78bfa; }
.send-btn:disabled { background:#2a3a4a !important; color:#64748b !important; cursor:not-allowed; }

::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:#080c14; }
::-webkit-scrollbar-thumb { background:#2a3a4a; border-radius:2px; }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>⚡ DreOS AGENT</h1>
    <div style="color:#aac4e0;font-size:10px;margin-top:2px;">Personal Intelligence Assistant</div>
  </div>
  <div class="header-right">
    <div class="mode-toggle">
      <button class="mode-btn quick active-quick" id="quickBtn" onclick="setMode('quick')">⚡ Quick</button>
      <button class="mode-btn deep" id="deepBtn" onclick="setMode('deep')">🔍 Deep</button>
    </div>
    <a href="/">← Dashboard</a>
  </div>
</div>

<div class="chat-container" id="chatContainer">
  <div class="message dreos">
    <div class="avatar dreos-av">⚡</div>
    <div class="bubble dreos-bubble">
      Hey Dre! I'm your DreOS agent — two modes available:<br><br>
      <strong style="color:#00d4ff;">⚡ Quick Mode</strong> — Fast answers from cached data. Great for quick checks.<br>
      <strong style="color:#a78bfa;">🔍 Deep Mode</strong> — I'll use my tools to fetch live data and analyze trends. Takes longer but much richer.<br><br>
      Toggle the mode in the top right. What do you want to know?
    </div>
  </div>
</div>

<div class="suggestions" id="suggestionBar">
  <span class="suggestion" onclick="sendSuggestion(this)">How are my stocks today?</span>
  <span class="suggestion" onclick="sendSuggestion(this)">How's crypto looking?</span>
  <span class="suggestion" onclick="sendSuggestion(this)">What's the weather this week?</span>
  <span class="suggestion" onclick="sendSuggestion(this)">How far along is DreOS?</span>
  <span class="suggestion" onclick="sendSuggestion(this)">Any big movers today?</span>
</div>

<div class="input-area">
  <input type="text" class="chat-input" id="chatInput" placeholder="Ask DreOS anything..." autocomplete="off">
  <button class="send-btn quick-send" id="sendBtn" onclick="sendMessage()">SEND ⚡</button>
</div>

<script>
const chatContainer = document.getElementById('chatContainer');
const chatInput     = document.getElementById('chatInput');
const sendBtn       = document.getElementById('sendBtn');
const quickBtn      = document.getElementById('quickBtn');
const deepBtn       = document.getElementById('deepBtn');
const suggestionBar = document.getElementById('suggestionBar');
let currentMode     = 'quick';

const quickSuggestions = [
  'How are my stocks today?',
  "How's crypto looking?",
  "What's the weather this week?",
  'How far along is DreOS?',
  'Any big movers today?'
];

const deepSuggestions = [
  'Any trends worth watching in NVDA?',
  'Check for price spikes above 5%',
  'Give me a full morning briefing',
  'Analyze my crypto portfolio trends',
  'Check if anything unusual happened today'
];

function setMode(mode) {
  currentMode = mode;

  if (mode === 'quick') {
    quickBtn.className = 'mode-btn quick active-quick';
    deepBtn.className  = 'mode-btn deep';
    sendBtn.className  = 'send-btn quick-send';
    sendBtn.textContent = 'SEND ⚡';
    chatInput.className = 'chat-input';
    chatInput.placeholder = 'Ask DreOS anything... (cached data)';
    renderSuggestions(quickSuggestions, false);
  } else {
    quickBtn.className = 'mode-btn quick';
    deepBtn.className  = 'mode-btn deep active-deep';
    sendBtn.className  = 'send-btn deep-send';
    sendBtn.textContent = 'ANALYZE 🔍';
    chatInput.className = 'chat-input deep-mode';
    chatInput.placeholder = 'Give DreOS a goal to investigate...';
    renderSuggestions(deepSuggestions, true);
  }
}

function renderSuggestions(list, isDeep) {
  suggestionBar.innerHTML = '';
  list.forEach(text => {
    const span = document.createElement('span');
    span.className = isDeep ? 'suggestion deep-sug' : 'suggestion';
    span.textContent = text;
    span.onclick = () => sendSuggestion(span);
    suggestionBar.appendChild(span);
  });
}

chatInput.addEventListener('keypress', function(e) {
  if (e.key === 'Enter') sendMessage();
});

function sendSuggestion(el) {
  chatInput.value = el.textContent;
  sendMessage();
}

function addMessage(text, role, tools) {
  const msg     = document.createElement('div');
  msg.className = `message ${role}`;

  const avatar  = document.createElement('div');
  const isDeep  = role === 'deep';
  avatar.className = `avatar ${role === 'user' ? 'user-av' : isDeep ? 'deep-av' : 'dreos-av'}`;
  avatar.textContent = role === 'user' ? '👤' : '⚡';

  const bubble  = document.createElement('div');
  bubble.className = `bubble ${role === 'user' ? 'user-bubble' : isDeep ? 'deep-bubble' : 'dreos-bubble'}`;
  bubble.innerHTML = text.replace(/\\n/g, '<br>');

  if (tools && tools.length > 0) {
    const toolDiv = document.createElement('div');
    toolDiv.className = 'tools-used';
    toolDiv.innerHTML = '🔧 Tools used: ' + tools.map(t => `<span class="tool-tag">${t}</span>`).join('');
    bubble.appendChild(toolDiv);
  }

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  chatContainer.appendChild(msg);
  chatContainer.scrollTop = chatContainer.scrollHeight;
  return bubble;
}

function addTyping(mode) {
  const msg     = document.createElement('div');
  msg.className = 'message dreos';
  msg.id        = 'typingIndicator';

  const avatar  = document.createElement('div');
  avatar.className = mode === 'deep' ? 'avatar deep-av' : 'avatar dreos-av';
  avatar.textContent = '⚡';

  const bubble  = document.createElement('div');
  bubble.className = mode === 'deep' ? 'bubble deep-bubble typing' : 'bubble dreos-bubble typing';
  bubble.id     = 'typingText';
  bubble.textContent = mode === 'deep' ? '🔍 Analyzing — fetching live data and running tools...' : '⚡ Thinking...';

  msg.appendChild(avatar);
  msg.appendChild(bubble);
  chatContainer.appendChild(msg);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTyping() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) indicator.remove();
}

async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message) return;

  chatInput.value = '';
  sendBtn.disabled = true;
  addMessage(message, 'user');
  addTyping(currentMode);

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: message, mode: currentMode })
    });

    const data = await response.json();
    removeTyping();

    const role = currentMode === 'deep' ? 'deep' : 'dreos';
    if (data.response) {
      addMessage(data.response, role, data.tools_used || []);
    } else {
      addMessage('Something went wrong — check your error log.', 'dreos', []);
    }
  } catch (error) {
    removeTyping();
    addMessage('Connection error — make sure Flask is running.', 'dreos', []);
  }

  sendBtn.disabled = false;
  chatInput.focus();
}
</script>
</body>
</html>
"""

# -----------------------------------------
# CHAT ROUTE — POST endpoint
# Receives message from browser
# Sends to Groq with data context
# Returns AI response
# -----------------------------------------
@app.route("/chat")
def chat_page():
    return render_template_string(CHAT_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat_api():
    try:
        user_message = request.json.get("message", "")
        mode         = request.json.get("mode", "quick")

        if not user_message:
            return jsonify({"response": "I didn't catch that — try again!"})

        # -----------------------------------------
        # DEEP MODE — uses autonomous agent
        # AI decides which tools to call
        # Returns richer analysis, takes longer
        # -----------------------------------------
        if mode == "deep":
            try:
                import sys
                agent_dir = os.path.join(os.path.dirname(__file__), "agent")
                if agent_dir not in sys.path:
                    sys.path.insert(0, agent_dir)
                    sys.path.insert(0, os.path.dirname(__file__))

                from autonomous_agent import run_agent
                import io
                from contextlib import redirect_stdout

                # Capture tool calls made during the run
                tools_used = []
                original_dispatch = None

                try:
                    from tool_registry import dispatch_tool as original_dispatch_fn
                    import tool_registry

                    def tracking_dispatch(tool_name, params=None):
                        tools_used.append(tool_name)
                        return original_dispatch_fn(tool_name, params)

                    tool_registry.dispatch_tool = tracking_dispatch

                    # Run the autonomous agent
                    f = io.StringIO()
                    with redirect_stdout(f):
                        answer = run_agent(user_message)

                    # Restore original dispatch
                    tool_registry.dispatch_tool = original_dispatch_fn

                except Exception:
                    answer = run_agent(user_message)

                return jsonify({
                    "response":   answer,
                    "mode":       "deep",
                    "tools_used": list(set(tools_used))
                })

            except Exception as e:
                return jsonify({
                    "response": f"Deep mode error: {str(e)}\n\nFalling back to quick mode...",
                    "mode": "error",
                    "tools_used": []
                })

        # -----------------------------------------
        # QUICK MODE — uses cached JSON data
        # Fast response from existing files
        # -----------------------------------------
        data    = load_all_data()
        market  = data["market"]
        context = data["context"]
        jira    = data["jira"]
        figma   = data["figma"]
        history = data["history"]
        brief   = data["brief"]

        big_5    = market.get("big_5_stocks", [])
        cryptos  = market.get("major_cryptos", [])
        potential= market.get("potential_stocks", [])
        tokens   = market.get("potential_tokens", [])
        mkt_sum  = market.get("summary", {})
        weather  = context.get("weather", {}).get("current", {})
        forecast = context.get("weather", {}).get("forecast", [])
        ai_news  = context.get("news", {}).get("ai_headlines", [])[:3]
        fin_news = context.get("news", {}).get("finance_headlines", [])[:3]
        jira_sum = jira.get("summary", {})
        hist_sum = history.get("summary", {})

        stocks_str   = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in big_5 if s.get('price')])
        pot_str      = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in potential if s.get('price')])
        crypto_str   = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in cryptos if s.get('price')])
        token_str    = "\n".join([f"{s['ticker']}: ${s.get('price',0):,.2f} ({s.get('change_pct',0):+.2f}%)" for s in tokens if s.get('price')])
        forecast_str = "\n".join([f"{f['date']}: {f['low']}°F-{f['high']}°F {f['description']}" for f in forecast])
        news_str     = "\n".join([f"- {h['source']}: {h['title']}" for h in ai_news + fin_news])

        data_context = f"""
Date/time: {datetime.now().strftime("%Y-%m-%d %H:%M")}
BIG 5 STOCKS: {stocks_str}
POTENTIAL STOCKS: {pot_str}
MAJOR CRYPTOS: {crypto_str}
POTENTIAL TOKENS: {token_str}
Top Gainer: {mkt_sum.get('top_gainer','N/A')} | Top Loser: {mkt_sum.get('top_loser','N/A')}
Gainers: {mkt_sum.get('gainers',0)} | Losers: {mkt_sum.get('losers',0)}
WEATHER: {weather.get('temperature')}°F — {weather.get('description')} | Wind: {weather.get('wind_mph')} mph
FORECAST: {forecast_str}
NEWS: {news_str}
DREOS: {jira_sum.get('pct_complete',0)}% complete | Current: {jira_sum.get('current_phase','N/A')}
HISTORY: {hist_sum.get('days_of_history',0)} days tracked
"""

        client   = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are DreOS — Dre's personal AI assistant in Quick Mode.
Answer fast and conversationally — like a smart colleague giving a quick summary.
Be specific with numbers. Keep responses under 100 words.
If someone asks for deep analysis suggest switching to Deep Mode.
Cached data: {data_context}"""
                },
                {"role": "user", "content": user_message}
            ]
        )

        answer = response.choices[0].message.content.strip()
        return jsonify({
            "response":   answer,
            "mode":       "quick",
            "tools_used": []
        })

    except Exception as e:
        return jsonify({"response": f"Something went wrong: {str(e)}", "tools_used": []})

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
