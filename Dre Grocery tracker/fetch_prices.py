"""
Weekly Grocery Report — Phase 2
Fetch latest prices using Groq AI

HOW TO RUN:
1. Open Terminal
2. Navigate to your Grocery Tracker folder
3. Run: pip install groq requests
4. Run: python fetch_prices.py
"""

import sqlite3
import json
from groq import Groq
from datetime import date

# -----------------------------------------
# YOUR GROQ API KEY
# -----------------------------------------
API_KEY = "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"

STORES = ["Market Basket", "Hannaford"]

print("\n📡 Fetching latest grocery prices...\n")

conn   = sqlite3.connect("grocery_tracker.db")
cursor = conn.cursor()

cursor.execute("SELECT id, name, category, unit FROM items")
items  = cursor.fetchall()
today  = date.today().strftime("%Y-%m-%d")
client = Groq(api_key=API_KEY)

item_list = "\n".join([f"- {row[1]} ({row[3]})" for row in items])

for store in STORES:
    print(f"  🏪 Fetching prices for {store}...")

    prompt = f"""
You are a grocery price expert familiar with New England supermarkets.
Provide realistic current retail prices for each item below as they would
appear at {store} in New Hampshire in {date.today().strftime("%B %Y")}.

Return ONLY a JSON object with item names as keys and prices as numeric values.
No explanation, no markdown, no extra text — just the raw JSON.

Example format:
{{"Chicken Breast": 3.99, "Milk": 3.49}}

Items to price:
{item_list}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        raw    = response.choices[0].message.content.strip()
        clean  = raw.replace("```json", "").replace("```", "").strip()
        prices = json.loads(clean)

        for item_id, name, category, unit in items:
            price = prices.get(name)
            if price:
                cursor.execute("""
                    DELETE FROM price_history
                    WHERE item_id = ? AND store = ? AND date_checked = ?
                """, (item_id, store, today))

                cursor.execute("""
                    INSERT INTO price_history (item_id, store, price, date_checked)
                    VALUES (?, ?, ?, ?)
                """, (item_id, store, price, today))

                print(f"    ✅ {name:<35} ${price:.2f}")

    except Exception as e:
        print(f"    ❌ Error: {str(e)}")

conn.commit()
conn.close()
print(f"\n✅ All prices updated for {today}\n")
