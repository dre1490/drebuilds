"""
Pulse Research - Daily AI News Logger
Step 2: Fetch top 5 AI headlines from NewsAPI

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your folder
3. Run: pip install requests
4. Run: python fetch_news.py
"""

import requests
from datetime import date

# -----------------------------------------
# YOUR API KEY
# Replace the text below with your actual key
# -----------------------------------------
API_KEY = "YOUR_NEWSAPI_KEY_HERE"

# -----------------------------------------
# SETTINGS
# You can change the topic to anything you want
# Examples: "Tesla", "Bitcoin", "Climate Change"
# -----------------------------------------
TOPIC = "Artificial Intelligence"
NUM_HEADLINES = 5

# -----------------------------------------
# FETCH HEADLINES FROM NEWSAPI
# This is a direct API call — no library needed
# We send a request and get back a JSON response
# -----------------------------------------
print(f"\n📡 Fetching top {NUM_HEADLINES} headlines for: '{TOPIC}'\n")

url = "https://newsapi.org/v2/everything"

params = {
    "q":        TOPIC,
    "language": "en",
    "sortBy":   "publishedAt",
    "pageSize": NUM_HEADLINES,
    "apiKey":   API_KEY,
}

response = requests.get(url, params=params)
data     = response.json()

# -----------------------------------------
# CHECK IF IT WORKED
# APIs return a status code — 200 means success
# -----------------------------------------
if data.get("status") != "ok":
    print(f"❌ API Error: {data.get('message', 'Unknown error')}")
    print("Check that your API key is correct.\n")
    exit()

# -----------------------------------------
# DISPLAY THE HEADLINES
# -----------------------------------------
articles = data["articles"]
today    = date.today().strftime("%Y-%m-%d")

print(f"{'#':<3} {'Source':<20} {'Headline'}")
print("-" * 80)

for i, article in enumerate(articles, 1):
    headline = article["title"]
    source   = article["source"]["name"]
    url      = article["url"]
    print(f"{i:<3} {source:<20} {headline[:60]}...")
    print(f"    🔗 {url}\n")

print("-" * 80)
print(f"✅ Done — {len(articles)} headlines fetched on {today}\n")
