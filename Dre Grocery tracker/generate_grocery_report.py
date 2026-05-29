"""
Weekly Grocery Report — Phase 3
Generate a professional PDF report with price comparisons and meal ideas

HOW TO RUN:
1. Open Terminal
2. Navigate to your Grocery Tracker folder
3. Run: pip install reportlab groq
4. Run: python generate_grocery_report.py
"""

import sqlite3
import json
from groq import Groq
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# -----------------------------------------
# SETTINGS
# -----------------------------------------
API_KEY     = "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"
DB_FILE     = "grocery_tracker.db"
REPORT_FILE = f"grocery_report_{date.today().strftime('%Y-%m-%d')}.pdf"
STORES      = ["Market Basket", "Hannaford"]

# Colors
DARK_BLUE   = colors.HexColor("#1F3864")
MID_BLUE    = colors.HexColor("#2E75B6")
LIGHT_BLUE  = colors.HexColor("#DCE6F1")
GREEN       = colors.HexColor("#70AD47")
RED         = colors.HexColor("#C00000")
ORANGE      = colors.HexColor("#ED7D31")
YELLOW      = colors.HexColor("#FFF2CC")
WHITE       = colors.white
LIGHT_GRAY  = colors.HexColor("#F5F5F5")

# -----------------------------------------
# STEP 1 — Pull data from database
# -----------------------------------------
print("\n🗄️  Reading grocery database...")

conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
today  = date.today().strftime("%Y-%m-%d")

cursor.execute("SELECT id, name, category, unit FROM items ORDER BY category, name")
items = cursor.fetchall()

# Get latest prices for each store
def get_latest_price(item_id, store):
    cursor.execute("""
        SELECT price FROM price_history
        WHERE item_id = ? AND store = ?
        ORDER BY date_checked DESC LIMIT 1
    """, (item_id, store))
    row = cursor.fetchone()
    return row[0] if row else None

# Build price data
price_data = []
for item_id, name, category, unit in items:
    mb_price = get_latest_price(item_id, STORES[0])
    hf_price = get_latest_price(item_id, STORES[1])
    price_data.append({
        "id": item_id, "name": name, "category": category,
        "unit": unit, "mb": mb_price, "hf": hf_price
    })

# Totals
mb_total = sum(d["mb"] for d in price_data if d["mb"])
hf_total = sum(d["hf"] for d in price_data if d["hf"])
cheaper_store = STORES[0] if mb_total < hf_total else STORES[1]
savings = abs(mb_total - hf_total)

conn.close()
print("✅ Data pulled successfully")

# -----------------------------------------
# STEP 2 — Generate AI content
# -----------------------------------------
print("🤖 Generating AI analysis and meal ideas...")

client = Groq(api_key=API_KEY)

# Price analysis
price_summary = "\n".join([
    f"- {d['name']}: Market Basket ${d['mb']:.2f} vs Hannaford ${d['hf']:.2f}"
    for d in price_data if d["mb"] and d["hf"]
])

analysis_prompt = f"""
You are a savvy grocery shopping expert. Analyze these price comparisons
between Market Basket (Bedford NH) and Hannaford (Goffstown NH) and write
a short 3-4 sentence shopping insight. Mention which store wins overall,
which categories have the biggest price differences, and one smart shopping tip.
Keep it friendly and practical.

Total basket: Market Basket ${mb_total:.2f} vs Hannaford ${hf_total:.2f}
Cheaper store: {cheaper_store} (saves ${savings:.2f})

Item by item prices:
{price_summary}
"""

analysis_response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": analysis_prompt}]
)
price_analysis = analysis_response.choices[0].message.content.strip()

# Meal ideas using items from the list
available_items = [d["name"] for d in price_data]
meal_prompt = f"""
Create exactly 3 quick weeknight meal ideas using ingredients from this grocery list.
Each meal must take 30 minutes or less to prepare.

Return ONLY a JSON array with exactly 3 meals. Each meal must have:
- "name": meal name
- "time": prep time (e.g. "25 minutes")
- "ingredients": list of ingredients used from the grocery list
- "instructions": 3-4 simple steps to make it

No markdown, no extra text — just raw JSON array.

Available ingredients: {", ".join(available_items)}
"""

meal_response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": meal_prompt}]
)

raw_meals = meal_response.choices[0].message.content.strip()
clean_meals = raw_meals.replace("```json", "").replace("```", "").strip()
meals = json.loads(clean_meals)

print("✅ AI content generated")

# -----------------------------------------
# STEP 3 — Build PDF
# -----------------------------------------
print("📄 Building PDF report...")

doc    = SimpleDocTemplate(
    REPORT_FILE,
    pagesize=letter,
    rightMargin=0.5*inch,
    leftMargin=0.5*inch,
    topMargin=0.5*inch,
    bottomMargin=0.5*inch
)

