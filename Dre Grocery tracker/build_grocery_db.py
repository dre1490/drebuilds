"""
Weekly Grocery Report — Phase 1
Build the grocery list database with starting prices

HOW TO RUN:
1. Open Terminal
2. Navigate to your Grocery Tracker folder
3. Run: python build_grocery_db.py
"""

import sqlite3
from datetime import date

print("\n🛒 Building Weekly Grocery database...\n")

conn   = sqlite3.connect("grocery_tracker.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS items")
cursor.execute("DROP TABLE IF EXISTS price_history")

# -----------------------------------------
# TABLE 1 — ITEMS
# Your grocery list with categories
# -----------------------------------------
cursor.execute("""
    CREATE TABLE items (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        category    TEXT NOT NULL,
        unit        TEXT NOT NULL
    )
""")

# -----------------------------------------
# TABLE 2 — PRICE HISTORY
# Tracks prices at each store over time
# -----------------------------------------
cursor.execute("""
    CREATE TABLE price_history (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id         INTEGER NOT NULL,
        store           TEXT NOT NULL,
        price           REAL,
        date_checked    TEXT NOT NULL,
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
""")

# -----------------------------------------
# YOUR GROCERY LIST
# (name, category, unit)
# -----------------------------------------
items = [
    # Meat & Seafood
    ("Chicken Breast",          "Meat",     "per lb"),
    ("Ribs",                    "Meat",     "per lb"),
    ("Steak",                   "Meat",     "per lb"),
    ("Ground Beef",             "Meat",     "per lb"),

    # Produce
    ("Limes",                   "Produce",  "each"),
    ("Onions",                  "Produce",  "per lb"),
    ("Garlic",                  "Produce",  "per head"),
    ("Green Onions",            "Produce",  "per bunch"),
    ("Celery",                  "Produce",  "per bunch"),
    ("Carrots",                 "Produce",  "per lb"),
    ("Red Pepper",              "Produce",  "each"),
    ("Red Onions",              "Produce",  "per lb"),
    ("Cherry Tomatoes",         "Produce",  "per pint"),
    ("Avocado",                 "Produce",  "each"),
    ("Blueberries",             "Produce",  "per pint"),
    ("Strawberries",            "Produce",  "per lb"),
    ("Pears",                   "Produce",  "each"),
    ("Blackberries",            "Produce",  "per pint"),
    ("Raspberries",             "Produce",  "per pint"),
    ("Bananas",                 "Produce",  "per lb"),

    # Dairy
    ("Milk",                    "Dairy",    "per gallon"),
    ("Creamer",                 "Dairy",    "per bottle"),
    ("Cookies & Cream Ice Cream","Dairy",   "per half gallon"),

    # Beverages
    ("Polar Springs Tonic Water","Beverages","per 6-pack"),
    ("Diet Coke",               "Beverages","per 12-pack"),
    ("Ginger Ale",              "Beverages","per 2L"),
    ("Wine",                    "Beverages","per bottle"),

    # Frozen
    ("Mickey Waffles (Frozen)", "Frozen",   "per box"),

    # Pantry
    ("Kids Box Pasta",          "Pantry",   "per box"),
]

today = date.today().strftime("%Y-%m-%d")
stores = ["Market Basket", "Hannaford"]

# Starting price estimates — realistic NH grocery prices
starting_prices = {
    "Chicken Breast":           [3.99, 4.49],
    "Ribs":                     [5.99, 6.49],
    "Steak":                    [9.99, 10.99],
    "Ground Beef":              [4.99, 5.29],
    "Limes":                    [0.49, 0.59],
    "Onions":                   [0.99, 1.19],
    "Garlic":                   [0.79, 0.89],
    "Green Onions":             [0.99, 1.09],
    "Celery":                   [1.99, 2.29],
    "Carrots":                  [1.49, 1.69],
    "Red Pepper":               [1.49, 1.69],
    "Red Onions":               [1.29, 1.49],
    "Cherry Tomatoes":          [3.49, 3.99],
    "Avocado":                  [1.29, 1.49],
    "Blueberries":              [3.99, 4.49],
    "Strawberries":             [3.49, 3.99],
    "Pears":                    [0.99, 1.19],
    "Blackberries":             [3.99, 4.49],
    "Raspberries":              [3.99, 4.29],
    "Bananas":                  [0.29, 0.35],
    "Milk":                     [3.49, 3.79],
    "Creamer":                  [3.99, 4.29],
    "Cookies & Cream Ice Cream":[4.99, 5.49],
    "Polar Springs Tonic Water":[5.99, 6.49],
    "Diet Coke":                [6.99, 7.49],
    "Ginger Ale":               [1.99, 2.29],
    "Wine":                     [12.99, 13.99],
    "Mickey Waffles (Frozen)":  [3.99, 4.49],
    "Kids Box Pasta":           [1.29, 1.49],
}

# Insert items and starting prices
for name, category, unit in items:
    cursor.execute("""
        INSERT INTO items (name, category, unit) VALUES (?, ?, ?)
    """, (name, category, unit))
    item_id = cursor.lastrowid

    prices = starting_prices.get(name, [0.00, 0.00])
    for i, store in enumerate(stores):
        cursor.execute("""
            INSERT INTO price_history (item_id, store, price, date_checked)
            VALUES (?, ?, ?, ?)
        """, (item_id, store, prices[i], today))

conn.commit()

# Confirm
cursor.execute("SELECT COUNT(*) FROM items")
item_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM price_history")
price_count = cursor.fetchone()[0]

print(f"  ✅ Items added:         {item_count}")
print(f"  ✅ Price records:       {price_count}")
print(f"  ✅ Stores tracked:      Market Basket, Hannaford")
print(f"  ✅ Date:                {today}")
print(f"\n✅ Grocery database built successfully!")
print(f"💾 Saved as: grocery_tracker.db\n")

conn.close()
