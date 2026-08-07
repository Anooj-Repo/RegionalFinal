# Prompt for Creating Milestones and Implementation Plan

Please create a detailed milestone-wise implementation plan for an enterprise-grade AI application based on the following requirements. Don't implement anything yet.

## Core Principles

* Enterprise-grade, production-ready code.
* Modular, scalable, and maintainable architecture.
* No hardcoded values or secrets.
* Environment-based configuration.
* Follow SOLID and DRY principles.
* Layered architec  ture with Repository Pattern, Service Layer, and Dependency Injection.
* Comprehensive logging and robust exception handling.
* Type-safe, reusable components.
* Easily extensible for future business domains.
* Separate backend, frontend and MCP folder
* Separate and unified setup and start batch files to run frontend, backend and mcp server.
* Separate database for backend application logic and mcp server logic
* Analyze TCS genai in https://genailab.tcs.in and identify the best gen lab api and models to use in an agent.
* Dedicated client wrapper for tcs gen ai calls for RAG.
* Use stich for the UI design through the MCP configured in the antigravity and later use that HTML to build the angular UI without any change in design.
* Create documentation like readme and architectural diagram.
* Create unit test project and provide option to run and save result of unit test.
* Create a detailed testcase for problem statement and create a regression automation testing project. Create a detailed regression test project and execute the automated regression test project and save the result.
* Keep regression test and unit test project seperate from the main frondend, backend and mcp server application
* Add git ignore file to remove all unwanted files. Make sure env file and database files are maintained.


---

# Technology Stack

## Frontend

* Angular 17 Standalone Components
* TypeScript
* RxJS
* UI implementation using Stitch MCP (as a dedicated milestone)

## Backend

* Python 3.12.8
* Flask
* SQLite Database
* REST APIs
* JWT Authentication
* Environment-based configuration

---

# Authentication & Administration

Implement:

* Login/Logout
* JWT Authentication
* Role-Based Access Control (RBAC)
* Separate Admin, User login and other role based on requirement.
* User Management
* Admin Console and other consoles based on the roles
* Master Data Management
* Knowledge Document Management
* Configuration Management
* Audit Logs
* Analytics Dashboard

Only administrators should be allowed to manage business data and knowledge documents.

---

# AI Architecture

Implement a LangGraph-based multi-agent architecture.

General Requirements:

* Use langraph for agents
* Node-based workflow
* Separate `agents` folder
* Identify and implement all the agents required for the business use case
* Each agent implemented in a separate file
* MCP tools attached to the respective agents. Check below code as example on how MCP tools are attached to agents.
agent_graph = create_react_agent(
            model=model,
            tools=tools,
            prompt="You are an AI Infrastructure Capacity Planning Advisor. Use tools to answer telemetry and FinOps questions."
        )
* Dynamic agent selection
* Parallel execution wherever possible
* Perform RAG retrieval through agent
* Before returning the final response add Reflection Agent and memory agent.

Requirements for chat in addition to general AI requirement considerations:
* Chat should have a separate supervisor agent and agent flow. 
* Chat should make sure all guardrail and PI masking is done. 
* Don't provide any hardcoded response in chat. 
* Chat should consider request and provide logical responses.

---

# MCP Integration

* Implement MCP Server as an independent background service running in a different port.
* Use MCP as tools attached to agents
* Use MCP for accessing live systems, applications, and external services.

---

# Knowledge Retrieval (RAG)

Use RAG for static knowledge sources such as:

* Policy documents
* Statements of Work (SOW)
* Business procedures
* SOPs
* Knowledge articles
* FAQs
* Regulatory documents
* Compliance documentation
* Static reference documents

Or based on requirement

Seed sample rag documents
Create upload folder in backend and add documents to upload to RAG

Do **not** use RAG for transactional or frequently changing business data.

---

# Guardrails

Execute before LLM calls:

* Prompt Injection Detection
* Jailbreak Prevention
* Toxicity Detection
* Sensitive Information Detection
* PII Masking
* SQL Injection Protection
* Content Moderation
* Question Relevance Verification
* Rate Limiting
* RBAC Validation
* Audit Logging

---

# Database

Derive entities from the problem statement and create:

* Normalized schema
* Relationships
* Indexes
* Seed data
* Sample datasets
* Separate database for backend application logic and mcp server logic

---

# Main functionalities in pages required

* Summary dashboard
* Analysis
* Implementation
* Text Chat
* Voice Chat (STT/TTS)
* Vision
* OCR
* Vector Embeddings

---

# Demo & Observability

Provide a collapsible execution log in a graphical node manner in all pages that runs agents showing:

* Input processing
* Guardrails executed
* Text masked
* Selected agents
* Agent inputs
* Agent outputs
* MCP tool called in agent
* RAG Knowledge retrieval
* Final orchestration flow
* confidence score, token used, cost of token etc.

---

# Definition of Done

The solution should:

* Build successfully
* Contain no TODOs
* Contain no hardcoded secrets
* Be secure by default
* Include complete implementation documentation
* Match documentation with implementation
* Be production-ready
* Be easily extensible for future business domains
* Innovative ideas
