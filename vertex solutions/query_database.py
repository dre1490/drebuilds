"""
Vertex Solutions - Customer Database Queries
Step 2: Run SQL queries to answer your manager's questions

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your SQL project folder
3. Run: python query_database.py
"""

import sqlite3

# -----------------------------------------
# Connect to the database
# -----------------------------------------
conn   = sqlite3.connect("vertex_solutions.db")
cursor = conn.cursor()

print("\n" + "=" * 55)
print("   VERTEX SOLUTIONS — Customer Database Report")
print("=" * 55)

# -----------------------------------------
# QUERY 1 — Total customers signed up this month
# -----------------------------------------
cursor.execute("""
    SELECT COUNT(*) 
    FROM customers
    WHERE signup_date LIKE '2026-05%'
""")
total = cursor.fetchone()[0]
print(f"\n📊 QUERY 1 — Total Customers This Month")
print(f"-" * 40)
print(f"   Total signups in May 2026: {total} customers")

# -----------------------------------------
# QUERY 2 — Customers by plan
# -----------------------------------------
cursor.execute("""
    SELECT plan, COUNT(*) as total_customers
    FROM customers
    GROUP BY plan
    ORDER BY total_customers DESC
""")
rows = cursor.fetchall()
print(f"\n📊 QUERY 2 — Customers by Plan")
print(f"-" * 40)
print(f"   {'Plan':<15} {'Customers':>10}")
for row in rows:
    print(f"   {row[0]:<15} {row[1]:>10}")

# -----------------------------------------
# QUERY 3 — Total revenue by plan
# -----------------------------------------
cursor.execute("""
    SELECT plan, 
           COUNT(*) as customers,
           SUM(monthly_fee) as total_revenue
    FROM customers
    GROUP BY plan
    ORDER BY total_revenue DESC
""")
rows = cursor.fetchall()
print(f"\n📊 QUERY 3 — Revenue by Plan")
print(f"-" * 40)
print(f"   {'Plan':<15} {'Customers':>10} {'Revenue':>12}")
total_revenue = 0
for row in rows:
    print(f"   {row[0]:<15} {row[1]:>10} ${row[2]:>10.2f}")
    total_revenue += row[2]
print(f"   {'TOTAL':<15} {'':>10} ${total_revenue:>10.2f}")

# -----------------------------------------
# QUERY 4 — Customers who haven't paid
# -----------------------------------------
cursor.execute("""
    SELECT name, email, plan, monthly_fee
    FROM customers
    WHERE paid = 'No'
    ORDER BY monthly_fee DESC
""")
rows = cursor.fetchall()
unpaid_total = sum(row[3] for row in rows)
print(f"\n📊 QUERY 4 — Unpaid Customers")
print(f"-" * 40)
print(f"   {'Name':<20} {'Plan':<12} {'Amount Due':>10}")
for row in rows:
    print(f"   {row[0]:<20} {row[2]:<12} ${row[3]:>8.2f}")
print(f"\n   ⚠️  Total outstanding: ${unpaid_total:.2f}")

print(f"\n{'=' * 55}")
print(f"✅ All queries ran successfully\n")

conn.close()
