"""
Horizon Capital - Interactive Fund Price Dashboard
Opens a visual chart in your browser showing all fund prices

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your Spread sheet automation folder
3. Run: python dashboard.py
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# -----------------------------------------
# SETTINGS
# -----------------------------------------
EXCEL_FILE = "horizon_capital_tracker.xlsx"

# -----------------------------------------
# STEP 1 — Read your Excel file
# Pandas reads the spreadsheet into a table
# we can work with in Python
# -----------------------------------------
print("\n📂 Reading Excel file...")

try:
    df = pd.read_excel(EXCEL_FILE, sheet_name="Fund Tracker", header=3)

    # Rename columns to make them easier to work with
    df.columns = ["Fund Name", "Ticker", "Price", "Date", "Status"]

    # Drop any rows with missing prices
    df = df.dropna(subset=["Price"])
    df = df[df["Price"] != "—"]

    # Make sure Price is a number
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Price"])

    print(f"✅ Found {len(df)} funds with price data\n")

except FileNotFoundError:
    print(f"❌ Could not find {EXCEL_FILE}")
    print("Make sure it's in the same folder as this script.\n")
    exit()

except Exception as e:
    print(f"❌ Error reading Excel: {str(e)}\n")
    exit()

# -----------------------------------------
# STEP 2 — Build the dashboard
# We create two charts:
# 1. A bar chart comparing all fund prices
# 2. A table showing the full data
# -----------------------------------------
print("📊 Building dashboard...")

colors = ["#1F3864", "#2E75B6", "#4472C4", "#70AD47", "#ED7D31"]

fig = make_subplots(
    rows=2, cols=1,
    row_heights=[0.65, 0.35],
    subplot_titles=("Fund Prices (NAV)", "Fund Details"),
    specs=[[{"type": "bar"}], [{"type": "table"}]]
)

# Bar chart
fig.add_trace(
    go.Bar(
        x=df["Ticker"],
        y=df["Price"],
        marker_color=colors[:len(df)],
        text=[f"${p:,.2f}" for p in df["Price"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Price: $%{y:,.2f}<extra></extra>",
        name="NAV Price"
    ),
    row=1, col=1
)

# Data table
fig.add_trace(
    go.Table(
        header=dict(
            values=["<b>Fund Name</b>", "<b>Ticker</b>", "<b>Price (NAV)</b>", "<b>Date Updated</b>", "<b>Status</b>"],
            fill_color="#1F3864",
            font=dict(color="white", size=12),
            align="left",
            height=30
        ),
        cells=dict(
            values=[
                df["Fund Name"],
                df["Ticker"],
                [f"${p:,.2f}" for p in df["Price"]],
                df["Date"],
                df["Status"]
            ],
            fill_color=[["#DCE6F1", "#FFFFFF"] * len(df)],
            font=dict(size=11),
            align="left",
            height=25
        )
    ),
    row=2, col=1
)

# Layout
fig.update_layout(
    title=dict(
        text="HORIZON CAPITAL — Daily Fund Price Dashboard",
        font=dict(size=20, color="#1F3864"),
        x=0.5
    ),
    showlegend=False,
    height=750,
    paper_bgcolor="white",
    plot_bgcolor="#F8FAFC",
    yaxis=dict(
        title="Price (USD)",
        tickprefix="$",
        gridcolor="#E0E0E0"
    ),
    xaxis=dict(title="Fund Ticker")
)

# -----------------------------------------
# STEP 3 — Save and open in browser
# -----------------------------------------
output_file = "dashboard.html"
fig.write_html(output_file)

print(f"✅ Dashboard built successfully!")
print(f"🌐 Opening in your browser...\n")

# Open in default browser
import webbrowser
webbrowser.open(f"file:///{os.path.abspath(output_file)}")
