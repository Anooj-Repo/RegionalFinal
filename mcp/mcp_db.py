"""
Database Helper & Schema Manager for MCP Server Logic (mcp/mcp.db)
"""

import sqlite3
import os
import json
from datetime import datetime

MCP_DB_PATH = os.path.join(os.path.dirname(__file__), "mcp.db")

def get_mcp_db_connection():
    conn = sqlite3.connect(MCP_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_mcp_db():
    conn = get_mcp_db_connection()
    cursor = conn.cursor()

    # 1. Project Plans WBS Table (XML/JSON structured data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_plans_wbs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_code TEXT NOT NULL,
        task_code TEXT NOT NULL,
        task_name TEXT NOT NULL,
        phase TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT,
        effort_days INTEGER DEFAULT 1,
        status TEXT DEFAULT 'Not Started',
        is_critical_path INTEGER DEFAULT 0,
        raw_xml_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Communication Logs Table (Slack/Teams/Email feeds)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS communication_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_code TEXT NOT NULL,
        source_type TEXT NOT NULL, -- Slack, Teams, Email
        sender TEXT NOT NULL,
        receiver TEXT NOT NULL,
        message_text TEXT NOT NULL,
        sentiment TEXT DEFAULT 'Neutral', -- Positive, Neutral, Negative
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. External Risk Feeds Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS external_risk_feeds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_code TEXT NOT NULL,
        category TEXT NOT NULL,
        threat_level TEXT NOT NULL, -- High, Medium, Low
        summary TEXT NOT NULL,
        details TEXT,
        published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()
    print("[MCP DB] mcp.db initialized successfully.")

if __name__ == '__main__':
    init_mcp_db()
