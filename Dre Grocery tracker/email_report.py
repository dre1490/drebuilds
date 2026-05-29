"""
Weekly Grocery Report — Phase 4
Email the PDF report to 1490dre@gmail.com

HOW TO RUN:
1. Open Terminal
2. Navigate to your Grocery Tracker folder
3. Run: python email_report.py
"""

import smtplib
import os
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date

# -----------------------------------------
# EMAIL SETTINGS
# -----------------------------------------
SMTP_HOST     = "smtp.gmail.com"
SMTP_PORT     = 587
SMTP_USERNAME = "1490dre@gmail.com"
SMTP_PASSWORD = "YOUR_GMAIL_APP_PASSWORD_HERE"
EMAIL_FROM    = "1490dre@gmail.com"
EMAIL_TO      = "1490dre@gmail.com"

# -----------------------------------------
# FIND THE LATEST REPORT
# -----------------------------------------
print("\n📧 Preparing to send grocery report...\n")

today       = date.today().strftime("%Y-%m-%d")
report_file = f"grocery_report_{today}.pdf"

if not os.path.exists(report_file):
    # Try finding any recent report
    reports = glob.glob("grocery_report_*.pdf")
    if reports:
        report_file = sorted(reports)[-1]
        print(f"  Using most recent report: {report_file}")
    else:
        print("❌ No report found. Run generate_grocery_report.py first.")
        exit()

# -----------------------------------------
# BUILD EMAIL
# -----------------------------------------
today_formatted = date.today().strftime("%B %d, %Y")

subject = f"🛒 Your Weekly Grocery Report — {today_formatted}"

body = f"""
Hi Dre!

Your weekly grocery price comparison report is ready for {today_formatted}.

This week's report includes:
  ✅ Price comparison between Market Basket and Hannaford
  ✅ Best price per item highlighted
  ✅ Total basket cost for each store
  ✅ Shopping insights and recommendations
  ✅ 3 quick 30-minute meal ideas

Open the attached PDF for the full report.

Happy shopping! 🛍️

— Your Weekly Grocery Tracker
"""

msg              = MIMEMultipart()
msg["From"]      = EMAIL_FROM
msg["To"]        = EMAIL_TO
msg["Subject"]   = subject
msg.attach(MIMEText(body, "plain"))

# Attach PDF
with open(report_file, "rb") as f:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={report_file}"
    )
    msg.attach(part)

# -----------------------------------------
# SEND EMAIL
# -----------------------------------------
try:
    print(f"  📨 Sending to {EMAIL_TO}...")
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD.replace(" ", ""))
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print(f"  ✅ Email sent successfully!")
    print(f"  📎 Attachment: {report_file}")
    print(f"  📬 Check your Gmail inbox at {EMAIL_TO}\n")

except Exception as e:
    print(f"  ❌ Email failed: {str(e)}\n")
    print("  💡 Make sure your Gmail App Password is correct")
    print("  💡 Make sure 2-Step Verification is enabled on your Google account\n")
