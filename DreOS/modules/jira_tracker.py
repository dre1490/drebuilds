"""
DreOS — Jira Project Tracker Module
Phase 4: Read DreOS phase tickets from Jira

Data source: Atlassian Jira API (private — requires API token)

Output: outputs/jira_data.json

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: python modules/jira_tracker.py
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import base64

load_dotenv()

# -----------------------------------------
# JIRA CREDENTIALS FROM .env
# -----------------------------------------
JIRA_EMAIL    = os.getenv("JIRA_EMAIL")
JIRA_TOKEN    = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN   = os.getenv("JIRA_DOMAIN")
PROJECT_KEY   = "KAN"

print("\n📋 DreOS Jira Project Tracker...\n")

# -----------------------------------------
# HOW JIRA AUTHENTICATION WORKS
# Jira uses Basic Auth — we combine email
# and token into a base64 encoded string
# This is standard for private business APIs
# -----------------------------------------
credentials = f"{JIRA_EMAIL}:{JIRA_TOKEN}"
encoded     = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded}",
    "Content-Type":  "application/json"
}

base_url = f"https://{JIRA_DOMAIN}/rest/api/3"

# -----------------------------------------
# STEP 1 — Fetch all tickets from your board
# JQL = Jira Query Language
# Similar to SQL but for Jira tickets
# -----------------------------------------
print(f"  🔍 Fetching tickets from {PROJECT_KEY} board...")

jira_data = {
    "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M"),
    "project":      "DreOS — Personal Intelligence Hub",
    "tickets":      [],
    "summary":      {},
    "status":       "ok"
}

try:
    jql_url    = f"{base_url}/search/jql"
    jql_params = {
        "jql":        f"project = {PROJECT_KEY} ORDER BY created ASC",
        "maxResults": 50,
        "fields":     "summary,status,priority,created,updated"
    }

    response = requests.get(jql_url, headers=headers, params=jql_params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Jira API returned {response.status_code}: {response.text[:200]}")

    issues = response.json().get("issues", [])

    # -----------------------------------------
    # STEP 2 — Parse each ticket
    # -----------------------------------------
    done_count        = 0
    in_progress_count = 0
    todo_count        = 0
    dreos_phases      = []

    for issue in issues:
        fields      = issue.get("fields", {})
        ticket_key  = issue.get("key")
        summary     = fields.get("summary", "")
        status      = fields.get("status", {}).get("name", "Unknown")
        priority    = fields.get("priority", {}).get("name", "Medium")
        updated     = fields.get("updated", "")[:10]

        ticket = {
            "key":      ticket_key,
            "summary":  summary,
            "status":   status,
            "priority": priority,
            "updated":  updated
        }

        jira_data["tickets"].append(ticket)

        # Count by status
        if status.lower() == "done":
            done_count += 1
        elif status.lower() == "in progress":
            in_progress_count += 1
        else:
            todo_count += 1

        # Print each ticket
        status_emoji = "✅" if status.lower() == "done" else "🔄" if status.lower() == "in progress" else "⏳"
        print(f"    {status_emoji} {ticket_key}: {summary[:50]}")

    # -----------------------------------------
    # STEP 3 — Build summary
    # -----------------------------------------
    total         = len(issues)
    pct_complete  = round((done_count / total * 100), 1) if total else 0

    # Find current phase
    in_progress_tickets = [t for t in jira_data["tickets"] if t["status"].lower() == "in progress"]
    current_phase       = in_progress_tickets[0]["summary"] if in_progress_tickets else "None in progress"

    # Find next phase
    todo_tickets  = [t for t in jira_data["tickets"] if t["status"].lower() == "to do"]
    next_phase    = todo_tickets[0]["summary"] if todo_tickets else "All done!"

    jira_data["summary"] = {
        "total_tickets":    total,
        "done":             done_count,
        "in_progress":      in_progress_count,
        "todo":             todo_count,
        "pct_complete":     pct_complete,
        "current_phase":    current_phase,
        "next_phase":       next_phase
    }

    print(f"\n  📊 Progress: {done_count}/{total} phases complete ({pct_complete}%)")
    print(f"  🔄 Current: {current_phase}")
    print(f"  ⏭️  Next: {next_phase}")

except Exception as e:
    jira_data["status"] = f"error: {str(e)}"
    print(f"  ❌ Jira error: {str(e)}")
    with open("error_log.txt", "a") as log:
        log.write(f"\n[{datetime.now()}] Jira error: {str(e)}\n")

# -----------------------------------------
# SAVE TO JSON
# -----------------------------------------
os.makedirs("outputs", exist_ok=True)

with open("outputs/jira_data.json", "w") as f:
    json.dump(jira_data, f, indent=2)

print(f"\n{'='*50}")
print(f"  ✅ Jira tracker complete — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  💾 Saved to: outputs/jira_data.json")
print(f"{'='*50}\n")
