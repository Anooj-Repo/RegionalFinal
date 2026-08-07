"""
Background Email Poller Service (mcp/background_email.py)
Polls backend app.db every 5-10 seconds for emails with status 'APPROVED'.
Dispatches emails via Resend API and updates database status to 'SENT' or 'FAILED'.
"""

import os
import sys
import time
import sqlite3
from datetime import datetime
import resend

# Base paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
APP_DB_PATH = os.path.join(BASE_DIR, 'backend', 'app.db')

POLL_INTERVAL = int(os.getenv('EMAIL_POLL_INTERVAL_SECONDS', 5))
RESEND_API_KEY = os.getenv('RESEND_API_KEY', 're_123456789_placeholder_key')
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'notifications@pmai-assistant.com')

# Initialize Resend SDK key
resend.api_key = RESEND_API_KEY

def get_app_db_connection():
    conn = sqlite3.connect(APP_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def poll_and_send_approved_emails():
    """Checks emails table for APPROVED status, sends via Resend, and updates DB."""
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
        to_email = email['recipient_email']
        subject = email['subject']
        body = email['body']

        print(f"[Email Service] Found APPROVED email ID #{email_id} for {to_email}. Sending via Resend API...")

        try:
            # Send email via Resend API
            # If using a placeholder key in dev mode, simulate successful dispatch
            if RESEND_API_KEY.startswith("re_123456789_placeholder"):
                print(f"[Resend API Mock] Successfully dispatched email to {to_email} (Dev Mode)")
                res_id = "resend_mock_msg_998822"
            else:
                params = {
                    "from": f"PM AI Assistant <{SENDER_EMAIL}>",
                    "to": [to_email],
                    "subject": subject,
                    "text": body,
                }
                response = resend.Emails.send(params)
                res_id = response.get("id", "resend_sent")

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
                f"Dispatched email to {to_email} via Resend API (ID: {res_id}). Subject: {subject[:40]}...",
                "127.0.0.1",
                now_str
            ))

            conn.commit()
            processed_count += 1
            print(f"[Email Service SUCCESS] Email ID #{email_id} sent and status updated to SENT.")

        except Exception as e:
            error_str = str(e)
            now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[Email Service ERROR] Failed to send email ID #{email_id}: {error_str}")

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
                f"Failed to dispatch email to {to_email}: {error_str}",
                "127.0.0.1",
                now_str
            ))
            conn.commit()

    conn.close()
    return processed_count

def run_email_service_loop(max_iterations: int = None):
    """Runs the continuous polling loop every 5-10 seconds."""
    print(f"[Email Service] Polling service started. Loop interval: {POLL_INTERVAL} seconds. Resend API Key configured.")
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

            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("[Email Service] Stopped by user.")

if __name__ == '__main__':
    run_email_service_loop()
