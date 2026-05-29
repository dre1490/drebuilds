"""
Horizon Capital - Fund Price Fetcher
Step 2: Fetch latest NAV prices from Yahoo Finance

HOW TO RUN:
1. Make sure Python is installed on your computer
2. Open Terminal (Mac) or Command Prompt (Windows)
3. Run: pip install yfinance
4. Run: python fetch_prices.py
"""

import yfinance as yf
from datetime import date

# -----------------------------------------
# FUND LIST
# Each entry is: ("Fund Name", "Ticker")
# To add a fund, just add a new line here
# -----------------------------------------
funds = [
    ("Vanguard 500 Index Fund",        "VFIAX"),
    ("Fidelity Contrafund",            "FCNTX"),
    ("T. Rowe Price Blue Chip Growth", "TRBCX"),
    ("American Funds Growth Fund",     "AGTHX"),
    ("Schwab Total Stock Market Index","SWTSX"),
]

# -----------------------------------------
# FETCH PRICES
# yfinance connects to Yahoo Finance and
# pulls the latest available price for each ticker
# -----------------------------------------
print(f"\n{'Fund Name':<36} {'Ticker':<8} {'NAV Price':>10}  {'Date'}")
print("-" * 68)

results = []
today = date.today().strftime("%Y-%m-%d")

for name, ticker in funds:
    try:
        data  = yf.Ticker(ticker)
        price = data.fast_info.get("lastPrice") or data.fast_info.get("previousClose")

        if price:
            price_str  = f"${price:,.2f}"
            status     = "✅"
        else:
            price_str  = "N/A"
            status     = "⚠️ "

        results.append((name, ticker, price, today))
        print(f"{name:<36} {ticker:<8} {price_str:>10}  {today}  {status}")

    except Exception as e:
        print(f"{name:<36} {ticker:<8} {'ERROR':>10}  {str(e)}")

print("-" * 68)
print(f"\n✅ Done — {len(results)} funds fetched on {today}\n")
