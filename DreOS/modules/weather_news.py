"""
DreOS — Weather + News Module
Phase 3: Fetch Bedford NH weather and top headlines

Data sources:
- Open-Meteo API: weather (free, no API key needed)
- NewsAPI: headlines (uses your existing key)

Output: outputs/context_data.json

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: python modules/weather_news.py
"""

import requests
import json
import os
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------
# SETTINGS
# -----------------------------------------
NEWS_API_KEY = os.getenv("NEWSAPI_KEY")
LOCATION     = "Bedford, NH"
LATITUDE     = 42.9454
LONGITUDE    = -71.5159

print("\n🌤️  DreOS Weather + News Module...\n")

# -----------------------------------------
# STEP 1 — WEATHER
# Open-Meteo is completely free
# No API key needed — just call the URL
# Returns temperature, weather code, wind speed
# -----------------------------------------
print("  🌡️  Fetching Bedford NH weather...")

weather_data = {}

try:
    weather_url    = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude":            LATITUDE,
        "longitude":           LONGITUDE,
        "current":             "temperature_2m,weathercode,windspeed_10m,precipitation",
        "daily":               "temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum",
        "temperature_unit":    "fahrenheit",
        "wind_speed_unit":     "mph",
        "precipitation_unit":  "inch",
        "timezone":            "America/New_York",
        "forecast_days":       3
    }

    response = requests.get(weather_url, params=weather_params, timeout=10)
    weather  = response.json()

    current  = weather.get("current", {})
    daily    = weather.get("daily", {})

    # Weather code to description mapping
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog", 51: "Light drizzle", 53: "Drizzle",
        55: "Heavy drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
        71: "Light snow", 73: "Snow", 75: "Heavy snow", 80: "Rain showers",
        81: "Heavy showers", 82: "Violent showers", 95: "Thunderstorm",
        96: "Thunderstorm with hail", 99: "Heavy thunderstorm with hail"
    }

    current_code = current.get("weathercode", 0)
    current_desc = weather_codes.get(current_code, "Unknown")
    current_temp = current.get("temperature_2m")
    wind_speed   = current.get("windspeed_10m")
    precip       = current.get("precipitation", 0)

    # 3 day forecast
    forecast = []
    dates    = daily.get("time", [])
    max_temps= daily.get("temperature_2m_max", [])
    min_temps= daily.get("temperature_2m_min", [])
    codes    = daily.get("weathercode", [])
    precips  = daily.get("precipitation_sum", [])

    for i in range(min(3, len(dates))):
        forecast.append({
            "date":        dates[i],
            "high":        max_temps[i],
            "low":         min_temps[i],
            "description": weather_codes.get(codes[i], "Unknown"),
            "precip_in":   precips[i]
        })

    weather_data = {
        "location":    LOCATION,
        "current": {
            "temperature": current_temp,
            "description": current_desc,
            "wind_mph":    wind_speed,
            "precip_in":   precip
        },
        "forecast":    forecast,
        "status":      "ok"
    }

    print(f"    ✅ {LOCATION}: {current_temp}°F — {current_desc}")
    print(f"    💨 Wind: {wind_speed} mph  |  🌧️  Precip: {precip} in")
    for day in forecast:
        print(f"    📅 {day['date']}: {day['low']}°F — {day['high']}°F  {day['description']}")

except Exception as e:
    weather_data = {"status": f"error: {str(e)}"}
    print(f"    ❌ Weather error: {str(e)}")

# -----------------------------------------
# STEP 2 — NEWS HEADLINES
# Reusing your NewsAPI key from Pulse Research
# Two topics: AI and Finance
# -----------------------------------------
print(f"\n  📰 Fetching headlines...")

news_data = {"ai_headlines": [], "finance_headlines": [], "status": "ok"}

if not NEWS_API_KEY or NEWS_API_KEY == "YOUR_NEWSAPI_KEY_HERE":
    print("    ⚠️  NewsAPI key not set in .env file")
    print("    Add NEWSAPI_KEY=your_key to your .env file")
    news_data["status"] = "missing api key"
else:
    news_url = "https://newsapi.org/v2/everything"

    # AI headlines
    try:
        ai_params = {
            "q":        "Artificial Intelligence",
            "language": "en",
            "sortBy":   "publishedAt",
            "pageSize": 5,
            "apiKey":   NEWS_API_KEY
        }
        ai_response = requests.get(news_url, params=ai_params, timeout=10)
        ai_articles = ai_response.json().get("articles", [])

        for article in ai_articles:
            news_data["ai_headlines"].append({
                "title":  article["title"],
                "source": article["source"]["name"],
                "url":    article["url"],
                "date":   article.get("publishedAt", "")[:10]
            })
            print(f"    🤖 {article['source']['name']}: {article['title'][:55]}...")

    except Exception as e:
        print(f"    ❌ AI news error: {str(e)}")

    # Finance headlines
    try:
        fin_params = {
            "q":        "stock market finance investing",
            "language": "en",
            "sortBy":   "publishedAt",
            "pageSize": 5,
            "apiKey":   NEWS_API_KEY
        }
        fin_response = requests.get(news_url, params=fin_params, timeout=10)
        fin_articles = fin_response.json().get("articles", [])

        print()
        for article in fin_articles:
            news_data["finance_headlines"].append({
                "title":  article["title"],
                "source": article["source"]["name"],
                "url":    article["url"],
                "date":   article.get("publishedAt", "")[:10]
            })
            print(f"    💰 {article['source']['name']}: {article['title'][:55]}...")

    except Exception as e:
        print(f"    ❌ Finance news error: {str(e)}")

# -----------------------------------------
# STEP 3 — COMBINE AND SAVE TO JSON
# Both weather and news go into one file
# This is the "note on the desk" for the agent
# -----------------------------------------
os.makedirs("outputs", exist_ok=True)

output = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "weather":   weather_data,
    "news":      news_data
}

with open("outputs/context_data.json", "w") as f:
    json.dump(output, f, indent=2)

# -----------------------------------------
# ERROR LOGGING
# -----------------------------------------
if weather_data.get("status") != "ok" or news_data.get("status") != "ok":
    with open("error_log.txt", "a") as log:
        log.write(f"\n[{datetime.now()}] Weather/News errors:\n")
        if weather_data.get("status") != "ok":
            log.write(f"  - Weather: {weather_data.get('status')}\n")
        if news_data.get("status") != "ok":
            log.write(f"  - News: {news_data.get('status')}\n")

print(f"\n{'='*50}")
print(f"  ✅ Weather + News complete — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  💾 Saved to: outputs/context_data.json")
print(f"{'='*50}\n")
