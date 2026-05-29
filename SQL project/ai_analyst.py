"""
Vertex Solutions - AI Analyst
Uses Groq AI to read your customer data and write a business analysis

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your SQL project folder
3. Run: pip install groq
4. Run: python ai_analyst.py
"""

import sqlite3
from groq import Groq
from datetime import date

# -----------------------------------------
# YOUR GROQ API KEY
# -----------------------------------------
API_KEY = "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"

# -----------------------------------------
# SIMPLE EXPLANATION:
# We connect to our database, pull the key
# numbers, then send them to the AI and ask
# it to write a business summary for us
# -----------------------------------------

# STEP 1 — Pull data from database
print("\n🗄️  Reading database...")

conn   = sqlite3.connect("vertex_solutions.db")
cursor = conn.cursor()

# Total customers
cursor.execute("SELECT COUNT(*) FROM customers")
total_customers = cursor.fetchone()[0]

# Revenue by plan
cursor.execute("""
    SELECT plan, COUNT(*) as customers, SUM(monthly_fee) as revenue
    FROM customers
    GROUP BY plan
    ORDER BY revenue DESC
""")
revenue_by_plan = cursor.fetchall()
total_revenue   = sum(row[2] for row in revenue_by_plan)

# Unpaid accounts
cursor.execute("""
    SELECT name, plan, monthly_fee
    FROM customers
    WHERE paid = 'No'
    ORDER BY monthly_fee DESC
""")
unpaid       = cursor.fetchall()
unpaid_total = sum(row[2] for row in unpaid)

conn.close()
print("✅ Data pulled successfully")

# -----------------------------------------
# STEP 2 — Build the data summary
# We organize the numbers into a clear
# text block that the AI can read and understand
# -----------------------------------------
today = date.today().strftime("%B %d, %Y")

revenue_breakdown = "\n".join([
    f"  - {row[0]}: {row[1]} customers, ${row[2]:,.2f} revenue"
    for row in revenue_by_plan
])

unpaid_breakdown = "\n".join([
    f"  - {row[0]} ({row[1]}): ${row[2]:,.2f} outstanding"
    for row in unpaid
]) if unpaid else "  - None"

data_summary = f"""
Date: {today}
Total Customers: {total_customers}
Total Monthly Revenue: ${total_revenue:,.2f}

Revenue by Plan:
{revenue_breakdown}

Unpaid Accounts ({len(unpaid)} total, ${unpaid_total:,.2f} outstanding):
{unpaid_breakdown}
"""

print("\n📋 Data summary ready")

# -----------------------------------------
# STEP 3 — Send to Groq AI
# This is the prompt — the instructions we
# give the AI telling it what to write
# Think of it like briefing a real analyst
# -----------------------------------------
print("🤖 Sending to AI analyst...\n")

client = Groq(api_key=API_KEY)

prompt = f"""
You are a senior business analyst at Vertex Solutions, a software company.
Review the following weekly customer data and write a short professional analysis.

Your analysis should:
- Summarize the overall performance in 2-3 sentences
- Highlight which plan is driving the most value and why
- Flag the unpaid accounts and recommend which to prioritize first
- End with one actionable recommendation for the team

Keep it concise, professional, and easy for a manager to read quickly.

Here is the data:
{data_summary}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

analysis = response.choices[0].message.content

# -----------------------------------------
# STEP 4 — Display the analysis
# -----------------------------------------
print("=" * 60)
print("   VERTEX SOLUTIONS — AI Analyst Report")
print("=" * 60)
print(analysis)
print("=" * 60)

# Save to a text file for reference
output_file = f"ai_analysis_{date.today().strftime('%Y-%m-%d')}.txt"
with open(output_file, "w") as f:
    f.write(f"VERTEX SOLUTIONS — AI Analysis\n")
    f.write(f"Generated: {today}\n\n")
    f.write(analysis)

print(f"\n💾 Analysis saved as: {output_file}\n")
