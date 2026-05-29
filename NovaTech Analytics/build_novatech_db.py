"""
NovaTech Analytics Platform
Phase 1: Build the database with three connected tables

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your NovaTech Analytics folder
3. Run: python build_novatech_db.py
"""

import sqlite3
from datetime import date, timedelta
import random

print("\n🗄️  Building NovaTech Analytics database...\n")

conn   = sqlite3.connect("novatech.db")
cursor = conn.cursor()

# -----------------------------------------
# DROP TABLES IF REBUILDING
# -----------------------------------------
cursor.execute("DROP TABLE IF EXISTS customers")
cursor.execute("DROP TABLE IF EXISTS sales")
cursor.execute("DROP TABLE IF EXISTS support_tickets")

# -----------------------------------------
# TABLE 1 — CUSTOMERS
# Tracks who signed up, what plan, and
# whether they cancelled (churned)
# -----------------------------------------
cursor.execute("""
    CREATE TABLE customers (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        email         TEXT NOT NULL,
        plan          TEXT NOT NULL,
        monthly_fee   REAL NOT NULL,
        signup_date   TEXT NOT NULL,
        status        TEXT NOT NULL,
        region        TEXT NOT NULL
    )
""")

plans = {
    "Starter":    49.99,
    "Growth":     149.99,
    "Enterprise": 499.99
}

regions = ["North America", "Europe", "Asia Pacific", "Latin America"]

customers = [
    ("James Carter",      "james.c@email.com",     "Enterprise", "2026-04-01", "Active",   "North America"),
    ("Sofia Reyes",       "sofia.r@email.com",      "Growth",     "2026-04-03", "Active",   "Latin America"),
    ("Marcus Johnson",    "marcus.j@email.com",     "Starter",    "2026-04-05", "Churned",  "North America"),
    ("Priya Patel",       "priya.p@email.com",      "Enterprise", "2026-04-06", "Active",   "Asia Pacific"),
    ("Tyler Brooks",      "tyler.b@email.com",      "Growth",     "2026-04-08", "Active",   "North America"),
    ("Aisha Williams",    "aisha.w@email.com",      "Starter",    "2026-04-10", "Active",   "Europe"),
    ("Derek Thompson",    "derek.t@email.com",      "Growth",     "2026-04-11", "Churned",  "North America"),
    ("Mei Chen",          "mei.c@email.com",        "Enterprise", "2026-04-12", "Active",   "Asia Pacific"),
    ("Carlos Mendez",     "carlos.m@email.com",     "Growth",     "2026-04-14", "Active",   "Latin America"),
    ("Rachel Green",      "rachel.g@email.com",     "Starter",    "2026-04-15", "Active",   "Europe"),
    ("Kevin O'Brien",     "kevin.ob@email.com",     "Enterprise", "2026-04-16", "Active",   "North America"),
    ("Fatima Hassan",     "fatima.h@email.com",     "Starter",    "2026-04-18", "Churned",  "Europe"),
    ("Jordan Lee",        "jordan.l@email.com",     "Growth",     "2026-04-19", "Active",   "Asia Pacific"),
    ("Samantha Cruz",     "sam.c@email.com",        "Enterprise", "2026-04-20", "Active",   "Latin America"),
    ("Nathan Wright",     "nathan.w@email.com",     "Starter",    "2026-04-21", "Active",   "North America"),
    ("Olivia Scott",      "olivia.s@email.com",     "Growth",     "2026-04-22", "Active",   "Europe"),
    ("Brandon King",      "brandon.k@email.com",    "Starter",    "2026-04-23", "Churned",  "North America"),
    ("Yuki Tanaka",       "yuki.t@email.com",       "Enterprise", "2026-04-24", "Active",   "Asia Pacific"),
    ("Danielle Moore",    "danielle.m@email.com",   "Growth",     "2026-04-25", "Active",   "North America"),
    ("Eric Davis",        "eric.d@email.com",       "Starter",    "2026-04-26", "Active",   "Europe"),
    ("Layla Ahmed",       "layla.a@email.com",      "Enterprise", "2026-05-01", "Active",   "Europe"),
    ("Ryan Foster",       "ryan.f@email.com",       "Growth",     "2026-05-02", "Active",   "North America"),
    ("Nina Patel",        "nina.p@email.com",       "Starter",    "2026-05-03", "Active",   "Asia Pacific"),
    ("Omar Hassan",       "omar.h@email.com",       "Growth",     "2026-05-04", "Active",   "Europe"),
    ("Chloe Martin",      "chloe.m@email.com",      "Enterprise", "2026-05-05", "Active",   "North America"),
    ("Diego Rivera",      "diego.r@email.com",      "Starter",    "2026-05-06", "Churned",  "Latin America"),
    ("Emma Wilson",       "emma.w@email.com",       "Growth",     "2026-05-07", "Active",   "Europe"),
    ("Liam Johnson",      "liam.j@email.com",       "Enterprise", "2026-05-08", "Active",   "North America"),
    ("Ava Thompson",      "ava.t@email.com",        "Starter",    "2026-05-09", "Active",   "Asia Pacific"),
    ("Noah Garcia",       "noah.g@email.com",       "Growth",     "2026-05-10", "Active",   "Latin America"),
]