styles = getSampleStyleSheet()
story  = []

# Custom styles
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Title"],
    fontSize=22,
    textColor=WHITE,
    alignment=TA_CENTER,
    spaceAfter=4,
    fontName="Helvetica-Bold"
)

subtitle_style = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontSize=10,
    textColor=WHITE,
    alignment=TA_CENTER,
    fontName="Helvetica"
)

section_style = ParagraphStyle(
    "Section",
    parent=styles["Heading1"],
    fontSize=13,
    textColor=WHITE,
    fontName="Helvetica-Bold",
    spaceAfter=6,
    spaceBefore=12
)

body_style = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontSize=10,
    textColor=colors.HexColor("#333333"),
    spaceAfter=6,
    leading=16
)

small_style = ParagraphStyle(
    "Small",
    parent=styles["Normal"],
    fontSize=9,
    textColor=colors.HexColor("#555555"),
    leading=14
)

# -----------------------------------------
# HEADER
# -----------------------------------------
header_data = [[
    Paragraph("🛒  Weekly Grocery Report", title_style),
]]
header_table = Table(header_data, colWidths=[7.5*inch])
header_table.setStyle(TableStyle([
    ("BACKGROUND",  (0,0), (-1,-1), DARK_BLUE),
    ("TOPPADDING",  (0,0), (-1,-1), 14),
    ("BOTTOMPADDING",(0,0),(-1,-1), 6),
    ("LEFTPADDING", (0,0), (-1,-1), 12),
]))
story.append(header_table)

sub_data = [[
    Paragraph(f"Market Basket (Bedford NH)  vs  Hannaford (Goffstown NH)  |  {date.today().strftime('%B %d, %Y')}", subtitle_style)
]]
sub_table = Table(sub_data, colWidths=[7.5*inch])
sub_table.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), MID_BLUE),
    ("TOPPADDING",    (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
]))
story.append(sub_table)
story.append(Spacer(1, 0.2*inch))

# -----------------------------------------
# SUMMARY BANNER
# -----------------------------------------
winner_color = GREEN if cheaper_store == STORES[0] else ORANGE
summary_data = [
    [
        Paragraph(f"Market Basket Total\n${mb_total:.2f}", ParagraphStyle("s", parent=styles["Normal"], fontSize=12, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold", leading=18)),
        Paragraph(f"Hannaford Total\n${hf_total:.2f}", ParagraphStyle("s", parent=styles["Normal"], fontSize=12, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold", leading=18)),
        Paragraph(f"Best Value\n{cheaper_store}\nSaves ${savings:.2f}", ParagraphStyle("s", parent=styles["Normal"], fontSize=12, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold", leading=18)),
    ]
]
summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
summary_table.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (0,0), MID_BLUE),
    ("BACKGROUND",    (1,0), (1,0), MID_BLUE),
    ("BACKGROUND",    (2,0), (2,0), GREEN),
    ("TOPPADDING",    (0,0), (-1,-1), 10),
    ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ("ALIGN",         (0,0), (-1,-1), "CENTER"),
    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ("GRID",          (0,0), (-1,-1), 1, WHITE),
]))
story.append(summary_table)
story.append(Spacer(1, 0.2*inch))

# -----------------------------------------
# PRICE COMPARISON TABLE
# -----------------------------------------
sec_data = [[Paragraph("📊  Price Comparison by Item", section_style)]]
sec_table = Table(sec_data, colWidths=[7.5*inch])
sec_table.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), DARK_BLUE),
    ("TOPPADDING",    (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING",   (0,0), (-1,-1), 10),
]))
story.append(sec_table)
story.append(Spacer(1, 0.05*inch))

