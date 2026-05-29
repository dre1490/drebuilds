"""
NovaTech Analytics Platform
Phase 5: Full Interactive Dashboard

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your NovaTech Analytics folder
3. Run: python novatech_dashboard.py
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
DB_FILE = "novatech.db"

# -----------------------------------------
# STEP 1 — Pull all data from database
# -----------------------------------------
print("\n🗄️  Reading NovaTech database...")

conn   = sqlite3.connect("novatech.db")
cursor = conn.cursor()

# MRR
cursor.execute("SELECT SUM(monthly_fee) FROM customers WHERE status = 'Active'")
mrr = cursor.fetchone()[0] or 0

# Churn
cursor.execute("SELECT COUNT(*) FROM customers")
total_customers = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM customers WHERE status = 'Churned'")
churned = cursor.fetchone()[0]
active = total_customers - churned
churn_rate = (churned / total_customers * 100) if total_customers else 0

# Revenue by plan
cursor.execute("""
    SELECT plan, COUNT(*) as customers, SUM(monthly_fee) as revenue
    FROM customers WHERE status = 'Active'
    GROUP BY plan ORDER BY revenue DESC
""")
by_plan = cursor.fetchall()
plan_names    = [row[0] for row in by_plan]
plan_counts   = [row[1] for row in by_plan]
plan_revenues = [row[2] for row in by_plan]

# Revenue by region
cursor.execute("""
    SELECT region, COUNT(*) as customers, SUM(monthly_fee) as revenue
    FROM customers WHERE status = 'Active'
    GROUP BY region ORDER BY revenue DESC
""")
by_region     = cursor.fetchall()
region_names  = [row[0] for row in by_region]
region_revs   = [row[2] for row in by_region]

# Top products
cursor.execute("""
    SELECT product, COUNT(*) as units, SUM(amount) as revenue
    FROM sales GROUP BY product ORDER BY revenue DESC
""")
products      = cursor.fetchall()
product_names = [row[0] for row in products]
product_units = [row[1] for row in products]
product_revs  = [row[2] for row in products]

# Sales by date
cursor.execute("""
    SELECT sale_date, SUM(amount) as daily_revenue
    FROM sales GROUP BY sale_date ORDER BY sale_date
""")
sales_by_date = cursor.fetchall()
sale_dates    = [row[0] for row in sales_by_date]
sale_amounts  = [row[1] for row in sales_by_date]

# Support tickets by priority
cursor.execute("""
    SELECT priority, COUNT(*) as total
    FROM support_tickets GROUP BY priority ORDER BY total DESC
""")
by_priority    = cursor.fetchall()
priority_names = [row[0] for row in by_priority]
priority_counts= [row[1] for row in by_priority]

# Satisfaction distribution
cursor.execute("""
    SELECT satisfaction, COUNT(*) as total
    FROM support_tickets
    WHERE satisfaction IS NOT NULL
    GROUP BY satisfaction ORDER BY satisfaction
""")
sat_data    = cursor.fetchall()
sat_scores  = [f"⭐ {row[0]}" for row in sat_data]
sat_counts  = [row[1] for row in sat_data]

# Support status
cursor.execute("""
    SELECT status, COUNT(*) as total
    FROM support_tickets GROUP BY status
