"""
Mock Enterprise Adapters for MCP Server Tooling.
Interfaces with mcp/mcp.db to provide enterprise PM, communication, and risk feed data.
"""

import sys
import os
import json
import sqlite3

# Ensure mcp directory is in path
mcp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if mcp_dir not in sys.path:
    sys.path.insert(0, mcp_dir)

from mcp_db import get_mcp_db_connection

class JiraWBSAdapter:
    """Adapter for querying WBS project plans, task schedules, and critical path items."""

    @staticmethod
    def query_project_plan(project_code: str):
        conn = get_mcp_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task_code, task_name, phase, start_date, end_date, effort_days, status, is_critical_path, raw_xml_json
            FROM project_plans_wbs
            WHERE project_code = ?
            ORDER BY task_code ASC
        """, (project_code,))
        rows = cursor.fetchall()
        conn.close()

        tasks = []
        for r in rows:
            tasks.append({
                "task_code": r["task_code"],
                "task_name": r["task_name"],
                "phase": r["phase"],
                "start_date": r["start_date"],
                "end_date": r["end_date"],
                "effort_days": r["effort_days"],
                "status": r["status"],
                "is_critical_path": bool(r["is_critical_path"]),
                "metadata": json.loads(r["raw_xml_json"]) if r["raw_xml_json"] else {}
            })
        return {
            "project_code": project_code,
            "total_tasks": len(tasks),
            "critical_path_tasks": [t for t in tasks if t["is_critical_path"]],
            "tasks": tasks
        }

class SlackTeamsEmailAdapter:
    """Adapter for fetching communication logs across Slack, Teams, and Email feeds."""

    @staticmethod
    def read_communication_logs(project_code: str = None, source_type: str = None, sentiment: str = None):
        conn = get_mcp_db_connection()
        cursor = conn.cursor()

        query = "SELECT id, project_code, source_type, sender, receiver, message_text, sentiment, timestamp FROM communication_logs WHERE 1=1"
        params = []

        if project_code:
            query += " AND project_code = ?"
            params.append(project_code)
        if source_type:
            query += " AND source_type = ?"
            params.append(source_type)
        if sentiment:
            query += " AND sentiment = ?"
            params.append(sentiment)

        query += " ORDER BY timestamp DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        logs = []
        for r in rows:
            logs.append({
                "id": r["id"],
                "project_code": r["project_code"],
                "source_type": r["source_type"],
                "sender": r["sender"],
                "receiver": r["receiver"],
                "message_text": r["message_text"],
                "sentiment": r["sentiment"],
                "timestamp": r["timestamp"]
            })
        return {
            "total_logs": len(logs),
            "logs": logs
        }

class ExternalRiskAdapter:
    """Adapter for retrieving third-party external risk and vulnerability feeds."""

    @staticmethod
    def fetch_risk_feeds(project_code: str = None):
        conn = get_mcp_db_connection()
        cursor = conn.cursor()

        query = "SELECT id, project_code, category, threat_level, summary, details, published_at FROM external_risk_feeds WHERE 1=1"
        params = []

        if project_code:
            query += " AND project_code = ?"
            params.append(project_code)

        query += " ORDER BY published_at DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        feeds = []
        for r in rows:
            feeds.append({
                "id": r["id"],
                "project_code": r["project_code"],
                "category": r["category"],
                "threat_level": r["threat_level"],
                "summary": r["summary"],
                "details": r["details"],
                "published_at": r["published_at"]
            })
        return {
            "total_feeds": len(feeds),
            "feeds": feeds
        }
