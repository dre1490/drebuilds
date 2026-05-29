"""
NovaTech Analytics Platform
Phase 4: AI Executive Summary using Groq

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your NovaTech Analytics folder
3. Run: python ai_executive_summary.py
"""

import sqlite3
from groq import Groq
from datetime import date

# -----------------------------------------
# YOUR GROQ API KEY
# -----------------------------------------
API_KEY = "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"

# -----------------------------------------
# STEP 1 — Pull all metrics from database
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
churn_rate = (churned / total_customers * 100) if total_customers else 0

# Revenue by plan
cursor.execute("""
    SELECT plan, COUNT(*) as customers, SUM(monthly_fee) as revenue
    FROM customers WHERE status = 'Active'
    GROUP BY plan ORDER BY revenue DESC
""")
by_plan = cursor.fetchall()

# Revenue by region
cursor.execute("""
    SELECT region, COUNT(*) as customers, SUM(monthly_fee) as revenue
    FROM customers WHERE status = 'Active'
    GROUP BY region ORDER BY revenue DESC
""")
by_region = cursor.fetchall()

# Top products
cursor.execute("""
    SELECT product, COUNT(*) as units, SUM(amount) as revenue
    FROM sales GROUP BY product ORDER BY revenue DESC LIMIT 3
""")
top_products = cursor.fetchall()

# Total sales
cursor.execute("SELECT SUM(amount), COUNT(*) FROM sales")
sales_row = cursor.fetchone()
total_sales = sales_row[0] or 0
total_transactions = sales_row[1] or 0

# Support metrics
cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'Open'")
open_tickets = cursor.fetchone()[0]

cursor.execute("SELECT AVG(resolution_hours) FROM support_tickets WHERE status = 'Resolved'")
avg_resolution = cursor.fetchone()[0] or 0

cursor.execute("SELECT AVG(satisfaction) FROM support_tickets WHERE satisfaction IS NOT NULL")
avg_satisfaction = cursor.fetchone()[0] or 0

conn.close()
print("✅ All metrics pulled successfully")

# -----------------------------------------
# STEP 2 — Build data summary for AI
# Organize everything into a clear brief
# the AI can read and understand
# -----------------------------------------
today = date.today().strftime("%B %d, %Y")

plan_breakdown = "\n".join([
    f"  - {row[0]}: {row[1]} customers, ${row[2]:,.2f}/month ({row[2]/mrr*100:.1f}% of MRR)"
    for row in by_plan
])

region_breakdown = "\n".join([
    f"  - {row[0]}: {row[1]} customers, ${row[2]:,.2f}/month"
    for row in by_region
])

product_breakdown = "\n".join([
    f"  - {row[0]}: {row[1]} units sold, ${row[2]:,.2f} total"
    for row in top_products
])

data_brief = f"""
Report Date: {today}

SUBSCRIPTION METRICS:
- Total Customers: {total_customers} ({churned} churned, {total_customers - churned} active)
- Monthly Recurring Revenue (MRR): ${mrr:,.2f}
- Churn Rate: {churn_rate:.1f}% (industry benchmark: 5-7%)

REVENUE BY PLAN:
{plan_breakdown}

REVENUE BY REGION:
{region_breakdown}

TOP SELLING ADD-ONS:
{product_breakdown}
- Total Add-on Revenue: ${total_sales:,.2f} across {total_transactions} transactions

SUPPORT & SATISFACTION:
- Open Tickets: {open_tickets}
- Average Resolution Time: {avg_resolution:.1f} hours (benchmark: under 24 hours)
- Average Satisfaction Score: {avg_satisfaction:.1f} / 5.0
"""

print("\n📋 Data brief prepared")

# -----------------------------------------
# STEP 3 — Send to Groq AI
# We give it a detailed role and clear
# instructions on what to write
# -----------------------------------------
print("🤖 Sending to AI analyst...\n")

client = Groq(api_key=API_KEY)

prompt = f"""
You are the Chief Analytics Officer at NovaTech, a fast growing SaaS company.
Review the following business metrics and write a concise executive summary
for the board of directors.

Your summary must include exactly these four sections:

1. BUSINESS HEALTH OVERVIEW
   2-3 sentences summarizing overall performance

2. WHAT IS WORKING
   2-3 specific strengths backed by the data

3. IMMEDIATE CONCERNS
   2-3 specific problems that need urgent attention with data to back them up

4. STRATEGIC RECOMMENDATION
   One clear, specific action the leadership team should take this week

Keep the tone professional but direct. Be specific with numbers.
A board member should be able to read this in under 2 minutes.

Here is the data:
{data_brief}
"""

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

summary = response.choices[0].message.content

# -----------------------------------------
# STEP 4 — Display and save the summary
# -----------------------------------------
print("=" * 60)
print("   NOVATECH — AI Executive Summary")
print("=" * 60)
print(summary)
print("=" * 60)

output_file = f"executive_summary_{date.today().strftime('%Y-%m-%d')}.txt"
with open(output_file, "w") as f:
    f.write(f"NOVATECH ANALYTICS — AI Executive Summary\n")
    f.write(f"Generated: {today}\n")
    f.write("=" * 60 + "\n\n")
    f.write(summary)

print(f"\n💾 Summary saved as: {output_file}\n")
