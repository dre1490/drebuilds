"""
NovaTech Analytics Platform
Phase 2: Query the database for key business metrics

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your NovaTech Analytics folder
3. Run: python query_novatech.py
"""

import sqlite3
from datetime import date

print("\n" + "=" * 60)
print("   NOVATECH ANALYTICS — Business Metrics Report")
print("=" * 60)

conn   = sqlite3.connect("novatech.db")
cursor = conn.cursor()

# -----------------------------------------
# METRIC 1 — Monthly Recurring Revenue (MRR)
# Total revenue from all active subscriptions
# This is the most important SaaS metric
# -----------------------------------------
cursor.execute("""
    SELECT SUM(monthly_fee)
    FROM customers
    WHERE status = 'Active'
""")
mrr = cursor.fetchone()[0] or 0
print(f"\n💰 METRIC 1 — Monthly Recurring Revenue (MRR)")
print(f"-" * 50)
print(f"   Total MRR: ${mrr:,.2f}")

# -----------------------------------------
# METRIC 2 — Churn Rate
# Percentage of customers who cancelled
# Lower is better — industry average is 5-7%
# -----------------------------------------
cursor.execute("SELECT COUNT(*) FROM customers")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM customers WHERE status = 'Churned'")
churned = cursor.fetchone()[0]

churn_rate = (churned / total * 100) if total else 0
print(f"\n📉 METRIC 2 — Churn Rate")
print(f"-" * 50)
print(f"   Total Customers:   {total}")
print(f"   Churned:           {churned}")
print(f"   Churn Rate:        {churn_rate:.1f}%")

# -----------------------------------------
# METRIC 3 — Revenue by Plan
# Which plan drives the most revenue
# -----------------------------------------
cursor.execute("""
    SELECT plan,
           COUNT(*) as customers,
           SUM(monthly_fee) as revenue
    FROM customers
    WHERE status = 'Active'
    GROUP BY plan
    ORDER BY revenue DESC
""")
by_plan = cursor.fetchall()
print(f"\n📊 METRIC 3 — Revenue by Plan")
print(f"-" * 50)
print(f"   {'Plan':<15} {'Customers':>10} {'Revenue':>12}")
for row in by_plan:
    print(f"   {row[0]:<15} {row[1]:>10} ${row[2]:>10.2f}")

# -----------------------------------------
# METRIC 4 — Revenue by Region
# Where your best customers are located
# -----------------------------------------
cursor.execute("""
    SELECT region,
           COUNT(*) as customers,
           SUM(monthly_fee) as revenue
    FROM customers
    WHERE status = 'Active'
    GROUP BY region
    ORDER BY revenue DESC
""")
by_region = cursor.fetchall()
print(f"\n🌍 METRIC 4 — Revenue by Region")
print(f"-" * 50)
print(f"   {'Region':<20} {'Customers':>10} {'Revenue':>12}")
for row in by_region:
    print(f"   {row[0]:<20} {row[1]:>10} ${row[2]:>10.2f}")

# -----------------------------------------
# METRIC 5 — Top Selling Products
# Which add-ons customers buy most
# -----------------------------------------
cursor.execute("""
    SELECT product,
           COUNT(*) as units_sold,
           SUM(amount) as total_revenue
    FROM sales
    GROUP BY product
    ORDER BY total_revenue DESC
    LIMIT 5
""")
top_products = cursor.fetchall()
print(f"\n🏆 METRIC 5 — Top Selling Products")
print(f"-" * 50)
print(f"   {'Product':<25} {'Units':>6} {'Revenue':>12}")
for row in top_products:
    print(f"   {row[0]:<25} {row[1]:>6} ${row[2]:>10.2f}")

# -----------------------------------------
# METRIC 6 — Support Ticket Summary
# Volume, open tickets, avg resolution time
# -----------------------------------------
cursor.execute("SELECT COUNT(*) FROM support_tickets")
total_tickets = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'Open'")
open_tickets = cursor.fetchone()[0]

cursor.execute("""
    SELECT AVG(resolution_hours)
    FROM support_tickets
    WHERE status = 'Resolved'
""")
avg_resolution = cursor.fetchone()[0] or 0

cursor.execute("""
    SELECT AVG(satisfaction)
    FROM support_tickets
    WHERE satisfaction IS NOT NULL
""")
avg_satisfaction = cursor.fetchone()[0] or 0

print(f"\n🎫 METRIC 6 — Support Tickets")
print(f"-" * 50)
print(f"   Total Tickets:          {total_tickets}")
print(f"   Open Tickets:           {open_tickets}")
print(f"   Avg Resolution Time:    {avg_resolution:.1f} hours")
print(f"   Avg Satisfaction Score: {avg_satisfaction:.1f} / 5.0")

# -----------------------------------------
# METRIC 7 — Total Sales Revenue
# All add-on purchases combined
# -----------------------------------------
cursor.execute("SELECT SUM(amount) FROM sales")
total_sales = cursor.fetchone()[0] or 0

cursor.execute("SELECT COUNT(*) FROM sales")
total_transactions = cursor.fetchone()[0]

print(f"\n🛒 METRIC 7 — Sales Transactions")
print(f"-" * 50)
print(f"   Total Transactions:  {total_transactions}")
print(f"   Total Sales Revenue: ${total_sales:,.2f}")

print(f"\n{'=' * 60}")
print(f"✅ All metrics pulled successfully — {date.today()}\n")

conn.close()