""")
ticket_status = cursor.fetchall()
status_labels = [row[0] for row in ticket_status]
status_counts = [row[1] for row in ticket_status]

cursor.execute("SELECT AVG(resolution_hours) FROM support_tickets WHERE status = 'Resolved'")
avg_resolution = cursor.fetchone()[0] or 0

cursor.execute("SELECT AVG(satisfaction) FROM support_tickets WHERE satisfaction IS NOT NULL")
avg_satisfaction = cursor.fetchone()[0] or 0

conn.close()
print("✅ Data pulled successfully")

# -----------------------------------------
# STEP 2 — Build dashboard
# -----------------------------------------
print("📊 Building dashboard...")

colors     = ["#1F3864", "#2E75B6", "#70AD47", "#ED7D31", "#FFC000"]
today      = date.today().strftime("%B %d, %Y")

fig = make_subplots(
    rows=3, cols=3,
    subplot_titles=(
        "Active vs Churned Customers",
        "Revenue by Plan",
        "Revenue by Region",
        "Daily Sales Revenue Trend",
        "Top Products by Revenue",
        "Top Products by Units Sold",
        "Support Tickets by Priority",
        "Customer Satisfaction Scores",
        "Ticket Status Overview",
    ),
    specs=[
        [{"type": "pie"},  {"type": "bar"},   {"type": "bar"}],
        [{"type": "bar"},  {"type": "bar"},   {"type": "bar"}],
        [{"type": "bar"},  {"type": "bar"},   {"type": "pie"}],
    ],
    vertical_spacing=0.18,
    horizontal_spacing=0.10
)

# Chart 1 — Active vs Churned pie
fig.add_trace(go.Pie(
    labels=["Active", "Churned"],
    values=[active, churned],
    marker_colors=["#70AD47", "#C00000"],
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
    name="Customer Status"
), row=1, col=1)

# Chart 2 — Revenue by plan
fig.add_trace(go.Bar(
    x=plan_names,
    y=plan_revenues,
    marker_color=colors[:len(plan_names)],
    text=[f"${r:,.0f}" for r in plan_revenues],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
    name="Plan Revenue"
), row=1, col=2)

# Chart 3 — Revenue by region
fig.add_trace(go.Bar(
    x=region_names,
    y=region_revs,
    marker_color=colors[:len(region_names)],
    text=[f"${r:,.0f}" for r in region_revs],
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
    name="Region Revenue"
), row=1, col=3)

# Chart 4 — Daily sales trend
fig.add_trace(go.Bar(
    x=sale_dates,
    y=sale_amounts,
    marker_color="#2E75B6",
    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>",
    name="Daily Sales"
), row=2, col=1)

# Chart 5 — Top products by revenue
fig.add_trace(go.Bar(
    x=product_revs,
    y=product_names,
    orientation="h",
    marker_color=colors[:len(product_names)],
    text=[f"${r:,.0f}" for r in product_revs],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.2f}<extra></extra>",
    name="Product Revenue"
), row=2, col=2)

# Chart 6 — Top products by units
fig.add_trace(go.Bar(
    x=product_units,
    y=product_names,
    orientation="h",
    marker_color="#70AD47",
    text=product_units,
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Units: %{x}<extra></extra>",
    name="Units Sold"
), row=2, col=3)

# Chart 7 — Tickets by priority
priority_colors = {
    "Critical": "#C00000",
    "High":     "#ED7D31",
    "Medium":   "#FFC000",
    "Low":      "#70AD47"
}
fig.add_trace(go.Bar(
    x=priority_names,
    y=priority_counts,
    marker_color=[priority_colors.get(p, "#2E75B6") for p in priority_names],
    text=priority_counts,
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Tickets: %{y}<extra></extra>",
    name="Ticket Priority"
), row=3, col=1)

# Chart 8 — Satisfaction scores
fig.add_trace(go.Bar(
    x=sat_scores,
    y=sat_counts,
    marker_color=["#C00000", "#ED7D31", "#FFC000", "#70AD47", "#1F3864"][:len(sat_scores)],
    text=sat_counts,
    textposition="outside",
    hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
    name="Satisfaction"
), row=3, col=2)

# Chart 9 — Ticket status pie
fig.add_trace(go.Pie(
    labels=status_labels,
    values=status_counts,
    marker_colors=["#70AD47", "#ED7D31"],
    textinfo="label+percent",
    hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
    name="Ticket Status"
), row=3, col=3)

# -----------------------------------------
# Layout
# -----------------------------------------
fig.update_layout(
    title=dict(
        text=f"NOVATECH ANALYTICS PLATFORM  |  Executive Dashboard  |  {today}",
        font=dict(size=18, color="#1F3864"),
        x=0.5
    ),
    showlegend=False,
    height=1100,
    paper_bgcolor="white",
    plot_bgcolor="#F8FAFC",
)

# Add KPI banner as annotation
fig.add_annotation(
    text=f"MRR: ${mrr:,.2f}   |   Churn Rate: {churn_rate:.1f}%   |   Avg Resolution: {avg_resolution:.1f}hrs   |   Satisfaction: {avg_satisfaction:.1f}/5.0",
    xref="paper", yref="paper",
    x=0.5, y=1.04,
    showarrow=False,
    font=dict(size=13, color="white"),
    bgcolor="#1F3864",
    borderpad=8
)

fig.update_yaxes(gridcolor="#E0E0E0")
fig.update_xaxes(tickangle=-35, row=2, col=1)

# -----------------------------------------
# STEP 3 — Save and open
# -----------------------------------------
output_file = "novatech_dashboard.html"
fig.write_html(output_file)

print(f"✅ Dashboard built successfully!")
print(f"🌐 Opening in your browser...\n")

webbrowser.open(f"file:///{os.path.abspath(output_file)}")
