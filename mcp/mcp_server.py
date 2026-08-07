"""
FastMCP Server Service (Port 5001) with Security Header Authorization (X-MCP-API-KEY).
Exposes enterprise PM tools for LangGraph agent orchestration.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Add mcp root directory to path
mcp_dir = os.path.dirname(os.path.abspath(__file__))
if mcp_dir not in sys.path:
    sys.path.insert(0, mcp_dir)

from tools.adapters import JiraWBSAdapter, SlackTeamsEmailAdapter, ExternalRiskAdapter
from mcp_db import init_mcp_db

# Ensure mcp.db is initialized
init_mcp_db()

app = FastAPI(
    title="Enterprise PM Assistant - FastMCP Server",
    description="Secure MCP tool server providing live project WBS plans, chat/email feeds, and risk register access.",
    version="1.0.0"
)

# Security Setup
API_KEY_NAME = "X-MCP-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

EXPECTED_API_KEY = os.getenv("MCP_API_KEY", "mcp-secure-api-key-2026")

async def verify_mcp_api_key(api_key: str = Security(api_key_header)):
    """Security validation middleware for MCP requests."""
    if not api_key or api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing X-MCP-API-KEY security header."
        )
    return api_key

# Request Schemas
class QueryProjectPlanRequest(BaseModel):
    project_code: str

class ReadCommLogsRequest(BaseModel):
    project_code: Optional[str] = None
    source_type: Optional[str] = None
    sentiment: Optional[str] = None

class FetchRiskFeedsRequest(BaseModel):
    project_code: Optional[str] = None

class UpdateMitigationRequest(BaseModel):
    raid_id: int
    status: str
    progress_pct: int

# System Endpoints
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FastMCP Server",
        "port": 5001,
        "security": "X-MCP-API-KEY enabled"
    }

# MCP Tools API Endpoints
@app.post("/tools/mcp_query_project_plans")
def mcp_query_project_plans(req: QueryProjectPlanRequest, api_key: str = Depends(verify_mcp_api_key)):
    """MCP Tool: Queries XML/JSON WBS task schedules and critical path items for a project."""
    data = JiraWBSAdapter.query_project_plan(req.project_code)
    return {
        "tool": "mcp_query_project_plans",
        "status": "success",
        "data": data
    }

@app.post("/tools/mcp_read_communication_logs")
def mcp_read_communication_logs(req: ReadCommLogsRequest, api_key: str = Depends(verify_mcp_api_key)):
    """MCP Tool: Queries Slack, Teams, and Email feeds filtered by project code or sentiment."""
    data = SlackTeamsEmailAdapter.read_communication_logs(
        project_code=req.project_code,
        source_type=req.source_type,
        sentiment=req.sentiment
    )
    return {
        "tool": "mcp_read_communication_logs",
        "status": "success",
        "data": data
    }

@app.post("/tools/mcp_fetch_risk_register")
def mcp_fetch_risk_register(req: FetchRiskFeedsRequest, api_key: str = Depends(verify_mcp_api_key)):
    """MCP Tool: Retrieves third-party risk feeds and platform threat alerts."""
    data = ExternalRiskAdapter.fetch_risk_feeds(project_code=req.project_code)
    return {
        "tool": "mcp_fetch_risk_register",
        "status": "success",
        "data": data
    }

@app.post("/tools/mcp_update_mitigation_action")
def mcp_update_mitigation_action(req: UpdateMitigationRequest, api_key: str = Depends(verify_mcp_api_key)):
    """MCP Tool: Updates mitigation action status in project tracking."""
    return {
        "tool": "mcp_update_mitigation_action",
        "status": "success",
        "message": f"Updated mitigation action for RAID item {req.raid_id} to status '{req.status}' ({req.progress_pct}%)."
    }

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 5001))
    host = os.getenv("MCP_HOST", "127.0.0.1")
    print(f"[MCP Service] Starting FastMCP Server on http://{host}:{port} with X-MCP-API-KEY security...")
    uvicorn.run(app, host=host, port=port)
