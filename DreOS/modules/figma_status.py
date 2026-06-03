"""
DreOS — Figma Design Status Module
Phase 5: Check status of your Figma design file

Data source: Figma API (private — requires personal access token)

Output: outputs/figma_data.json

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: python modules/figma_status.py
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------
# FIGMA CREDENTIALS FROM .env
# -----------------------------------------
FIGMA_TOKEN   = os.getenv("FIGMA_API_TOKEN")
FIGMA_FILE_ID = "bZbfXpqt2KdzmlVmH6qXBe"  # from your file URL

print("\n🎨 DreOS Figma Design Status...\n")

# -----------------------------------------
# HOW FIGMA AUTHENTICATION WORKS
# Figma uses Bearer token authentication
# Much simpler than Basic Auth — just send
# the token directly in the header
# No encoding needed
# -----------------------------------------
headers = {
    "X-Figma-Token": FIGMA_TOKEN
}

base_url = "https://api.figma.com/v1"

figma_data = {
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "file":      {},
    "pages":     [],
    "summary":   {},
    "status":    "ok"
}

try:
    # -----------------------------------------
    # STEP 1 — Fetch file metadata
    # Gets file name, last modified, version
    # -----------------------------------------
    print(f"  📁 Fetching Figma file details...")

    file_url      = f"{base_url}/files/{FIGMA_FILE_ID}"
    file_response = requests.get(file_url, headers=headers, timeout=10)

    if file_response.status_code == 403:
        raise Exception("Invalid Figma token — check your API token in .env")
    elif file_response.status_code == 404:
        raise Exception("Figma file not found — check the file ID")
    elif file_response.status_code != 200:
        raise Exception(f"Figma API returned {file_response.status_code}")

    file_info     = file_response.json()
    file_name     = file_info.get("name", "Unknown")
    last_modified = file_info.get("lastModified", "")[:10]
    version       = file_info.get("version", "Unknown")
    thumbnail     = file_info.get("thumbnailUrl", "")

    print(f"    ✅ File: {file_name}")
    print(f"    📅 Last modified: {last_modified}")
    print(f"    🔢 Version: {version}")

    # -----------------------------------------
    # STEP 2 — Get pages in the file
    # Pages are like tabs in a design file
    # -----------------------------------------
    pages     = file_info.get("document", {}).get("children", [])
    page_list = []

    print(f"\n  📄 Pages in file:")
    for page in pages:
        page_info = {
            "id":   page.get("id"),
            "name": page.get("name"),
            "type": page.get("type")
        }
        page_list.append(page_info)
        print(f"    📄 {page.get('name')}")

    # -----------------------------------------
    # STEP 3 — Check if recently updated
    # Flag if file hasn't been touched in 7 days
    # -----------------------------------------
    today         = datetime.now().date()
    modified_date = datetime.strptime(last_modified, "%Y-%m-%d").date()
    days_since    = (today - modified_date).days
    recently_updated = days_since <= 7

    if recently_updated:
        activity_status = f"Active — updated {days_since} day(s) ago"
    else:
        activity_status = f"Inactive — last updated {days_since} days ago"

    print(f"\n  📊 Activity: {activity_status}")

    # -----------------------------------------
    # BUILD OUTPUT
    # -----------------------------------------
    figma_data["file"] = {
        "name":          file_name,
        "last_modified": last_modified,
        "version":       version,
        "days_since":    days_since,
        "thumbnail":     thumbnail
    }

    figma_data["pages"]   = page_list
    figma_data["summary"] = {
        "total_pages":      len(page_list),
        "recently_updated": recently_updated,
        "activity_status":  activity_status,
        "days_since":       days_since
    }

except Exception as e:
    figma_data["status"] = f"error: {str(e)}"
    print(f"  ❌ Figma error: {str(e)}")
    with open("error_log.txt", "a") as log:
        log.write(f"\n[{datetime.now()}] Figma error: {str(e)}\n")

# -----------------------------------------
# SAVE TO JSON
# -----------------------------------------
os.makedirs("outputs", exist_ok=True)

with open("outputs/figma_data.json", "w") as f:
    json.dump(figma_data, f, indent=2)

print(f"\n{'='*50}")
print(f"  ✅ Figma status complete — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"  💾 Saved to: outputs/figma_data.json")
print(f"{'='*50}\n")
