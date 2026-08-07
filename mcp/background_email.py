"""
Background Email Poller Service (mcp/background_email.py)
Polls backend app.db every 5-10 seconds for emails with status 'APPROVED'.
Dispatches emails via Resend API to linusimon@gmail.com and updates database status to 'SENT' or 'FAILED'.
"""

import os
import sys
import time
import sqlite3
import ssl
import requests
from datetime import datetime
from dotenv import load_dotenv
import resend

# Workaround for enterprise corporate SSL inspection certificates
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

# Base paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_DB_PATH = os.path.join(BASE_DIR, 'backend', 'app.db')
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Target email override specified by user for testing
OVERRIDE_RECIPIENT_EMAIL = "linusimon@gmail.com"

def get_app_db_connection():
    conn = sqlite3.connect(APP_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def poll_and_send_approved_emails():
    """Checks emails table for APPROVED status, sends via Resend, and updates DB."""
    # Reload env dynamically to catch updated keys
    load_dotenv(ENV_PATH, override=True)

    raw_key = os.getenv('RESEND_API_KEY', '').strip()
    resend_key = raw_key if raw_key.startswith('re_') else f"re_{raw_key}"
    resend.api_key = resend_key

    POLL_INTERVAL = int(os.getenv('EMAIL_POLL_INTERVAL_SECONDS', 5))
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'onboarding@resend.dev')

    # Default Resend sandbox sender if custom domain is not verified
    sender = "onboarding@resend.dev" if "pmai-assistant.com" in SENDER_EMAIL else SENDER_EMAIL

    if not os.path.exists(APP_DB_PATH):
        print(f"[Email Service Warning] Database not found at {APP_DB_PATH}")
        return 0

    conn = get_app_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, recipient_email, recipient_role, subject, body, created_by
        FROM emails
        WHERE status = 'APPROVED'
    """)
    approved_emails = cursor.fetchall()

    if not approved_emails:
        conn.close()
        return 0

    processed_count = 0
    for email in approved_emails:
        email_id = email['id']
        original_recipient = email['recipient_email']

        # Mandatory Override to linusimon@gmail.com as requested by user
        target_email = OVERRIDE_RECIPIENT_EMAIL
        subject = f"[PM-AI Alert] {email['subject']}"
        body = f"--- ORIGINAL INTENDED RECIPIENT: {original_recipient} ({email['recipient_role']}) ---\n\n" + email['body']

        print(f"[Email Service] Dispatching APPROVED email ID #{email_id} to {target_email} via Resend API...")

        try:
            res_id = None
            # Attempt 1: Standard Resend SDK call
            try:
                params = {
                    "from": f"PM AI Assistant <{sender}>",
                    "to": [target_email],
                    "subject": subject,
                    "text": body,
                }
                response = resend.Emails.send(params)
                res_id = response.get("id", "resend_sent_id") if isinstance(response, dict) else str(response)
            except Exception as resend_err:
                print(f"[Resend SDK Warning] SDK call failed ({resend_err}). Retrying via direct HTTPS REST API...")
                # Fallback Attempt 2: Direct REST call with verify=False for enterprise corporate SSL inspection environments
                api_url = "https://api.resend.com/emails"
                headers = {
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "from": f"PM AI Assistant <{sender}>",
                    "to": [target_email],
                    "subject": subject,
                    "text": body
                }
                res = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
                if res.status_code in [200, 201]:
                    res_id = res.json().get("id", "resend_rest_sent")
                else:
                    raise Exception(f"Resend REST API returned HTTP {res.status_code}: {res.text}")

            now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

            # Update email status to SENT
            cursor.execute("""
                UPDATE emails
                SET status = 'SENT', sent_at = ?, error_message = NULL
                WHERE id = ?
            """, (now_str, email_id))

            # Insert Audit Log entry
            cursor.execute("""
                INSERT INTO audit_logs (user_name, user_role, action, target_type, target_id, details, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Email Poller Service",
                "System",
                "EMAIL_SENT",
                "EmailDraft",
                str(email_id),
                f"Dispatched email ID #{email_id} to {target_email} via Resend API (ID: {res_id}). Subject: {subject[:40]}...",
                "127.0.0.1",
                now_str
            ))

            conn.commit()
            processed_count += 1
            print(f"[Email Service SUCCESS] Email ID #{email_id} sent to {target_email} (Resend ID: {res_id}) and status updated to SENT.")

        except Exception as e:
            error_str = str(e)
            now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[Email Service ERROR] Failed to send email ID #{email_id} to {target_email}: {error_str}")

            cursor.execute("""
                UPDATE emails
                SET status = 'FAILED', error_message = ?
                WHERE id = ?
            """, (error_str, email_id))

            cursor.execute("""
                INSERT INTO audit_logs (user_name, user_role, action, target_type, target_id, details, ip_address, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Email Poller Service",
                "System",
                "EMAIL_DISPATCH_FAILED",
                "EmailDraft",
                str(email_id),
                f"Failed to dispatch email ID #{email_id} to {target_email}: {error_str}",
                "127.0.0.1",
                now_str
            ))
            conn.commit()

    conn.close()
    return processed_count

def run_email_service_loop(max_iterations: int = None):
    """Runs the continuous polling loop every 5-10 seconds."""
    print(f"[Email Service] Polling service active. Destination forced to: {OVERRIDE_RECIPIENT_EMAIL}. Resend API Key active.")
    iteration = 0
    try:
        while True:
            iteration += 1
            count = poll_and_send_approved_emails()
            if count > 0:
                print(f"[Email Service Loop] Processed {count} approved emails in iteration #{iteration}.")

            if max_iterations and iteration >= max_iterations:
                print(f"[Email Service Loop] Reached max iterations ({max_iterations}). Stopping.")
                break

            time.sleep(5)
    except KeyboardInterrupt:
        print("[Email Service] Stopped by user.")

if __name__ == '__main__':
    run_email_service_loop()
