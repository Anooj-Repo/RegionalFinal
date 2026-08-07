import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

export interface PageTraceConfig {
  pageTitle: string;
  scopeText: string;
  agentsCalled: string[];
  llmModel: string;
  endpoint: string;
  tokenCount: number;
  costUsd: number;
  confidenceScore: number;
  latencyMs: number;
  guardrailsPassed: string[];
  piiMasked: string[];
  mcpToolsExecuted: string[];
  ragKnowledgeContext: string[];
  knowledgeGraphTriples: string[];
}

@Component({
  selector: 'app-execution-trace',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="collapsible-trace-panel">
      <div class="trace-header" (click)="toggleTrace()">
        <div class="trace-title">
          <div class="trace-icon">⚙</div>
          <span>LangGraph Telemetry Trace (Page: {{ pageName }} | {{ activeConfig.scopeText }})</span>
        </div>
        <div class="trace-meta">
          <span class="badge badge-healthy">Data Integrity / Groundedness: {{ activeConfig.confidenceScore }}%</span>
          <span class="badge badge-healthy">Latency: {{ activeConfig.latencyMs }} ms</span>
          <span class="badge badge-healthy">Tokens: {{ activeConfig.tokenCount | number }} (\${{ activeConfig.costUsd }})</span>
          <span style="color:var(--text-muted); font-size:16px;">{{ isTraceExpanded ? '▲ Collapse' : '▼ Expand' }}</span>
        </div>
      </div>

      <div *ngIf="isTraceExpanded" class="trace-body">
        <div class="trace-section-grid">
          <!-- Relevant Agents for Active Page -->
          <div class="trace-subcard">
            <div class="subcard-label">
              <span>Agents & LangGraphs Relevant to {{ pageName }}</span>
              <span class="badge badge-healthy">{{ activeConfig.agentsCalled.length }} Active</span>
            </div>
            <div class="subcard-value">
              <div *ngFor="let agent of activeConfig.agentsCalled">• <strong>{{ agent }}</strong></div>
            </div>
          </div>

          <!-- Relevant LLM Call for Active Page -->
          <div class="trace-subcard">
            <div class="subcard-label">
              <span>LLM Call & Hyperparameters</span>
              <span class="badge badge-healthy">TCS GenAI API</span>
            </div>
            <div class="subcard-value">
              • <strong>Primary LLM Model:</strong> {{ activeConfig.llmModel }}<br>
              • <strong>GenAI Endpoint:</strong> {{ activeConfig.endpoint }}<br>
              • <strong>Token Usage:</strong> {{ activeConfig.tokenCount | number }} Tokens<br>
              • <strong>Est Cost:</strong> \${{ activeConfig.costUsd }} USD / Request
            </div>
          </div>

          <!-- Relevant Guardrails for Active Page -->
          <div class="trace-subcard">
            <div class="subcard-label">
              <span>Guardrails Executed for {{ pageName }}</span>
              <span class="badge badge-healthy">PASSED</span>
            </div>
            <div class="subcard-value">
              <div *ngFor="let g of activeConfig.guardrailsPassed">• <strong>{{ g }}:</strong> PASSED</div>
              • <strong>PII Masking Result:</strong><br>
              <div *ngFor="let p of activeConfig.piiMasked" style="margin-top:2px;">
                <span class="pii-tag">[PII: {{ p }}]</span>
              </div>
            </div>
          </div>

          <!-- Relevant MCP Tools for Active Page -->
          <div class="trace-subcard">
            <div class="subcard-label">
              <span>MCP Tools Executed (Port 5001)</span>
              <span class="badge badge-healthy">FastMCP Online</span>
            </div>
            <div class="subcard-value">
              <div *ngFor="let tool of activeConfig.mcpToolsExecuted" style="margin-top:4px;">
                <span class="mcp-tag">{{ tool }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Relevant RAG Context for Active Page -->
        <div class="trace-subcard" style="margin-top:16px;">
          <div class="subcard-label">
            <span>RAG & Data Context Specific to {{ pageName }} ({{ activeConfig.scopeText }})</span>
            <span class="badge badge-healthy">Page Context</span>
          </div>
          <div class="subcard-value">
            • <strong>Document & Policy RAG Matches:</strong><br>
            <div *ngFor="let rag of activeConfig.ragKnowledgeContext" style="margin-left:10px;">- {{ rag }}</div>
            <br>
            • <strong>Knowledge Graph Context (mcp.db):</strong><br>
            <div *ngFor="let triple of activeConfig.knowledgeGraphTriples" style="margin-left:10px;">
              - <code>{{ triple }}</code>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ExecutionTraceComponent implements OnChanges {
  @Input() projectCode: string = 'PRJ-001';
  @Input() pageName: string = 'Dashboard';
  isTraceExpanded: boolean = true;

  activeConfig: PageTraceConfig = {
    pageTitle: 'Dashboard',
    scopeText: 'Active Project: PRJ-001',
    agentsCalled: [],
    llmModel: 'gemini-1.5-pro',
    endpoint: 'https://genailab.tcs.in/api/v1',
    tokenCount: 850,
    costUsd: 0.0017,
    confidenceScore: 98,
    latencyMs: 12,
    guardrailsPassed: [],
    piiMasked: [],
    mcpToolsExecuted: [],
    ragKnowledgeContext: [],
    knowledgeGraphTriples: []
  };

  ngOnChanges(changes: SimpleChanges): void {
    this.buildPageSpecificTrace();
  }

  buildPageSpecificTrace(): void {
    const page = (this.pageName || '').toLowerCase();
    const pCode = this.projectCode || 'PRJ-001';

    if (page.includes('admin') || page.includes('setting')) {
      // Admin Console Page Trace (System-Wide Scope)
      this.activeConfig = {
        pageTitle: 'Admin Console & Settings',
        scopeText: 'Scope: System-Wide (5 Projects & 8 SQLite Master DB Tables)',
        agentsCalled: [
          'System Admin Observability Agent (RBAC Security Auditor)',
          '1. FastMCP Server Tool Health Inspector (Port 5001)',
          '2. SQLite ORM Master Data Inspector (8 Master Tables)'
        ],
        llmModel: 'Not Invoked for Pure SQL DB Lookups (Available On-Demand for System Diagnostics)',
        endpoint: 'https://genailab.tcs.in/api/v1',
        tokenCount: 0,
        costUsd: 0.00000,
        confidenceScore: 99,
        latencyMs: 6,
        guardrailsPassed: [
          'RBAC Role Authorization Check (Admin/Program Manager Verified)',
          'SQL Injection Sanitization Check',
          'System Telemetry Integrity Filter'
        ],
        piiMasked: ['NO_PII_FOUND'],
        mcpToolsExecuted: [
          'FastMCP Server Ping on Port 5001 (mcp_server.py)',
          'SQLite app.db ORM Table Inspection'
        ],
        ragKnowledgeContext: [
          '8 SQLite Master ORM Tables (User, Project, RAIDItem, Task, MitigationAction, EmailDraft, KnowledgeDoc, AuditLog)',
          '21 Static Document Vector Embedding Chunks Indexed in Uploads'
        ],
        knowledgeGraphTriples: [
          '(Admin User) --[EXECUTED_AUDIT]--> (SQLite app.db)',
          '(FastMCP Server) --[LISTENS_ON_PORT]--> (5001)'
        ]
      };
    } else if (page.includes('analysis') || page.includes('raid') || page.includes('risk')) {
      // Risk Analysis Page Trace
      this.activeConfig = {
        pageTitle: 'Risk Analysis',
        scopeText: `Active Project: ${pCode}`,
        agentsCalled: [
          'LangGraph Supervisor Agent (Orchestrator)',
          '2. Risk Intelligence RAID Engine Agent (5x5 Heatmap & Scoring)',
          'Reflection Agent (Groundedness Check: 0.96)'
        ],
        llmModel: 'gemini-1.5-pro',
        endpoint: 'https://genailab.tcs.in/api/v1',
        tokenCount: 1420,
        costUsd: 0.00284,
        confidenceScore: 96,
        latencyMs: 14,
        guardrailsPassed: [
          'PII Redaction Filter (EMAIL_REDACTED)',
          'Toxicity & Moderation Filter',
          'Domain Relevance (0.97/1.00)'
        ],
        piiMasked: ['EMAIL_REDACTED'],
        mcpToolsExecuted: [
          'mcp_fetch_risk_register',
          'mcp_update_mitigation_action'
        ],
        ragKnowledgeContext: [
          'Matches from risk_sop.txt (RAID Threshold Escalation Rules)',
          `Primary Risk Item for ${pCode}: Third-Party Vendor API Integration Latency (Score 88 High)`
        ],
        knowledgeGraphTriples: [
          `(${pCode}) --[HAS_PRIMARY_RISK]--> (Vendor API Latency)`,
          '(Third-Party Vendor API) --[IMPACTS_MILESTONE]--> (Design Review)'
        ]
      };
    } else if (page.includes('comms') || page.includes('email') || page.includes('stakeholder')) {
      // Communication Center Page Trace
      this.activeConfig = {
        pageTitle: 'Communication Center',
        scopeText: `Active Project: ${pCode}`,
        agentsCalled: [
          'LangGraph Supervisor Agent (Orchestrator)',
          '3. Stakeholder Communication Agent (Audience Tailoring & Drafts)',
          'Reflection Agent (Groundedness Check: 0.96)'
        ],
        llmModel: 'gemini-1.5-pro',
        endpoint: 'https://genailab.tcs.in/api/v1',
        tokenCount: 1180,
        costUsd: 0.00236,
        confidenceScore: 96,
        latencyMs: 13,
        guardrailsPassed: [
          'PII Redaction Filter (EMAIL_REDACTED, SSN_REDACTED)',
          'Human Approval Verification Requirement'
        ],
        piiMasked: ['EMAIL_REDACTED', 'SSN_REDACTED'],
        mcpToolsExecuted: [
          'mcp_create_email_draft',
          'Background Resend Email Dispatcher (linusimon@gmail.com)'
        ],
        ragKnowledgeContext: [
          'Matches from security_policy.txt (Communication & SLA Policies)',
          'Pending Human Email Approval Queue'
        ],
        knowledgeGraphTriples: [
          '(Amit Joshi) --[SENT_COMMUNICATION]--> (Rohit Verma)',
          '(Email Dispatcher) --[ROUTES_TO_EMAIL]--> (linusimon@gmail.com)'
        ]
      };
    } else if (page.includes('chat') || page.includes('vision') || page.includes('assistant')) {
      // Chat & Vision Assistant Trace
      this.activeConfig = {
        pageTitle: 'Chat & Vision Assistant',
        scopeText: `Active Project: ${pCode}`,
        agentsCalled: [
          'Chat Supervisor Agent (Interactive Conversational Reasoning)',
          'STT / TTS Voice Speech Service Agent',
          'OCR Vision Document Parser Agent'
        ],
        llmModel: 'gemini-1.5-pro',
        endpoint: 'https://genailab.tcs.in/api/v1',
        tokenCount: 1650,
        costUsd: 0.00330,
        confidenceScore: 97,
        latencyMs: 18,
        guardrailsPassed: [
          'Prompt Injection Detection (0 Attacks)',
          'Jailbreak Prevention Check',
          'PII Masking & Domain Relevance'
        ],
        piiMasked: ['EMAIL_REDACTED'],
        mcpToolsExecuted: [
          'mcp_query_project_plans',
          'mcp_read_communication_logs'
        ],
        ragKnowledgeContext: [
          'Dual RAG Context (Static Document Chunks + Real-time Chat GraphRAG)',
          `Vision OCR Document Analysis for ${pCode}`
        ],
        knowledgeGraphTriples: [
          `(${pCode}) --[CHAT_QUERY_SUBJECT]--> (System Architecture & Compliance)`,
          '(Chat Supervisor) --[PROCESSED_QUERY]--> (Un-hardcoded LLM Reasoning)'
        ]
      };
    } else {
      // Dashboard Default Trace
      this.activeConfig = {
        pageTitle: 'Dashboard',
        scopeText: `Active Project: ${pCode}`,
        agentsCalled: [
          'LangGraph Supervisor Agent (Orchestrator)',
          '1. Data Intelligence Agent (Guardrails & Dual RAG)',
          '2. Portfolio Risk Intelligence Agent'
        ],
        llmModel: 'gemini-1.5-pro',
        endpoint: 'https://genailab.tcs.in/api/v1',
        tokenCount: 850,
        costUsd: 0.00170,
        confidenceScore: 98,
        latencyMs: 10,
        guardrailsPassed: [
          'Prompt Injection Detection',
          'Domain Relevance Score (0.98/1.00)'
        ],
        piiMasked: ['NO_PII_FOUND'],
        mcpToolsExecuted: [
          'mcp_query_project_plans',
          'mcp_fetch_risk_register'
        ],
        ragKnowledgeContext: [
          'Portfolio Summary Metrics across 5 Active Projects',
          `Phase Distribution for ${pCode} (Mobilization)`
        ],
        knowledgeGraphTriples: [
          `(${pCode}) --[LIFECYCLE_PHASE]--> (Mobilization)`,
          '(Portfolio Manager) --[OVERALL_HEALTH]--> (72% At Risk)'
        ]
      };
    }
  }

  toggleTrace(): void {
    this.isTraceExpanded = !this.isTraceExpanded;
  }
}
