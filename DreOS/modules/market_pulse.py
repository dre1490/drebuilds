"""
DreOS — Market Pulse Module
Phase 2: Fetch prices for all 25 assets

Data sources:
- yfinance: stocks and mutual funds
- CoinGecko API: crypto tokens (free, no API key needed)

Output: outputs/market_data.json

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: pip install yfinance requests python-dotenv
4. Run: python modules/market_pulse.py
"""

import yfinance as yf
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

print("\n📈 DreOS Market Pulse — Fetching all 25 assets...\n")

# -----------------------------------------
# ASSET LISTS
# -----------------------------------------
big_5_stocks = {
    "AAPL":  "Apple",
    "MSFT":  "Microsoft",
    "GOOGL": "Google",
    "AMZN":  "Amazon",
    "NVDA":  "Nvidia"
}

potential_stocks = {
    "PLTR": "Palantir",
    "AMD":  "AMD",
    "META": "Meta",
    "RIVN": "Rivian",
    "TSLA": "Tesla"
}

mutual_funds = {
    "VFIAX": "Vanguard 500 Index",
    "FCNTX": "Fidelity Contrafund",
    "TRBCX": "T. Rowe Price Blue Chip",
    "AGTHX": "American Funds Growth",
    "SWTSX": "Schwab Total Market"
}

major_cryptos = {
    "bitcoin":        "BTC",
    "ethereum":       "ETH",
    "binancecoin":    "BNB",
    "solana":         "SOL",
    "ripple":         "XRP"
}

potential_tokens = {
    "polygon-ecosystem-token": "POL",
    "arbitrum":       "ARB",
    "chainlink":      "LINK",
    "uniswap":        "UNI",
    "aave":           "AAVE"
}

# -----------------------------------------
# HELPER — Fetch stock or fund price
# Same pattern from Horizon Capital project
# -----------------------------------------
def fetch_equity_price(ticker, name):
    try:
        data  = yf.Ticker(ticker)
        price = data.fast_info.get("lastPrice") or data.fast_info.get("previousClose")
        prev  = data.fast_info.get("previousClose") or price
        change_pct = ((price - prev) / prev * 100) if prev else 0
        return {
            "ticker":     ticker,
            "name":       name,
            "price":      round(price, 2) if price else None,
            "change_pct": round(change_pct, 2),
            "status":     "ok" if price else "error"
        }
    except Exception as e:
        return {"ticker": ticker, "name": name, "price": None, "change_pct": 0, "status": f"error: {str(e)}"}

# -----------------------------------------
# FETCH STOCKS
# -----------------------------------------
print("  📊 Fetching Big 5 Stocks...")
big_5_results = []
for ticker, name in big_5_stocks.items():
    result = fetch_equity_price(ticker, name)
    big_5_results.append(result)
    status = f"${result['price']:,.2f} ({result['change_pct']:+.2f}%)" if result["price"] else "Error"
    print(f"    {ticker:<6} {status}")

print("\n  📊 Fetching Potential Stocks...")
potential_stock_results = []
for ticker, name in potential_stocks.items():
    result = fetch_equity_price(ticker, name)
    potential_stock_results.append(result)
    status = f"${result['price']:,.2f} ({result['change_pct']:+.2f}%)" if result["price"] else "Error"
    print(f"    {ticker:<6} {status}")

print("\n  📊 Fetching Mutual Funds...")
fund_results = []
for ticker, name in mutual_funds.items():
    result = fetch_equity_price(ticker, name)
    fund_results.append(result)
    status = f"${result['price']:,.2f}" if result["price"] else "Error"
    print(f"    {ticker:<6} {status}")

# -----------------------------------------
# FETCH CRYPTO
# CoinGecko API — free, no key needed
# New concept: calling a REST API directly
# -----------------------------------------
print("\n  🪙 Fetching Major Cryptos (CoinGecko)...")

all_crypto_ids = list(major_cryptos.keys()) + list(potential_tokens.keys())
crypto_url     = "https://api.coingecko.com/api/v3/simple/price"
crypto_params  = {
    "ids":           ",".join(all_crypto_ids),
    "vs_currencies": "usd",
    "include_24hr_change": "true"
}

