"""
NovaTech Analytics Platform
Phase 6: Email Alerts for Critical Business Metrics

HOW TO RUN:
1. Open Terminal / Command Prompt
2. Navigate to your NovaTech Analytics folder
3. Run: python novatech_alerts.py
"""

import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

# -----------------------------------------
# MAILTRAP SETTINGS
# -----------------------------------------
SMTP_HOST     = "sandbox.smtp.mailtrap.io"
SMTP_PORT     = 2525
SMTP_USERNAME = "6cba633f05a265"
SMTP_PASSWORD = "55ffb250f367b5"
EMAIL_FROM    = "analytics@novatech.com"
EMAIL_TO      = "executive@novatech.com"

# -----------------------------------------
# ALERT THRESHOLDS
# These are the tripwires — if any metric
# crosses these lines an alert fires
# -----------------------------------------
MAX_CHURN_RATE       = 7.0   # % — industry benchmark
MAX_OPEN_TICKETS     = 10    # anything above this needs attention
MIN_SATISFACTION     = 4.0   # out of 5.0
MAX_RESOLUTION_HOURS = 24.0  # industry best practice

# -----------------------------------------
# STEP 1 — Pull metrics from database
# -----------------------------------------
print("\n🗄️  Reading NovaTech database...")

conn   = sqlite3.connect("novatech.db")
cursor = conn.cursor()

cursor.execute("SELECT SUM(monthly_fee) FROM customers WHERE status = 'Active'")
mrr = cursor.fetchone()[0] or 0

cursor.execute("SELECT COUNT(*) FROM customers")
total_customers = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM customers WHERE status = 'Churned'")
churned = cursor.fetchone()[0]
churn_rate = (churned / total_customers * 100) if total_customers else 0

cursor.execute("SELECT COUNT(*) FROM support_tickets WHERE status = 'Open'")
open_tickets = cursor.fetchone()[0]

cursor.execute("SELECT AVG(resolution_hours) FROM support_tickets WHERE status = 'Resolved'")
avg_resolution = cursor.fetchone()[0] or 0

cursor.execute("SELECT AVG(satisfaction) FROM support_tickets WHERE satisfaction IS NOT NULL")
avg_satisfaction = cursor.fetchone()[0] or 0

cursor.execute("SELECT SUM(amount) FROM sales")
total_sales = cursor.fetchone()[0] or 0

conn.close()
print("✅ Metrics pulled successfully")

# -----------------------------------------
# STEP 2 — Check alert conditions
# Each metric is checked against its threshold
# If it crosses the line it gets added to alerts
# -----------------------------------------
print("\n🔍 Checking alert conditions...")

alerts   = []
warnings = []
clear    = []

# Churn rate check
if churn_rate > MAX_CHURN_RATE:
    alerts.append({
        "metric":    "Churn Rate",
        "value":     f"{churn_rate:.1f}%",
        "threshold": f"{MAX_CHURN_RATE}%",
        "message":   f"Churn rate is {churn_rate:.1f}% — more than double the {MAX_CHURN_RATE}% benchmark. Immediate retention action required.",
        "severity":  "🔴 CRITICAL"
    })
else:
    clear.append(f"✅ Churn Rate: {churn_rate:.1f}% — within benchmark")

# Open tickets check
if open_tickets > MAX_OPEN_TICKETS:
    alerts.append({
        "metric":    "Open Support Tickets",
        "value":     str(open_tickets),
        "threshold": str(MAX_OPEN_TICKETS),
        "message":   f"{open_tickets} tickets are currently open — above the {MAX_OPEN_TICKETS} ticket threshold. Support team needs immediate attention.",
        "severity":  "🔴 CRITICAL"
    })
else:
    clear.append(f"✅ Open Tickets: {open_tickets} — within threshold")

# Satisfaction check
if avg_satisfaction < MIN_SATISFACTION:
    warnings.append({
        "metric":    "Customer Satisfaction",
        "value":     f"{avg_satisfaction:.1f}/5.0",
        "threshold": f"{MIN_SATISFACTION}/5.0",
        "message":   f"Average satisfaction score is {avg_satisfaction:.1f}/5.0 — below the {MIN_SATISFACTION} minimum. Customer experience needs review.",
        "severity":  "🟡 WARNING"
    })
else:
    clear.append(f"✅ Satisfaction: {avg_satisfaction:.1f}/5.0 — above minimum")

# Resolution time check
if avg_resolution > MAX_RESOLUTION_HOURS:
    warnings.append({
        "metric":    "Avg Resolution Time",
        "value":     f"{avg_resolution:.1f} hours",
        "threshold": f"{MAX_RESOLUTION_HOURS} hours",
        "message":   f"Average resolution time is {avg_resolution:.1f} hours — exceeding the {MAX_RESOLUTION_HOURS} hour benchmark. Support processes need review.",
        "severity":  "🟡 WARNING"
    })
else:
    clear.append(f"✅ Resolution Time: {avg_resolution:.1f}hrs — within benchmark")

# Print results to terminal
all_issues = alerts + warnings
for issue in all_issues:
    print(f"  {issue['severity']} {issue['metric']}: {issue['value']} (threshold: {issue['threshold']})")
for c in clear:
    print(f"  {c}")

# -----------------------------------------
# STEP 3 — Send alert email if needed
# -----------------------------------------
today = date.today().strftime("%B %d, %Y")

if all_issues:
    print(f"\n📧 {len(all_issues)} issue(s) detected — sending alert email...")

    critical_count = len(alerts)
    warning_count  = len(warnings)

    subject = f"🚨 NovaTech Analytics Alert — {critical_count} Critical, {warning_count} Warning — {today}"

    critical_section = ""
    if alerts:
        critical_section = "🔴 CRITICAL ISSUES — IMMEDIATE ACTION REQUIRED\n"
        critical_section += "-" * 50 + "\n"
        for a in alerts:
            critical_section += f"\n{a['metric']}\n"
            critical_section += f"Current Value: {a['value']}  |  Threshold: {a['threshold']}\n"
            critical_section += f"{a['message']}\n"

    warning_section = ""
    if warnings:
        warning_section = "\n🟡 WARNINGS — MONITOR CLOSELY\n"
        warning_section += "-" * 50 + "\n"
        for w in warnings:
            warning_section += f"\n{w['metric']}\n"
            warning_section += f"Current Value: {w['value']}  |  Threshold: {w['threshold']}\n"
            warning_section += f"{w['message']}\n"

    clear_section = "\n✅ METRICS WITHIN NORMAL RANGE\n"
    clear_section += "-" * 50 + "\n"
    for c in clear:
        clear_section += f"{c}\n"

    body = f"""
NovaTech Analytics — Automated Alert System
Generated: {today}

BUSINESS SNAPSHOT:
  MRR:           ${mrr:,.2f}
  Total Sales:   ${total_sales:,.2f}
  Customers:     {total_customers} total ({churned} churned)

{"=" * 50}

{critical_section}
{warning_section}
{clear_section}

{"=" * 50}
This is an automated alert from the NovaTech Analytics Platform.
Please review the full dashboard and executive report for details.

— NovaTech Automated Analytics System
    """

    try:
        msg            = MIMEMultipart()
        msg["From"]    = EMAIL_FROM
        msg["To"]      = EMAIL_TO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

        print(f"✅ Alert email sent successfully!")
        print(f"📬 Check your Mailtrap inbox!\n")

    except Exception as e:
        print(f"❌ Email failed: {str(e)}\n")

else:
    print(f"\n✅ All metrics within normal range — no alerts needed!")
    print(f"📅 Date: {today}\n")
