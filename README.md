# Enterprise Program Management AI Assistant for Risk Analysis & Stakeholder Communication

An enterprise-grade, production-ready AI application designed for Program Managers, Project Managers, Technical Leads, and Executive Leadership. 
The system synthesizes project plans (WBS XML/JSON), real-time communication feeds (Slack, Teams, Email), static SOP/SOW compliance policy documents, and third-party risk feeds to automatically detect risks, generate RAID mitigation strategies, and draft audience-tailored communications with **Mandatory Human-in-the-Loop Approval**.

---

## Technical Stack & Architecture

- **Frontend:** Angular 17 Standalone Components, TypeScript, RxJS, custom CSS design tokens matching Stitch MCP layouts (`frontend/`).
- **Backend REST API:** Python 3.12 + Flask (`backend/run.py` on Port 5000) with SQLAlchemy ORM (`backend/app.db`).
- **MCP Server & Tooling:** Independent FastMCP Server (`mcp/mcp_server.py` on Port 5001) with API Token security validation (`X-MCP-API-KEY`).
- **Background Email Dispatcher:** 5–10s polling worker (`mcp/background_email.py`) dispatching approved emails via **Resend API** to `linusimon@gmail.com`.
- **Background Streaming Agent:** Polls communication feeds into unstructured vector buffer (`mcp/background_stream.py`).
- **Multi-Agent Architecture (LangGraph):**
  1. **Data Intelligence Graph:** Ingestion, PII masking, dual RAG indexing.
  2. **Risk Intelligence Graph:** Deterministic RAID Rule Engine + LLM Risk Scoring + Reflection Agent.
  3. **Communication Graph:** Stakeholder copy generator & Human Approval draft creator.
- **Dual RAG System:** Static RAG (PDF/DOCX/TXT SOWs & SOPs) + Unstructured GraphRAG (`(Subject) --[Predicate]--> (Object)` Knowledge Graph triples).

---

## Getting Started & Execution

### 1. One-Click Setup
Run `setup.bat` to create the Python virtual environment, install all dependencies, and seed the databases:
```cmd
setup.bat
```

### 2. Launching Services

- **Launch All Services Together:**
  ```cmd
  start.bat
  ```
  *(Launches Backend 5000, MCP Server 5001, Background Email Worker, and Angular Web App 4200 in separate windows)*

- **Or Launch Individual Executables:**
  - `start_backend.bat` -> Flask API on http://localhost:5000
  - `start_mcp.bat` -> FastMCP Tool Server on http://localhost:5001
  - `start_background_services.bat` -> Email Dispatcher & Streaming Worker
  - `start_frontend.bat` -> Angular Web Application on http://localhost:4200

---

## Role-Based Workspaces & Pages

1. **Program Manager Workspace (`/program-manager`):** Executive Portfolio Health, 5x5 Risk Heatmap Matrix, Projects Portfolio, Gantt Milestone Timeline, Risk Center, Human Approval Communication Center, and Exportable Reports.
2. **Project Manager Workspace (`/project-manager`):** WBS Task Grid, Overdue Task Alert Block, Risk Register Inspector (Score 85/100 High), and Visual Dependency Map Flowchart.
3. **Tech Lead / Team Lead Workspace (`/team-lead`):** Team Overview, Workload Heatmap Matrix (Developer/QA utilization %), Sprint Backlog with Story Points, Engineering RAID, and Technical Document Hub.
4. **System & Technical Admin Workspace (`/system-admin`):** Real-Time Graphical Node Execution Trace component, Audio STT/TTS telemetry, LLM Token & Cost metrics ($0.297 / 148.5k tokens), Security Audit Stream, and MCP status monitor.

---

## Standalone Testing Projects

- **Unit Test Suite:**
  ```cmd
  .\venv\Scripts\python.exe tests/unit/run_unit_tests.py
  ```
  *(Executes 8 unit tests; saves results to `tests/unit/unit_test_results.json`)*

- **Automated Regression Suite:**
  ```cmd
  .\venv\Scripts\python.exe tests/regression/run_regression_tests.py
  ```
  *(Executes end-to-end regression validation; saves results to `tests/regression/regression_results.json`)*
