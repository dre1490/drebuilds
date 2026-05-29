"""
Vertex Solutions - Interactive Customer Dashboard
Opens a visual chart in your browser showing customer and revenue data

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your SQL project folder
3. Run: python dashboard.py
"""

import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date
import os
import webbrowser

# -----------------------------------------
# SETTINGS
# -----------------------------------------
DB_FILE = "vertex_solutions.db"

# -----------------------------------------
# STEP 1 — Pull data from database
# -----------------------------------------
print("\n🗄️  Reading database...")

conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Customers by plan
cursor.execute("""
    SELECT plan, COUNT(*) as total
    FROM customers
    GROUP BY plan
    ORDER BY total DESC
""")
by_plan = cursor.fetchall()
plans   = [row[0] for row in by_plan]
counts  = [row[1] for row in by_plan]

# Revenue by plan
cursor.execute("""
    SELECT plan, SUM(monthly_fee) as revenue
    FROM customers
    GROUP BY plan
    ORDER BY revenue DESC
""")
by_revenue   = cursor.fetchall()
rev_plans    = [row[0] for row in by_revenue]
rev_amounts  = [row[1] for row in by_revenue]

# Paid vs unpaid
cursor.execute("""
    SELECT paid, COUNT(*) as total
    FROM customers
    GROUP BY paid
""")
payment_data = cursor.fetchall()
payment_labels = [row[0] for row in payment_data]
payment_counts = [row[1] for row in payment_data]

# Unpaid customers detail
cursor.execute("""
    SELECT name, plan, monthly_fee
    FROM customers
    WHERE paid = 'No'
    ORDER BY monthly_fee DESC
""")
unpaid = cursor.fetchall()

conn.close()
print("✅ Data pulled successfully")

# -----------------------------------------
# STEP 2 — Build dashboard
# -----------------------------------------
print("📊 Building dashboard...")

colors       = ["#1F3864", "#2E75B6", "#70AD47"]
today        = date.today().strftime("%B %d, %Y")

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Customers by Plan",
        "Monthly Revenue by Plan",
        "Paid vs Unpaid Accounts",
        "Unpaid Account Details"
    ),
    specs=[
        [{"type": "bar"},  {"type": "bar"}],
        [{"type": "pie"},  {"type": "table"}]
    ],
    vertical_spacing=0.18,
    horizontal_spacing=0.12
)

# Chart 1 — Customers by plan
fig.add_trace(
    go.Bar(
        x=plans,
        y=counts,
        marker_color=colors[:len(plans)],
        text=counts,
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Customers: %{y}<extra></extra>",
        name="Customers"
    ),
    row=1, col=1
)

# Chart 2 — Revenue by plan
fig.add_trace(
    go.Bar(
        x=rev_plans,
        y=rev_amounts,
        marker_color=colors[:len(rev_plans)],
        text=[f"${r:,.2f}" for r in rev_amounts],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
        name="Revenue"
    ),
    row=1, col=2
)

# Chart 3 — Paid vs unpaid pie
fig.add_trace(
    go.Pie(
        labels=payment_labels,
        values=payment_counts,
        marker_colors=["#70AD47", "#C00000"],
        textinfo="label+percent",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
        name="Payment Status"
    ),
    row=2, col=1
)

# Chart 4 — Unpaid detail table
fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>Customer</b>", "<b>Plan</b>", "<b>Amount Due</b>"],
            fill_color="#C00000",
            font=dict(color="white", size=11),
            align="left",
            height=28
        ),
        cells=dict(
            values=[
                [row[0] for row in unpaid],
                [row[1] for row in unpaid],
                [f"${row[2]:,.2f}" for row in unpaid]
            ],
            fill_color=[["#FFF2CC", "#FFFFFF"] * len(unpaid)],
            font=dict(size=10),
            align="left",
            height=24
        )
    ),
    row=2, col=2
)

# Layout
fig.update_layout(
    title=dict(
        text=f"VERTEX SOLUTIONS — Customer Dashboard  |  {today}",
        font=dict(size=18, color="#1F3864"),
        x=0.5
    ),
    showlegend=False,
    height=750,
    paper_bgcolor="white",
    plot_bgcolor="#F8FAFC",
)

fig.update_yaxes(gridcolor="#E0E0E0", row=1, col=1)
fig.update_yaxes(gridcolor="#E0E0E0", tickprefix="$", row=1, col=2)

# -----------------------------------------
# STEP 3 — Save and open in browser
# -----------------------------------------
output_file = "dashboard.html"
fig.write_html(output_file)

print(f"✅ Dashboard built successfully!")
print(f"🌐 Opening in your browser...\n")

webbrowser.open(f"file:///{os.path.abspath(output_file)}")
