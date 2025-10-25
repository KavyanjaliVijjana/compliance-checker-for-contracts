import smtplib
import requests
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText

# --- Load environment variables ---
load_dotenv()

# --- Configuration (Loaded from .env file) ---
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# --- Initial Validation ---
missing_vars = [
    var for var, val in {
        "EMAIL_SENDER": EMAIL_SENDER,
        "EMAIL_PASSWORD": EMAIL_PASSWORD,
        "EMAIL_RECEIVER": EMAIL_RECEIVER,
        "SLACK_WEBHOOK_URL": SLACK_WEBHOOK_URL
    }.items() if not val
]

if missing_vars:
    print(f"FATAL ERROR: Missing environment variables: {', '.join(missing_vars)}")
    print("Please ensure all required values are defined in your .env file.")
    exit()

# ----------------------------------------------------------------------

def send_email_notification(subject: str, body: str, receiver_email: str):
    """
    Sends an email notification using SMTP over TLS (Secure Mail Transfer Protocol).
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = receiver_email
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"✅ Email notification SENT to {receiver_email}: '{subject}'")
    except Exception as e:
        print(f"❌ ERROR: Failed to send email to {receiver_email}. Details: {e}")

# ----------------------------------------------------------------------

def send_slack_notification(message_text: str):
    """
    Sends a real-time notification to a Slack channel using an Incoming Webhook.
    """
    payload = {
        "text": message_text,
        "username": "ComplianceBot 🕵️‍♂️",
        "icon_emoji": ":shield:",
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Slack notification SENT successfully.")
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to send Slack notification. Details: {e}")

# ----------------------------------------------------------------------

if __name__ == '__main__':
    print("--- Testing Email Notification ---")
    email_subject = "ACTION REQUIRED: Compliance Template Updated!"
    email_body = "A change was detected in a scraped compliance template. Review immediately."
    send_email_notification(email_subject, email_body, EMAIL_RECEIVER)

    print("\n--- Testing Slack Notification ---")
    slack_message = "🚨 CRITICAL ALERT: Template Scraping Error! A link failed. Intervention required."
    send_slack_notification(slack_message)
