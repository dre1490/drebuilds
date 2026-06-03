"""
DreOS — PDF Morning Report
Phase 7b: Generate a clean one page PDF morning brief

Data source: outputs/brief_data.json

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: python modules/pdf_report.py
"""

import json
import os
from datetime import date, datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from dotenv import load_dotenv

load_dotenv()

print("\n📄 DreOS PDF Morning Report — Building...\n")

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

# Colors
DARK_BLUE  = colors.HexColor("#1F3864")
MID_BLUE   = colors.HexColor("#2E75B6")
LIGHT_BLUE = colors.HexColor("#DCE6F1")
GREEN      = colors.HexColor("#70AD47")
RED        = colors.HexColor("#C00000")
ORANGE     = colors.HexColor("#ED7D31")
YELLOW     = colors.HexColor("#FFC000")
WHITE      = colors.white
DARK_BG    = colors.HexColor("#0f1923")

# -----------------------------------------
# STYLES
# -----------------------------------------
styles    = getSampleStyleSheet()
thin      = colors.HexColor("#CCCCCC")

title_style = ParagraphStyle("T", parent=styles["Title"],
    fontSize=18, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold")

subtitle_style = ParagraphStyle("S", parent=styles["Normal"],
    fontSize=10, textColor=WHITE, alignment=TA_CENTER)

section_style = ParagraphStyle("Sec", parent=styles["Heading1"],
    fontSize=11, textColor=WHITE, fontName="Helvetica-Bold")

body_style = ParagraphStyle("B", parent=styles["Normal"],
    fontSize=10, textColor=colors.HexColor("#333333"), leading=16)

small_style = ParagraphStyle("Sm", parent=styles["Normal"],
    fontSize=9, textColor=colors.HexColor("#444444"), leading=14)

cell_style = ParagraphStyle("C", parent=styles["Normal"],
    fontSize=8, textColor=colors.HexColor("#333333"), alignment=TA_CENTER)

# -----------------------------------------
# BUILD PDF
# -----------------------------------------
os.makedirs("outputs", exist_ok=True)
report_file = f"outputs/dreos_morning_report_{date.today().strftime('%Y-%m-%d')}.pdf"

doc   = SimpleDocTemplate(report_file, pagesize=letter,
        rightMargin=0.4*inch, leftMargin=0.4*inch,
        topMargin=0.4*inch, bottomMargin=0.4*inch)
story = []

def section_header(title, color=None):
    data = [[Paragraph(title, section_style)]]
    t    = Table(data, colWidths=[7.7*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color or MID_BLUE),
        ("TOPPADDING",    (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
    ]))
    return t

# HEADER
h = Table([[Paragraph("⚡  DreOS — Morning Intelligence Brief", title_style)]], colWidths=[7.7*inch])
h.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK_BLUE),("TOPPADDING",(0,0),(-1,-1),14),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
story.append(h)

current_w = weather.get("current", {})
s = Table([[Paragraph(f"{today}  |  Bedford NH: {current_w.get('temperature')}°F — {current_w.get('description')}  |  💨 {current_w.get('wind_mph')} mph", subtitle_style)]], colWidths=[7.7*inch])
s.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),MID_BLUE),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story.append(s)
story.append(Spacer(1, 0.12*inch))

# AI BRIEF
story.append(section_header("🤖  AI Morning Brief"))
story.append(Spacer(1, 0.06*inch))
story.append(Paragraph(brief_text, body_style))
story.append(Spacer(1, 0.12*inch))

# MARKET DATA — Two column layout
story.append(section_header("📊  Market Pulse"))
story.append(Spacer(1, 0.06*inch))

def market_table(stocks, show_change=True):
    header = [
        Paragraph("<b>Ticker</b>", cell_style),
        Paragraph("<b>Price</b>", cell_style),
    ]
    if show_change:
        header.append(Paragraph("<b>Change</b>", cell_style))
    rows = [header]
    for s in stocks:
        if not s.get("price"):
            continue
        change_color = "#70AD47" if s.get("change_pct", 0) >= 0 else "#C00000"
        arrow        = "▲" if s.get("change_pct", 0) >= 0 else "▼"
        row = [
            Paragraph(f"<b>{s['ticker']}</b>", cell_style),
            Paragraph(f"${s['price']:,.2f}", cell_style),
        ]
        if show_change:
            row.append(Paragraph(f"<font color='{change_color}'>{arrow}{abs(s.get('change_pct',0)):.2f}%</font>", cell_style))
        rows.append(row)
    cols = [1.0*inch, 1.0*inch, 0.8*inch] if show_change else [1.2*inch, 1.0*inch]
    t    = Table(rows, colWidths=cols)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0), DARK_BLUE),
        ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
        ("GRID",          (0,0),(-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0),(-1,-1), 3),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("BACKGROUND",    (0,1),(-1,-1), colors.HexColor("#F8F8F8")),
    ]))
    return t

