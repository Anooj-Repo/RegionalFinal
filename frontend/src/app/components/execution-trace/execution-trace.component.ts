import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-execution-trace',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="collapsible-trace-panel">
      <div class="trace-header" (click)="toggleTrace()">
        <div class="trace-title">
          <div class="trace-icon">⚙</div>
          <span>LangGraph Agent Execution Log & Telemetry Trace (Active Project: PRJ-001)</span>
        </div>
        <div class="trace-meta">
          <span class="badge badge-healthy">Confidence: 95%</span>
          <span class="badge badge-healthy">Latency: 18 ms</span>
          <span class="badge badge-healthy">Tokens: 1,590 ($0.00318)</span>
          <span style="color:var(--text-muted); font-size:16px;">{{ isTraceExpanded ? '▲ Collapse' : '▼ Expand' }}</span>
        </div>
      </div>

      <div *ngIf="isTraceExpanded" class="trace-body">
        <div class="trace-section-grid">
          <div class="trace-subcard">
            <div class="subcard-label">
              <span>Agents & LangGraphs Called</span>
              <span class="badge badge-healthy">6 Active</span>
            </div>
            <div class="subcard-value">
              • <strong>LangGraph Supervisor Agent</strong> (Orchestrator)<br>
              • <strong>1. Data Intelligence Agent</strong> (Guardrails & Dual RAG)<br>
              • <strong>2. Risk Intelligence Agent</strong> (RAID Engine & LLM Reasoning)<br>
              • <strong>3. Stakeholder Communication Agent</strong> (Audience Tailoring)<br>
              • <strong>Reflection Agent</strong> (Groundedness Check: 0.96)<br>
              • <strong>Memory Agent</strong> (Conversational Context)
            </div>
          </div>

          <div class="trace-subcard">
            <div class="subcard-label">
              <span>LLM & Endpoint Configuration</span>
              <span class="badge badge-healthy">TCS GenAI API</span>
            </div>
            <div class="subcard-value">
              • <strong>Primary LLM Model:</strong> gemini-1.5-pro<br>
              • <strong>GenAI Endpoint:</strong> https://genailab.tcs.in/api/v1<br>
              • <strong>Hyperparameters:</strong> Temp = 0.2, Top-P = 0.95, Max Tokens = 2048<br>
              • <strong>Token Usage:</strong> 1,250 Prompt / 340 Completion (Total 1,590)<br>
              • <strong>Est Cost:</strong> $0.00318 USD / Request
            </div>
          </div>

          <div class="trace-subcard">
            <div class="subcard-label">
              <span>Guardrails Executed & PII Redaction</span>
              <span class="badge badge-healthy">PASSED</span>
            </div>
            <div class="subcard-value">
              • <strong>Prompt Injection Detection:</strong> PASSED (0 Attacks)<br>
              • <strong>SQL Injection Check:</strong> PASSED (Sanitized)<br>
              • <strong>Toxicity / Moderation:</strong> PASSED (Clean)<br>
              • <strong>Domain Relevance Score:</strong> 0.96 / 1.00<br>
              • <strong>PII Masking Result:</strong><br>
                - <span class="pii-tag">[PII: EMAIL_REDACTED]</span><br>
                - <span class="pii-tag">[PII: SSN_REDACTED]</span>
            </div>
          </div>

          <div class="trace-subcard">
            <div class="subcard-label">
              <span>MCP Tools Executed (Port 5001)</span>
              <span class="badge badge-healthy">FastMCP Online</span>
            </div>
            <div class="subcard-value">
              • <span class="mcp-tag">mcp_query_project_plans</span> (Parsed XML/JSON WBS)<br>
              • <span class="mcp-tag">mcp_read_communication_logs</span> (Teams/Slack feeds)<br>
              • <span class="mcp-tag">mcp_fetch_risk_register</span> (External Threat Feeds)<br>
              • <span class="mcp-tag">mcp_update_mitigation_action</span> (Action Checklist)
            </div>
          </div>
        </div>

        <div class="trace-subcard" style="margin-top:16px;">
          <div class="subcard-label">
            <span>Dual RAG & Knowledge Graph Context Retrieved</span>
            <span class="badge badge-healthy">Static + GraphRAG</span>
          </div>
          <div class="subcard-value">
            • <strong>Static Document RAG:</strong> 21 Policy & SOW Chunks Indexed (Matches from <code>security_policy.txt</code> & <code>risk_sop.txt</code>)<br>
            • <strong>Knowledge Graph Triples:</strong><br>
              - <code>(Amit Joshi) --[SENT_MESSAGE_TO]--> (Rohit Verma)</code><br>
              - <code>(Third-Party Vendor API) --[IMPACTS_MILESTONE]--> (Design Review)</code><br>
              - <code>(Project Orion Upgrade) --[HAS_RISK_INDICATOR]--> (Schedule Delay)</code>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ExecutionTraceComponent {
  isTraceExpanded: boolean = true;

  toggleTrace(): void {
    this.isTraceExpanded = !this.isTraceExpanded;
  }
}
