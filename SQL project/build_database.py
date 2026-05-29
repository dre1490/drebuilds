"""
Vertex Solutions - Customer Database
Step 1: Build the database and fill it with fake customer data

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your SQL project folder
3. Run: python build_database.py
"""

import sqlite3
from datetime import date, timedelta
import random

# -----------------------------------------
# STEP 1 — Create the database
# SQLite creates a single file on your computer
# No server, no setup — just a file
# -----------------------------------------
print("\n🗄️  Building Vertex Solutions database...\n")

conn   = sqlite3.connect("vertex_solutions.db")
cursor = conn.cursor()

# -----------------------------------------
# STEP 2 — Create the customers table
# This is standard SQL you may recognize
# -----------------------------------------
cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT NOT NULL,
        email         TEXT NOT NULL,
        plan          TEXT NOT NULL,
        monthly_fee   REAL NOT NULL,
        signup_date   TEXT NOT NULL,
        paid          TEXT NOT NULL
    )
""")

# -----------------------------------------
# STEP 3 — Fill it with fake customer data
# 20 fake customers across 3 plans
# -----------------------------------------
plans = {
    "Basic":      29.99,
    "Pro":        79.99,
    "Enterprise": 199.99
}

customers = [
    ("James Carter",     "james.carter@email.com",     "Pro",        "2026-05-01", "Yes"),
    ("Sofia Reyes",      "sofia.reyes@email.com",      "Basic",      "2026-05-03", "Yes"),
    ("Marcus Johnson",   "marcus.j@email.com",         "Enterprise", "2026-05-03", "No"),
    ("Priya Patel",      "priya.patel@email.com",      "Pro",        "2026-05-05", "Yes"),
    ("Tyler Brooks",     "tyler.b@email.com",          "Basic",      "2026-05-06", "Yes"),
    ("Aisha Williams",   "aisha.w@email.com",          "Enterprise", "2026-05-07", "Yes"),
    ("Derek Thompson",   "derek.t@email.com",          "Basic",      "2026-05-08", "No"),
    ("Mei Chen",         "mei.chen@email.com",         "Pro",        "2026-05-09", "Yes"),
    ("Carlos Mendez",    "carlos.m@email.com",         "Pro",        "2026-05-10", "Yes"),
    ("Rachel Green",     "rachel.g@email.com",         "Basic",      "2026-05-10", "Yes"),
    ("Kevin O'Brien",    "kevin.ob@email.com",         "Enterprise", "2026-05-11", "Yes"),
    ("Fatima Hassan",    "fatima.h@email.com",         "Basic",      "2026-05-12", "No"),
    ("Jordan Lee",       "jordan.lee@email.com",       "Pro",        "2026-05-13", "Yes"),
    ("Samantha Cruz",    "sam.cruz@email.com",         "Enterprise", "2026-05-13", "Yes"),
    ("Nathan Wright",    "nathan.w@email.com",         "Basic",      "2026-05-14", "Yes"),
    ("Olivia Scott",     "olivia.s@email.com",         "Pro",        "2026-05-15", "Yes"),
    ("Brandon King",     "brandon.k@email.com",        "Basic",      "2026-05-16", "No"),
    ("Yuki Tanaka",      "yuki.t@email.com",           "Enterprise", "2026-05-16", "Yes"),
    ("Danielle Moore",   "danielle.m@email.com",       "Pro",        "2026-05-17", "Yes"),
    ("Eric Davis",       "eric.davis@email.com",       "Basic",      "2026-05-18", "Yes"),
]

for name, email, plan, signup_date, paid in customers:
    fee = plans[plan]
    cursor.execute("""
        INSERT INTO customers (name, email, plan, monthly_fee, signup_date, paid)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, plan, fee, signup_date, paid))

conn.commit()

# -----------------------------------------
# STEP 4 — Confirm it worked
# -----------------------------------------
cursor.execute("SELECT COUNT(*) FROM customers")
count = cursor.fetchone()[0]

cursor.execute("SELECT name, plan, monthly_fee, paid FROM customers LIMIT 5")
rows = cursor.fetchall()

print(f"{'Name':<20} {'Plan':<12} {'Fee':>8}  {'Paid'}")
print("-" * 50)
for row in rows:
    print(f"{row[0]:<20} {row[1]:<12} ${row[2]:>6.2f}  {row[3]}")

print(f"\n... and {count - 5} more customers")
print(f"\n✅ Database created successfully!")
print(f"💾 Saved as: vertex_solutions.db\n")

conn.close()