# Table headers
header_row = [
    Paragraph("<b>Item</b>", ParagraphStyle("h", parent=styles["Normal"], fontSize=9, textColor=WHITE, fontName="Helvetica-Bold")),
    Paragraph("<b>Unit</b>", ParagraphStyle("h", parent=styles["Normal"], fontSize=9, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold")),
    Paragraph("<b>Market Basket</b>", ParagraphStyle("h", parent=styles["Normal"], fontSize=9, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold")),
    Paragraph("<b>Hannaford</b>", ParagraphStyle("h", parent=styles["Normal"], fontSize=9, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold")),
    Paragraph("<b>Best Price</b>", ParagraphStyle("h", parent=styles["Normal"], fontSize=9, textColor=WHITE, alignment=TA_CENTER, fontName="Helvetica-Bold")),
]

table_data = [header_row]
current_category = None

for d in price_data:
    # Category separator
    if d["category"] != current_category:
        current_category = d["category"]
        cat_row = [
            Paragraph(f"<b>{current_category}</b>", ParagraphStyle("cat", parent=styles["Normal"], fontSize=9, textColor=DARK_BLUE, fontName="Helvetica-Bold")),
            "", "", "", ""
        ]
        table_data.append(cat_row)

    mb    = d["mb"]
    hf    = d["hf"]
    best  = "Market Basket" if (mb and hf and mb <= hf) else "Hannaford"
    best_price = min(p for p in [mb, hf] if p) if (mb or hf) else None

    row = [
        Paragraph(d["name"], ParagraphStyle("n", parent=styles["Normal"], fontSize=9)),
        Paragraph(d["unit"], ParagraphStyle("n", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER)),
        Paragraph(f"${mb:.2f}" if mb else "—", ParagraphStyle("n", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER)),
        Paragraph(f"${hf:.2f}" if hf else "—", ParagraphStyle("n", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER)),
        Paragraph(f"${best_price:.2f} ({best[:2]})" if best_price else "—", ParagraphStyle("n", parent=styles["Normal"], fontSize=9, alignment=TA_CENTER, textColor=GREEN if best_price else colors.black)),
    ]
    table_data.append(row)

price_table = Table(table_data, colWidths=[2.5*inch, 1.0*inch, 1.3*inch, 1.2*inch, 1.5*inch])
price_table_style = [
    ("BACKGROUND",    (0,0), (-1,0), DARK_BLUE),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ("GRID",          (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
]

# Alternating rows
for i, row in enumerate(table_data[1:], 1):
    if len(str(row[1])) == 0 or row[1] == "":
        price_table_style.append(("BACKGROUND", (0,i), (-1,i), LIGHT_BLUE))
    elif i % 2 == 0:
        price_table_style.append(("BACKGROUND", (0,i), (-1,i), LIGHT_GRAY))
    else:
        price_table_style.append(("BACKGROUND", (0,i), (-1,i), WHITE))

price_table.setStyle(TableStyle(price_table_style))
story.append(price_table)
story.append(Spacer(1, 0.2*inch))

# -----------------------------------------
# PRICE ANALYSIS
# -----------------------------------------
sec_data2 = [[Paragraph("💡  Shopping Insights", section_style)]]
sec_table2 = Table(sec_data2, colWidths=[7.5*inch])
sec_table2.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), DARK_BLUE),
    ("TOPPADDING",    (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING",   (0,0), (-1,-1), 10),
]))
story.append(sec_table2)
story.append(Spacer(1, 0.1*inch))
story.append(Paragraph(price_analysis, body_style))
story.append(Spacer(1, 0.2*inch))

# -----------------------------------------
# MEAL IDEAS
# -----------------------------------------
sec_data3 = [[Paragraph("🍽️  3 Quick Meal Ideas (30 Minutes or Less)", section_style)]]
sec_table3 = Table(sec_data3, colWidths=[7.5*inch])
sec_table3.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), DARK_BLUE),
    ("TOPPADDING",    (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING",   (0,0), (-1,-1), 10),
]))
story.append(sec_table3)
story.append(Spacer(1, 0.1*inch))

meal_colors = [MID_BLUE, GREEN, ORANGE]

for i, meal in enumerate(meals):
    # Meal header
    meal_header = [[
        Paragraph(f"<b>{i+1}. {meal['name']}</b>  ⏱ {meal['time']}", ParagraphStyle(
            "mh", parent=styles["Normal"], fontSize=11,
            textColor=WHITE, fontName="Helvetica-Bold"
        ))
    ]]
    meal_header_table = Table(meal_header, colWidths=[7.5*inch])
    meal_header_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), meal_colors[i]),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ]))
    story.append(meal_header_table)

    # Ingredients and steps
    ingredients = ", ".join(meal["ingredients"])
    story.append(Spacer(1, 0.05*inch))
    story.append(Paragraph(f"<b>Ingredients:</b> {ingredients}", small_style))
    story.append(Spacer(1, 0.05*inch))

    if isinstance(meal["instructions"], list):
        for step_num, step in enumerate(meal["instructions"], 1):
            story.append(Paragraph(f"{step_num}. {step}", small_style))
    else:
        story.append(Paragraph(meal["instructions"], small_style))

    story.append(Spacer(1, 0.15*inch))

# -----------------------------------------
# FOOTER
# -----------------------------------------
footer_data = [[
    Paragraph(
        f"Generated automatically by your Weekly Grocery Tracker  |  {date.today().strftime('%B %d, %Y')}  |  Prices are estimates and may vary",
        ParagraphStyle("footer", parent=styles["Normal"], fontSize=8, textColor=WHITE, alignment=TA_CENTER)
    )
]]
footer_table = Table(footer_data, colWidths=[7.5*inch])
footer_table.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), DARK_BLUE),
    ("TOPPADDING",    (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
]))
story.append(footer_table)

# Build PDF
doc.build(story)
print(f"✅ PDF report generated!")
print(f"📁 Saved as: {REPORT_FILE}\n")