major_crypto_results    = []
potential_token_results = []

try:
    response    = requests.get(crypto_url, params=crypto_params, timeout=10)
    crypto_data = response.json()

    for coin_id, symbol in major_cryptos.items():
        coin   = crypto_data.get(coin_id, {})
        price  = coin.get("usd")
        change = coin.get("usd_24h_change", 0)
        major_crypto_results.append({
            "ticker":     symbol,
            "name":       coin_id.title(),
            "price":      round(price, 2) if price else None,
            "change_pct": round(change, 2) if change else 0,
            "status":     "ok" if price else "error"
        })
        status = f"${price:,.2f} ({change:+.2f}%)" if price else "Error"
        print(f"    {symbol:<6} {status}")

    print("\n  🪙 Fetching Potential Tokens...")
    for coin_id, symbol in potential_tokens.items():
        coin   = crypto_data.get(coin_id, {})
        price  = coin.get("usd")
        change = coin.get("usd_24h_change", 0)
        potential_token_results.append({
            "ticker":     symbol,
            "name":       coin_id.title(),
            "price":      round(price, 2) if price else None,
            "change_pct": round(change, 2) if change else 0,
            "status":     "ok" if price else "error"
        })
        status = f"${price:,.2f} ({change:+.2f}%)" if price else "Error"
        print(f"    {symbol:<6} {status}")

except Exception as e:
    print(f"    ❌ CoinGecko error: {str(e)}")

# -----------------------------------------
# CALCULATE SUMMARY STATS
# -----------------------------------------
all_stocks  = big_5_results + potential_stock_results
gainers     = [s for s in all_stocks if s["change_pct"] > 0]
losers      = [s for s in all_stocks if s["change_pct"] < 0]
top_gainer  = max(all_stocks, key=lambda x: x["change_pct"]) if all_stocks else None
top_loser   = min(all_stocks, key=lambda x: x["change_pct"]) if all_stocks else None

# -----------------------------------------
# SAVE TO JSON
# This is the "note on the desk" the agent reads
# -----------------------------------------
os.makedirs("outputs", exist_ok=True)

output = {
    "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M"),
    "big_5_stocks":      big_5_results,
    "potential_stocks":  potential_stock_results,
    "mutual_funds":      fund_results,
    "major_cryptos":     major_crypto_results,
    "potential_tokens":  potential_token_results,
    "summary": {
        "total_assets":  25,
        "gainers":       len(gainers),
        "losers":        len(losers),
        "top_gainer":    f"{top_gainer['ticker']} +{top_gainer['change_pct']}%" if top_gainer else "N/A",
        "top_loser":     f"{top_loser['ticker']} {top_loser['change_pct']}%" if top_loser else "N/A",
    }
}

with open("outputs/market_data.json", "w") as f:
    json.dump(output, f, indent=2)

# -----------------------------------------
# LOG TO ERROR LOG
# -----------------------------------------
errors = [a for a in big_5_results + potential_stock_results + fund_results
          + major_crypto_results + potential_token_results
          if a["status"] != "ok"]

if errors:
    with open("error_log.txt", "a") as log:
        log.write(f"\n[{datetime.now()}] Market Pulse errors:\n")
        for e in errors:
            log.write(f"  - {e['ticker']}: {e['status']}\n")

print(f"\n{'='*50}")
print(f"  ✅ Market Pulse complete — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  📊 Gainers: {len(gainers)}  |  Losers: {len(losers)}")
if top_gainer:
    print(f"  🏆 Top gainer: {top_gainer['ticker']} {top_gainer['change_pct']:+.2f}%")
if top_loser:
    print(f"  📉 Top loser:  {top_loser['ticker']} {top_loser['change_pct']:+.2f}%")
print(f"  💾 Saved to: outputs/market_data.json")
if errors:
    print(f"  ⚠️  {len(errors)} errors logged to error_log.txt")
print(f"{'='*50}\n")