for name, email, plan, signup_date, status, region in customers:
    fee = plans[plan]
    cursor.execute("""
        INSERT INTO customers (name, email, plan, monthly_fee, signup_date, status, region)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (name, email, plan, fee, signup_date, status, region))

# -----------------------------------------
# TABLE 2 — SALES TRANSACTIONS
# Every purchase made by customers
# Links to customers via customer_id
# -----------------------------------------
cursor.execute("""
    CREATE TABLE sales (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id   INTEGER NOT NULL,
        product       TEXT NOT NULL,
        amount        REAL NOT NULL,
        sale_date     TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
""")

products = [
    ("Analytics Pro Add-on",   199.99),
    ("API Access",             99.99),
    ("Custom Reporting",       149.99),
    ("Data Export Suite",      79.99),
    ("Priority Support",       49.99),
    ("Team Seats x5",          249.99),
    ("White Label License",    499.99),
    ("Training Package",       299.99),
]

random.seed(42)
base_date = date(2026, 4, 1)

for _ in range(60):
    customer_id = random.randint(1, 30)
    product, amount = random.choice(products)
    days_offset = random.randint(0, 49)
    sale_date = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO sales (customer_id, product, amount, sale_date)
        VALUES (?, ?, ?, ?)
    """, (customer_id, product, amount, sale_date))

# -----------------------------------------
# TABLE 3 — SUPPORT TICKETS
# Every support request, resolution time,
# and customer satisfaction score
# -----------------------------------------
cursor.execute("""
    CREATE TABLE support_tickets (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id       INTEGER NOT NULL,
        issue             TEXT NOT NULL,
        status            TEXT NOT NULL,
        priority          TEXT NOT NULL,
        created_date      TEXT NOT NULL,
        resolution_hours  INTEGER,
        satisfaction      INTEGER,
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
""")

issues = [
    "Login issues",
    "Billing question",
    "Feature request",
    "Data export error",
    "API integration help",
    "Dashboard not loading",
    "Account upgrade",
    "Performance issue",
]

priorities  = ["Low", "Medium", "High", "Critical"]
statuses    = ["Resolved", "Resolved", "Resolved", "Open"]

for _ in range(50):
    customer_id      = random.randint(1, 30)
    issue            = random.choice(issues)
    status           = random.choice(statuses)
    priority         = random.choice(priorities)
    days_offset      = random.randint(0, 49)
    created_date     = (base_date + timedelta(days=days_offset)).strftime("%Y-%m-%d")
    resolution_hours = random.randint(1, 72) if status == "Resolved" else None
    satisfaction     = random.randint(3, 5) if status == "Resolved" else None

    cursor.execute("""
        INSERT INTO support_tickets
        (customer_id, issue, status, priority, created_date, resolution_hours, satisfaction)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (customer_id, issue, status, priority, created_date, resolution_hours, satisfaction))

conn.commit()

# -----------------------------------------
# CONFIRM IT WORKED
# -----------------------------------------
cursor.execute("SELECT COUNT(*) FROM customers")
c_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sales")
s_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM support_tickets")
t_count = cursor.fetchone()[0]

print(f"  ✅ Customers table:        {c_count} records")
print(f"  ✅ Sales table:            {s_count} records")
print(f"  ✅ Support tickets table:  {t_count} records")
print(f"\n✅ NovaTech database built successfully!")
print(f"💾 Saved as: novatech.db\n")

conn.close()