big_5       = market.get("big_5_stocks", [])
potential   = market.get("potential_stocks", [])
cryptos     = market.get("major_cryptos", [])
tokens      = market.get("potential_tokens", [])
funds       = market.get("mutual_funds", [])

market_layout = Table([
    [
        Table([[Paragraph("<b>Big 5 Stocks</b>", small_style)], [market_table(big_5)]], colWidths=[2.8*inch]),
        Table([[Paragraph("<b>Potential Stocks</b>", small_style)], [market_table(potential)]], colWidths=[2.8*inch]),
        Table([[Paragraph("<b>Mutual Funds</b>", small_style)], [market_table(funds, show_change=False)]], colWidths=[2.1*inch]),
    ]
], colWidths=[2.8*inch, 2.8*inch, 2.1*inch])
story.append(market_layout)
story.append(Spacer(1, 0.08*inch))

crypto_layout = Table([
    [
        Table([[Paragraph("<b>Major Cryptos</b>", small_style)], [market_table(cryptos)]], colWidths=[3.8*inch]),
        Table([[Paragraph("<b>Potential Tokens</b>", small_style)], [market_table(tokens)]], colWidths=[3.9*inch]),
    ]
], colWidths=[3.8*inch, 3.9*inch])
story.append(crypto_layout)
story.append(Spacer(1, 0.12*inch))

# NEWS
story.append(section_header("📰  Top Headlines"))
story.append(Spacer(1, 0.06*inch))

ai_news  = news.get("ai_headlines", [])[:3]
fin_news = news.get("finance_headlines", [])[:3]

news_rows = [[
    Paragraph("<b>🤖 AI News</b>", small_style),
    Paragraph("<b>💰 Finance News</b>", small_style)
]]
max_rows = max(len(ai_news), len(fin_news))
for i in range(max_rows):
    ai  = Paragraph(f"• {ai_news[i]['source']}: {ai_news[i]['title']}", small_style) if i < len(ai_news) else Paragraph("", small_style)
    fin = Paragraph(f"• {fin_news[i]['source']}: {fin_news[i]['title']}", small_style) if i < len(fin_news) else Paragraph("", small_style)
    news_rows.append([ai, fin])

news_table = Table(news_rows, colWidths=[3.85*inch, 3.85*inch])
news_table.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,0), DARK_BLUE),
    ("TEXTCOLOR",     (0,0),(-1,0), WHITE),
    ("GRID",          (0,0),(-1,-1), 0.5, colors.HexColor("#CCCCCC")),
    ("TOPPADDING",    (0,0),(-1,-1), 4),
    ("BOTTOMPADDING", (0,0),(-1,-1), 4),
    ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ("BACKGROUND",    (0,1),(-1,-1), colors.HexColor("#F8F8F8")),
]))
story.append(news_table)
story.append(Spacer(1, 0.12*inch))

# PROJECT STATUS
story.append(section_header("🎯  DreOS Project Status", ORANGE))
story.append(Spacer(1, 0.06*inch))

pct       = jira.get("pct_complete", 0)
done_ct   = jira.get("done", 0)
total_ct  = jira.get("total_tickets", 0)
current   = jira.get("current_phase", "N/A")
next_ph   = jira.get("next_phase", "N/A")
fig_status= figma.get("activity_status", "N/A")

status_data = [
    [Paragraph("<b>Progress</b>", cell_style), Paragraph(f"{pct}% ({done_ct}/{total_ct} phases)", cell_style)],
    [Paragraph("<b>Current Phase</b>", cell_style), Paragraph(current, cell_style)],
    [Paragraph("<b>Next Phase</b>", cell_style), Paragraph(next_ph, cell_style)],
    [Paragraph("<b>Figma Status</b>", cell_style), Paragraph(fig_status, cell_style)],
]
status_table = Table(status_data, colWidths=[1.5*inch, 6.2*inch])
status_table.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(0,-1), DARK_BLUE),
    ("TEXTCOLOR",     (0,0),(0,-1), WHITE),
    ("GRID",          (0,0),(-1,-1), 0.5, colors.HexColor("#CCCCCC")),
    ("TOPPADDING",    (0,0),(-1,-1), 5),
    ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ("BACKGROUND",    (1,0),(-1,-1), colors.HexColor("#F8F8F8")),
]))
story.append(status_table)
story.append(Spacer(1, 0.12*inch))

# FOOTER
ft = Table([[Paragraph(f"DreOS Personal Intelligence Hub  |  {today}  |  drebuilds.io", subtitle_style)]], colWidths=[7.7*inch])
ft.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),DARK_BLUE),("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8)]))
story.append(ft)

doc.build(story)

print(f"  ✅ PDF report generated!")
print(f"  📁 Saved as: {report_file}")
print(f"\n{'='*50}")
print(f"  💾 {report_file}")
print(f"{'='*50}\n")
