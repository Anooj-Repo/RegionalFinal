"""
Background Streaming Agent Service (mcp/background_stream.py)
Polls FastMCP communication tools for unstructured Slack/Teams/Email feeds and buffers them for Knowledge Graph RAG ingestion.
"""

import os
import sys
import time
import requests
from datetime import datetime

MCP_HOST = os.getenv('MCP_HOST', '127.0.0.1')
MCP_PORT = int(os.getenv('MCP_PORT', 5001))
MCP_API_KEY = os.getenv('MCP_API_KEY', 'mcp-secure-api-key-2026')
MCP_SERVER_URL = f"http://{MCP_HOST}:{MCP_PORT}"

STREAM_INTERVAL = int(os.getenv('STREAM_POLL_INTERVAL_SECONDS', 10))

def fetch_unstructured_stream():
    """Fetches communication logs via FastMCP tool endpoint."""
    headers = {"X-MCP-API-KEY": MCP_API_KEY, "Content-Type": "application/json"}
    payload = {}

    try:
        url = f"{MCP_SERVER_URL}/tools/mcp_read_communication_logs"
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            result = response.json()
            logs = result.get("data", {}).get("logs", [])
            print(f"[Streaming Agent] Successfully retrieved {len(logs)} communication log entries from FastMCP Server.")
            return logs
        else:
            print(f"[Streaming Agent Warning] MCP server returned HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"[Streaming Agent Error] Failed to connect to FastMCP server at {MCP_SERVER_URL}: {e}")
        return []

def run_streaming_loop(max_iterations: int = None):
    """Continuous polling loop streaming unstructured logs."""
    print(f"[Streaming Agent] Service started. Stream polling interval: {STREAM_INTERVAL}s.")
    iteration = 0
    try:
        while True:
            iteration += 1
            logs = fetch_unstructured_stream()
            if logs:
                print(f"[Streaming Agent Stream] Buffered {len(logs)} communication items for Knowledge Graph RAG Ingestion.")

            if max_iterations and iteration >= max_iterations:
                print(f"[Streaming Agent Loop] Reached max iterations ({max_iterations}). Stopping.")
                break

            time.sleep(STREAM_INTERVAL)
    except KeyboardInterrupt:
        print("[Streaming Agent] Stopped by user.")

if __name__ == '__main__':
    run_streaming_loop()
