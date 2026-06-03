"""
DreOS — Email Delivery Module
Phase 8a: Email the morning brief PDF to your Gmail

Data source: outputs/brief_data.json + latest PDF report

HOW TO RUN:
1. Open Terminal
2. Navigate to your DreOS folder
3. Run: python modules/email_delivery.py
"""

import smtplib
import os
import json
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date, datetime
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------------
# EMAIL SETTINGS FROM .env
# -----------------------------------------
GMAIL_USER     = "1490dre@gmail.com"
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_TO       = "1490dre@gmail.com"

print("\n📧 DreOS Email Delivery — Sending morning brief...\n")

# -----------------------------------------
# LOAD BRIEF DATA FOR EMAIL BODY
# -----------------------------------------
def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return {}

brief_data = load_json("outputs/brief_data.json")
brief_text = brief_data.get("brief", "See attached PDF for your morning brief.")
today      = brief_data.get("date", date.today().strftime("%A, %B %d, %Y"))
jira       = brief_data.get("jira", {})
market     = brief_data.get("market", {})
weather    = brief_data.get("weather", {}).get("current", {})
mkt_summary= market.get("summary", {})

# -----------------------------------------
# FIND LATEST PDF
# -----------------------------------------
today_str   = date.today().strftime("%Y-%m-%d")
report_file = f"outputs/dreos_morning_report_{today_str}.pdf"

if not os.path.exists(report_file):
    reports = glob.glob("outputs/dreos_morning_report_*.pdf")
    if reports:
        report_file = sorted(reports)[-1]
        print(f"  Using most recent report: {report_file}")
    else:
        print("  ❌ No PDF report found — run pdf_report.py first")
        exit()

# -----------------------------------------
# BUILD EMAIL BODY
# Clean HTML email that looks great in Gmail
# -----------------------------------------
subject = f"⚡ DreOS Morning Brief — {today}"

html_body = f"""
<html>
<body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px;">

<div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">

  <!-- Header -->
  <div style="background: #1F3864; padding: 20px 24px;">
    <h1 style="color: white; margin: 0; font-size: 20px;">⚡ DreOS Morning Brief</h1>
    <p style="color: #aac4e0; margin: 4px 0 0; font-size: 13px;">
      {today} &nbsp;|&nbsp; Bedford NH: {weather.get('temperature')}°F — {weather.get('description')}
    </p>
  </div>

  <!-- KPI Bar -->
  <div style="background: #2E75B6; padding: 12px 24px; display: flex; gap: 20px;">
    <span style="color: white; font-size: 12px;">
      🏆 Top Gainer: <strong style="color: #90EE90;">{mkt_summary.get('top_gainer', 'N/A')}</strong>
    </span>
    <span style="color: white; font-size: 12px;">
      📉 Top Loser: <strong style="color: #FFB3B3;">{mkt_summary.get('top_loser', 'N/A')}</strong>
    </span>
    <span style="color: white; font-size: 12px;">
      🎯 DreOS: <strong>{jira.get('pct_complete', 0)}% complete</strong>
    </span>
  </div>

  <!-- AI Brief -->
  <div style="padding: 20px 24px;">
    <h2 style="color: #1F3864; font-size: 14px; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px;">🤖 AI Morning Brief</h2>
    <p style="color: #333; font-size: 13px; line-height: 1.8; margin: 0;">{brief_text}</p>
  </div>

  <!-- Divider -->
  <div style="height: 1px; background: #e0e0e0; margin: 0 24px;"></div>

  <!-- Project Status -->
  <div style="padding: 16px 24px;">
    <h2 style="color: #1F3864; font-size: 14px; margin: 0 0 8px; text-transform: uppercase; letter-spacing: 1px;">🎯 Project Status</h2>
    <p style="color: #333; font-size: 13px; margin: 4px 0;">
      <strong>Progress:</strong> {jira.get('pct_complete', 0)}% ({jira.get('done', 0)}/{jira.get('total_tickets', 0)} phases complete)
    </p>
    <p style="color: #333; font-size: 13px; margin: 4px 0;">
      <strong>Currently:</strong> {jira.get('current_phase', 'N/A')}
    </p>
    <p style="color: #333; font-size: 13px; margin: 4px 0;">
      <strong>Up next:</strong> {jira.get('next_phase', 'N/A')}
    </p>
  </div>

  <!-- Footer -->
  <div style="background: #1F3864; padding: 12px 24px; text-align: center;">
    <p style="color: #aac4e0; margin: 0; font-size: 11px;">
      DreOS Personal Intelligence Hub &nbsp;|&nbsp; drebuilds.io &nbsp;|&nbsp; {today}
    </p>
    <p style="color: #aac4e0; margin: 4px 0 0; font-size: 11px;">
      Full report attached as PDF
    </p>
  </div>

</div>
</body>
</html>
"""

# -----------------------------------------
# BUILD AND SEND EMAIL
# -----------------------------------------
try:
    msg              = MIMEMultipart("alternative")
    msg["From"]      = GMAIL_USER
    msg["To"]        = EMAIL_TO
    msg["Subject"]   = subject

    msg.attach(MIMEText(html_body, "html"))

    # Attach PDF
    with open(report_file, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename=DreOS_Morning_Brief_{today_str}.pdf"
        )
        msg.attach(part)

    print(f"  📨 Connecting to Gmail...")
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD.replace(" ", ""))
        server.sendmail(GMAIL_USER, EMAIL_TO, msg.as_string())

    print(f"  ✅ Email sent to {EMAIL_TO}")
    print(f"  📎 PDF attached: {os.path.basename(report_file)}")
    print(f"  📬 Check your Gmail inbox!")

except Exception as e:
    print(f"  ❌ Email failed: {str(e)}")
    with open("error_log.txt", "a") as log:
        log.write(f"\n[{datetime.now()}] Email error: {str(e)}\n")

print(f"\n{'='*50}")
print(f"  ✅ Email delivery complete — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*50}\n")
